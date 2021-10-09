import psycopg2
import config


def init():
    """
    Initiates the connection with the database.
    :return: A tuple of (the connection object, the cursor to perform commands).
    """
    conn = psycopg2.connect(dbname=config.db_name, user=config.user,
                            password=config.password, host=config.db_host)
    return conn, conn.cursor()


def get_users_data(table_name: str) -> list:
    """
    Retrieves all the rows in the table table_name.
    :param table_name: The name of the table.
    :return: A list of lists where each inner list is a row in the DB.
    """
    conn, cur = init()

    cur.execute(f"SELECT user_id, first_name, last_name, birthdate, img_path FROM {table_name};")
    data = cur.fetchall()

    conn.commit()
    cur.close()
    conn.close()

    res = []
    for row in data:
        res.append(row)
    return res


def get_ids(table_name: str) -> list:
    """
    Retrieves the user_id of all the users inside the 'table_name' table.
    :param table_name: The name of the table to be searched.
    :return: A list of the user_ids of the users inside the table.
    """
    conn, cur = init()

    cur.execute(f"SELECT user_id FROM {table_name};")
    data = cur.fetchall()

    conn.commit()
    conn.close()
    cur.close()

    return [user[0] for user in data]


def handle_row(table_name: str, user: list) -> None:
    """
    Checks if the row user is in the database and either add it or update it.
    :param table_name: The table to check in.
    :param user: A list containing the row info of that user.
    """
    conn, cur = init()

    if user[0] in get_ids(table_name):
        user = [user[1], user[2], user[3], user[4], user[0]]

        cur.execute(f"""
            UPDATE {table_name} SET first_name = %s, last_name = %s, 
            birthdate = %s, img_path = %s WHERE user_id = %s;
            """, user)
    else:
        cur.execute(
            f"INSERT INTO {table_name} (user_id, first_name, last_name, birthdate, img_path) "
            f"VALUES (%s, %s, %s, %s, %s)", user)

    conn.commit()
    conn.close()


def create_table_users(table_name: str) -> None:
    """
    Creates the table that will have the data from output.csv.
    :param table_name: The name of the table to be created.
    """
    conn, cur = init()

    cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name}(
                id SERIAL PRIMARY KEY NOT NULL,
                user_id varchar (10) NOT NULL,
                first_name varchar (20) NOT NULL,
                last_name varchar (20) NOT NULL,
                birthdate varchar (40) NOT NULL,
                img_path varchar (300) NOT NULL
            );
        """)

    conn.commit()
    cur.close()
    conn.close()
