# PostgreSQL 与 SQL Server 语法补录清单

## 目录顺序

首页、目录和上一章／下一章都按 **01 → 32 → 方言专题 → 参考附录** 排列。三种模式先看到第 01 章起的主课程。PostgreSQL 的 33–35 章和 SQL Server 的 36–38 章归到主课程之后的对应专题入口。新增专题沿用现有 URL，最终章节号等题目和难度顺序确定后统一编排。

01–32 章里已有的分页、日期函数、全文搜索、事务等例子继续在各自的入门位置使用。专题章展开原生子句、语义边界、版本与项目用法。术语、现有例子与专题互相链接。每套专题独立成篇。

## 范围和判定

- 版本基线是 PostgreSQL 19、SQL Server 2025 和笔记已有的 MySQL 26.10。较低版本可用的写法标最低版本。SQL Server 另记数据库兼容级别、版本更新、版本类型、平台和预览条件。扩展注明名称、前置组件和最低版本。[PostgreSQL 19 发行说明](https://www.postgresql.org/docs/19/release-19.html) · [SQL Server 2025 发行说明](https://learn.microsoft.com/en-us/sql/sql-server/what-s-new-in-sql-server-2025?view=sql-server-ver17) · [MySQL 26.10 语句](https://dev.mysql.com/doc/refman/26.10/en/sql-statements.html)
- “独自语法”按实际写法和行为判断。方言独有的语句、子句、签名、类型、运算符和对象都入表。两个目标引擎都支持而 MySQL 不支持的语法，两边各自讲，例如 MERGE 和 FULL OUTER JOIN。四舍五入、NULL、约束和锁的实际结果存在差异时，同名写法也要单列。共有且行为相同的语法指向现有例子。[MySQL 26.10 函数与运算符](https://dev.mysql.com/doc/refman/26.10/en/functions.html)
- 主体覆盖数据库引擎及官方随附组件可执行的 SQL。客户端命令、系统过程、管理对象、发行变更进附录。第三方扩展先将 pgvector、PostGIS、TimescaleDB 列入独立扩展清单。微软文档中的 Azure、Synapse、Fabric 条目记录各自适用产品。这样可从目录追到产品边界、版本差异及扩展依赖。
- 下列专题的“已有”是工作区的现状，有一个例子即计为已有入口。“补录”列出了需要扩写的具体语法。逐项查验使用[方言官方参考索引](DIALECT-REFERENCE-INDEX.md)，官方文档一个页面可能包含多个需单列的子句或函数签名。

## PostgreSQL 专题

| 拟定专题 | 已有入口 | 补录范围 |
| --- | --- | --- |
| SQL 基本元素与名称解析 | 03、27、31 | 双引号保留词和名称折叠、`E'…'`、`U&'…'`、美元引号、`::`、日期与区间字面量、布尔值、`IS [NOT] DISTINCT FROM`、行值比较、数组形式的 `ANY/ALL`、操作符及函数重载、`search_path` 和模式限定 |
| 查询、联结与结果形状 | 04–17、32、34 | `DISTINCT ON` 并列与稳定排序、`NULLS FIRST/LAST`、`FETCH … WITH TIES`、`LATERAL` 的 INNER/LEFT 形式及表函数、`TABLESAMPLE`、`ROWS FROM`、CTE 的 `MATERIALIZED/NOT MATERIALIZED`、递归 `SEARCH/CYCLE`、集合运算 `ALL`、原生 FULL JOIN |
| 聚合、窗口与集合函数 | 12–13、32、35 | `FILTER`、`GROUPING SETS/CUBE/ROLLUP`、`GROUPING()`、聚合内部的 `DISTINCT/ORDER BY`、`WITHIN GROUP`、百分位数、回归统计、`ARRAY_AGG/STRING_AGG`、命名窗口、`ROWS/RANGE/GROUPS` 与 `EXCLUDE`、`generate_series` 和 `generate_subscripts`、19 的窗口 `IGNORE NULLS/RESPECT NULLS` |
| 写入、同步与批量装载 | 19–20、32–33 | INSERT/UPDATE/DELETE/MERGE 的 `RETURNING`；`OLD/NEW`、初始值与生成列；`OVERRIDING SYSTEM/USER VALUE`、`UPDATE … FROM`、`DELETE … USING`、可写 CTE、`ON CONFLICT` 的目标、约束名、部分索引推断、`DO NOTHING/UPDATE/SELECT`；`MERGE` 的条件、分支顺序、重复来源、`DELETE/DO NOTHING`、`merge_action()`；`COPY FROM/TO`、格式、NULL、错误策略、服务器路径，以及客户端 `\copy` |
| 内置类型与类型行为 | 11、27、31、34–35 | 数字与特殊值、`serial` 与 identity、`uuid/uuidv7()`、`bytea`、位串、`money`、`interval`、`timestamptz`、`AT TIME ZONE`、无限日期、数组和维度、`ROW` 与组合类型、`ENUM/DOMAIN`、区间和多区间、`inet/cidr/macaddr`、几何类型、XML、JSON、`oid/regclass/regtype`、`pg_lsn`、伪类型，以及隐式转换与索引匹配 |
| 字符串、正则、时间和运算符 | 08–11、27 | `ILIKE`、`SIMILAR TO`、`~/~*/!~/!~*`、正则系列及捕获结果、`format`、`quote_ident/quote_literal`、字节与字符函数、`date_trunc/date_bin/extract/age`、事务时间与实时钟、跨时区边界、编码与排序规则 |
| 数组、JSONB、SQL/JSON、XML 与全文 | 18、32、34 | 数组下标与切片、包含／交集、`unnest WITH ORDINALITY`、多数组展开；JSONB 下标、路径提取、键检查、`@>/?/?\|/?&/@?/@@`、`jsonb_set/jsonb_insert`、记录集转换、`jsonpath`、`JSON_TABLE/JSON_EXISTS/JSON_QUERY/JSON_VALUE`；`XMLTABLE`、XPath；`tsvector/tsquery`、词典、权重、排名与 GIN |
| 表结构、约束、视图与分区 | 21–22、35 | identity、sequence 的 `OWNED BY/nextval/currval/setval`、`TEMP/UNLOGGED`、`ON COMMIT`、`LIKE … INCLUDING`、生成列、`ALTER TABLE … USING`、`NOT VALID/VALIDATE`、延迟约束与 `SET CONSTRAINTS`、`NULLS NOT DISTINCT`、排斥约束、`WITHOUT OVERLAPS/PERIOD`；继承与 `ONLY`、分区定义与挂接、物化视图及并发刷新、视图安全选项 |
| 索引、统计和执行计划 | 29–30、35 | B-tree、Hash、GiST、SP-GiST、GIN、BRIN；部分、表达式、覆盖、多列索引；`INCLUDE`、算子类、NULL 排序、`CREATE/REINDEX … CONCURRENTLY`、唯一性推断、`CREATE STATISTICS`、`EXPLAIN` 的执行、缓冲、WAL、序列化、I/O 与输出选项 |
| 例程、触发器、自定义对象 | 23–25、32 | `DO`、SQL 函数与 PL/pgSQL、`DECLARE/BEGIN/EXCEPTION`、`RETURN QUERY`、控制流与循环、动态 `EXECUTE … USING`、`GET DIAGNOSTICS`、`RAISE`、函数波动性与严格性、游标 `WITH HOLD`；行级／语句级、转换表、约束触发器、事件触发器；自定义类型、转换、运算符、聚合、访问方法、操作符族、文本搜索对象及扩展的创建与变更 |
| 事务、锁、权限与会话 | 26、28、32 | `SET TRANSACTION`、快照、可序列化重试、`FOR UPDATE/NO KEY UPDATE/SHARE/KEY SHARE`、`NOWAIT/SKIP LOCKED`、`LOCK TABLE`、会话／事务级 advisory locks、两阶段提交、`LISTEN/NOTIFY/UNLISTEN`、`PREPARE/EXECUTE/DEALLOCATE`、`SET LOCAL`；角色继承、成员与默认权限、RLS、`SECURITY DEFINER`、安全的名称解析 |
| 管理、系统对象、复制与扩展 | 02–03、29–30 | `pg_catalog`、`pg_stat_*`、`VACUUM/ANALYZE/REPACK/CLUSTER/REINDEX`、`CHECKPOINT`、`ALTER SYSTEM`、定期维护的并发影响；数据库、表空间和排序规则；FDW、外部服务器、用户映射、`IMPORT FOREIGN SCHEMA`；publication/subscription、slot、序列复制、备用库 `WAIT`；官方模块与客户端命令 |
| 版本与迁移附录 | 各页部分版本提示 | 按发布说明登记变更和旧写法。18 核对虚拟生成列、`uuidv7()`、`RETURNING OLD/NEW`、时间约束。19 核对窗口 NULL 处理、`DO SELECT`、`REPACK`、`WAIT`、`COPY` 新选项和复制语法。兼容写法与过时写法分别标明状态。[18 发行说明](https://www.postgresql.org/docs/18/release-18.html) · [19 发行说明](https://www.postgresql.org/docs/19/release-19.html) |

完整核对入口。[语句](https://www.postgresql.org/docs/19/sql-commands.html) · [函数与运算符](https://www.postgresql.org/docs/19/functions.html) · [数据类型](https://www.postgresql.org/docs/19/datatype.html) · [PL/pgSQL](https://www.postgresql.org/docs/19/plpgsql.html) · [官方模块](https://www.postgresql.org/docs/19/contrib.html) · [客户端工具](https://www.postgresql.org/docs/19/reference-client.html)

## SQL Server 专题

| 拟定专题 | 已有入口 | 补录范围 |
| --- | --- | --- |
| 批次、名称解析和表达式 | 02–03、10–11、27、31 | `USE`、`dbo`、四段名称、`[标识符]`、`QUOTED_IDENTIFIER`、`N'…'`、`@变量/@@状态`、`DECLARE/SET/SELECT` 赋值差异、批次作用域、客户端 `GO` 和 sqlcmd 变量、运算符优先级、类型优先级、`CAST/CONVERT/PARSE` 与 `TRY_*` |
| 查询、联结和分页 | 04–17、32、37 | `TOP (n) [PERCENT] [WITH TIES]`、`OFFSET/FETCH`、`APPLY` 的 CROSS/OUTER 写法、原生 FULL JOIN、`PIVOT/UNPIVOT`、静态与动态列、`TABLESAMPLE`、`FOR BROWSE`、CTE 的批次分号、`MAXRECURSION`、`WINDOW` 定义、分页的并列与 NULL 排序 |
| 聚合、窗口与分析函数 | 12–13、32 | `COUNT_BIG`、`STRING_AGG … WITHIN GROUP`、条件聚合、`GROUPING SETS/ROLLUP/CUBE/GROUPING_ID`、百分位、近似聚合、排序及窗口的 `ROWS/RANGE`、窗口 `IGNORE NULLS` 的各函数门槛、`GENERATE_SERIES`、`CHOOSE/IIF/GREATEST/LEAST` |
| 写入、批处理和载入 | 19–20、36 | `OUTPUT/OUTPUT INTO`、`inserted/deleted/$action`、触发器限制、提交失败时的输出；`MERGE` 的目标/来源/条件/多匹配/取消重试；`UPDATE … FROM`、别名 DELETE、`TOP` 在 DML 中的含义、`INSERT … EXEC`、`SELECT INTO`、`SET IDENTITY_INSERT`、`BULK INSERT/OPENROWSET(BULK…)`、错误行、批量大小、格式文件、bcp |
| 类型、字符串与时间 | 06、08–11、27、31、38 | `bit`、`money`、`uniqueidentifier`、`NEWID/NEWSEQUENTIALID`、`datetime2/datetimeoffset`、`rowversion`、`sql_variant`、表变量与用户定义表类型、`hierarchyid`、geometry/geography、XML、原生 JSON、VECTOR、旧 LOB 类型；`ISNULL` 的返回类型、NULL 与字符串连接、`DATEADD/DATEDIFF[_BIG]/DATEFROMPARTS/EOMONTH/DATETRUNC/DATE_BUCKET`、`AT TIME ZONE/SWITCHOFFSET`、Unicode 与排序规则 |
| JSON、XML、全文、正则和模糊匹配 | 09、18、32、37 | `FOR JSON PATH/AUTO`、`OPENJSON` 默认键值与 `WITH`、`JSON_VALUE/QUERY/MODIFY/PATH_EXISTS/ISJSON`、路径和索引；`FOR XML`、XML schema collection、`query/value/exist/nodes/modify`、`OPENXML`；`CONTAINS/FREETEXT` 及表值版本、全文目录和语言；`STRING_SPLIT`、字符类、正则全系列、编辑距离及相似度 |
| 表结构、约束、视图与分区 | 21–22、31、38 | `IDENTITY` vs sequence、`NEXT VALUE FOR`、`DBCC CHECKIDENT`、`#temp/##temp/@table`、`PERSISTED`、`WITH CHECK/NOCHECK` 与受信约束、`CREATE OR ALTER`、`sp_rename`、schemas、synonyms、`SCHEMABINDING` 与索引视图、`PARTITION FUNCTION/SCHEME`、`SWITCH`、`FILESTREAM/FileTable` 和内存优化表 |
| 时态、变更跟踪、图与账本 | 38 | `SYSTEM_VERSIONING/PERIOD/FOR SYSTEM_TIME` 的 AS OF、FROM TO、BETWEEN、CONTAINED IN、ALL；`rowversion` 的并发检查；CDC 与 Change Tracking、`CHANGETABLE`；`AS NODE/AS EDGE`、`MATCH/SHORTEST_PATH`、边约束；账本表、历史表和验证接口 |
| 索引、统计、计划与诊断 | 29–30、38 | clustered / nonclustered / heap、`INCLUDE`、筛选与计算列索引、columnstore、XML/空间/全文/JSON/向量索引；`ONLINE/RESUMABLE/WAIT_AT_LOW_PRIORITY`、压缩、索引维护；`CREATE/UPDATE STATISTICS`、`SET STATISTICS IO/TIME`、SHOWPLAN、实际计划、`OPTION` 提示、Query Store、计划强制、运行时 DMV、Extended Events |
| 程序结构与服务队列 | 23–25、32、36 | 存储过程、OUTPUT 参数、RETURN 状态、`EXECUTE … WITH RESULT SETS`、`sp_executesql`、`QUOTENAME`，用户定义函数的标量与表值形式、表值参数和 READONLY、批次、循环及游标；DML/DDL/LOGON 触发器、转换数据与递归；`WAITFOR`，Service Broker 的消息类型、契约、服务、队列、会话和收发 |
| 事务、隔离和错误处理 | 26、36、38 | 自动提交／显式／隐式事务、`@@TRANCOUNT`、`SAVE TRANSACTION`、快照与 RCSI、`XACT_ABORT`、`TRY…CATCH/XACT_STATE/THROW`、旧 `RAISERROR` 的差异与迁移、`UPDLOCK/HOLDLOCK/READPAST/NOWAIT`、`NOLOCK` 的读取风险、超时、死锁重试、`sp_getapplock` |
| 权限、加密和审计 | 28 | 登录名、数据库用户、contained user、服务器与数据库角色、`GRANT/DENY/REVOKE`、`EXECUTE AS/REVERT`、所有权链、模块签名、`SESSION_CONTEXT`、RLS、动态数据掩码、列加密、证书与密钥、审计、敏感度分类 |
| 实例、备份、系统对象和外部数据 | 02–03、29–30 | `ALTER DATABASE [SCOPED CONFIGURATION]`、兼容级别、`SET` 选项、`sys.*`、管理 DMV 和系统过程；`BACKUP/RESTORE` 的完整、差异、日志及还原序列；`DBCC`、SQL Agent、Always On、复制选项；linked server、`OPENQUERY/OPENROWSET/OPENDATASOURCE`、外部表、PolyBase 和文件格式 |
| 版本与迁移附录 | 各页部分版本提示 | 按发布说明追踪 2016–2025 中影响现有代码的功能。2025 专项核对原生 JSON 和索引、向量类型和检索、正则与模糊匹配、新日期及聚合写法、外部模型对象，逐项记录兼容级别、更新版本及预览状态。补录被弃用或移除的 DDL、旧文本类型、旧系统对象和替代写法。[2025 发行说明](https://learn.microsoft.com/en-us/sql/sql-server/what-s-new-in-sql-server-2025?view=sql-server-ver17) · [JSON 类型](https://learn.microsoft.com/en-us/sql/t-sql/data-types/json-data-type?view=sql-server-ver17) · [JSON 索引](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-json-index-transact-sql?view=sql-server-ver17) |

完整核对入口。[T-SQL 参考](https://learn.microsoft.com/en-us/sql/t-sql/language-reference?view=sql-server-ver17) · [语句](https://learn.microsoft.com/en-us/sql/t-sql/statements/statements?view=sql-server-ver17) · [函数](https://learn.microsoft.com/en-us/sql/t-sql/functions/functions?view=sql-server-ver17) · [语言元素](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/language-elements-transact-sql?view=sql-server-ver17) · [数据类型](https://learn.microsoft.com/en-us/sql/t-sql/data-types/data-types-transact-sql?view=sql-server-ver17) · [系统目录](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/catalog-views-transact-sql?view=sql-server-ver17) · [动态管理对象](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-objects/system-dynamic-management-objects?view=sql-server-ver17)

## 开工与验收顺序

1. 先调正目录和章节导航，回归三个模式。然后记录现有 38 章的知识点对应位置，避免重复编例。
2. 逐条读索引与官方语法图，登记名称、独有差异、最低版本、前置条件和章节位置。每项必须落到新示例、现有锚点、共有语法说明或明确的适用产品／扩展。按语法变体查漏，例如 `MERGE` 的每个分支、`SET` 的各选项、JSON 各函数与运算符。
3. 先补查询、表达式和写入，再补类型、DDL、例程、并发及性能，最后补管理、组件和版本专题。大专题按内容拆章。每写完一章调用独立 subagent 审查语义、版本、标签和示例。
4. 每个知识点给最小可复制示例、适用标签、执行前后的左对齐表格，结果表标题放产生该结果的完整 SQL。DDL 用变更前后的元数据，错误用错误码及状态，并发用两个会话的步骤和结果。逐项记录实跑、语法检查或文档核对的状态。
