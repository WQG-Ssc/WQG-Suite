import sqlite3 as sql
main_db = r"Files\data\main_test.db"
other_db = r"Files\data\other.db"

def exception_handler(func):
    def wrapper(*args, **kwargs):
        try: 
            return func(*args, **kwargs)
        except sql.Error as error:
            print(f'An error occurred in {func.__name__}: {error}')
            return False
    return wrapper

@exception_handler
def loadMainData(data_type, *args):
    conn = sql.connect(main_db)
    cur = conn.cursor()

    if data_type == "branches":
        cur.execute("SELECT name FROM Branches")

    if data_type == "goals":
        cur.execute(f"SELECT name, total_difficulty, time, benefit, limit_date, priority, state, ID, files, progress, custom_characteristics FROM Goals WHERE ID LIKE '{args[0]}.%' ORDER BY ID")

    if data_type == "goal":
        cur.execute("SELECT * FROM Goals WHERE ID == ?", args)
        goal_data = cur.fetchone()
        conn.close()
        return list(goal_data)

    if data_type == "branch":
        cur.execute("SELECT name FROM Branches WHERE RowID == ?", args)
        branch_name = cur.fetchone()
        conn.close()
        return branch_name

    if data_type == "skills":
        cur.execute("SELECT * FROM Skills")

    if data_type == "day_stats":
        cur.execute(f"SELECT date, [{args[0]}] FROM Days")

    if data_type == "names":
        if args[0] == "Goals":
            cur.execute(f"SELECT name, ID FROM Goals")
        else:
            cur.execute(f"SELECT name FROM {args[0]}")
    
    if data_type == "graphs":
        cur.execute("SELECT * FROM Graphs")

    if data_type == "goal_custom":#Custom characteristics
        cur.execute("SELECT cc_stats FROM Goals WHERE ID == ?", (args))
        cc_stats = cur.fetchone()
        conn.close()
        return cc_stats

    if data_type == "characteristic":
        cur.execute("SELECT c_type, v_type, c_values, is_showing_in_gl FROM Characteristics WHERE name == ?", (args))

    if data_type == "skill_stat":
        cur.execute(f"SELECT date, [{args[0]}] FROM Skills_statistics WHERE '{args[0]}' IS NOT NULL")

    if data_type == "statistics":
        cur.execute("SELECT start_time, end_time, date FROM Main_statistics WHERE task_ID == ?", args)

    if data_type == "graph_color":
        cur.execute("SELECT color FROM Graphs WHERE name == ?", args)
        color = cur.fetchone()
        conn.close()
        return color

    data = cur.fetchall()
    conn.close()
    return data

@exception_handler
def saveMainData(data_type, args):
    conn = sql.connect(main_db)
    cur = conn.cursor()
    if data_type == "branch":
        cur.execute("INSERT INTO Branches (name) VALUES (?)", (args,))
    if data_type == "goal":
        cur.execute("INSERT INTO Goals (ID, name, total_difficulty, time, benefit, limit_date, priority, used_skills, state, note, files, progress, custom_characteristics) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", args)
    if data_type == "skill":
        cur.execute(f"INSERT INTO Skills (name) VALUES ('{args}')")
        cur.execute(f"ALTER TABLE Skills_statistics ADD COLUMN '{args}' REAL")
    if data_type == "Characteristics":
        cur.execute("INSERT INTO Characteristics (name, c_type, v_type, c_values, showing_in_gl) VALUES (?, ?, ?, ?, ?)", args)
    conn.commit()
    conn.close()

@exception_handler
def updateMainData(data_type, args):
    conn = sql.connect(main_db)
    cur = conn.cursor()
    if data_type == "branch":
        cur.execute("UPDATE Branches SET name = ? WHERE name == ?", (args,))
    if data_type == "goal":
        cur.execute("UPDATE Goals SET ID = ?, name = ?, total_difficulty = ?, time = ?, benefit = ?, limit_date = ?, priority = ?, used_skills = ?, state = ?, note = ?, files = ?, progress = ?, custom_characteristics = ? WHERE ID == ?", args)
    if data_type == "skill":
        cur.execute("UPDATE Skills SET name = ? WHERE name = ?", (args,))
    if data_type == "Characteristics":
        cur.execute("UPDATE Characteristics SET c_type = ?, v_type = ?, c_value = ?, showing_in_gl = ? WHERE name == ?", args)
    conn.commit()
    conn.close()

@exception_handler
def deleteMainData(data_type, *args):
    conn = sql.connect(main_db)
    cur = conn.cursor()
    if data_type == "branch":
        cur.execute("DELETE FROM Branches WHERE name == ?", args)
    if data_type == "goal":
        cur.execute("DELETE FROM Goals WHERE ID == ?", args)
    conn.commit()
    conn.close()

@exception_handler
def getGoalTree(goal_id):
    conn = sql.connect(main_db)
    cur = conn.cursor()
    cur.execute(f"SELECT ID, name, progress, time FROM Goals WHERE ID LIKE '{goal_id}%' ORDER BY ID ASC")
    goal_tree = cur.fetchall()
    conn.close()
    return goal_tree

@exception_handler
def getGoalIDs(parent_id):
    conn = sql.connect(main_db)
    cur = conn.cursor()
    cur.execute(f"SELECT ID FROM Goals WHERE ID LIKE '{parent_id}%'")
    goal_tree = cur.fetchall()
    conn.close()
    return goal_tree