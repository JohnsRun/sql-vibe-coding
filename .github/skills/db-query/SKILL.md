---
name: db-query
description: Execute read-only SQL queries (SELECT and DESCRIBE only) against Oracle database. No data modification allowed.
argument-hint: Provide the SQL SELECT or DESCRIBE query to execute
user-invocable: true
---

# Skill Instructions

## Purpose

Execute read-only SQL queries against Oracle database:
- `SELECT` statements for data retrieval
- `DESC` / `DESCRIBE` statements for schema inspection

No data modification, creation, or deletion operations allowed.

## Hard Safety Rules (Mandatory)

1. Only execute single statements that begin with:
   - `SELECT`
   - `DESC` or `DESCRIBE`
   - `WITH` (CTE, must end with SELECT)

2. **Strictly reject** all non-query operations:
   - DML: `INSERT`, `UPDATE`, `DELETE`, `MERGE`
   - DDL: `CREATE`, `ALTER`, `DROP`, `TRUNCATE`, `RENAME`, `COMMENT`
   - TCL: `COMMIT`, `ROLLBACK`, `SAVEPOINT`
   - DCL: `GRANT`, `REVOKE`
   - PL/SQL: `BEGIN`, `DECLARE`, `CALL`, `EXEC`, `EXECUTE`
   - Session/System: `SET`, `SHOW`, `HOST`

3. Reject multi-statement SQL (no semicolon-separated statements).

4. If any non-query operation is detected, output only:
   ```
   ERROR: Query operation rejected. Only SELECT and DESCRIBE statements are allowed.
   ```

## Schema Reference - Data Dictionary Lookup

Before executing any query, consult `.github/skills/db-query/reference/data-dict.md`:
- **Check table/column names** against data dictionary
- **Verify Chinese/English mappings** for column references
- **Validate column types** and valid value ranges
- **Use correct English column names** in SQL (e.g., `FIRST_NAME`, not `名字`)
- **Provide bilingual context** in response (English column + Chinese meaning)

Example: For `ADDRESS` column, reference shows it maps to `家庭住址` (home address).

## Schema Exploration Workflow (Mandatory Pre-Query Step)

⚠️ **CRITICAL**: Before executing business queries, especially for unfamiliar tables or Chinese data:

1. **Execute DESCRIBE to inspect table structure**:
   ```sql
   DESCRIBE TABLE_NAME
   ```
   - Understand all column names and data types
   - Identify key fields and their meanings

2. **Query sample records** to understand data storage format:
   ```sql
   SELECT * FROM TABLE_NAME WHERE ROWNUM <= 5
   ```
   - Verify actual data format (especially for Chinese fields)
   - Understand field storage patterns (e.g., LAST_NAME vs FIRST_NAME order)
   - Avoid assumptions about naming conventions

3. **Example Issue Encountered**:
   - ❌ Assumed: LAST_NAME='范', FIRST_NAME='冰冰' (standard order)
   - ✅ Actual DB: LAST_NAME='冰冰', FIRST_NAME='范' (reversed order)
   - Impact: Multiple retry queries needed; efficiency reduced

## Chinese Data Query Special Handling

When querying Chinese personal names or similar multi-character fields:

1. **Never assume LAST_NAME/FIRST_NAME storage order** - must inspect sample data first
2. **For name searches**, use flexible matching patterns:
   - Full name search: `WHERE CONCAT(LAST_NAME, FIRST_NAME) = '范冰冰'`
   - Or fuzzy: `WHERE LAST_NAME LIKE '%范%' OR FIRST_NAME LIKE '%冰冰%'`
3. **Always validate** by querying sample records first before filtering
4. **Document findings** in query comments for future reference

## Oracle MCP Usage - Automated Workflow

**Auto-Connection Flow (Fully Automated)**:

1. Check if database connection is active
   - If yes → proceed to query execution
   - If no → proceed to step 2

2. Resolve database/environment names case-insensitively (default: `DEV`):
   - `DEV` / `dev` → `Oracle_DEV`
   - `UAT` / `uat` → `Oracle_UAT`
   - `PROD` / `prod` → `Oracle_PROD`

3. List available saved connections
   - If resolved connection exists → auto-connect to it
   - If resolved connection not found → ask user for exact connection name

4. Activate SQL execution tools automatically

5. Execute query through Oracle MCP `sql_run` tool with `SYNCHRONOUS` execution mode

**Result**: User simply provides SQL query → Connection handled automatically ✅

## Response Behavior

1. Execute the validated SELECT/DESCRIBE statement.
2. Return results in markdown table format.
3. For large result sets, display first 100 rows by default.
4. Include row count and execution summary if applicable.
5. If no rows returned, display table header only.

## Supported Example Prompts

- "Query all users from USER_TAB_COLUMNS"
- "Select data from employees where salary > 50000"
- "Describe the structure of the ORDERS table"
- "List all tables in the current schema"

## Unsupported Example Prompts

- "Insert a new record into users"
- "Create a new table for products"
- "Delete old records from logs"
- "Update employee salaries"
