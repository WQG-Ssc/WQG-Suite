import sqlite3 as sql
import WSwidgets as ws
import re
from PyQt6.QtCore import QDate
main_db = r"Files\data\main_test.db"
other_db = r"Files\data\other.db"

def exception_handler(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
        #try: 
        #    return func(*args, **kwargs)
        #except Exception as error:
        #    print(f'An error occurred in {func.__name__}: {error}')
        #    return False
    return wrapper

@exception_handler
def loadMainData(data_type, *args, one=False):
    conn = sql.connect(main_db)
    cur = conn.cursor()

    if data_type == "branches":
        cur.execute("SELECT name FROM Branches")

    if data_type == "goals":
        cur.execute(f"SELECT name, time, benefit, limit_date, priority, state, ID, files, progress, custom_characteristics, showing_in_list FROM Goals WHERE ID LIKE '{args[0]}.%' ORDER BY ID")

    if data_type == "goal":
        cur.execute("SELECT * FROM Goals WHERE ID == ?", args)

    if data_type == "branch":
        cur.execute("SELECT name, custom_characteristics, sections_position FROM Branches WHERE RowID == ?", args)

    if data_type == "branch_id":
        cur.execute("SELECT RowID FROM Branches WHERE name == ?", args)

    if data_type == "skills":
        cur.execute("SELECT * FROM Skills")

    if data_type == "days_data":
        cur.execute(f"SELECT date, [{args[0]}] FROM Days")

    if data_type == "day_data":
        cur.execute("SELECT [Mental state], [Physical state], [Day rate], [Work time] FROM Days WHERE date == ?", args)
    
    if data_type == "graphs":
        cur.execute("SELECT * FROM Graphs")

    if data_type == "goal_custom":#Custom characteristics
        cur.execute("SELECT cc_stats, is_group FROM Goals WHERE ID == ?", args)

    if data_type == "characteristic":
        cur.execute("SELECT c_type, v_type FROM Characteristics WHERE name == ?", args)

    if data_type == "skill_stat":
        cur.execute(f"SELECT date, [{args[0]}] FROM Skills_statistics WHERE [{args[0]}] IS NOT NULL")

    if data_type == "statistics":
        cur.execute("SELECT start_time, end_time, date FROM Main_statistics WHERE task_ID == ?", args)

    if data_type == "day_stats":
        cur.execute("SELECT start_time, end_time, task_ID FROM Main_statistics WHERE date == ? ORDER BY start_time", args)

    if data_type == "group_statistics":
        cur.execute(f"SELECT start_time, end_time, date FROM Main_statistics WHERE task_ID LIKE '{args[0]}.%'")

    if data_type == "graph_color":
        cur.execute("SELECT color FROM Graphs WHERE name == ?", args)

    if data_type == "names":
        if args[0] == "Goals":
            cur.execute(f"SELECT name, ID FROM Goals")
        else:
            cur.execute(f"SELECT name FROM {args[0]}")

    if data_type == "get_goal_ids":
        cur.execute(f"SELECT ID FROM Goals WHERE ID LIKE '{args[0]}.%'")

    if data_type == "task":
        cur.execute("SELECT used_skills, busy FROM Tasks WHERE name == ?", args)

    if data_type == "plans":
        cur.execute("SELECT start_time, end_time, task_ID FROM Plans WHERE date == ? ORDER BY start_time", args)

    if one:
        data = cur.fetchone()
    else:
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
        cur.execute(f"INSERT INTO Skills (name, time) VALUES ('{args}', 0.0)")
        cur.execute(f"ALTER TABLE Skills_statistics ADD COLUMN '{args}' REAL")

    if data_type == "skills_stats":
        print(f"args:{args}")
        values = f"'{args[1]}','{args[3]}',{args[2]}"
        cur.execute(f"INSERT INTO Skills_statistics (date, task_ID, {args[0]}) VALUES ({values})")

    if data_type == "Characteristics":
        cur.execute("INSERT INTO Characteristics (name, c_type, v_type) VALUES (?, ?, ?)", args)
        
    if data_type == "day":
        cur.execute("INSERT INTO Days (date, 'Mental state', 'Physical state', 'Day rate', 'Work time') VALUES (?, ?, ?, ?, ?)", args)

    if data_type == "day_data":
        cur.execute("INSERT INTO Days ('Mental state', 'Physical state', 'Day rate', 'Work time', date) VALUES (?, ?, ?, ?, ?)", args)

    if data_type == "statistics":
        cur.execute("INSERT INTO Main_statistics (start_time, end_time, task_ID, date, busy) VALUES (?, ?, ?, ?, ?)", args)

    if data_type == "task":
        cur.execute("SELECT name FROM Tasks WHERE name == ?", (args[2],))
        exists = cur.fetchone()
        if exists:
            cur.execute("UPDATE Tasks SET used_skills = ?, busy = ? WHERE name == ?", args)
        else:
            cur.execute("INSERT INTO Tasks (used_skills, busy, name) VALUES (?, ?, ?)", args)

    if data_type == "Plans":
        cur.execute("INSERT INTO Plans (start_time, end_time, task_id, date, busy) VALUES (?, ?, ?, ?, ?)", args)
    conn.commit()
    conn.close()
    return True

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

    if data_type == "goal_characts":
        cur.execute("UPDATE Goals SET cc_stats = ?, progress = ? WHERE ID == ?", args)

    if data_type == "progress":
        cur.execute("UPDATE Goals SET progress = ? WHERE ID == ?", args)

    if data_type == "goal_characts_stats":
        cur.execute("UPDATE Goals SET cc_stats = ? WHERE ID == ?", args)

    if data_type == "goal_state":
        cur.execute("UPDATE Goals SET state = ? WHERE ID == ?", args)

    if data_type == "day_data":
        cur.execute("UPDATE Days SET 'Mental state' = ?, 'Physical state' = ?, 'Day rate' = ?, 'Work time' WHERE date == ?", args)

    if data_type == "skill_value":
        cur.execute(f"UPDATE Skills SET time = ? WHERE name == ?", args)

    if data_type == "goal_id":
        cur.execute("UPDATE Main_statistics SET task_ID = ? WHERE task_ID == ?", args)
        cur.execute("UPDATE Skills_statistics SET task_ID = ? WHERE task_ID == ?", args)

    if data_type == "time_block":
        print(f"args:{args}")
        cur.execute("UPDATE Plans SET end_time = ? WHERE start_time == ? and end_time == ? and task_ID == ? and date == ?", (args[0], args[1].start_time, args[1].end_time, args[1].task_id, args[2]))
        
    conn.commit()
    conn.close()
    return True

@exception_handler
def deleteMainData(data_type, *args):
    conn = sql.connect(main_db)
    cur = conn.cursor()
    if data_type == "branch":
        cur.execute("DELETE FROM Branches WHERE RowID == ?", args)
        cur.execute(f"DELETE FROM Goals WHERE ID LIKE '{args[0]}.%'")

    if data_type == "goal":
        cur.execute("DELETE FROM Goals WHERE ID == ?", (args[0],))
        if args[1]:
            cur.execute(f"DELETE FROM Goals WHERE ID LIKE '{args[0]}.%'")

    if data_type == "characteristic":
        cur.execute("DELETE FROM Characteristics WHERE name == ?", args)

    if data_type == "statistics":
        cur.execute("DELETE FROM Main_statistics WHERE task_ID == ?", (args[0],))
        if args[1]:
            cur.execute(f"DELETE FROM Main_statistics WHERE task_ID LIKE '{args[0]}.%'")

    if data_type == "stats":
        cur.execute("DELETE FROM Main_statistics WHERE date == ?", (args))

    if data_type == "skills_stats":
        cur.execute("DELETE FROM Skills_statistics WHERE task_ID == ?", (args[0],))
        if args[1]:
            cur.execute(f"DELETE FROM Skills_statistics WHERE task_ID LIKE '{args[0]}.%'")

    if data_type == "Plans":
        cur.execute("DELETE FROM Plans WHERE date == ?", args)

    if data_type == "clear table":
        cur.execute(f"DELETE FROM {args[0]}")

    if data_type == "time block":
        cur.execute("DELETE FROM Plans WHERE date == ? and start_time == ? and end_time == ?", args)

    if data_type == "task":
        cur.execute("SELECT name FROM Tasks WHERE name == ?", args)
        if cur.fetchone():
            cur.execute("DELETE FROM Tasks WHERE name == ?", args)
            return True
        else:
            return False

    conn.commit()
    conn.close()

@exception_handler
def recalculateValues(layer):#Recalculates values of time, dynamic characteristics and skills of groups, then calls recalculateProgress() method to recalculate progress of the group
    conn = sql.connect(main_db)
    cur = conn.cursor()
    supergoal_id = ".".join(layer[:-1])

    print(f"supergoal_id:{supergoal_id}")
    cur.execute("SELECT progress, custom_characteristics, cc_stats FROM Goals WHERE ID == ?", (supergoal_id,))
    progress, characts, supergoal_cc_stats = cur.fetchone()
    print(f"characts:{characts}")
    charactsToRecalc = []
    allCharacts = {}
    if characts:
        characts = characts.split(",")
        for charact in characts:
            charact, value = charact.split(":")
            if loadMainData("characteristic", charact, one=True)[0] == "dynamic":
                allCharacts[charact] = 0
                charactsToRecalc.append(charact)
            else:
                allCharacts[charact] = value

    cur.execute(f"SELECT ID FROM Goals WHERE ID LIKE '{supergoal_id}.%'")
    raw_ids = cur.fetchall()

    ids = [item[0] for item in raw_ids]
    print(f"ids:{ids}")
    regex = re.compile(f"^{supergoal_id}\.[^.]+$")
    layer_list = [item for item in ids if regex.match(item)]

    print(f"charactsToRecalc{charactsToRecalc}")

    skills_dict = {}
    cc_stats_dict = {charact:{} for charact in charactsToRecalc}
    time = 0.0

    skills = ""
    ccs = ""
    cc_stats = ""

    if layer_list:
        for goal in layer_list:
            goal_id = goal
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
                            print(stat)
                            charact_name, stats = stat.split(":")
                            if charact_name in charactsToRecalc:
                                for record in stats.split(","):
                                    date, value = record.split(" ")
                                    if date in cc_stats_dict[charact_name]:
                                        cc_stats_dict[charact_name][date] += float(value)
                                    else:
                                        cc_stats_dict[charact_name][date] = float(value)

        if skills_dict:
            for skill in skills_dict.keys():
                skills += f"{skill}:{skills_dict[skill]},"
            skills = skills.rstrip(",")

            print(f"skills:{skills}")
            print(f"time:{time}")

            if charactsToRecalc:
                for charact in cc_stats_dict.keys():
                    records = ""
                    for date in cc_stats_dict[charact].keys():
                        records += f"{date} {cc_stats_dict[charact][date]},"
                    if not records:
                        records = QDate.currentDate().toString('yyyy-MM-dd') + " 0"
                    else:
                        records = records.rstrip(",")
                    cc_stats += f"{charact}:{records}|"
                cc_stats = cc_stats.rstrip("|")
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
    recalculateProgress(supergoal_id, progress.split(":")[1], supergoal_cc_stats, True)

@exception_handler
def getGoalTree(goal_id):
    conn = sql.connect(main_db)
    cur = conn.cursor()
    cur.execute(f"SELECT ID, name, progress, time, custom_characteristics, is_group, state FROM Goals WHERE ID == '{goal_id}'")
    goal_tree = cur.fetchall()
    cur.execute(f"SELECT ID, name, progress, time, custom_characteristics, is_group, state FROM Goals WHERE ID LIKE '{goal_id}.%' ORDER BY ID ASC")
    goal_tree += cur.fetchall()
    conn.close()
    return goal_tree

def recalculateProgress(goal_id, p_charact, cc_stats, isGroup=False, returning=False):#Recalculates progress of given goal
    if p_charact == "Hours":
        goal_time = 0
        records = loadMainData("statistics", goal_id)
        if isGroup:
            records += loadMainData("group_statistics", goal_id)
        for record in records:
            start_time = ws.calculate_msecs(record[0])
            end_time = ws.calculate_msecs(record[1])
            record_time = end_time - start_time
            goal_time += record_time
        print(f"records:{records}")
        print(goal_id, p_charact, cc_stats)
        goal_time /= 3600000
        progress_str = f"{goal_time}:Hours"
        print(f"goal_time:{goal_time}")
    else:
        cc_stats = loadMainData("goal_custom", goal_id, one=True)[0]
        charact_stats = [item.split(":")[1] for item in cc_stats.split("|") if item.split(":")[0] == p_charact][0]
        print(f"characts_stats:{charact_stats}")
        progress_str = str(sum([float(item.split(" ")[1]) for item in charact_stats.split(",")])) + ":" + p_charact
        print(progress_str)
        print(goal_id)
    if returning:
        return progress_str
    updateMainData("progress", [progress_str, goal_id])

def recalculateSkills():#Calculate values of all skills
    skills = loadMainData("names", "Skills")
    for skill in skills:
        stats = loadMainData("skill_stat", skill[0])
        skill_value = sum([item[1] for item in stats])
        updateMainData("skill_value", [skill_value, skill[0]])

def addSkillStat(task_id, task_time, date):
    task = task_id.split(":")
    if len(task_id.split(".")) > 1:
        skill_list = []
        skills_values = []
        goal_data = loadMainData("goal", task_id, one=True)
        skills = goal_data[6]
        goal_time = goal_data[2]
        for skill in skills.split(","):
            name, value = skill.split(":")
            skill_time = task_time * (float(value) / goal_time)
            skill_list.append(f"[{name}]")
            skills_values.append(str(skill_time))
        skill = ",".join(skill_list)
        skill_value = ",".join(skills_values)
    elif task[0] == "s":
        skill = f"[{task[1]}]"
        skill_value = float(task_time)
    elif task[0] == "t":
        if ws.getBusyValue(task_id):
            used_skills = loadMainData("task", task[1], one=True)[1]
            skill_list = []
            skills_values = []
            for skill in used_skills.split(","):
                name, p = skill.split(":")
                skill_list.append(f"[{name}]")
                skills_values.append(task_time * (p / 100))
            skill = ",".join(skill_list)
            skill_value = ",".join(skills_values)
        else:
            return None
    else:
        return None
    saveMainData("skills_stats", [skill, date, skill_value, task_id])