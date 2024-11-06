import configparser
import sqlite3 as sql
import WSwidgets as ws
import re, socket, datetime
from PyQt6.QtCore import QDate
main_db = r"Files\data\main.db"
other_db = r"Files\data\other.db"
user_config_file = r"Files\config\user.ini"

def loadMainData(data_type, *args, one=False):
    conn = sql.connect(main_db)
    cur = conn.cursor()

    if data_type == "branches":
        cur.execute("SELECT name FROM Branches ORDER BY RowID")

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
        cur.execute(f"SELECT date, [{args[0]}] FROM Days WHERE [{args[0]}] IS NOT NULL ORDER BY date")

    if data_type == "day_data":
        cur.execute("SELECT [Mental state], [Physical state], [Day rate], [Work time] FROM Days WHERE date == ?", args)
    
    if data_type == "graphs":
        cur.execute("SELECT * FROM Graphs")

    if data_type == "goal_custom":#Custom characteristics
        cur.execute("SELECT cc_stats, is_group FROM Goals WHERE ID == ?", args)

    if data_type == "characteristic":
        cur.execute("SELECT c_type, v_type FROM Characteristics WHERE name == ?", args)

    if data_type == "skill_stat":
        cur.execute(f"SELECT date, [{args[0]}] FROM Skills_statistics WHERE [{args[0]}] IS NOT NULL ORDER BY date")

    if data_type == "statistics":
        cur.execute("SELECT start_time, end_time, date FROM Main_statistics WHERE task_ID == ? ORDER BY date", args)

    if data_type == "day_stats":
        cur.execute("SELECT start_time, end_time, task_ID FROM Main_statistics WHERE date == ? ORDER BY start_time", args)

    if data_type == "group_statistics":
        cur.execute(f"SELECT start_time, end_time, date FROM Main_statistics WHERE task_ID LIKE '{args[0]}.%' ORDER BY date")

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

    if data_type == "recently completed goals":
        date = QDate.currentDate().addDays(-8).toString("yyyy-MM-dd")
        cur.execute(f"SELECT name, files, time, id FROM Goals WHERE limit_date > '{date}' and state == 'completed'")

    if data_type == "completing goals":
        cur.execute(f"SELECT name, files, progress, time, custom_characteristics, id FROM Goals WHERE state == 'completing'")

    if data_type == "author":
        cur.execute("SELECT author FROM Phrases WHERE phrase == ?", args)

    if data_type == "entered_days":
        cur.execute(f"SELECT date FROM Days WHERE date >= '{args[0]}'")
        
    if data_type == "check_today":
        cur.execute(f"SELECT date FROM Days WHERE date == '{args[0]}'")

    if one:
        data = cur.fetchone()
    else:
        data = cur.fetchall()
    conn.close()
    return data

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
        values = f"'{args[1]}','{args[3]}',{args[2]}"
        cur.execute(f"INSERT INTO Skills_statistics (date, task_ID, {args[0]}) VALUES ({values})")

    if data_type == "Characteristics":
        cur.execute("INSERT INTO Characteristics (name, c_type, v_type) VALUES (?, ?, ?)", args)

    if data_type == "day_data":
        cur.execute("SELECT date FROM Days WHERE date == ?", (args[4],))
        if cur.fetchone():
            cur.execute("UPDATE Days SET 'Mental state' = ?, 'Physical state' = ?, 'Day rate' = ?, 'Work time' = ? WHERE date == ?", args)
        else:
            cur.execute("INSERT INTO Days ('Mental state', 'Physical state', 'Day rate', 'Work time', date) VALUES (?, ?, ?, ?, ?)", args)

    if data_type == "statistics":
        for stat in args:
            cur.execute("INSERT INTO Main_statistics (start_time, end_time, task_ID, date, busy) VALUES (?, ?, ?, ?, ?)", stat)

    if data_type == "task":
        cur.execute("SELECT name FROM Tasks WHERE name == ?", (args[2],))
        exists = cur.fetchone()
        if exists:
            cur.execute("UPDATE Tasks SET used_skills = ?, busy = ? WHERE name == ?", args)
        else:
            cur.execute("INSERT INTO Tasks (used_skills, busy, name) VALUES (?, ?, ?)", args)

    if data_type == "Plans":
        for block in args:
            cur.execute("INSERT INTO Plans (start_time, end_time, task_id, date, busy) VALUES (?, ?, ?, ?, ?)", block)

    conn.commit()
    conn.close()
    return True

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
        cur.execute("UPDATE Goals SET cc_stats = ?, progress = ?, state = ? WHERE ID == ?", args)

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
        cur.execute("UPDATE Plans SET end_time = ? WHERE start_time == ? and end_time == ? and task_ID == ? and date == ?", (args[0], args[1].start_time, args[1].end_time, args[1].task_id, args[2]))
        
    conn.commit()
    conn.close()
    return True

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

def loadOtherData(data_type, *args, one=False):
    conn = sql.connect(other_db)
    cur = conn.cursor()
    if data_type == "names":
        cur.execute(f"SELECT name FROM {args[0]}")

    if data_type == "author":
        cur.execute("SELECT image FROM Authors WHERE name == ?", args)

    if data_type == "phrase author":
        cur.execute(f"SELECT author FROM Phrases WHERE name = '{args[0]}'")

    if data_type == "phrases for day":
        cur.execute("SELECT name, author FROM Phrases WHERE date == ?", args)

    if data_type == "phrase date":
        cur.execute("SELECT date FROM Phrases WHERE name == ?", args)

    if data_type == "phrases":
        cur.execute("SELECT name, author, date FROM Phrases")

    if data_type == "top 12":
        cur.execute("SELECT RowID, goal_id FROM Top12")

    if one:
        data = cur.fetchone()
    else:
        data = cur.fetchall()
    conn.close()
    return data

def saveOtherData(data_type, *args):
    conn = sql.connect(other_db)
    cur = conn.cursor()
    if data_type == "phrase":
        cur.execute("INSERT INTO Phrases (date, name, author) VALUES (?, ?, ?)", args)
    if data_type == "author":
        cur.execute("INSERT INTO Authors (name, image) VALUES (?, ?)", args)
    if data_type == "top goal":
        cur.execute("INSERT INTO Top12 (goal_id) VALUES (?)", args)
    if data_type == "resave_top":
        cur.execute("DELETE FROM Top12")
        for item in sorted(args[0], key=lambda x:x.text(0)):
            cur.execute(f"INSERT INTO Top12 (goal_id) VALUES ('{item.text(5)}')")

    conn.commit()
    conn.close()

def deleteOtherData(data_type, *args):
    conn = sql.connect(other_db)
    cur = conn.cursor()
    if data_type == "phrase":
        cur.execute("DELETE FROM Phrases WHERE name == ?", args)
    if data_type == "author":
        cur.execute("DELETE FROM Authors WHERE name == ?", args)
        cur.execute("SELECT name FROM Phrases WHERE author == ?", args)
        parser = configparser.ConfigParser()
        parser.read(user_config_file)
        last_showed_phrase = parser.get("Data", "last_showed_phrase")
        phrases = cur.fetchall()
        if phrases:
            for phrase in phrases:
                if phrase[0] == last_showed_phrase:
                    parser.set("Data", "last_showed_phrase", "")
                    parser.set("Data", "last_showed_phrase_date", "")
            with open(user_config_file, "w") as config_file:
                parser.write(config_file)

        cur.execute("DELETE FROM Phrases WHERE author == ?", args)
    if data_type == "top goal":
        cur.execute("DELETE FROM Top12 WHERE goal_id == ?", args)
    conn.commit()
    conn.close()
    
def updateOtherData(data_type, *args):
    conn = sql.connect(other_db)
    cur = conn.cursor()
    if data_type == "author":
        cur.execute("UPDATE Authors SET image = ? WHERE name == ?", args)
    conn.commit()
    conn.close()

def recalculateValues(layer):#Recalculates values of time, dynamic characteristics and skills of groups, then calls recalculateProgress() method to recalculate progress of the group
    conn = sql.connect(main_db)
    cur = conn.cursor()
    supergoal_id = ".".join(layer[:-1])

    cur.execute("SELECT progress, custom_characteristics, cc_stats FROM Goals WHERE ID == ?", (supergoal_id,))
    progress, characts, supergoal_cc_stats = cur.fetchone()
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
    regex = re.compile(f"^{supergoal_id}\.[^.]+$")
    layer_list = [item for item in ids if regex.match(item)]

    skills_dict = {}
    cc_stats_dict = {charact:{} for charact in charactsToRecalc}
    time = 0.0
    skills = ""
    ccs = ""
    cc_stats = ""

    if layer_list:
        for goal in layer_list:
            goal_id = goal
            if charactsToRecalc:
                cur.execute("SELECT used_skills, time, custom_characteristics, cc_stats FROM Goals WHERE ID == ?", (goal_id,))
            else:
                cur.execute("SELECT used_skills, time FROM Goals WHERE ID == ?", (goal_id,))

            goal_data = cur.fetchone()
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
                                    if date in cc_stats_dict[charact_name]:
                                        cc_stats_dict[charact_name][date] += float(value)
                                    else:
                                        cc_stats_dict[charact_name][date] = float(value)

        if skills_dict:
            for skill in skills_dict.keys():
                skills += f"{skill}:{skills_dict[skill]},"
            skills = skills.rstrip(",")

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
    else:
        cur.execute("UPDATE Goals SET used_skills = ?, time = ? WHERE ID == ?", (skills, time, supergoal_id))
    conn.commit()
    conn.close()
    recalculateProgress(supergoal_id, progress.split(":")[1], True)

def getGoalTree(goal_id):
    conn = sql.connect(main_db)
    cur = conn.cursor()
    cur.execute(f"SELECT ID, name, progress, time, custom_characteristics, is_group, state FROM Goals WHERE ID == '{goal_id}'")
    goal_tree = cur.fetchall()
    cur.execute(f"SELECT ID, name, progress, time, custom_characteristics, is_group, state FROM Goals WHERE ID LIKE '{goal_id}.%' ORDER BY ID ASC")
    goal_tree += cur.fetchall()
    conn.close()
    return goal_tree

def recalculateProgress(goal_id, p_charact, isGroup=False, returning=False):#Recalculates progress of given goal
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
        goal_time /= 3600000
        progress_str = f"{goal_time}:Hours"
    else:
        cc_stats = loadMainData("goal_custom", goal_id, one=True)[0]
        charact_stats = [item.split(":")[1] for item in cc_stats.split("|") if item.split(":")[0] == p_charact][0]
        progress_str = str(sum([float(item.split(" ")[1]) for item in charact_stats.split(",")])) + ":" + p_charact
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
            used_skills = loadMainData("task", task[1], one=True)[0]
            skill_list = []
            skills_values = []
            for skill in used_skills.split(","):
                name, p = skill.split(":")
                skill_list.append(f"[{name}]")
                skills_values.append(str(task_time * (float(p) / 100)))
            skill = ",".join(skill_list)
            skill_value = ",".join(skills_values)
        else:
            return None
    else:
        return None
    saveMainData("skills_stats", [skill, date, skill_value, task_id])

def recalculateDaysWorkTime():
    conn = sql.connect(main_db)
    cur = conn.cursor()
    cur.execute("SELECT start_time, end_time, date FROM Main_statistics WHERE busy == 1")
    stats = cur.fetchall()
    if any(stats):
        last_date = ""
        day_stats = {}
        for stat in stats:
            if stat[2] == last_date:
                day_stats[stat[2]] += (ws.calculate_msecs(stat[1]) - ws.calculate_msecs(stat[0])) / 3600000
            else:
                day_stats[stat[2]] = (ws.calculate_msecs(stat[1]) - ws.calculate_msecs(stat[0])) / 3600000
            last_date = stat[2]

        for date, value in day_stats.items():
            cur.execute(f"SELECT date FROM Days WHERE date == '{date}'")
            if cur.fetchone():
                cur.execute(f"UPDATE Days SET 'Work time' == {value} WHERE date == '{date}'")
            else:
                cur.execute(f"INSERT INTO Days ('Work time', date) VALUES ({value}, '{date}')")
    conn.commit()
    conn.close()

def synchronizePlans():
    conn = sql.connect(main_db)
    cur = conn.cursor()
    cur.execute("SELECT * FROM Plans")
    data = cur.fetchall()
    if data:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("192.168.0.106", 1234))
        server.listen(1)
        user, adress = server.accept()
        data_str = ""
        for record in data:
            record = [str(item) for item in record]
            data_str += ",".join(record) + "|"
        data_str = data_str.rstrip("|")
        
        user.send(data_str.encode("utf-8"))
        server.close()
    conn.close()

def continue_on_phone(tasks):
    if tasks:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("192.168.0.106", 1234))
        server.listen(1)
        user, adress = server.accept()
        task_str = ""
        for task in tasks:
            task_str += ",".join(task) + "|"
        task_str = task_str.rstrip("|")
        user.send(task_str.encode("utf-8"))
        server.close()

def listen():
    conn = sql.connect(main_db)
    cur = conn.cursor()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("192.168.0.106", 1234))
    server.listen(1)
    user, adress = server.accept()
    data = user.recv(12582912).decode("utf-8")
    c_task_str, main_stats_str, plans_str = data.split("$")
    completed_tasks = []
    if c_task_str:
        for block in c_task_str.split("|"):
            completed_tasks.append(block.split(","))

    if main_stats_str:
        for record in main_stats_str.split("|"):
            record = record.split(",")
            cur.execute(f"INSERT INTO Main_statistics (start_time, end_time, task_id, date, busy) VALUES ('{record[0]}', '{record[1]}', '{record[2]}', '{record[3]}', {record[4]})")

    if plans_str:
        plans = plans_str.split("|")
        cur.execute(f"DELETE FROM Plans WHERE date == '{QDate().currentDate().toString('yyyy-MM-dd')}'")
        for record in plans:
            record = record.split(",")
            cur.execute(f"INSERT INTO Plans (start_time, end_time, task_id, date, busy) VALUES ('{record[0]}', '{record[1]}', '{record[2]}', '{record[3]}', {record[4]})")

    conn.commit()
    conn.close()
    server.close()
    return completed_tasks

def isSubgoal(goal_id):
    if len(goal_id.split(".")) > 2:
        return True
    else:
        return False