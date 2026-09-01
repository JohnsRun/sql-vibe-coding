"""Export Oracle package body DDL through a constrained command-line interface.

Required environment variables:
    ORA_HOST
    ORA_PORT
    ORA_SERVICE_DEV
    ORA_USER_QUERY_DEV
    ORA_PASSWORD_QUERY_DEV
    ORA_SERVICE_UAT
    ORA_USER_QUERY_UAT
    ORA_PASSWORD_QUERY_UAT

Optional environment variables:
    ORACLE_CLIENT_LIB_DIR  Path to Oracle Instant Client libraries.
"""
import argparse
from pathlib import Path
import os
import re
import sys

import oracledb


_ENVIRONMENT_VARIABLES = {
    "DEV": ("ORA_SERVICE_DEV", "ORA_USER_QUERY_DEV", "ORA_PASSWORD_QUERY_DEV"),
    "UAT": ("ORA_SERVICE_UAT", "ORA_USER_QUERY_UAT", "ORA_PASSWORD_QUERY_UAT"),
}
_OBJECT_NAME_PATTERN = re.compile(r"^[A-Z][A-Z0-9_$#]*$")
_DDL_QUERY = """
SELECT DBMS_METADATA.GET_DDL(
         'PACKAGE_BODY',
         :object_name,
         USER
       ) AS package_body_ddl
  FROM dual
"""


def _load_config(environment: str) -> dict[str, str | int]:
    """Load connection settings without exposing their values."""
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


def _read_ddl(config: dict[str, str | int], object_name: str) -> str | None:
    """Fetch one package body DDL CLOB using the current database user."""
    dsn = f"{config['host']}:{config['port']}/{config['service']}"
    with oracledb.connect(
        user=config["user"], password=config["password"], dsn=dsn
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(_DDL_QUERY, object_name=object_name)
            row = cursor.fetchone()
    if row is None or row[0] is None:
        return None
    ddl = row[0].read() if hasattr(row[0], "read") else str(row[0])
    return ddl if isinstance(ddl, str) else ddl.decode("utf-8")


def _save_ddl(object_name: str, ddl: str) -> Path:
    """Persist the complete DDL in the agent-owned temporary output directory."""
    temp_directory = Path(__file__).resolve().parent.parent / "temp"
    temp_directory.mkdir(parents=True, exist_ok=True)
    output_path = temp_directory / f"{object_name}.package_body.sql"
    output_path.write_text(ddl, encoding="utf-8")
    return output_path


def _print_result(environment: str, output_path: Path, ddl: str) -> None:
    """Print the saved location and the requested 10-line SQL preview."""
    workspace_root = Path(__file__).resolve().parents[4]
    print("---")
    print(f"Connection: {environment}")
    print()
    print(f"Saved: {output_path.relative_to(workspace_root)}")
    print()
    print("```sql")
    print("\n".join(ddl.splitlines()[:10]))
    print("```")


def main(argv: list[str] | None = None) -> int:
    """Export one validated package body and print its first 10 DDL lines."""
    parser = argparse.ArgumentParser(description="Export one Oracle package body DDL.")
    parser.add_argument(
        "--env",
        choices=("DEV", "UAT"),
        default="DEV",
        type=str.upper,
        help="Connection environment; defaults to DEV.",
    )
    parser.add_argument("--object-name", required=True, help="Oracle package name.")
    args = parser.parse_args(argv)
    object_name = args.object_name.upper()

    if not _OBJECT_NAME_PATTERN.fullmatch(object_name):
        print("INVALID_OBJECT_NAME: Use one ordinary Oracle package name.", file=sys.stderr)
        return 2

    try:
        config = _load_config(args.env)
        ddl = _read_ddl(config, object_name)
    except ValueError as error:
        print(f"CONFIGURATION_ERROR: {error}", file=sys.stderr)
        return 2
    except oracledb.DatabaseError as error:
        print(f"ORACLE_ERROR: {error}", file=sys.stderr)
        return 1

    if ddl is None:
        print(f"NO_DDL: No package body metadata found for {object_name}.", file=sys.stderr)
        return 1

    output_path = _save_ddl(object_name, ddl)
    _print_result(args.env, output_path, ddl)
    return 0


if __name__ == "__main__":
    client_library = os.environ.get("ORACLE_CLIENT_LIB_DIR")
    if client_library:
        oracledb.init_oracle_client(lib_dir=client_library)
    raise SystemExit(main())