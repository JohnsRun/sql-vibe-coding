---
description: "Use when creating or editing Oracle script files (.sql, .pkb, .pkg). Following the the coding standard"
name: "SQL Script Coding Standard."
applyTo: "**/*.{sql,pkb,pkg}"
---
You are an expert Oracle Database developer. Your task is to generate valid, efficient, and beautifully formatted Oracle PL/SQL code based on the user's instructions. You must adhere strictly to the following formatting and structural rules:

### 1. Code Layout & Alignment

- Indentation: Use 4 spaces per indentation level. Do not use hard tabs.
- Multi-line Statements: Indent subqueries, JOIN clauses, and nested loops cleanly.
- Vertical Alignment: Vertically align variable declarations, assignment operators (`:=`), and `INTO` columns where possible for maximum readability.
- One Clause Per Line: Keep SELECT, FROM, WHERE, GROUP BY, and ORDER BY clauses on separate lines.

### 2. Version Control

- When creating the DDL of the procedure, package, and function, must include a changelog at the top of DDL body with the following details:

  - Version (e.g., `v001`)
  - Author (Default `Admin`)
  - Date (e.g., `2024-06-01`)
  - Description ("Initial version" for the first version)
    **Template:**

  ```sql
  create or replace procedure procedure_name is
  ----------------------------------------------------------------------
  -- |Version |Author |Date      |Description
  -- |v001    |Admin  |2024-06-01|Initial version  
  ----------------------------------------------------------------------
    begin
        -- procedure body
  ```
  **⚠️ IMPORTANT:** The whole changelog comment block **MUST be left-aligned with NO leading spaces**. The first - should align with the first letter of `CREATE`.
- For the changes in the script, maintain changelog and increment the version number (e.g., `v002`, `v003`, etc.) with a brief description of the change.
- You also need to add the comments in the changed snippets, while `--v002s` means the start of the second version of the script and `--v002e` means the end.
- Comment the previous version snippets changed instead of removing them.

  ```sql
  --v003s
  select * from A
  where 1 = 1
  --v002s
  --where 1 <> 1
  --v002e
  --v003e

  ```
