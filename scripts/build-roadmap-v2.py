"""Generate the 16-stage HTML reference edition from the roadmap and existing examples."""

import csv
from html import escape, unescape
from itertools import groupby
from pathlib import Path
import re

from roadmap_practical import practical_topics


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "roadmap-v2"
ENGINES = {
    "postgresql": ("PostgreSQL", "sql_notes_lab.", "postgres（sql_notes_lab 模式）", "#setup-postgresql"),
    "sqlserver": ("SQL Server", "dbo.", "SQLNotesLab", "#setup-sqlserver"),
    "mysql": ("MySQL", "", "learn_sql_lab", "#setup"),
}
STAGES = (
    ("relational", "relational rdbms nosql", "订单 101 和 103 是否属于同一客户？", "是，两行的 customer_id 都是 1。"),
    ("syntax", "keywords data-types operators select insert delete update", "哪一个关键字用于修改现有行？", "UPDATE，配合 WHERE 缩小范围。"),
    ("ddl", "truncate-table alter-table create-table drop-table", "什么命令清空数据但保留字段？", "TRUNCATE TABLE。"),
    ("dml", "select from where join group-by order-by having insert update delete", "对组数目设门槛时用哪个关键字？", "HAVING 可按聚合结果保留组。"),
    ("aggregates", "sum count avg min max group-by having", "把 SUM(qty) 改成 COUNT(*) 会统计什么？", "明细行数。练习数据有 5 行，总数量为 8。"),
    ("constraints", "primary-key foreign-key unique not-null check", "哪个约束保证明细对应的订单存在？", "订单号外键。"),
    ("joins", "inner-join left-join right-join full-join self-join cross-join", "怎样保留没有下单的客户？", "把 customers 放在 LEFT JOIN 左侧。"),
    ("subqueries", "scalar column row derived nested correlated", "哪类子查询会引用外层查询的别名？", "相关子查询。"),
    ("functions", "concat length substring replace upper lower floor abs mod round ceiling case nullif coalesce date time timestamp datepart dateadd", "怎样避免分母为 0 的除法？", "使用 NULLIF(分母, 0)，使分母为零时结果为 NULL。"),
    ("views", "view-create view-change view-drop", "修改视图定义会改变订单表里的状态吗？", "订单行保持原值，新的视图查询按更新后的定义返回。"),
    ("indexes", "indexes query-optimization", "有索引的小表在计划中仍可能全表扫描吗？", "可能，优化器会按代价选择访问方式。"),
    ("transactions", "begin commit rollback savepoint acid isolation", "想保留保存点之前的修改，要回滚到哪里？", "回滚到指定保存点，确认后再决定是否提交。"),
    ("integrity-security", "integrity grant-revoke security", "哪条命令可以收回已授予的 SELECT 权限？", "REVOKE。还需检查是否有其他授权来源。"),
    ("routines", "procedure function", "哪一种例程可以放进 SELECT 表达式取值？", "本章的标量存储函数。"),
    ("performance", "analysis use-index efficient-join reduce-subquery projection", "只需要状态时要查哪些列？", "只选 status，过滤可以继续用 order_id。"),
    ("advanced", "window rank dense-rank lead lag row-number first-value recursive pivot cte dynamic", "哪两个排名函数对并列后的下一位处理不同？", "RANK 会跳号，DENSE_RANK 连续编号。"),
)
PRACTICAL_NAME = "SQL 实务细节"
NEW_LABELS = {
    "nosql": "SQL 与 NoSQL 对照关系行与文档", "join": "JOIN 为订单带出客户",
    "procedure": "存储过程按参数读取明细", "function": "存储函数在 SELECT 中取值",
    "window": "窗口函数 OVER 保留明细并汇总",
}
DIV = re.compile(r'<div data-dialects="(postgresql|sqlserver|mysql)">')
LINK = re.compile(r'href="([^"/:#]+\.html(?:#[^"]*)?)"')
SQL = re.compile(r'<figure>.*?<pre><code>(.*?)</code></pre></figure>', re.S)
RESULT_CAPTION = re.compile(
    r'<caption class="sql-statement-caption"><span class="sql-caption-line">'
    r'<code>.*?</code><span class="sql-caption-context">([^<]+)</span></span></caption>', re.S,
)
FIXTURE_PROJECTIONS = (
    ("rdbms self-join window", "orders", "order_id customer_id", {}),
    ("relational", "orders", "order_id customer_id", {"order_id": "101"}),
    ("keywords scalar indexes query-optimization foreign-key", "orders", "order_id", {}),
    ("select", "orders", "order_id customer_id ordered_on status", {"order_id": "101"}),
    ("case projection begin", "orders", "order_id status", {"order_id": "101"}),
    ("rollback savepoint isolation dynamic", "orders", "order_id status", {"order_id": "102"}),
    ("where group-by having cte pivot view-create", "orders", "order_id status", {}),
    ("order-by rank dense-rank", "orders", "order_id ordered_on", {}),
    ("date datepart dateadd", "orders", "order_id ordered_on", {"order_id": "101"}),
    ("lead lag row-number first-value", "orders", "order_id customer_id ordered_on", {"customer_id": "1"}),
    ("join inner-join efficient-join", "orders", "order_id customer_id", {"order_id": "102"}),
    ("join inner-join efficient-join", "customers", "customer_id name", {}),
    ("left-join right-join", "orders", "order_id customer_id", {}),
    ("left-join right-join", "customers", "customer_id name", {"customer_id": "4"}),
    ("cross-join", "customers", "customer_id name", {"customer_id": ("1", "2")}),
    ("cross-join", "products", "product_id name", {"product_id": "4"}),
    ("column correlated", "orders", "order_id customer_id status", {}),
    ("column correlated nested", "customers", "customer_id name", {}),
    ("nested", "orders", "order_id customer_id", {}),
    ("nested", "order_items", "order_id product_id", {}),
    ("coalesce", "customers", "customer_id city", {"customer_id": "3"}),
    ("from count derived integrity", "order_items", "order_id product_id", {}),
    ("integrity reduce-subquery", "orders", "order_id", {}),
    ("sum avg min max row reduce-subquery", "order_items", "order_id product_id qty", {}),
    ("analysis use-index", "order_items", "order_id product_id", {}),
    ("acid", "order_items", "order_id product_id qty", {"order_id": "101"}),
    ("operators", "order_items", "order_id product_id qty unit_price", {"order_id": "101", "product_id": "1"}),
    ("procedure function", "order_items", "order_id product_id qty", {"order_id": "101", "product_id": "1"}),
)


def route():
    text = (ROOT / "SQL-ROADMAP.md").read_text(encoding="utf-8")
    chapters = re.split(r"(?m)^## \d{2} (.+)\n", text)[1:]
    line = re.compile(r"(?m)^### (.+)$|^( *)- \[ \] (?:\*\*(.+?)\*\*|(.+?))　(.+)$")
    chapter_items = []
    for heading, body in zip(chapters[::2], chapters[1::2]):
        group = ""
        entries = []
        for group_heading, indent, strong, inline, purpose in line.findall(body):
            if group_heading:
                group = group_heading
            else:
                entries.append(((strong or inline).replace(chr(96), ""), purpose, group, bool(indent)))
        chapter_items.append((heading, entries))
    return chapter_items


def legacy_points():
    sections, labels = {}, {}
    for path in sorted((ROOT / "reference").glob("sql-roadmap-0*.html")):
        text = path.read_text(encoding="utf-8")
        sections.update((anchor, LINK.sub(r'href="../reference/\1"', body)) for anchor, body in
                        re.findall(r'<section class="point" id="([^"]+)"[^>]*>(.*?)</section>', text, re.S))
        jump = re.search(r'<nav class="jump".*?</nav>', text, re.S)[0]
        labels.update((anchor, unescape(label)) for anchor, label in re.findall(r'<a href="#([^"]+)">([^<]+)</a>', jump))
    labels.update(NEW_LABELS)
    return sections, labels


def figure(sql, engine):
    return f'<figure><figcaption>SQL · {engine}</figcaption><pre><code>{escape(sql, quote=False)}</code></pre></figure>'


def result(sql, columns, rows, label="预期结果"):
    caption = f'<caption>{escape(label)}</caption>'
    grid_class = "sql-grid-viewport sql-input-grid" if sql is None else "sql-grid-viewport"
    if sql:
        statement = escape(sql, quote=False)
        caption = (f'<caption class="sql-statement-caption"><span class="sql-caption-line"><code>{statement}</code>'
                   f'<span class="sql-caption-context">{escape(label)}</span></span></caption>')
    head = "".join(f'<th scope="col">{escape(column)}</th>' for column in columns)
    body = "".join(
        "<tr>" + "".join(f'<td class="sql-null"><code>NULL</code></td>' if value is None
                         else f"<td><code>{escape(str(value))}</code></td>" for value in row) + "</tr>"
        for row in rows
    )
    if not rows:
        body = f'<tr><td colspan="{len(columns)}">0 行</td></tr>'
    return f'''<div class="{grid_class}" role="region" aria-label="{escape(label)}" tabindex="0">
<table class="sql-result">
{caption}
<thead><tr>{head}</tr></thead><tbody>{body}</tbody>
</table></div>'''


def variant(mode, sql, tables, extra="", *, uses_lab=True):
    engine, _, database, setup = ENGINES[mode]
    positions = {
        "postgresql": "PostgreSQL 查询窗口或 psql 提示符", "mysql": "MySQL 查询窗口或 mysql 提示符",
        "sqlserver": "SSMS 查询窗口或 sqlcmd 提示符，GO 分隔批次" if "\nGO\n" in sql else "SQL Server 查询窗口",
    }
    setup_note = (f'已<a href="../lessons/0001-first-query.html{setup}">导入订单练习数据</a>'
                  f'并连接到 <code>{database}</code>。') if uses_lab else "使用已连接的查询窗口。"
    return f'''<div data-dialects="{mode}">
{figure(sql, engine)}
<p class="sql-input-note"><strong>执行位置</strong> {positions[mode]}<br>
<strong>前提</strong> {setup_note}{extra}</p>
{chr(10).join(tables)}
</div>'''


def writes(key):
    for mode, (_, schema, _, _) in ENGINES.items():
        table = f"{schema}order_items"
        if key == "insert":
            target, before, after = "order_id = 102 AND product_id = 4", [], [(102, 4, 1)]
            change = f"INSERT INTO {table} (order_id, product_id, qty, unit_price)\nVALUES (102, 4, 1, 5.00);"
        else:
            target, before = "order_id = 101 AND product_id = 1", [(101, 1, 2)]
            if key == "update":
                after = [(101, 1, 3)]
                change = f"UPDATE {table} SET qty = 3\nWHERE {target};"
            else:
                after = []
                change = f"DELETE FROM {table}\nWHERE {target};"
        query = f"SELECT order_id, product_id, qty\nFROM {table} WHERE {target};"
        begin = {"postgresql": "BEGIN;", "mysql": "START TRANSACTION;", "sqlserver": "BEGIN TRANSACTION;"}[mode]
        rollback = "ROLLBACK TRANSACTION;" if mode == "sqlserver" else "ROLLBACK;"
        sql = "\n".join((begin, query, change, query, rollback, query))
        columns = ("order_id", "product_id", "qty")
        tables = [
            result(None, columns, before, "执行前 · order_items（目标记录）"),
            result(query, columns, after, "预期结果 · 操作后"),
            result(query, columns, before, "预期结果 · 回滚后"),
        ]
        yield variant(mode, sql, tables, f"使用没有打开事务的新连接。需要 SELECT 和 {key.upper()} 权限。第一条查询结果与表格一致时，再执行修改及后续验证。")


def basic_write(key):
    for mode, (_, schema, _, _) in ENGINES.items():
        marker = "1 = 0" if key == "insert" else "order_id = 101"
        table = f"rv2_basic_{key}"
        if mode == "sqlserver":
            table = "#" + table
            setup = f"SELECT order_id, status INTO {table} FROM {schema}orders WHERE {marker};"
        else:
            temp = "TEMP" if mode == "postgresql" else "TEMPORARY"
            setup = f"CREATE {temp} TABLE {table} AS\nSELECT order_id, status FROM {schema}orders WHERE {marker};"
        changes = {
            "insert": f"INSERT INTO {table} (order_id, status) VALUES (101, 'paid');",
            "delete": f"DELETE FROM {table} WHERE order_id = 101;",
            "update": f"UPDATE {table} SET status = 'pending' WHERE order_id = 101;",
        }
        rows = {"insert": [(101, "paid")], "delete": [], "update": [(101, "pending")]}[key]
        query = f"SELECT order_id, status FROM {table};"
        extra = "在有临时表权限的新连接中运行。第一步从订单表建立临时表，关闭连接后可重新练习。"
        yield variant(mode, "\n".join((setup, changes[key], query)),
                      [result(query, ("order_id", "status"), rows)], extra)
    yield f'<p>本例只写入当前会话的临时表。<a href="04-dml.html#{key}">第 04 阶段</a>展示在订单明细上修改并回滚。</p>'


def compare_nosql():
    for mode, (_, schema, _, _) in ENGINES.items():
        before = f"SELECT order_id, status FROM {schema}orders WHERE order_id = 101;"
        if mode == "sqlserver":
            after = f"SELECT (SELECT order_id, status FROM {schema}orders WHERE order_id = 101\n  FOR JSON PATH, WITHOUT_ARRAY_WRAPPER) AS order_document;"
        else:
            fn = "jsonb_build_object" if mode == "postgresql" else "JSON_OBJECT"
            after = f"SELECT {fn}('order_id', order_id, 'status', status) AS order_document\nFROM {schema}orders WHERE order_id = 101;"
        yield variant(mode, f"{before}\n{after}", [
            result(None, ("order_id", "status"), [(101, "paid")], "执行前 · orders（订单 101）"),
            result(after, ("order_document",), [('{"order_id":101,"status":"paid"}',)], "预期结果 · 文档字段"),
        ])
    yield '<p>关系表把值放在固定字段中。文档模型把相关字段组织在一个对象里，可包含数组或嵌套对象。第二条 SQL 展示同一笔订单的文档投影，键的顺序和空格可因方言而异。</p>'


def window_intro():
    for mode, (_, schema, _, _) in ENGINES.items():
        sql = (f"SELECT order_id, customer_id, COUNT(*) OVER (PARTITION BY customer_id) AS customer_orders\n"
               f"FROM {schema}orders ORDER BY order_id;")
        yield variant(mode, sql, [result(sql, ("order_id", "customer_id", "customer_orders"),
                                         [(101, 1, 2), (102, 2, 1), (103, 1, 2), (104, 3, 1)])])
    yield '<p><code>OVER</code> 指定计算范围。客户 1 的两笔订单各保留一行，两行都读到该客户的订单数 2。</p>'


def cross_join():
    for mode, (_, schema, _, _) in ENGINES.items():
        sql = (f"SELECT c.name, p.name AS product FROM {schema}customers AS c\n"
               f"CROSS JOIN {schema}products AS p\n"
               "WHERE c.customer_id IN (1, 2) AND p.product_id = 4 ORDER BY c.customer_id;")
        yield variant(mode, sql, [result(sql, ("name", "product"), [("Ana", "Pen"), ("Bo", "Pen")])])
    yield '<p>两名客户分别和同一件商品配对，得到 2 × 1 = 2 行。</p>'


def split_variants(section):
    starts = list(DIV.finditer(section))
    return [
        (match[1], section[match.start():starts[i+1].start() if i+1 < len(starts) else len(section)])
        for i, match in enumerate(starts)
    ]


def routine(key):
    for mode, (_, schema, _, _) in ENGINES.items():
        name = f"{schema}rv2_qty_{key}"
        parameter = {"postgresql": "p_order", "sqlserver": "@id", "mysql": "p_order"}[mode]
        fetch = f"SELECT qty FROM {schema}order_items WHERE order_id = {parameter} AND product_id = 1"
        if key == "procedure":
            query = f"CALL {name}(101);" if mode != "sqlserver" else f"EXEC {name} 101;"
            definitions = {
                "postgresql": f"CREATE PROCEDURE {name}(p_order INT, INOUT qty INT)\nLANGUAGE SQL AS $$ {fetch} $$;",
                "sqlserver": f"CREATE PROCEDURE {name} @id INT AS\n{fetch};\nGO",
                "mysql": f"CREATE PROCEDURE {name}(IN p_order INT)\n{fetch};",
            }
            if mode == "postgresql":
                query = f"CALL {name}(101, NULL);"
            suffix = "(INT, INT)" if mode == "postgresql" else ""
        else:
            query = f"SELECT {name}(101) AS qty;"
            definitions = {
                "postgresql": f"CREATE FUNCTION {name}(p_order INT) RETURNS INT\nLANGUAGE SQL AS $$ {fetch} $$;",
                "sqlserver": (f"CREATE FUNCTION {name}(@id INT) RETURNS INT AS\n"
                              f"BEGIN RETURN ({fetch}); END;\nGO"),
                "mysql": f"CREATE FUNCTION {name}(p_order INT) RETURNS INT\nREADS SQL DATA RETURN ({fetch});",
            }
            suffix = "(INT)" if mode == "postgresql" else ""
        extra = "使用新连接和未占用的例程名。先执行 CREATE，成功后再调用和清理。"
        privileges = {
            "postgresql": "需有模式的 CREATE 权限及练习表的读取权限。创建者可以调用本例。",
            "sqlserver": f"需有数据库的 CREATE {key.upper()} 权限、dbo 模式的 ALTER 权限及读取权。",
            "mysql": "需有 CREATE ROUTINE、EXECUTE、ALTER ROUTINE 和练习表的读取权限。",
        }
        if mode == "mysql" and key == "function":
            extra += '二进制日志开启时，创建函数的账号还需满足<a href="https://dev.mysql.com/doc/refman/8.4/en/stored-programs-logging.html">存储函数日志规则</a>。'
        code = f"{definitions[mode]}\n{query}\nDROP {key.upper()} {name}{suffix};"
        yield variant(mode, code, [result(query, ("qty",), [(2,)])], extra + privileges[mode])
    yield ('<p>过程由 <code>CALL</code> 或 <code>EXEC</code> 执行。PostgreSQL 通过输出参数返回数量。</p>'
           if key == "procedure" else '<p>标量函数可以在 <code>SELECT</code> 的表达式中返回一个值。</p>')
    yield '''<p class="sources"><a href="https://www.postgresql.org/docs/18/sql-call.html">PostgreSQL CALL</a> ·
<a href="https://learn.microsoft.com/en-us/sql/t-sql/statements/create-function-transact-sql">Microsoft Learn 例程</a> ·
<a href="https://dev.mysql.com/doc/refman/8.4/en/create-procedure.html">MySQL 例程</a></p>'''


def constraint(key, source):
    for mode, (_, schema, _, _) in ENGINES.items():
        if key == "foreign-key":
            table = f"{schema}rv2_order_ref"
            suffix = " ENGINE=InnoDB" if mode == "mysql" else ""
            code = (f"CREATE TABLE {table} (\n"
                    f"  order_id INT NOT NULL, FOREIGN KEY (order_id) REFERENCES {schema}orders(order_id)\n"
                    f"){suffix};\nINSERT INTO {table} (order_id) VALUES (101);")
            query = f"SELECT order_id FROM {table};"
            yield variant(mode, f"{code}\n{query}\nDROP TABLE {table};",
                          [result(query, ("order_id",), [(101,)])],
                          "在专用练习库使用未占用的表名。账号需能创建和删除该表，并有 orders 的 REFERENCES 权限。确认 CREATE 成功后再执行其余语句。")
            continue
        table = ("#" if mode == "sqlserver" else "") + f"rv2_{key.replace('-', '_')}"
        rule = {"primary-key": "id INT PRIMARY KEY", "unique": "id INT UNIQUE",
                "not-null": "id INT NOT NULL", "check": "id INT CHECK (id > 0)"}[key]
        create = {"postgresql": "CREATE TEMP TABLE", "mysql": "CREATE TEMPORARY TABLE", "sqlserver": "CREATE TABLE"}[mode]
        drop = "DROP TEMPORARY TABLE" if mode == "mysql" else "DROP TABLE"
        query = f"SELECT id FROM {table};"
        sql = f"{create} {table} ({rule});\nINSERT INTO {table} VALUES (1);\n{query}\n{drop} {table};"
        yield variant(mode, sql, [result(query, ("id",), [(1,)])], "使用可创建临时表的新连接。")
    yield ("<details><summary>进阶 · 观察约束拒绝非法行</summary>\n"
           f"{source}\n</details>")


def pivot(source):
    advanced = []
    for mode, block in split_variants(source):
        sql = unescape(SQL.search(block)[1])
        pivot_sql, unpivot_sql = sql.split(";\n", 1)
        pivot_sql += ";"
        if mode != "sqlserver":
            orders = ENGINES[mode][1] + "orders"
            pivot_sql = ("SELECT COUNT(CASE WHEN status = 'paid' THEN 1 END) AS paid,\n"
                         "       COUNT(CASE WHEN status = 'pending' THEN 1 END) AS pending\n"
                         f"FROM {orders};")
        yield variant(mode, pivot_sql, [
            result(pivot_sql, ("paid", "pending"), [(3, 1)], "预期结果 · 行转列"),
        ], "需要读取订单表。")
        advanced.append(variant(mode, unpivot_sql, [
            result(unpivot_sql, ("status", "order_count"), [("paid", 3), ("pending", 1)], "预期结果 · 列转行"),
        ], "先运行上方行转列示例，确认两列的计数。"))
    yield '<p>先把每种状态的计数放成一列。SQL Server 用 PIVOT，PostgreSQL 和 MySQL 可用条件聚合得到同样的两列。</p>'
    yield '<details><summary>进阶 · 把两列还原成两行</summary>\n' + "\n".join(advanced) + "</details>"


def index_catalog():
    queries = {
        "postgresql": ("SELECT indexname AS index_name FROM pg_indexes\n"
                       "WHERE tablename = 'path_index' AND schemaname = pg_my_temp_schema()::regnamespace::text;"),
        "sqlserver": ("SELECT name AS index_name FROM tempdb.sys.indexes\n"
                      "WHERE object_id = OBJECT_ID('tempdb..#path_index') AND name = 'path_ix';"),
        "mysql": "SHOW INDEX FROM path_index WHERE Key_name = 'path_ix';",
    }
    yield '<details><summary>进阶 · 查看和删除索引</summary>'
    for mode, query in queries.items():
        label = "预期结果 · 部分列" if mode == "mysql" else "预期结果"
        columns = ("Key_name", "Column_name") if mode == "mysql" else ("index_name",)
        rows = [("path_ix", "order_id")] if mode == "mysql" else [("path_ix",)]
        drop = {
            "postgresql": "DROP INDEX pg_temp.path_ix;",
            "sqlserver": "DROP INDEX path_ix ON #path_index;",
            "mysql": "DROP INDEX path_ix ON path_index;",
        }[mode]
        yield variant(mode, f"{query}\n{drop}\n{query}", [
            result(query, columns, rows, label + " · 删除前"),
            result(query, columns, [], label + " · 删除后"),
        ],
                      "接着在上方创建临时表和索引的同一连接执行。")
    yield "</details>"


def enrich(body, key):
    if key in {"create-table", "alter-table", "truncate-table", "drop-table"}:
        for mode, block in split_variants(body):
            changed = block
            if key == "drop-table":
                changed = changed.replace("\nINSERT INTO path_drop VALUES (1);", "")
                if mode == "mysql":
                    changed = changed.replace("DROP TABLE path_drop", "DROP TEMPORARY TABLE path_drop")
                if mode == "postgresql":
                    changed = changed.replace("DROP TABLE path_drop", "DROP TABLE pg_temp.path_drop")
            changed = changed.replace("新连接。", "使用新连接，临时表创建成功后再执行后续语句。", 1)
            body = body.replace(block, changed, 1)
    if key == "indexes":
        body += "\n" + "\n".join(index_catalog())
    if key == "grant-revoke":
        def show_revoke(match):
            sql = unescape(match[1])
            check, tail = sql.split("\nREVOKE ", 1)
            statement = check.split(";\n", 2)[-1]
            revoke, cleanup = tail.split(";\n", 1)
            extended = f"{check}\nREVOKE {revoke};\n{statement}\n{cleanup}"
            return match[0].replace(match[1], escape(extended, quote=False))
        body = SQL.sub(show_revoke, body)
        body = re.sub(r'(<caption class="sql-statement-caption"><span class="sql-caption-line"><code>(.*?)</code>.*?</table></div>)',
                      lambda m: m[0] + "\n" + result(unescape(m[2]), ("explicit_read",), [(0,)], "预期结果 · 撤权后"),
                      body, flags=re.S)
        blocks = dict(split_variants(body))
        pg = blocks["postgresql"]
        body = body.replace(pg, pg.replace("explicit_read", "can_read"), 1)
        mysql = blocks["mysql"]
        suffix = mysql[mysql.rfind("</div>")+6:]
        role = "'path_order_reader'"
        query = f"SHOW GRANTS FOR {role};"
        sql = (f"CREATE ROLE {role};\nGRANT SELECT ON learn_sql_lab.orders TO {role};\n"
               f"{query}\nREVOKE SELECT ON learn_sql_lab.orders FROM {role};\n{query}\nDROP ROLE {role};")
        columns = ("观察项", "预期")
        mysql_variant = variant("mysql", sql, [
            result(query, columns, [("orders 的 SELECT 授权", "出现")], "预期观察 · 授权后"),
            result(query, columns, [("orders 的 SELECT 授权", "消失")], "预期观察 · 撤权后"),
        ], "在专用练习实例，用具备 CREATE ROLE、DROP ROLE 及该表 SELECT 授权权的管理账号。确认角色名未占用，CREATE 成功后再执行后续语句。")
        body = body.replace(mysql, mysql_variant + suffix, 1)
    if key in {"query-optimization", "analysis", "view-create", "view-change", "view-drop"}:
        for mode, block in split_variants(body):
            if mode != "sqlserver":
                changed = re.sub(r"SQL Server (?:需要 SHOWPLAN 权限，使用 SSMS 或 sqlcmd 逐批执行|用 GO 分批|使用 SSMS 或 sqlcmd 按 GO 分批)。", "", block)
                body = body.replace(block, changed, 1)
    if key == "isolation":
        body += '<p>SQL Server 的 SET 会影响当前会话的后续事务。练习结束后关闭该练习连接。</p>'
    return body


def without_heading(section):
    return re.sub(r"\s*<h2>.*?</h2>", "", section, count=1, flags=re.S)


def practice_rows():
    """Read the shared fixture rows from the PostgreSQL setup script."""
    setup = (ROOT / "assets" / "setup-postgresql.sql").read_text(encoding="utf-8")
    tables = {}
    for table, columns, values in re.findall(r"INSERT INTO (\w+) \(([^)]+)\) VALUES\s*(.*?);", setup, re.S):
        fields = columns.split(", ")
        rows = csv.reader(re.findall(r"\(([^()]*)\)", values), quotechar="'", skipinitialspace=True)
        tables[table] = [
            dict(zip(fields, (None if value == "NULL" else value for value in row), strict=True))
            for row in rows
        ]
    return tables


def input_grids(key, stage, mode, block, fixtures):
    if key == "pivot" and "预期结果 · 列转行" in block:
        counts = tuple(sum(row["status"] == status for row in fixtures["orders"]) for status in ("paid", "pending"))
        return [result(None, ("paid", "pending"), [counts], "列转行前 · 聚合结果")]
    if key == "indexes" and "删除前" in block:
        return []
    if key in {"insert", "delete", "update"} and stage == "syntax":
        temp = ("#" if mode == "sqlserver" else "") + f"rv2_basic_{key}"
        columns = ("order_id", "status")
        rows = [] if key == "insert" else [
            tuple(row[column] for column in columns) for row in fixtures["orders"] if row["order_id"] == "101"
        ]
        return [result(None, columns, rows, f"{key.upper()} 前 · {temp}")]
    if key == "full-join":
        return [
            result(None, ("id",), [(1,)], "执行前 · a（派生表）"),
            result(None, ("id",), [(2,)], "执行前 · b（派生表）"),
        ]
    temp_inputs = {
        "alter-table": ("ALTER TABLE 前 · path_alter", ("order_id",), []),
        "truncate-table": ("TRUNCATE TABLE 前 · path_truncate", ("id",), [(1,)]),
        "drop-table": ("DROP TABLE 前 · path_drop", ("id",), []),
        "commit": ("写入前 · path_commit", ("id",), []),
        "view-change": ("修改定义前 · path_view_change", ("order_id", "status"), None),
        "view-drop": ("DROP VIEW 前 · path_view_drop", ("order_id", "status"), None),
    }
    if key in temp_inputs:
        label, columns, rows = temp_inputs[key]
        if rows is None:
            rows = [tuple(row[column] for column in columns)
                    for row in fixtures["orders"] if row["status"] == "pending"]
        if mode == "sqlserver" and key in {"alter-table", "truncate-table", "drop-table", "commit"}:
            label = label.replace(" · path_", " · #path_")
        return [result(None, columns, rows, label)]

    inputs = []
    for keys, table, fields, selected in FIXTURE_PROJECTIONS:
        if key not in keys.split():
            continue
        columns = fields.split()
        rows = [tuple(row[column] for column in columns) for row in fixtures[table]
                if all(row[column] in (values if isinstance(values, tuple) else (values,))
                       for column, values in selected.items())]
        label = f"执行前 · {table}" + ("（相关行）" if selected else "")
        inputs.append(result(None, columns, rows, label))
    return inputs


def compare_tables(body, key, stage, fixtures):
    """Put the relevant input rows above the existing output tables."""
    blocks = []
    for mode, block in split_variants(body):
        inputs = input_grids(key, stage, mode, block, fixtures)
        if inputs:
            first_grid = block.index('<div class="sql-grid-viewport"')
            data = "\n".join(inputs)
            if len(inputs) > 1:
                data = f'<div class="grid sql-input-tables">\n{data}\n</div>'
            block = block[:first_grid] + data + "\n" + block[first_grid:]
        if key == "grant-revoke":
            block = block.replace('aria-label="预期结果"', 'aria-label="预期结果 · 授权后"')
            block = block.replace('>预期结果</span>', '>预期结果 · 授权后</span>')
        blocks.append(block)
    assert blocks, key
    start = DIV.search(body).start()
    return RESULT_CAPTION.sub(r'<caption>\1</caption>', body[:start] + "".join(blocks))


def dialect_tags():
    tags = " ".join(f'<span class="dialect-tag" data-engine="{mode}">{engine}</span>'
                    for mode, (engine, *_) in ENGINES.items())
    return f'<p class="dialect-tags">{tags}</p>'


def card(key, label, purpose, sections, stage, fixtures):
    if key in {"insert", "update", "delete"}:
        body = "\n".join(basic_write(key) if stage == "syntax" else writes(key))
    elif key == "nosql":
        body = "\n".join(compare_nosql())
    elif key == "window":
        body = "\n".join(window_intro())
    elif key == "cross-join":
        body = "\n".join(cross_join())
    elif key == "pivot":
        body = "\n".join(pivot(without_heading(sections[key])))
    elif key in {"procedure", "function"}:
        body = "\n".join(routine(key))
    elif key in {"primary-key", "foreign-key", "unique", "not-null", "check"}:
        body = "\n".join(constraint(key, without_heading(sections[key])))
    else:
        source = sections["inner-join" if key == "join" else key]
        body = enrich(without_heading(source), key)
    body = compare_tables(body, key, stage, fixtures)
    if not re.search(r"</div>\s*<p>", body):
        body += f"\n<p>{escape(purpose)}</p>"
    return f'''<section class="point" id="{key}" data-dialects="postgresql sqlserver mysql">
<h2>{escape(label)}</h2>
{body.strip()}
{dialect_tags()}
</section>'''


def page(title, main, pager="", *, homepage=False):
    header = (ROOT / "reference" / "sql-roadmap.html").read_text(encoding="utf-8").split("<main", 1)[0]
    header = re.sub(r"<title>.*?</title>", f"<title>{escape(title)} · SQL 路线速查</title>", header)
    header = re.sub(
        r'<nav aria-label="主导航">.*?</nav>',
        '<nav aria-label="主导航"><a href="../index.html">章节目录</a>\n'
        '<a href="../v1.html">v1 旧版</a></nav>',
        header, count=1, flags=re.S,
    )
    if homepage:
        header = header.replace('="../', '="')
    return f"{header}<main class=\"wrap roadmap-v2\">\n{main}\n{pager}\n</main>\n</body>\n</html>\n"


def stage_file(i):
    slug = STAGES[i][0] if i < len(STAGES) else "practical"
    return f"{i+1:02}-{slug}.html"


def stage_directory(i, name, topics):
    chapter = f"{OUTPUT.name}/{stage_file(i)}"
    groups = []
    ordinal = 1
    for category, entries in groupby(topics, key=lambda topic: topic[3]):
        if category:
            groups.append(f"<h3>{escape(category)}</h3>")
        items = []
        for anchor, label, _, _, nested in entries:
            link = f'<a href="{chapter}#{anchor}">{escape(label)}</a>'
            if nested:
                items[-1][1].append(f"<li>{link}</li>")
            else:
                items.append((link, []))
        groups.append(f'<ol class="roadmap-topic-list" start="{ordinal}">')
        for link, children in items:
            subtopics = "\n<ol>\n" + "\n".join(children) + "\n</ol>\n" if children else ""
            groups.append(f"<li>{link}{subtopics}</li>")
        groups.append("</ol>")
        ordinal += len(items)
    return f'''<section class="panel roadmap-stage">
<h2><a href="{chapter}"><span aria-hidden="true">{i+1:02}</span>{escape(name)}</a></h2>
{chr(10).join(groups)}
</section>'''


def practical_card(topic):
    variants = []
    for mode, (_, schema, _, _) in ENGINES.items():
        sql = topic.sql[mode] if isinstance(topic.sql, dict) else topic.sql
        tables = topic.tables[mode] if isinstance(topic.tables, dict) else topic.tables
        extra = topic.requirements[mode] if isinstance(topic.requirements, dict) else topic.requirements
        grids = [result(None if table.before else "", table.columns, table.rows, table.title) for table in tables]
        variants.append(variant(mode, sql.replace("@lab.", schema), grids, escape(extra), uses_lab="@lab." in sql))
    links = " · ".join(f'<a href="{escape(href)}">{escape(label)}</a>' for label, href in topic.links)
    references = f'<p class="sources">{links}</p>' if links else ""
    return f'''<section class="point" id="{topic.anchor}" data-dialects="postgresql sqlserver mysql">
<h2>{escape(topic.title)}</h2>
{chr(10).join(variants)}
<p>{escape(topic.explanation)}</p>
{references}
{dialect_tags()}
</section>'''


def write_chapter(i, names, topics, items, question, answer):
    name = names[i]
    jump = []
    group = ""
    for ordinal, (key, label, _, category, _) in enumerate(topics, 1):
        if group != category:
            if jump:
                jump.append("</ol>")
            jump.append(f'<p><strong>{escape(category)}</strong></p><ol start="{ordinal}">')
            group = category
        elif not jump:
            jump.append("<ol>")
        jump.append(f'<li><a href="#{key}">{escape(label)}</a></li>')
    self_check = f'''<section class="panel"><h2>合上示例试一题</h2><p>{question}</p>
<details><summary>查看答案</summary><p>{answer}</p></details></section>'''
    previous = f'<a rel="prev" href="{stage_file(i-1)}">← {escape(names[i-1])}</a>' if i else ""
    next_ = f'<a rel="next" href="{stage_file(i+1)}">{escape(names[i+1])} →</a>' if i + 1 < len(names) else ""
    pager = f'<nav class="pager" aria-label="章节导航">{previous}<a href="../index.html">章节目录</a>{next_}</nav>'
    main_html = f'''<p class="kicker">第 {i+1:02} 章 · 共 {len(names)} 章</p>
<h1>{escape(name)}</h1>
<div class="layout">
<article class="content" aria-label="知识点">
{chr(10).join(items)}
{self_check}
</article>
<nav class="jump" aria-label="本阶段知识点"><strong>本阶段知识点</strong>
{chr(10).join(jump)}
</ol></nav>
</div>'''
    (OUTPUT / stage_file(i)).write_text(page(name, main_html, pager), encoding="utf-8")


def main():
    chapters = route()
    sections, labels = legacy_points()
    fixtures = practice_rows()
    assert len(chapters) == len(STAGES)
    assert sum(len(checklist) for _, checklist in chapters) == 99
    OUTPUT.mkdir(exist_ok=True)
    names = [name for name, _ in chapters] + [PRACTICAL_NAME]
    toc = []
    for i, ((name, checklist), (stage, anchors, question, answer)) in enumerate(zip(chapters, STAGES)):
        topics = [(key, labels.get(key, text), purpose, category, nested)
                  for key, (text, purpose, category, nested) in zip(anchors.split(), checklist, strict=True)]
        items = [card(key, label, purpose, sections, stage, fixtures) for key, label, purpose, _, _ in topics]
        write_chapter(i, names, topics, items, question, answer)
        toc.append(stage_directory(i, name, topics))
    practice = list(practical_topics(fixtures))
    topics = [(topic.anchor, topic.title, "", topic.group, False) for topic in practice]
    write_chapter(len(chapters), names, topics, [practical_card(topic) for topic in practice],
                  "要查询 2 月整月，3 月 1 日应当包含在结果里吗？",
                  "用 2 月 1 日（含）到 3 月 1 日（不含）的半开区间。")
    toc.append(stage_directory(len(chapters), PRACTICAL_NAME, topics))
    intro = '''<h1>SQL 路线速查</h1>
<p class="lead">16 个学习阶段和第 17 章实务补足。先选数据库，再点击知识点查看可运行 SQL 和结果。</p>'''
    columns = ["<div>\n" + "\n".join(column) + "\n</div>" for column in (toc[:8], toc[8:])]
    contents = '<nav class="grid roadmap-directory" aria-label="章节目录">\n' + "\n".join(columns) + "\n</nav>"
    primary = '<p class="sources">路线依据 <a href="https://roadmap.sh/sql">roadmap.sh SQL 路线图</a></p>'
    (ROOT / "index.html").write_text(
        page("章节目录", "\n".join((intro, contents, primary)), homepage=True), encoding="utf-8",
    )
    (OUTPUT / "index.html").write_text('''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SQL 路线速查</title>
<link rel="canonical" href="../index.html">
<script>location.replace('../index.html' + location.search + location.hash);</script>
</head>
<body><p><a href="../index.html">打开 SQL 路线速查首页</a></p></body>
</html>
''', encoding="utf-8")
    print(f"Built {len(names)} chapters, including {len(practice)} practical topics.")


if __name__ == "__main__":
    main()
