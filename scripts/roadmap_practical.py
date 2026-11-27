"""Examples for the practical SQL chapter that follows the roadmap."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Table:
    title: str
    columns: tuple
    rows: tuple
    before: bool = False


@dataclass(frozen=True)
class Topic:
    anchor: str
    title: str
    group: str
    sql: str | dict
    tables: tuple | dict
    explanation: str
    requirements: str | dict = "只读查询。"
    links: tuple = ()


def output(columns, *rows, title="预期结果"):
    return Table(title, tuple(columns.split()), rows)


def before(name, columns, *rows):
    return Table("执行前 · " + name, tuple(columns.split()), rows, True)


def temporary_copy(name, query):
    return {
        "postgresql": f"CREATE TEMP TABLE {name} AS\n{query};",
        "mysql": f"CREATE TEMPORARY TABLE {name} AS\n{query};",
        "sqlserver": query.replace("\nFROM", f"\nINTO #{name}\nFROM", 1) + ";",
    }


def practical_topics(fixtures):
    def source(name, fields, **match):
        cols = fields.split()
        return before(name, fields, *(tuple(row[col] for col in cols) for row in fixtures[name]
                                      if all(row[col] == value for col, value in match.items())))

    orders = source("orders", "order_id customer_id ordered_on status")
    order_dates = source("orders", "order_id ordered_on")
    cities = source("customers", "customer_id city")
    items = source("order_items", "order_id product_id qty unit_price", order_id="101", product_id="1")

    yield Topic("alias", "AS 给列和表起别名", "查询写法",
                """SELECT i.qty * i.unit_price AS line_total
FROM @lab.order_items AS i
WHERE i.order_id = 101 AND i.product_id = 1;""",
                (items, output("line_total", ("40.00",))),
                "i 是本查询内的表别名，line_total 是结果列名。其他查询仍用底表原名。")
    yield Topic("alias-filter", "列别名 用派生表在 WHERE 中筛选", "查询写法",
                """SELECT x.order_id, x.line_total
FROM (
    SELECT order_id, qty * unit_price AS line_total
    FROM @lab.order_items WHERE order_id = 101
) AS x
WHERE x.line_total >= 20;""",
                (source("order_items", "order_id product_id qty unit_price", order_id="101"),
                 output("order_id line_total", (101, "40.00"))),
                "同层 ORDER BY 可以用结果列别名。要按计算值做 WHERE 筛选，先用派生表或 CTE 给表达式命名，外层就能用这个列名。")
    yield Topic("logic-order", "AND / OR 用括号明确筛选范围", "查询写法",
                """SELECT order_id
FROM @lab.orders
WHERE (customer_id = 1 OR customer_id = 2) AND status = 'pending'
ORDER BY order_id;""",
                (source("orders", "order_id customer_id status"), output("order_id", (102,))),
                "AND 的优先级高于 OR。括号让待付款条件同时约束两个客户，只返回 102。去掉括号后，客户 1 的 101、103 也会出现。")
    yield Topic("left-join-filter", "LEFT JOIN 在 ON 里限制右表", "查询写法",
                """SELECT c.customer_id, o.order_id
FROM @lab.customers AS c
LEFT JOIN @lab.orders AS o
    ON o.customer_id = c.customer_id AND o.status = 'pending'
ORDER BY c.customer_id;""",
                (source("customers", "customer_id name"), source("orders", "order_id customer_id status"),
                 output("customer_id order_id", (1, None), (2, 102), (3, None), (4, None))),
                "ON 决定哪些右表行可以匹配，保留全部客户。把右表状态条件挪到 WHERE，补出的 NULL 行会被过滤。")
    yield Topic("stable-top", "ORDER BY 用唯一键稳定取前 N 行", "查询写法",
                {
                    "postgresql": "SELECT order_id, ordered_on FROM @lab.orders\nORDER BY ordered_on DESC, order_id DESC LIMIT 2;",
                    "mysql": "SELECT order_id, ordered_on FROM @lab.orders\nORDER BY ordered_on DESC, order_id DESC LIMIT 2;",
                    "sqlserver": "SELECT TOP (2) order_id, ordered_on FROM @lab.orders\nORDER BY ordered_on DESC, order_id DESC;",
                },
                (order_dates, output("order_id ordered_on", (104, "2025-02-02"), (103, "2025-02-02"))),
                "两笔订单同一天时，唯一的 order_id 决定谁先显示。分页也应明确全部排序键。")
    yield Topic("literal-like", "LIKE ESCAPE 按字面查找百分号和下划线", "查询写法",
                """SELECT label FROM (
    SELECT 'save_10%' AS label UNION ALL SELECT 'saveX10x'
) AS samples
WHERE label LIKE '%!_10!%' ESCAPE '!';""",
                (before("samples", "label", ("save_10%",), ("saveX10x",)), output("label", ("save_10%",))),
                "未转义的 % 匹配任意长度，_ 匹配一个字符。本例用 ! 转义输入里的通配符。")

    yield Topic("where-null", "WHERE IS NULL 查缺失值", "NULL 与空白",
                "SELECT customer_id, city FROM @lab.customers WHERE city IS NULL;",
                (cities, output("customer_id city", (3, None))),
                "WHERE 只保留条件为 TRUE 的行。city = NULL 和 city <> '北京' 遇到 NULL 都得到 UNKNOWN。查已有城市用 IS NOT NULL。筛出非北京并包含缺失城市，可用 city <> '北京' OR city IS NULL。SQL Server 的 Unicode 字面量写成 N'北京'。")
    null_safe = {
        "postgresql": ("IS NOT DISTINCT FROM", ""),
        "sqlserver": ("IS NOT DISTINCT FROM", "N"),
        "mysql": ("<=>", ""),
    }
    yield Topic("null-safe", "NULL 安全比较 让两个缺失值相等", "NULL 与空白",
                {
                    mode: f"""WITH incoming AS (
    SELECT 1 AS customer_id, {prefix}'北京' AS city
    UNION ALL SELECT 2, NULL UNION ALL SELECT 3, NULL
)
SELECT c.customer_id, c.city, i.city AS incoming_city
FROM @lab.customers AS c JOIN incoming AS i ON i.customer_id = c.customer_id
WHERE c.city {operator} i.city ORDER BY c.customer_id;"""
                    for mode, (operator, prefix) in null_safe.items()
                },
                (cities, before("incoming", "customer_id city", (1, "北京"), (2, None), (3, None)),
                 output("customer_id city incoming_city", (1, "北京", "北京"), (3, None, None))),
                "这里找现有城市和导入城市一致的客户。客户 1 的城市相同，客户 3 两侧均缺失，都视为一致。客户 2 只有一侧缺失。",
                {"postgresql": "使用可访问练习表的查询连接。",
                 "sqlserver": "SQL Server 2022 或更新版本。",
                 "mysql": "使用可访问练习表的查询连接。"},
                (("PostgreSQL 比较谓词", "https://www.postgresql.org/docs/18/functions-comparison.html"),
                 ("SQL Server IS DISTINCT FROM", "https://learn.microsoft.com/en-us/sql/t-sql/queries/is-distinct-from-transact-sql")))
    yield Topic("count-null", "COUNT(*) 和 COUNT(列) 区分总行数与非空数", "NULL 与空白",
                "SELECT COUNT(*) AS customers, COUNT(city) AS known_city FROM @lab.customers;",
                (cities, output("customers known_city", (4, 3))),
                "COUNT(*) 数全部行。COUNT(city) 跳过 NULL，空字符串仍计入。")
    yield Topic("null-default", "COALESCE 给 NULL 设置显示值", "NULL 与空白",
                """SELECT customer_id, COALESCE(city, 'Unknown') AS displayed_city
FROM @lab.customers ORDER BY customer_id;""",
                (cities, output("customer_id displayed_city", (1, "北京"), (2, "上海"), (3, "Unknown"), (4, "北京"))),
                "从左到右取第一个非 NULL 的值。这里改的是查询显示，底表仍可用 IS NULL 查到缺失城市。")
    yield Topic("not-in-null", "NOT IN 遇到 NULL 时用 NOT EXISTS 查未匹配行", "NULL 与空白",
                """WITH exclusions AS (SELECT 2 AS customer_id UNION ALL SELECT NULL)
SELECT c.customer_id FROM @lab.customers AS c
WHERE c.customer_id NOT IN (SELECT customer_id FROM exclusions);

WITH exclusions AS (SELECT 2 AS customer_id UNION ALL SELECT NULL)
SELECT c.customer_id FROM @lab.customers AS c
WHERE NOT EXISTS (SELECT 1 FROM exclusions AS e WHERE e.customer_id = c.customer_id)
ORDER BY c.customer_id;""",
                (source("customers", "customer_id"), before("exclusions", "customer_id", (2,), (None,)),
                 output("customer_id", title="NOT IN 的结果"),
                 output("customer_id", (1,), (3,), (4,), title="NOT EXISTS 的结果")),
                "列表中含 NULL 时，没找到等值也无法断定“不在列表里”。NOT EXISTS 直接检查是否存在相等的排除项。")
    yield Topic("trim-blanks", "TRIM + NULLIF 清理首尾空格并识别空白值", "NULL 与空白",
                "SELECT TRIM('  Ana  ') AS clean_name,\n"
                "       NULLIF(TRIM('   '), '') AS missing_text;",
                (before("字符串参数", "name_text blank_text", ("␠␠Ana␠␠", "␠␠␠")),
                 output("clean_name missing_text", ("Ana", None))),
                "␠ 表示普通空格。TRIM 默认去除首尾的普通空格；全空格清理后可用 NULLIF 归一为 NULL。")
    control_chars = {
        "postgresql": ("chr(9)", "chr(160)", ""),
        "mysql": ("CHAR(9 USING utf8mb4)", "CONVERT(0xC2A0 USING utf8mb4)", ""),
        "sqlserver": ("NCHAR(9)", "NCHAR(160)", "N"),
    }
    yield Topic("invisible-space", "REPLACE 清理 Tab 和不换行空格", "NULL 与空白",
                {
                    mode: f"SELECT TRIM(REPLACE(REPLACE(raw_text, {tab}, ' '), {nbsp}, ' ')) AS clean_name\n"
                          f"FROM (SELECT CONCAT({tab}, {prefix}'Ana', {nbsp}) AS raw_text) AS s;"
                    for mode, (tab, nbsp, prefix) in control_chars.items()
                },
                (before("字符串参数", "raw_text", ("[Tab]Ana[NBSP]",)), output("clean_name", ("Ana",))),
                "先把制表符和不换行空格换成普通空格，再 TRIM。中间的普通空格会保留；换行符可用相同办法处理。")
    yield Topic("string-length", "字符数、字节数与尾随空格", "NULL 与空白",
                {
                    "postgresql": "SELECT CHAR_LENGTH('A ') AS chars, OCTET_LENGTH('A ') AS bytes;",
                    "mysql": "SELECT CHAR_LENGTH('A ') AS chars, LENGTH('A ') AS bytes;",
                    "sqlserver": "SELECT LEN(N'A ') AS len_result,\n       LEN(CONCAT(N'A ', N'_')) - 1 AS chars, DATALENGTH(N'A ') AS bytes;",
                },
                {
                    "postgresql": (before("字符串参数", "text", ("A␠",)), output("chars bytes", (2, 2))),
                    "mysql": (before("字符串参数", "text", ("A␠",)), output("chars bytes", (2, 2))),
                    "sqlserver": (before("nvarchar 字符串", "text", ("A␠",)), output("len_result chars bytes", (1, 2, 4))),
                },
                "␠ 表示尾随空格。SQL Server 的 LEN 跳过尾随空格，拼接非空格字符再减 1 可保留它。字节数随编码与数据类型变化。")

    yield Topic("numeric-division", "CAST 先转小数再相除", "数值与日期时间",
                """SELECT CAST(CAST(qty AS DECIMAL(8,2)) / 3 AS DECIMAL(8,2)) AS qty_per_box
FROM @lab.order_items WHERE order_id = 101 AND product_id = 1;""",
                (items, output("qty_per_box", ("0.67",))),
                "在除法前转换操作数，除法后再统一输出精度。PostgreSQL 与 SQL Server 两个整数相除会截断，MySQL 的 / 和 DIV 有不同语义。")
    yield Topic("date-range", "日期时间 WHERE 用半开区间筛整天或整月", "数值与日期时间",
                """SELECT order_id, ordered_on FROM @lab.orders
WHERE ordered_on >= CAST('20250201' AS DATE)
  AND ordered_on < CAST('20250301' AS DATE)
ORDER BY ordered_on, order_id;""",
                (order_dates, output("order_id ordered_on", (102, "2025-02-01"), (103, "2025-02-02"), (104, "2025-02-02"))),
                "包含起点、排除下一段的起点。时间戳列也可用这一思路覆盖最后一天所有时刻；边界参数应使用与列相容的日期时间类型。")
    month = {
        "postgresql": "CAST(date_trunc('month', CAST(ordered_on AS timestamp)) AS DATE)",
        "mysql": "CAST(DATE_FORMAT(ordered_on, '%Y-%m-01') AS DATE)",
        "sqlserver": "DATEFROMPARTS(YEAR(ordered_on), MONTH(ordered_on), 1)",
    }
    yield Topic("month-group", "按月分组 用月初日期作为分组键", "数值与日期时间",
                {mode: f"SELECT {expr} AS month_start, COUNT(*) AS order_count\n"
                       f"FROM @lab.orders GROUP BY {expr} ORDER BY month_start;"
                 for mode, expr in month.items()},
                (order_dates, output("month_start order_count", ("2025-01-01", 1), ("2025-02-01", 3))),
                "月初日期同时包含年和月，可按时间顺序排序。要先筛某个时间范围时，用原日期列和半开区间。")
    date_format = {
        "postgresql": "TO_CHAR(ordered_on, 'YYYY/MM/DD')",
        "mysql": "DATE_FORMAT(ordered_on, '%Y/%m/%d')",
        "sqlserver": "CONVERT(char(10), ordered_on, 111)",
    }
    yield Topic("date-display", "日期格式化 在输出时转换为文本", "数值与日期时间",
                {mode: f"SELECT {expr} AS display_date FROM @lab.orders\nWHERE order_id = 102;"
                 for mode, expr in date_format.items()},
                (source("orders", "order_id ordered_on", order_id="102"), output("display_date", ("2025/02/01",))),
                "按日期类型筛选、排序和计算，最后在 SELECT 中转为显示文本。日期解析时也应明确输入格式。")
    yield Topic("time-zone", "时区转换 将东京本地时间换算为 UTC", "数值与日期时间",
                {
                    "postgresql": "SELECT (TIMESTAMP '2025-02-01 09:00:00' AT TIME ZONE 'Asia/Tokyo')\n"
                                  "       AT TIME ZONE 'UTC' AS utc_value;",
                    "mysql": "SELECT CONVERT_TZ('2025-02-01 09:00:00', '+09:00', '+00:00') AS utc_value;",
                    "sqlserver": "SELECT CAST(CAST('2025-02-01T09:00:00' AS datetime2(0))\n"
                                 "       AT TIME ZONE 'Tokyo Standard Time' AT TIME ZONE 'UTC' AS datetime2(0)) AS utc_value;",
                },
                (before("时间参数", "local_time zone", ("2025-02-01 09:00:00", "东京（UTC+09:00）")),
                 output("utc_value", ("2025-02-01 00:00:00",))),
                "先指定源时间的时区，再转换到目标时区。存储时间点时约定 UTC；涉及夏令时的地区应使用具备规则的命名时区，MySQL 使用命名时区需加载时区表。",
                requirements={"postgresql": "只读查询。", "mysql": "示例使用 UTC 偏移量。",
                              "sqlserver": "SQL Server 2016+。可在 sys.time_zone_info 核对时区名称。"},
                links=(("PostgreSQL 日期时间函数", "https://www.postgresql.org/docs/18/functions-datetime.html"),
                       ("SQL Server AT TIME ZONE", "https://learn.microsoft.com/en-us/sql/t-sql/queries/at-time-zone-transact-sql"),
                       ("MySQL CONVERT_TZ", "https://dev.mysql.com/doc/refman/8.4/en/date-and-time-functions.html")))

    yield merge_topic(fixtures)
    yield from index_topics(orders)


def merge_topic(fixtures):
    sql = {}
    for mode, create, table in (
        ("postgresql", "CREATE TEMP TABLE", "rv2_order_sync"),
        ("sqlserver", "CREATE TABLE", "#rv2_order_sync"),
        ("mysql", "CREATE TEMPORARY TABLE", "rv2_order_sync"),
    ):
        sql[mode] = (
            f"{create} {table} (order_id INT PRIMARY KEY, status VARCHAR(12));\n"
            f"INSERT INTO {table} SELECT order_id, status FROM @lab.orders WHERE order_id IN (101, 102);\n\n"
        )
        if mode == "mysql":
            sql[mode] += (
                f"INSERT INTO {table} (order_id, status)\n"
                "VALUES (102, 'paid'), (105, 'pending') AS incoming\n"
                "ON DUPLICATE KEY UPDATE status = incoming.status;\n"
            )
        else:
            sql[mode] += (
                f"MERGE INTO {table} AS t\n"
                "USING (VALUES (102, 'paid'), (105, 'pending')) AS s(order_id, status)\n"
                "ON t.order_id = s.order_id\n"
                "WHEN MATCHED THEN UPDATE SET status = s.status\n"
                "WHEN NOT MATCHED THEN INSERT (order_id, status) VALUES (s.order_id, s.status);\n"
            )
        sql[mode] += f"SELECT order_id, status FROM {table} ORDER BY order_id;"
    existing = tuple((row["order_id"], row["status"]) for row in fixtures["orders"]
                     if row["order_id"] in {"101", "102"})
    return Topic(
        "merge", "MERGE / UPSERT 按订单号更新或插入", "数据同步",
        sql,
        (before("同步目标（临时表）", "order_id status", *existing),
         before("同步来源", "order_id status", (102, "paid"), (105, "pending")),
         output("order_id status", (101, "paid"), (102, "paid"), (105, "pending"), title="同步后")),
        "ON 用订单号识别同一行。来源 102 已存在便更新，105 尚未存在便插入，目标 101 保持原值。每个来源键应只有一行。MySQL 方案由主键或唯一键冲突触发。需要用 WHEN NOT MATCHED BY SOURCE 处理缺失目标时，先核对来源是否为完整快照。",
        {
            "postgresql": "PostgreSQL 15+。使用允许创建临时表的新连接。",
            "mysql": "MySQL 8.0.19+。使用主键触发的 UPSERT，需有创建临时表权限。",
            "sqlserver": "使用允许创建临时表的新连接。MERGE 语句以分号结束。",
        },
        (
            ("PostgreSQL MERGE", "https://www.postgresql.org/docs/18/sql-merge.html"),
            ("SQL Server MERGE", "https://learn.microsoft.com/en-us/sql/t-sql/statements/merge-transact-sql"),
            ("MySQL ON DUPLICATE KEY UPDATE", "https://dev.mysql.com/doc/refman/8.4/en/insert-on-duplicate.html"),
            ("PostgreSQL 停用缺失行示例", "../reference/33-postgresql-write.html#merge-action"),
            ("SQL Server 停用缺失行示例", "../reference/36-sqlserver-write.html#merge-source"),
        ),
    )


def index_topics(orders):
    predicate = "WHERE customer_id = 1 AND ordered_on >= CAST('20250201' AS DATE)\nORDER BY ordered_on, order_id;"
    cols = "order_id ordered_on"
    matched = output(cols, (103, "2025-02-02"))
    yield Topic(
        "index-choice", "选择索引 先看等值列、范围列和排序", "索引实操",
        "SELECT order_id, ordered_on FROM @lab.orders\n" + predicate, (orders, matched),
        "从频繁查询出发。本例先以 customer_id 等值定位，再对 ordered_on 做范围扫描，order_id 是并列时的排序键，因此可试 (customer_id, ordered_on, order_id)。常见 B-tree 对左侧键约束较强时更容易缩小扫描范围。还要衡量选择性、写入成本和已有索引。",
        links=(("PostgreSQL 多列索引", "https://www.postgresql.org/docs/18/indexes-multicolumn.html"),
               ("SQL Server 索引设计指南", "https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-index-design-guide"))
    )
    copies = temporary_copy("rv2_index_orders", "SELECT order_id, customer_id, ordered_on\nFROM @lab.orders")
    index_sql = {}
    for mode, setup in copies.items():
        table = "#rv2_index_orders" if mode == "sqlserver" else "rv2_index_orders"
        index_sql[mode] = (
            f"{setup}\nCREATE INDEX ix_rv2_customer_date ON {table} (customer_id, ordered_on, order_id);\n"
            f"SELECT order_id, ordered_on FROM {table}\n{predicate}"
        )
    yield Topic(
        "index-create", "CREATE INDEX 把多列索引建到查询对象上", "索引实操",
        index_sql, (orders, matched),
        "索引属于被查询的表。这段先复制练习订单，再在临时表上建索引。索引改变的是访问路径，查询仍返回订单 103。对已有业务表应先检查现有索引定义和执行计划。",
        "使用可创建临时表的新连接。同一会话重复练习时，另开连接可重新创建临时表。",
        (("第 11 章 · 查看和删除索引", "11-indexes.html#indexes"),)
    )
    sample_query = """SELECT o.order_id, ROW_NUMBER() OVER (ORDER BY o.order_id) AS sample_id
FROM @lab.orders AS o
CROSS JOIN @lab.order_items AS a CROSS JOIN @lab.order_items AS b
CROSS JOIN @lab.order_items AS c CROSS JOIN @lab.order_items AS d"""
    plan_sql = {}
    for mode, setup in temporary_copy("rv2_plan_orders", sample_query).items():
        table = "#rv2_plan_orders" if mode == "sqlserver" else "rv2_plan_orders"
        query = f"SELECT order_id FROM {table} WHERE sample_id = 1;"
        index = f"CREATE INDEX ix_rv2_sample ON {table} (sample_id);"
        if mode == "postgresql":
            analyze = "EXPLAIN (ANALYZE, BUFFERS, COSTS OFF) "
            plan_sql[mode] = f"{setup}\nANALYZE {table};\n{analyze}{query}\n{index}\n{analyze}{query}"
        elif mode == "mysql":
            plan_sql[mode] = f"{setup}\nEXPLAIN ANALYZE {query}\n{index}\nEXPLAIN ANALYZE {query}"
        else:
            plan_sql[mode] = f"{setup}\nSET STATISTICS IO ON;\n{query}\n{index}\n{query}\nSET STATISTICS IO OFF;"
    yield Topic(
        "index-verify", "执行计划 对比加索引前后的实际读数", "索引实操",
        plan_sql,
        {
            "postgresql": (
                before("练习复制表（前两行，共 2500 行）", "sample_id order_id", (1, 101), (2, 101)),
                output("阶段 实际访问路径 输出行数",
                       ("建索引前", "Seq Scan，过滤掉 2499 行", 1),
                       ("建索引后", "Index Scan using ix_rv2_sample", 1),
                       title="PostgreSQL 19.0 · 实测节选"),
            ),
            "mysql": (
                before("练习复制表（前两行，共 2500 行）", "sample_id order_id", (1, 101), (2, 101)),
                output("阶段 实际访问路径 输出行数",
                       ("建索引前", "Table scan，读取 2500 行后过滤", 1),
                       ("建索引后", "Index lookup using ix_rv2_sample", 1),
                       title="MySQL 9.5.0 · 实测节选"),
            ),
            "sqlserver": (
                before("练习复制表（前两行，共 2500 行）", "sample_id order_id", (1, 101), (2, 101)),
                output("阶段 order_id 计划观察",
                       ("建索引前", 101, "查看扫描节点和 logical reads"),
                       ("建索引后", 101, "检查是否用 ix_rv2_sample 查找"),
                       title="SQL Server · 预期结果与观察项"),
            ),
        },
        "用同一个连接和参数跑两次查询。PostgreSQL 看实际行数与 Buffers，MySQL 看实际行数与访问节点，SQL Server 看实际计划与 Messages 的 logical reads。计划和读数受数据分布、统计信息及缓存影响，记录实际观测后再判断收益。",
        {
            "postgresql": "使用可创建临时表的新连接。EXPLAIN ANALYZE 会执行这里的只读查询。",
            "mysql": "MySQL 8.0.18+。使用可创建临时表的新连接。",
            "sqlserver": "在 SSMS 中启用「包括实际执行计划」（Ctrl+M），账号需有 SHOWPLAN 权限。在同一新连接中按序运行。",
        },
        (
            ("PostgreSQL EXPLAIN", "https://www.postgresql.org/docs/18/sql-explain.html"),
            ("MySQL EXPLAIN ANALYZE", "https://dev.mysql.com/doc/refman/8.4/en/explain.html"),
            ("SQL Server 查看实际执行计划", "https://learn.microsoft.com/en-us/sql/relational-databases/performance/display-an-actual-execution-plan"),
        ),
    )
