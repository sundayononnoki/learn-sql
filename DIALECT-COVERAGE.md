# 原生 SQL 语法覆盖记录

学习顺序为第 01–32 章、当前方言专题、参考附录。新版专题从第 32 章进入。第 33 章和第 36 章也可向前回到主课程。

本次新增 **393 个知识点**，其中 PostgreSQL 187 个、SQL Server 206 个。新建第 39–63 章，并扩写第 33、34、36、37 章。第 35、38 章原有知识点仍可在各自的专题中找到。

PostgreSQL 在隔离的 19.0 实例里核对了 187 个新增示例，包括六个需要两个连接或准备事务的示例。逻辑复制、序列复制、外部表和备用库示例使用了独立的本地节点。SQL Server 的 206 个新增示例经 T-SQL 语法解析与独立文档审查，结果表标为预期结果。

各章按本次新增点计数。所有新增知识点均有适用标签、输入表、SQL 和结果表。结果表标题指向用于核对该表的语句。

## PostgreSQL

| 章节 | 新增点 | 验证 | 审查 |
| --- | ---: | --- | --- |
| [33 · 数据写入与同步](reference/33-postgresql-write.html) | 11 | 11 个实跑 | 独立审查 |
| [34 · 原生查询、数组与 JSONB](reference/34-postgresql-query.html) | 9 | 9 个实跑 | 独立审查 |
| [39 · SQL 基本元素与名称解析](reference/39-postgresql-syntax.html) | 13 | 13 个实跑 | 独立审查 |
| [40 · 聚合、窗口与集合函数](reference/40-postgresql-analytics.html) | 14 | 14 个实跑 | 独立审查 |
| [41 · 内置类型与类型行为](reference/41-postgresql-types.html) | 16 | 16 个实跑 | 独立审查 |
| [42 · 字符串、正则、时间和运算符](reference/42-postgresql-functions.html) | 15 | 15 个实跑 | 独立审查 |
| [43 · 数组、JSONB、SQL/JSON、XML 与全文](reference/43-postgresql-documents.html) | 14 | 14 个实跑 | 独立审查 |
| [44 · 表结构、约束、视图与分区](reference/44-postgresql-schema.html) | 15 | 15 个实跑 | 独立审查 |
| [45 · 索引、统计和执行计划](reference/45-postgresql-plans.html) | 14 | 14 个实跑 | 独立审查 |
| [46 · 例程、触发器与自定义对象](reference/46-postgresql-routines.html) | 16 | 16 个实跑 | 独立审查 |
| [47 · 事务、锁、权限与会话](reference/47-postgresql-transactions.html) | 13 | 13 个实跑 | 独立审查 |
| [48 · 管理、系统对象、复制与扩展](reference/48-postgresql-administration.html) | 12 | 12 个实跑 | 独立审查 |
| [49 · PostgreSQL 版本与迁移附录](reference/49-postgresql-versions.html) | 13 | 13 个实跑 | 独立审查 |
| [62 · 对象生命周期与会话工具](reference/62-postgresql-utilities.html) | 12 | 12 个实跑 | 独立审查 |

## SQL Server

| 章节 | 新增点 | 验证 | 审查 |
| --- | ---: | --- | --- |
| [36 · 数据同步、OUTPUT 与事务](reference/36-sqlserver-write.html) | 12 | 12 个语法解析 | 独立审查 |
| [37 · APPLY、行列转换与 JSON](reference/37-sqlserver-query.html) | 10 | 10 个语法解析 | 独立审查 |
| [50 · 批次、名称解析和表达式](reference/50-sqlserver-batches.html) | 15 | 15 个语法解析 | 独立审查 |
| [51 · 聚合、窗口与分析函数](reference/51-sqlserver-analytics.html) | 15 | 15 个语法解析 | 独立审查 |
| [52 · 类型、字符串与时间](reference/52-sqlserver-types.html) | 18 | 18 个语法解析 | 独立审查 |
| [53 · JSON、XML、全文、正则和模糊匹配](reference/53-sqlserver-documents.html) | 21 | 21 个语法解析 | 独立审查 |
| [54 · 表结构、约束、视图与分区](reference/54-sqlserver-schema.html) | 13 | 13 个语法解析 | 独立审查 |
| [55 · 时态、变更跟踪、图与账本](reference/55-sqlserver-history-graph.html) | 11 | 11 个语法解析 | 独立审查 |
| [56 · 索引、统计、计划与诊断](reference/56-sqlserver-plans.html) | 13 | 13 个语法解析 | 独立审查 |
| [57 · 程序结构与服务队列](reference/57-sqlserver-routines.html) | 11 | 11 个语法解析 | 独立审查 |
| [58 · 事务、隔离和错误处理](reference/58-sqlserver-transactions.html) | 11 | 11 个语法解析 | 独立审查 |
| [59 · 权限、加密和审计](reference/59-sqlserver-security.html) | 12 | 12 个语法解析 | 独立审查 |
| [60 · 实例、备份、系统对象和外部数据](reference/60-sqlserver-administration.html) | 14 | 14 个语法解析 | 独立审查 |
| [61 · SQL Server 版本与迁移附录](reference/61-sqlserver-versions.html) | 17 | 17 个语法解析 | 独立审查 |
| [63 · 诊断与对象实用语句](reference/63-sqlserver-utilities.html) | 13 | 13 个语法解析 | 独立审查 |

## 官方索引核对范围

[补录清单](DIALECT-SYLLABUS.md)的专题均已有承载章节。[官方参考索引](DIALECT-REFERENCE-INDEX.md)包含 1,889 个目录条目，其中 234 项已链接到引用同一文档页面的示例。目录也收录共有语法、云产品专有功能以及已弃用的入口。链接按官方文档页面登记。子句、选项与签名的覆盖状态逐项核对。

当前记录的颗粒度是专题和已编例的语法。官方索引剩余条目仍需逐项判定适用产品、语法变体和是否已有例子。统计以实际示例和验证方式为准。
