import sqlite3 as sql
import re
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
        cur.execute(f"SELECT name, time, benefit, limit_date, priority, state, ID, files, progress, custom_characteristics, showing_in_list FROM Goals WHERE ID LIKE '{args[0]}.%' ORDER BY ID")

    if data_type == "goal":
        cur.execute("SELECT * FROM Goals WHERE ID == ?", args)
        goal_data = cur.fetchone()
        conn.close()
        return list(goal_data)

    if data_type == "branch":
        cur.execute("SELECT name, custom_characteristics, sections_position FROM Branches WHERE RowID == ?", args)
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
        cur.execute("SELECT c_type, v_type FROM Characteristics WHERE name == ?", args)
        charact = cur.fetchone()
        conn.close()
        return charact

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
        cur.execute("INSERT INTO Branches (name, sections_position) VALUES (?, ?)", args)

    if data_type == "goal":
        cur.execute("INSERT INTO Goals (ID, name, time, benefit, limit_date, priority, used_skills, state, note, files, progress, custom_characteristics, cc_stats, is_group, showing_in_list) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", args)

    if data_type == "skill":
        cur.execute(f"INSERT INTO Skills (name) VALUES ('{args}')")
        cur.execute(f"ALTER TABLE Skills_statistics ADD COLUMN '{args}' REAL")

    if data_type == "Characteristics":
        cur.execute("INSERT INTO Characteristics (name, c_type, v_type) VALUES (?, ?, ?)", args)
        
    conn.commit()
    conn.close()

@exception_handler
def recalculateValues(layer):
    conn = sql.connect(main_db)
    cur = conn.cursor()
    supergoal_id = ".".join(layer[:-1])

    print(f"supergoal_id:{supergoal_id}")
    cur.execute("SELECT custom_characteristics FROM Goals WHERE ID == ?", (supergoal_id,))
    characts = cur.fetchone()[0]
    print(f"characts:{characts}")
    charactsToRecalc = []
    allCharacts = {}
    if characts:
        characts = characts.split(",")
        for charact in characts:
            charact, value = charact.split(":")
            if loadMainData("characteristic", charact)[0] == "dynamic":
                allCharacts[charact] = 0
                charactsToRecalc.append(charact)
            else:
                allCharacts[charact] = value

    cur.execute(f"SELECT ID FROM Goals WHERE ID LIKE '{supergoal_id}.%'")
    raw_ids = cur.fetchall()

    ids = [item[0] for item in raw_ids]
    print(f"ids:{ids}")
    regex = re.compile(f"^{supergoal_id}\.[^.]+$")
    layer_length = len([item for item in ids if regex.match(item)])

    print(f"layer_length: {layer_length}")

    print(f"charactsToRecalc{charactsToRecalc}")

    skills_dict = {}
    cc_stats_dict = {}
    time = 0.0

    skills = ""
    ccs = ""
    cc_stats = ""

    if layer_length:
        for goal in range(1, layer_length + 1):
            goal_id = ".".join(layer[:-1] + [str(goal)])
            print(f"selected id:{goal_id}")
            if charactsToRecalc:
                cur.execute("SELECT used_skills, time, custom_characteristics, cc_stats FROM Goals WHERE ID == ?", (goal_id,))
            else:
                cur.execute("SELECT used_skills, time FROM Goals WHERE ID == ?", (goal_id,))

            goal_data = cur.fetchone()
            print(f"goal_data:{goal_data}")
            if goal_data[0]:
                for skill in goal_data[0].split(","):
                    skill_name, value = skill.split(":")
                    if skill_name in skills_dict:
                        skills_dict[skill_name] += float(value)
                    else:
                        skills_dict[skill_name] = float(value)

                time += goal_data[1]
                if charactsToRecalc and goal_data[2]:
                    for charact in goal_data[2].split(","):
                        charact_name, value = charact.split(":")
                        if charact_name in charactsToRecalc:
                            allCharacts[charact_name] += float(value)

                    if goal_data[3]:
                        for stat in goal_data[3].split("|"):
                            charact_name, stats = stat.split(":")
                            if charact_name in charactsToRecalc:
                                for record in stats.split(","):
                                    date, value = record.split(" ")
                                    if date in cc_stats_dict[charact_name][date]:
                                        cc_stats_dict[charact_name][date] += float(value)
                                    else:
                                        cc_stats_dict[charact_name][date] = float(value)

        if skills_dict:
            for skill in skills_dict.keys():
                skills += f"{skill}:{skills_dict[skill]},"
            skills = skills.rstrip(",")

            print(f"skills:{skills}")
            print(f"time:{time}")

            if cc_stats_dict:
                for charact in cc_stats_dict.keys():
                    records = ""
                    for date in cc_stats_dict[charact].keys():
                        records += f"{date}:{cc_stats_dict[charact][date]}"
                    cc_stats += f"{charact}:{records}|"
                cc_stats.rstrip("|")
    else:
        for dynamic_cc in charactsToRecalc:
            allCharacts.pop(dynamic_cc)

    if allCharacts:
        for cc in allCharacts.keys():
            ccs += cc + ":" + str(allCharacts[cc]) + ","
        ccs = ccs.rstrip(",")

    if charactsToRecalc:
        cur.execute("UPDATE Goals SET used_skills = ?, time = ?, custom_characteristics = ?, cc_stats = ? WHERE ID == ?", (skills, time, ccs, cc_stats, supergoal_id))
        print(f"ccs:{ccs}")
        print(f"cc_stats:{cc_stats}")
    else:
        cur.execute("UPDATE Goals SET used_skills = ?, time = ? WHERE ID == ?", (skills, time, supergoal_id))

    conn.commit()
    conn.close()

@exception_handler
def updateMainData(data_type, args):
    conn = sql.connect(main_db)
    cur = conn.cursor()
    if data_type == "branch":
        cur.execute("UPDATE Branches SET name = ? WHERE name == ?", args)
    if data_type == "displaying_characts":
        cur.execute("UPDATE Branches SET custom_characteristics = ?, sections_position = ? WHERE RowID == ?", args)
    if data_type == "sections_pos":
        cur.execute("UPDATE Branches SET sections_position = ? WHERE RowID == ?", args)
    if data_type == "goal":
        cur.execute("UPDATE Goals SET ID = ?, name = ?, time = ?, benefit = ?, limit_date = ?, priority = ?, used_skills = ?, state = ?, note = ?, files = ?, progress = ?, custom_characteristics = ?, cc_stats = ?, is_group = ?, showing_in_list = ? WHERE ID == ?", args)
    if data_type == "Characteristics":
        cur.execute("UPDATE Characteristics SET name = ?, c_type = ?, v_type = ? WHERE name == ?", args)
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
    if data_type == "characteristic":
        cur.execute("DELETE FROM Characteristics WHERE name == ?", args)
    conn.commit()
    conn.close()

@exception_handler
def getGoalTree(goal_id):
    conn = sql.connect(main_db)
    cur = conn.cursor()
    cur.execute(f"SELECT ID, name, progress, time, is_group FROM Goals WHERE ID LIKE '{goal_id}%' ORDER BY ID ASC")
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