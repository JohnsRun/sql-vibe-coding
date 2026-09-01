"""Run one safe Oracle DQL or approved DML statement using environment-only credentials."""
import argparse
import os
import re
import sys

import oracledb


_ENVIRONMENT_VARIABLES = {
    "DEV": ("ORA_SERVICE_DEV", "ORA_USER_ACTION_DEV", "ORA_PASSWORD_ACTION_DEV"),
    "UAT": ("ORA_SERVICE_UAT", "ORA_USER_ACTION_UAT", "ORA_PASSWORD_ACTION_UAT"),
}
_ALLOWED_OPERATIONS = {"INSERT", "UPDATE", "DELETE", "MERGE"}
_PROHIBITED_OPERATIONS = re.compile(
    r"\b(ALTER|BEGIN|CALL|COMMIT|CREATE|DECLARE|DROP|EXEC(?:UTE)?|GRANT|"
    r"REVOKE|ROLLBACK|SAVEPOINT|SHOW|TRUNCATE)\b",
    re.IGNORECASE,
)
_READ_ONLY_PROHIBITED_OPERATIONS = re.compile(
    r"\b(ALTER|BEGIN|CALL|COMMIT|CREATE|DECLARE|DELETE|DROP|EXEC(?:UTE)?|GRANT|"
    r"INSERT|MERGE|REVOKE|ROLLBACK|SAVEPOINT|TRUNCATE|UPDATE)\b|\bFOR\s+UPDATE\b",
    re.IGNORECASE,
)


def _load_config(environment: str) -> dict:
    """Load the selected connection settings without exposing their values."""
    service_variable, user_variable, password_variable = _ENVIRONMENT_VARIABLES[environment]
    required = ("ORA_HOST", "ORA_PORT", service_variable, user_variable, password_variable)
    missing = [variable for variable in required if not os.environ.get(variable)]
    if missing:
        raise ValueError(
            f"Missing required {environment} environment variable(s): " + ", ".join(missing)
        )
    try:
        port = int(os.environ["ORA_PORT"])
    except ValueError as error:
        raise ValueError("ORA_PORT must be an integer.") from error
    return {
        "host": os.environ["ORA_HOST"],
        "port": port,
        "service": os.environ[service_variable],
        "user": os.environ[user_variable],
        "password": os.environ[password_variable],
    }


_client_lib = os.environ.get("ORACLE_CLIENT_LIB_DIR")
if _client_lib:
    oracledb.init_oracle_client(lib_dir=_client_lib)


def _strip_literals_and_comments(sql: str) -> str:
    """Replace literals and comments so keyword checks only see executable SQL."""
    output = []
    index = 0
    while index < len(sql):
        if sql.startswith("--", index):
            end = sql.find("\n", index)
            index = len(sql) if end == -1 else end
        elif sql.startswith("/*", index):
            end = sql.find("*/", index + 2)
            if end == -1:
                raise ValueError("SQL contains an unterminated comment.")
            index = end + 2
        elif sql[index] == "'":
            output.append(" ")
            index += 1
            while index < len(sql):
                if sql[index] == "'":
                    index += 1
                    if index < len(sql) and sql[index] == "'":
                        index += 1
                        continue
                    break
                index += 1
            else:
                raise ValueError("SQL contains an unterminated string literal.")
        else:
            output.append(sql[index])
            index += 1
    return "".join(output)


def _has_top_level_where(sql: str) -> bool:
    depth = 0
    for token in re.finditer(r"\b\w+\b|[()]", sql, re.IGNORECASE):
        value = token.group().upper()
        if value == "(":
            depth += 1
        elif value == ")":
            depth = max(depth - 1, 0)
        elif value == "WHERE" and depth == 0:
            return True
    return False


def validate_sql(sql: str) -> tuple[str, str]:
    """Return one permitted DQL or bounded DML statement and its operation."""
    statement = sql.strip()
    normalized = _strip_literals_and_comments(statement)
    if normalized.endswith(";"):
        statement = statement[:-1].rstrip()
        normalized = normalized[:-1].rstrip()
    if not statement:
        raise ValueError("SQL must not be empty.")
    if ";" in normalized:
        raise ValueError("Only one SQL statement is allowed.")

    operation = re.match(r"^(SELECT|WITH|INSERT|UPDATE|DELETE|MERGE)\b", normalized, re.IGNORECASE)
    if not operation:
        raise ValueError("Only SELECT, WITH, INSERT, UPDATE, DELETE, or MERGE statements are allowed.")

    operation_name = operation.group(1).upper()
    prohibited_operations = (
        _READ_ONLY_PROHIBITED_OPERATIONS
        if operation_name in {"SELECT", "WITH"}
        else _PROHIBITED_OPERATIONS
    )
    if prohibited_operations.search(normalized):
        raise ValueError("The SQL contains an unsupported operation.")

    if operation_name in {"UPDATE", "DELETE"} and not _has_top_level_where(normalized):
        raise ValueError(f"{operation_name} statements must include a top-level WHERE predicate.")
    return statement, operation_name


def validate_dml_sql(sql: str) -> tuple[str, str]:
    """Backward-compatible alias for the action validator."""
    return validate_sql(sql)


def execute_dml(sql: str, config: dict) -> int:
    """Execute one DML statement and commit it after successful execution."""
    dsn = f"{config['host']}:{config['port']}/{config['service']}"
    with oracledb.connect(user=config["user"], password=config["password"], dsn=dsn) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            rowcount = cursor.rowcount
        connection.commit()
        return rowcount


def execute_query(sql: str, config: dict) -> tuple[list[str], list[tuple]]:
    """Execute one read-only query without committing and return its rows."""
    dsn = f"{config['host']}:{config['port']}/{config['service']}"
    with oracledb.connect(
        user=config["user"], password=config["password"], dsn=dsn
    ) as connection, connection.cursor() as cursor:
        cursor.execute(sql)
        columns = [column[0].lower() for column in cursor.description]
        return columns, cursor.fetchall()


def _markdown_cell(value) -> str:
    if value is None:
        return ""
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def print_query_result(columns: list[str], rows: list[tuple]) -> None:
    """Print query results as a GitHub-Flavored Markdown table."""
    if not rows:
        print("NO_DATA")
        return
    print("| " + " | ".join(columns) + " |")
    print("| " + " | ".join("---" for _ in columns) + " |")
    for row in rows:
        print("| " + " | ".join(_markdown_cell(value) for value in row) + " |")


def main(argv=None) -> int:
    """Validate and execute one Oracle DQL or DML statement, then print Markdown output."""
    parser = argparse.ArgumentParser(description="Run one safe Oracle DQL or approved DML statement.")
    parser.add_argument(
        "--env",
        choices=("DEV", "UAT"),
        default="DEV",
        type=str.upper,
        help="Connection environment; defaults to DEV.",
    )
    parser.add_argument("--sql", required=True, help="One SELECT, WITH, INSERT, UPDATE, DELETE, or MERGE statement.")
    args = parser.parse_args(argv)

    try:
        sql, operation = validate_sql(args.sql)
    except ValueError as error:
        print(f"INVALID_SQL: {error}", file=sys.stderr)
        return 2
    try:
        config = _load_config(args.env)
    except ValueError as error:
        print(f"CONFIGURATION_ERROR: {error}", file=sys.stderr)
        return 2

    try:
        if operation in _ALLOWED_OPERATIONS:
            rowcount = execute_dml(sql, config)
        else:
            columns, rows = execute_query(sql, config)
    except oracledb.DatabaseError:
        print("EXECUTION_ERROR: Oracle database execution failed.", file=sys.stderr)
        return 1
    except (OSError, RuntimeError, TypeError, ValueError):
        print("EXECUTION_ERROR: Database action failed.", file=sys.stderr)
        return 1

    print("---")
    print(f"Connection: {args.env}")
    print()
    if operation in _ALLOWED_OPERATIONS:
        print("| operation | affected_rows |")
        print("| --- | ---: |")
        print(f"| {operation} | {rowcount} |")
    else:
        print_query_result(columns, rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())