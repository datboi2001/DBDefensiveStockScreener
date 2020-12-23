import psycopg2
from psycopg2 import extensions
from credentials import passcode, username, port, dbname, host


def create_connection() -> (extensions.connection, extensions.cursor):
    """Create connection and cursor to PostgreSQL database"""
    conn = psycopg2.connect(dbname=dbname, user=username,
                            password=passcode, host=host,
                            port=port)
    conn.autocommit = True
    cur = conn.cursor()
    return conn, cur


def close_connection(conn: extensions.connection, cur: extensions.cursor) -> None:
    conn.close()
    cur.close()


def execute_query(cur: extensions.cursor, query):
    cur.execute(query)
    result = cur.fetchall()
    return result


def create_query(criteria: {str: str}) -> str:
    base_query = f"select * from \"{criteria['exchange']}\" where "
    manipulated_form = sorted(criteria.items())
    for i in list(manipulated_form):
        crit, value = i
        if crit == "exchange" or value.lower().strip() == "any":
            manipulated_form.remove(i)

    if not manipulated_form:
        base_query = base_query.replace(" where", ";")
    for i in range(len(manipulated_form)):
        crit, value = manipulated_form[i]
        if i != len(manipulated_form) - 1:
            base_query += f"{crit} {value.strip()} and "
        else:
            base_query += f"{crit} {value.strip()};"
    return base_query
