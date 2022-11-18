import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Connected to {db_file}, sqlite version: {sqlite3.version}")
    except Error as e:
        print(e)
    finally:
        if conn:
            return conn


def create_connection_in_memory():
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(":memory:")
        print(f"Connected, sqlite version: {sqlite3.version}")
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def execute_sql(connect, sql):
    """ Execute sql
   :param connect: Connection object
   :param sql: a SQL script
   :return:
   """
    try:
        c = connect.cursor()
        c.execute(sql)
    except Error as e:
        print(e)


def select_task_by_status(conn, status):
    """
   Query tasks by priority
   :param conn: the Connection object
   :param status:
   :return:
   """
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE status=?", (status,))

    rows = cur.fetchall()
    return rows


def select_all(conn, table):
    """
   Query all rows in the table
   :param conn: the Connection object
   :return:
   """
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table}")
    rows = cur.fetchall()

    return rows


def select_where(conn, table, **query):
    """
   Query tasks from table with data from **query dict
   :param conn: the Connection object
   :param table: table name
   :param query: dict of attributes and values
   :return:
   """
    cur = conn.cursor()
    qs = []
    values = ()
    for k, v in query.items():
        qs.append(f"{k}=?")
        values += (v,)
    q = " AND ".join(qs)
    cur.execute(f"SELECT * FROM {table} WHERE {q}", values)
    rows = cur.fetchall()
    return rows


def update(conn, table, id, **kwargs):
    """
   update status, begin_date, and end date of a task
   :param conn:
   :param table: table name
   :param id: row id
   :return:
   """
    parameters = [f"{k} = ?" for k in kwargs]
    parameters = ", ".join(parameters)
    values = tuple(v for v in kwargs.values())
    values += (id,)

    sql = f''' UPDATE {table}
             SET {parameters}
             WHERE id = ?'''
    try:
        cur = conn.cursor()
        cur.execute(sql, values)
        conn.commit()
        print("OK")
    except sqlite3.OperationalError as e:
        print(e)


def delete_where(conn, table, **kwargs):
    """
   Delete from table where attributes from
   :param conn:  Connection to the SQLite database
   :param table: table name
   :param kwargs: dict of attributes and values
   :return:
   """
    qs = []
    values = tuple()
    for k, v in kwargs.items():
        qs.append(f"{k}=?")
        values += (v,)
    q = " AND ".join(qs)

    sql = f'DELETE FROM {table} WHERE {q}'
    cur = conn.cursor()
    cur.execute(sql, values)
    conn.commit()
    print("Deleted")


def delete_all(conn, table):
    """
   Delete all rows from table
   :param conn: Connection to the SQLite database
   :param table: table name
   :return:
   """
    sql = f'DELETE FROM {table}'
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    print("Deleted")


def add_player(conn_ta, player):
    """
    Create a new project into the projects table
    :param conn_ta:
    :param player:
    :return: player id
    """
    sql = '''INSERT INTO players(team_id, number, name, surname, position)
             VALUES(?,?,?,?,?)'''
    cur = conn_ta.cursor()
    cur.execute(sql, player)
    conn_ta.commit()
    return cur.lastrowid


def add_team(conn_pro, team):
    """
    Create a new task into the projects table
    :param conn_pro:
    :param team:
    :return: team id
    """
    sql = '''INSERT INTO teams(nationality, team_group)
              VALUES(?,?)'''
    cur = conn_pro.cursor()
    cur.execute(sql, team)
    conn_pro.commit()
    return cur.lastrowid


def add_match(conn_pro, match):
    """
    Create a new task into the projects table
    :param conn_pro:
    :param match:
    :return: team id
    """
    sql = '''INSERT INTO matches(team_A_id, team_B_id,versus, date, status)
              VALUES(?,?,?,?,?)'''
    cur = conn_pro.cursor()
    cur.execute(sql, match)
    conn_pro.commit()
    return cur.lastrowid


def update_unique(connection, table, id, **kwargs):
    try:
        update(connection, table, id, **kwargs)
    except sqlite3.IntegrityError:
        print(f'Taki wpis do tabeli: {table} istnieje.')


def add_unique(items, items_id, keyword):
    j = 1
    for i in items:
        try:
            if keyword == 'team':
                data_type = [f'Drużyna {i[0]} dodana.', f'Dane dotyczące drużyny: {i[0]} istnieją.']
                i_id = add_team(conn, i)
            elif keyword == 'player':
                data_type = [f'Zawodnik {i[2]} {i[3]} dodany.', f'Dane dotyczące zawodnika: {i[2]} {i[3]} istnieją.']
                i_id = add_player(conn, i)
            else:
                data_type = [f'Mecz {i[2]} dodany.', f'Dane dotyczące meczu: {i[2]} istnieją.']
                i_id = add_match(conn, i)
            items_id.append(i_id)
            print(data_type[0])
        except sqlite3.IntegrityError:
            items_id.append(j)
            j += 1
            print(data_type[1])


if __name__ == '__main__':
    create_football_team = """
    -- drużyny table
    CREATE TABLE IF NOT EXISTS teams (
      id integer PRIMARY KEY,
      nationality VARCHAR(250) NOT NULL,
      team_group VARCHAR(250) NOT NULL,
      UNIQUE(nationality)
    );
    """

    create_football_player = """
    -- zawodnicy table
    CREATE TABLE IF NOT EXISTS players (
      id integer PRIMARY KEY,
      team_id integer NOT NULL,
      number integer NOT NULL,
      name VARCHAR(250) NOT NULL,
      surname VARCHAR(250) NOT NULL,
      position VARCHAR(250) NOT NULL,
      FOREIGN KEY (team_id) REFERENCES teams (id),
      UNIQUE(name, surname)
    );
    """

    create_matches = """
    -- mecze table
    CREATE TABLE IF NOT EXISTS matches (
      id integer PRIMARY KEY,
      team_A_id integer NOT NULL,
      team_B_id integer NOT NULL,
      versus text NOT NULL,
      date text NOT NULL,
      status VARCHAR(250) NOT NULL,
      FOREIGN KEY (team_A_id) REFERENCES teams (id),
      FOREIGN KEY (team_B_id) REFERENCES teams (id),
      UNIQUE(team_A_id, team_B_id)
    );
    """

    conn = create_connection('database.db')

    if conn is not None:
        execute_sql(conn, create_football_team)
        execute_sql(conn, create_football_player)
        execute_sql(conn, create_matches)

    team_id = []
    players_id = []
    matches_id = []
    if conn is not None:
        teams = [
            ("POLSKA", "C"),
            ("ARABIA SAUDYJSKA", "C"),
            ("MEKSYK", "C"),
            ("ARGENTYNA", "C")
        ]
        add_unique(teams, team_id, 'team')

        POSITION = ['Bramkarz', 'Obrońca', 'Pomocnik', 'Napastnik']

        players = [
            (team_id[0], 9, "Robert", "Lewandowski", POSITION[3]),
            (team_id[0], 12, "Arkadiusz", "Milik", POSITION[3]),
            (team_id[0], 18, "Karol", "Świderski", POSITION[3]),
            (team_id[0], 19, "Wojciech", "Szczęsny", POSITION[0]),
            (team_id[0], 21, "Kamil", "Glik", POSITION[1]),
            (team_id[0], 23, "Jan", "Bednarek", POSITION[1]),
            (team_id[0], 8, "Jakub", "Kiwior", POSITION[1]),
            (team_id[0], 10, "Robert", "Gumny", POSITION[1]),
            (team_id[0], 11, "Grzegorz", "Krychowiak", POSITION[2]),
            (team_id[0], 17, "Piotr", "Zieliński", POSITION[2]),
            (team_id[0], 13, "Kamil", "Grosicki", POSITION[2]),
            (team_id[1], 12, "Alexis", "Vega", POSITION[3]),
            (team_id[1], 10, "Hirving", "Lozano", POSITION[3]),
            (team_id[1], 1, "Raul", "Jimenez", POSITION[3]),
            (team_id[1], 8, "Guillermo", "Ochoa", POSITION[0]),
            (team_id[1], 24, "Jorge", "Sanchez", POSITION[1]),
            (team_id[1], 5, "Kevin", "Alvarez", POSITION[1]),
            (team_id[1], 13, "Nestor", "Araujo", POSITION[1]),
            (team_id[1], 14, "Cesar", "Montez", POSITION[1]),
            (team_id[1], 17, "Andres", "Guardado", POSITION[2]),
            (team_id[1], 19, "Hector", "Herrera", POSITION[2]),
            (team_id[1], 21, "Charly", "Rodriguez", POSITION[2]),
        ]
        add_unique(players, players_id, 'player')

        matches = [
            (team_id[0], team_id[2], f'{teams[0][0]} vs {teams[2][0]}', '22.11.2022, godz. 17:00', 'Odbyty'),
            (team_id[0], team_id[1], f'{teams[0][0]} vs {teams[1][0]}', '26.11.2022, godz. 14:00', 'Nieodbyty'),
            (team_id[0], team_id[3], f'{teams[0][0]} vs {teams[3][0]}', '30.11.2022, godz. 20:00', 'Nieodbyty'),
        ]
        add_unique(matches, matches_id, 'match')
        update_unique(conn, "players", players_id[6], name="Artur", surname="Jędrzejczyk")
        update_unique(conn, "matches", matches_id[0], status="Niedbyty")

        delete_where(conn, "matches", status="Odbyty")

        print(select_all(conn, "matches"))
        print(select_where(conn, 'players', team_id=team_id[0]))
        conn.close()
