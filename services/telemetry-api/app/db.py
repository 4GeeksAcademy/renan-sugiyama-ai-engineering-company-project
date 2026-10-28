from typing import Any

from psycopg import sql
from psycopg.types.json import Jsonb
from psycopg_pool import ConnectionPool


def insert_telemetry_rows(pool: ConnectionPool, rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0

    row_placeholders = sql.SQL("({})").format(
        sql.SQL(", ").join(sql.Placeholder() for _ in range(5))
    )
    values_clause = sql.SQL(", ").join(row_placeholders for _ in rows)
    statement = sql.SQL(
        """
        INSERT INTO public.telemetry_events
            (event_type, timestamp, service, tags, level)
        VALUES {}
        ON CONFLICT ((tags ->> 'event_id')) DO NOTHING
        RETURNING tags ->> 'event_id'
        """
    ).format(values_clause)

    parameters: list[Any] = []
    for row in rows:
        parameters.extend(
            (
                row["event_type"],
                row["timestamp"],
                row["service"],
                Jsonb(row["tags"]),
                row["level"],
            )
        )

    with pool.connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(statement, parameters)
            return len(cursor.fetchall())