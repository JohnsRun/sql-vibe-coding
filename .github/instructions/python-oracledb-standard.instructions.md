---
applyTo: "**/*.py"
---
# Python 数据库连接规范（Oracle）

## 强制规则

1. 只要 Python 代码需要连接数据库，必须使用 `oracledb` 包。
2. 禁止使用其他数据库驱动建立连接（例如 `sqlite3`、`pymysql`、`psycopg2`、`mysql.connector` 等），除非用户明确豁免。
3. 连接示例、工具函数、脚本模板都必须以 `oracledb` 为默认实现。

## 编码要求

1. 必须显式导入：`import oracledb`。
2. 建立连接时优先使用 `oracledb.connect(...)`。
3. 需要连接池时使用 `oracledb.create_pool(...)`。
4. 关闭资源时应关闭 cursor 和 connection（或连接池），避免泄漏。

## 输出与建议

1. 当用户请求“连接数据库”的 Python 代码时，默认输出基于 `oracledb` 的可执行示例。
2. 如果用户给出的现有代码使用了其他驱动，应先建议迁移到 `oracledb`，再继续实现需求。
3. 如果用户明确要求非 Oracle 数据库或明确要求其他驱动，按用户要求执行，并说明这是对本规范的例外。
