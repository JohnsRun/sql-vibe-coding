---
name: db-action
description: Generate and execute DDL/DML statements (CREATE, ALTER, INSERT, UPDATE, DELETE, etc.) against Oracle database. Requires user confirmation before execution.
argument-hint: Describe the database action to perform (create table, insert data, update records, etc.)
user-invocable: true
---
# Skill Instructions

## Purpose

Generate and execute data manipulation and schema modification statements:

- **DML**: `INSERT`, `UPDATE`, `DELETE`, `MERGE`
- **DDL**: `CREATE`, `ALTER`, `DROP`, `TRUNCATE`, `RENAME`, `COMMENT`

All generated statements must be:

1. Displayed to the user in full
2. Explicitly confirmed by the user before execution
3. Executed only after approval
4. Execute `commit;` after DML operation.

## Hard Safety Rules (Mandatory)

1. **Generate-Confirm-Execute workflow**:

   - Step 1: Generate the complete SQL statement based on user intent
   - Step 2: Display the statement in a clear, formatted code block
   - Step 3: Request explicit user confirmation (e.g., "Do you want to proceed?")
   - Step 4: Execute only after user approves
2. **Allowed Operations**:

   - DML: `INSERT`, `UPDATE`, `DELETE`, `MERGE`
   - DDL: `CREATE TABLE`, `CREATE INDEX`, `ALTER TABLE`, `DROP TABLE`, `DROP INDEX`, `TRUNCATE TABLE`, `RENAME TABLE`, `COMMENT ON`
   - Other: `TRUNCATE`, `RENAME`
3. **Strictly Reject**:

   - Read-only queries (use `db-query` skill instead): `SELECT`, `WITH`, `DESC`, `DESCRIBE`
   - TCL: `COMMIT`, `ROLLBACK`, `SAVEPOINT`
   - DCL: `GRANT`, `REVOKE`
   - PL/SQL execution: `BEGIN`, `DECLARE`, `CALL`, `EXEC`, `EXECUTE`
   - System operations: `SET`, `SHOW`, `HOST`
4. **Oracle INSERT Syntax**:

   - **Single row INSERT**: Standard Oracle supports one row per INSERT statement
     ```sql
     INSERT INTO table_name (col1, col2) VALUES (val1, val2);
     ```
   - **Multiple rows**: Use one of these approaches:
     - **Separate INSERT statements**: Generate multiple individual INSERT statements (one row each)
     - **INSERT ALL** (Oracle 9i+): For inserting multiple rows in a single statement
       ```sql
       INSERT ALL
         INTO table_name (col1, col2) VALUES (val1a, val2a)
         INTO table_name (col1, col2) VALUES (val1b, val2b)
       SELECT * FROM dual;
       ```
   - **When user requests multiple rows**: Generate separate INSERT statements, each inserting one row, displayed together before confirmation
5. **Multi-Statement SQL**: Support multiple statements if they form a logical unit (e.g., disable constraints + insert + enable constraints).

   - Display all statements together before requesting confirmation.
6. **Never auto-execute**: Always wait for user confirmation before running any statement.
7. **Syntax**: Oracle SQL standard

## Oracle MCP Usage

1. Resolve database/environment names case-insensitively:

   - `DEV` → `Oracle_DEV`
   - `UAT` → `Oracle_UAT`
   - `PROD` → `Oracle_PROD`
2. Default to `DEV` (connection: `Oracle_DEV`) if no database specified.
3. Connect to the resolved saved connection name first if not already connected.
4. If connection does not exist, ask the user for the exact saved connection name.
5. **Auto-Connection (Before SQL Generation)**:

   - Check if database connection is active
     - If yes → proceed to generation
     - If no → auto-connect to default or specified database:
       - Resolve env names: `DEV` → `Oracle_DEV`, `UAT` → `Oracle_UAT`, `PROD` → `Oracle_PROD`
       - List saved connections and auto-connect
       - If connection fails, ask user for exact name
   - Activate SQL execution tools automatically
6. **Before Execution**:

   - Parse the generated SQL for syntax
   - Display it clearly to the user with line numbers
   - Use `vscode_askQuestions` tool or inline request for confirmation
7. Execute through Oracle MCP `sql_run` or `sqlcl_run` with `SYNCHRONOUS` execution mode only after user approval.

**Result**: User provides action description → Connection + Generation + Confirmation + Execution all streamlined ✅

## Response Behavior

### Generation Phase

1. Generate the complete SQL statement(s) based on user requirements.
2. Display in markdown code block with proper formatting and line numbers.
3. Include a brief description of what the statement will do.
4. Highlight any potential data impact (e.g., "This will delete 1000 records").

### Confirmation Phase

5. Request explicit user confirmation using clear language:
   - "Do you want to proceed with this operation?"
   - "Confirm execution?"
   - Present a yes/no choice

### Execution Phase

6. Execute only after user approval.
7. Return execution result (rows affected, errors, success message).
8. Provide a summary of changes made.

## Supported Example Prompts

- "Create a new table for customer orders"
- "Insert 5 new employee records"
- "Update all inactive accounts to status='archived'"
- "Delete test data from the temp table"
- "Add a new column to the products table"
- "Create an index on the email column"

## Unsupported Example Prompts

- "Query all customers" (use `db-query` skill)
- "Show the table structure" (use `db-query` skill)
- "Select recent transactions" (use `db-query` skill)
