# -*- coding: cp1251 -*-
import sys, configparser, os
from win10toast import ToastNotifier
import sqlite3 as sql
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QLineEdit, QHBoxLayout, QWidget, QSizePolicy, QMessageBox, QDialog, QStackedWidget, QLineEdit, QCheckBox, QFileDialog
from PyQt6.QtGui import QAction, QFont, QIcon
from PyQt6.QtCore import Qt, QTime, QTimer, QSize, QDate, QEvent
import WSwidgets as ws
import DataManager

data_base = r"Files\data\main_test.db"
config_path = r"Files\config\time_manager\config.ini"
version = "0.1.1 public"
app_icon_path = os.path.abspath(r"Files\icons\Time Manager icon.ico")

style_sheet = """
QPushButton{
    color: #FFD300
    }
QPushButton#Round{
    background-color: #000000;
    border: 2px solid #FFD300;
    border-radius: 28
    }
QPushButton::pressed#Round{
    background-color: #7F6900;
    }
QPushButton::disabled#Round{
    border: 2px solid #d9d9d9
    }
QPushButton#CommonButton{
    border: 1px solid #FFD300
    }
QPushButton::pressed#CommonButton{
    background-color: #7F6900
    }
QLineEdit{
    background-color: #000000;
    color: #FFD300;
    border: none;
    font: 16pt 'Segoe UI'
    }
QLineEdit#Timer{
    font: 12pt 'Segoe UI'
    }
QLabel{
    color: #FFD300;
    font: 16pt 'Segoe UI'
    }
QLabel#Info{
    color: #FFD300;
    font: 12pt 'Segoe UI'
    }
QWidget{
    background-color: #000000
    }
QListWidget{
    border: 1px solid #FFD300;
    color: #FFD300;
    }"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.load_data()
        self.initializeUI()

    def load_data(self):
        self.task_ID = ""
        self.directory = ""
        self.isPaused = True
        self.isTimerEnabled = False
        self.isRecurring = False
        self.isTimeouted = False
        self.timer_remaining_time = 0
        self.main_timer_remaining_time = 0
        self.timer = None
        self.isRecordStarted = False
        self.dialog = None
        self.record_time = QTime.fromString("00:00:00", "hh:mm:ss")
        self.timer_data = ["", "", "", "", ""]
        self.toaster = ToastNotifier()
        self.timer = QTimer()
        self.timer.timeout.connect(self.send_notification)
        if os.path.exists(config_path):
            config = configparser.ConfigParser()
            config.read(config_path)

            self.task_ID = config.get("Data", "Task_ID")
            self.task_name = config.get("Data", "Task_name")
            self.record_time = config.get("Data", "Record_time")
            self.timer_data = config.get("Timers", "Timer_1").split(",")
            self.timer_remaining_time = config.getint("Data", "Additional_timer_remaining_time")
            self.directory = config.get("Data", "Directory")
            if self.timer_data == [""]:
                self.timer_data = ["", "", "", "", ""]
            if self.timer_data[2] == "True":
                self.isRecurring = True
            if self.timer_data[3] == "True":
                self.isTimerEnabled = True
            if self.record_time != "00:00:00":
                self.isRecordStarted = True

            self.record_time = QTime.fromString(self.record_time, "hh:mm:ss")
        else:
            config = configparser.ConfigParser()
            config.add_section("Data")
            config.set("Data", "Record_time", "00:00:00")
            config.set("Data", "Task_ID", "")
            config.set("Data", "Task_name", "")
            config.set("Data", "Additional_timer_remaining_time", "0")
            config.set("Data", "Directory", "")

            config.add_section("Timers")
            config.set("Timers", "Timer_1", "")

            with open(config_path, "w") as config_file:
                config.write(config_file)

    def initializeUI(self):
        self.setWindowTitle("WS Time Manager")
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.setFixedSize(450, 350)
        self.setWindowIcon(QIcon(app_icon_path))

        self.setUpMainWindow()
        self.show()

    def setUpMainWindow(self):
        self.main_timer = QTimer()
        self.main_timer.setInterval(1000)
        self.main_timer.timeout.connect(self.update_time)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.time_label = QLabel(self.record_time.toString())
        self.time_label.setStyleSheet("color: #FFD300; font: 55pt 'Segoe UI'; font-weight: bold")

        self.stop_button = QPushButton()
        self.stop_button.setObjectName("Round")
        self.stop_button.setFixedSize(56, 56)
        self.stop_button.setIcon(QIcon(r"Files\Icons\stop.png"))
        self.stop_button.setIconSize(QSize(56, 56))
        self.stop_button.clicked.connect(self.clear_timer)
        
        self.toggle_button = QPushButton()
        self.toggle_button.clicked.connect(self.toggle_record)
        self.toggle_button.setObjectName("Round")
        self.toggle_button.setIcon(QIcon(r"Files\Icons\start.png"))
        self.toggle_button.setFixedSize(56, 56)
        self.toggle_button.setIconSize(QSize(56, 56))

        self.timers_button = QPushButton()
        self.timers_button.setFixedSize(22, 22)
        self.timers_button.clicked.connect(self.set_timers)
        if self.isTimerEnabled:
            self.timers_button.setIcon(QIcon(r"Files\Icons\hourglass_on.png"))
        else:
            self.timers_button.setIcon(QIcon(r"Files\Icons\hourglass_off.png"))

        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Add Title...")

        if not self.title_edit.text():
            self.toggle_button.setEnabled(False)
        if not self.isRecordStarted:
            self.stop_button.setEnabled(False)

        generate_stats_button = QPushButton()
        generate_stats_button.setIcon(QIcon(r"Files\icons\generate stats.png"))
        generate_stats_button.setIconSize(QSize(25, 25))
        generate_stats_button.setToolTip("Generate statistics")
        generate_stats_button.clicked.connect(self.generate_stats)

        info_button = QPushButton()
        info_button.setIcon(QIcon(r"Files\icons\info.png"))
        info_button.setIconSize(QSize(25, 25))
        info_button.setToolTip("Info")
        info_button.clicked.connect(self.show_info)

        buttons_h_box = QHBoxLayout()
        buttons_h_box.addStretch()
        buttons_h_box.addWidget(generate_stats_button)
        buttons_h_box.addWidget(info_button)

        h_box = QHBoxLayout()
        h_box.addStretch()
        h_box.addWidget(self.stop_button, alignment=Qt.AlignmentFlag.AlignRight)
        h_box.addSpacing(30)
        h_box.addWidget(self.toggle_button, alignment=Qt.AlignmentFlag.AlignLeft)
        h_box.addWidget(self.timers_button)
        h_box.addSpacing(114)

        main_v_box = QVBoxLayout()
        main_v_box.addStretch()
        main_v_box.addWidget(self.title_edit, alignment=Qt.AlignmentFlag.AlignCenter)
        main_v_box.addWidget(self.time_label, alignment=Qt.AlignmentFlag.AlignCenter)
        main_v_box.addLayout(h_box)
        main_v_box.addStretch()
        main_v_box.addLayout(buttons_h_box)

        container = QWidget()
        container.setLayout(main_v_box)

        if self.task_ID:
            self.title_edit.setText(self.task_name)
            self.expand_line_edit()
        self.title_edit.textChanged.connect(self.expand_line_edit)

        self.object_manager = ws.ObjectManager(self, self.title_edit, ["Skills", "Goals"])
        self.object_manager.selected.connect(self.get_task_id)

        if self.task_ID:
            self.object_manager.isSelected = True

        self.stacked_widget.addWidget(container)

    def get_task_id(self, name, goal_id, object_type):
        if object_type == "Goals":
            if DataManager.loadMainData("goal", goal_id)[13]:
                QMessageBox.warning(self, "Groups cannot be selected directly for completing", "Select group's subgoal to start completing the group")
                self.title_edit.setText("")
                self.object_manager.isSelected = False
            else:
                self.task_ID = goal_id
                self.task_name = name
        else:
            self.task_ID = "s:" + name
            self.task_name = name

    def show_info(self):
        self.dialog = QDialog()
        self.dialog.setWindowIcon(QIcon(app_icon_path))
        self.dialog.setWindowTitle("Help")
        title = QLabel("Help")
        title.setFont(QFont('Segoe UI', 14))
        info = QLabel("""
1.Records\n
        1.1 To start a record press the 'start' button.\n
        1.2.To pause the record press the same button again.\n
        1.3 To finish the record press the 'finish' button.\n
2. Timer\n
        2.1 To set a timer click on the 'set timer' button,
        enter timer interval and click on 'toggle timer' checkbox.\n
        2.2 Timer interval must be longer than 10 seconds.\n
        2.3 Press 'recurring' button in 'set timer' window to make the timer recurring.\n
        2.4 When you toggle the timer its remaining time resets to zero. (if exists).\n
        2.5 Timer starts when you toggle the record on.\n
        2.6 You can see the timer is on from the 'set timer' button - it will light yellow.\n
        2.7 If turn on the timer when the recording is enabled, timer will be enabled after restarting the recording.\n
3. Statistics\n
        3.1 Click the "Generate Statistics" button and select the directory where you want to put the file, if you haven't already done so\n
        3.2 Statistics cannot be generated if record is on.\n
        3.3 Statistics stores in database file.""")
        info.setObjectName("Info")
        
        v_box = QVBoxLayout()
        v_box.addWidget(title)
        v_box.addWidget(info)
        self.dialog.setLayout(v_box)
        self.dialog.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.dialog.setFixedSize(self.dialog.sizeHint())
        self.dialog.show()

    def generate_stats(self):
        if self.isPaused:
            if not self.directory:
                self.get_dir()
            if self.directory:
                self.dialog = QDialog()
                self.dialog.setWindowIcon(QIcon(app_icon_path))
                self.dialog.setWindowTitle("Choose generating mode")
                self.dialog.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
                self.dialog.setModal(True)

                label = QLabel("Generate only today's statistics or all database?")
                one_button = QPushButton("Only today's")
                one_button.setObjectName("CommonButton")
                one_button.setFixedSize(75, 20)
                one_button.clicked.connect(self.generate_today)
                all_button = QPushButton("All database")
                all_button.setObjectName("CommonButton")
                all_button.setFixedSize(75, 20)
                all_button.clicked.connect(self.generate_all)
                choose_dir_button = QPushButton()
                choose_dir_button.clicked.connect(self.get_dir)
                choose_dir_button.setIcon(QIcon(r"Files\icons\Add dir.png"))
                choose_dir_button.setFixedSize(20, 20)
                choose_dir_button.setObjectName("CommonButton")
        
                h_box = QHBoxLayout()
                h_box.addWidget(one_button)
                h_box.addWidget(all_button)
                h_box.addWidget(choose_dir_button)
                h_box.addStretch()

                v_box = QVBoxLayout()
                v_box.addWidget(label)
                v_box.addLayout(h_box)

                self.dialog.setLayout(v_box)
                self.dialog.setFixedSize(self.dialog.sizeHint())
                self.dialog.show()
        else:
            QMessageBox.warning(self, "Warning", "Pause the record to generate statistics")

    def get_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "Choose a directory to save textual statistics file")
        if directory:
            self.directory = directory

    def generate_today(self):
        try:
            records_dict = {}
            date = QDate.currentDate().toString("dd/MM/yyyy")
            file_name = r"\today's statistics.txt"
            conn = sql.connect(data_base)
            cur = conn.cursor()
            cur.execute("SELECT start_time, end_time, task_ID FROM Main_statistics WHERE date == ?", (date,))
            records = cur.fetchall()
            if records:
                for record in records:
                    records_dict[record[2]] = 0
                for record in records:
                    start_time = self.calculate_msecs(record[0])
                    end_time = self.calculate_msecs(record[1])
                    record_time = end_time - start_time
                    records_dict[record[2]] += record_time

                self.write_stats(records_dict, file_name, date)
                self.dialog.close()
                QMessageBox.information(self, "WS Time Manager", "Statistics successfully generated!")
            else:
                QMessageBox.warning(self, "No statistics", "Data base is empty yet")
        except Exception:
            QMessageBox.warning(self, "Error", "Error: ")

    def generate_all(self):
        try:
            file_name = r"\statistics.txt"
            date_list = []
            conn = sql.connect(data_base)
            cur = conn.cursor()
            cur.execute("SELECT date FROM Main_statistics")
            dates = cur.fetchall()

            if dates:
                for date in dates:
                    if date[0] not in date_list:
                        date_list.append(date[0])
                for date in date_list:
                    cur.execute("SELECT start_time, end_time, task_ID FROM Main_statistics WHERE date == ?", (date,))
                    records = cur.fetchall()
                    records_dict = {}
                    for record in records:
                        records_dict[record[2]] = 0
                    for record in records:
                        start_time = self.calculate_msecs(record[0])
                        end_time = self.calculate_msecs(record[1])
                        record_time = end_time - start_time
                        records_dict[record[2]] += record_time

                    self.write_stats(records_dict, file_name, date)
                self.dialog.close()
                QMessageBox.information(self, "WS Time Manager", "Statistics successfully generated!")
            else:
                QMessageBox.warning(self, "No statistics", "Data base is empty yet")
        except Exception as error:
            QMessageBox.warning(self, "Error", f"Error: {error}")

    def write_stats(self, records_dict, file_name, date):
        with open(self.directory + file_name, "a") as file:
            file.write(f"Statistics for {date}:\n")
            for record in records_dict.items():
                file.write(f"{record[0]}: {self.to_str(record[1])}\n")
            file.write('\n')

    def set_timers(self):
        title = QLabel("Add timer for notifications")

        self.timer_name_edit = QLineEdit()
        self.timer_name_edit.setPlaceholderText("Add title...")
        self.timer_name_edit.setMaxLength(25)
        self.timer_name_edit.setObjectName("Timer")

        is_rec_button = QPushButton()
        is_rec_button.setCheckable(True)
        is_rec_button.setFixedSize(22, 22)
        is_rec_button.clicked.connect(lambda: self.toggle_recurring(is_rec_button))

        t_edit = QLineEdit()
        t_edit.setFixedWidth(80)
        t_edit.setInputMask("00:00:00")

        self.toggle_timer_button = QPushButton()
        self.toggle_timer_button.setFixedSize(22, 22)
        self.toggle_timer_button.setCheckable(True)
        self.toggle_timer_button.clicked.connect(lambda: self.toggle_timer(self.toggle_timer_button, t_edit))

        self.timer_note = QLineEdit()
        self.timer_note.setPlaceholderText("Add note...")
        self.timer_note.setObjectName("Timer")

        done_button = QPushButton("Done")
        done_button.setFixedWidth(45)
        done_button.clicked.connect(lambda: self.save_timers(t_edit))

        if self.timer_data[0]:
            t_edit.setText(self.timer_data[0])
            self.timer_name_edit.setText(self.timer_data[1])
            self.timer_note.setText(self.timer_data[4])

        if self.isTimerEnabled:
            self.toggle_timer_button.setChecked(True)
            self.toggle_timer(self.toggle_timer_button, t_edit)
        else: 
            self.toggle_timer_button.setIcon(QIcon(r"Files\icons\checkbox_off.png"))

        if self.isRecurring:
            is_rec_button.setIcon(QIcon(r"Files\icons\recurring_on.png"))
            is_rec_button.setChecked(True)
        else:
            is_rec_button.setIcon(QIcon(r"Files\icons\recurring_off.png"))

        t_edit.textChanged.connect(self.turn_off_timer_button)

        self.timer_h_box = QHBoxLayout()
        self.timer_h_box.addWidget(t_edit)
        self.timer_h_box.addWidget(self.timer_name_edit)
        self.timer_h_box.addWidget(is_rec_button)
        self.timer_h_box.addWidget(self.toggle_timer_button)
        self.timer_h_box.addWidget(self.timer_note)
        self.timer_h_box.addStretch()

        self.main_v_box = QVBoxLayout()
        self.main_v_box.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_v_box.addSpacing(25)
        self.main_v_box.addLayout(self.timer_h_box)
        self.main_v_box.addStretch()
        self.main_v_box.addWidget(done_button, alignment=Qt.AlignmentFlag.AlignRight)

        container = QWidget()
        container.setLayout(self.main_v_box)

        self.stacked_widget.addWidget(container)
        self.stacked_widget.setCurrentIndex(1)

    def save_timers(self, t_edit):
        interval = t_edit.text()
        if interval == "::":
            interval = ""
        self.timer_data[0] = interval
        self.timer_data[1] = self.timer_name_edit.text()
        self.timer_data[2] = self.isRecurring
        self.timer_data[3] = self.isTimerEnabled
        self.timer_data[4] = self.timer_note.text()

        timer_data = ""
        for data in self.timer_data:
            timer_data += "," + str(data)
        timer_data = timer_data[1:]

        config = configparser.ConfigParser()
        config.read(config_path)
        config.set("Timers", "Timer_1", timer_data)
        with open(config_path, "w") as config_file:
            config.write(config_file)

        self.previous_page()
        
    def turn_off_timer_button(self):
        self.toggle_timer_button.setChecked(False)
        self.toggle_timer(self.toggle_timer_button)

    def previous_page(self):
        self.stacked_widget.removeWidget(self.stacked_widget.currentWidget())
        self.stacked_widget.setCurrentIndex(self.stacked_widget.currentIndex() - 1)

    def toggle_record(self):
        if self.object_manager.isSelected:
            self.stop_button.setEnabled(True)
            if self.isPaused:
                self.isRecordStarted = True
                self.isPaused = False
                self.toggle_button.setIcon(QIcon(r"Files\Icons\pause.png"))
                self.interval_start_time = QTime.currentTime().toString()
                self.main_timer.start()
                if self.isTimerEnabled:
                    if not self.isTimeouted:
                        if self.timer_remaining_time: #Включить таймер
                            self.timer.setInterval(self.timer_remaining_time)
                            self.timer_remaining_time = 0
                            self.timer.timeout.connect(self.set_normal)
                            self.timer.start()
                        else:
                            self.create_timer(self.timer_data[0])
                            self.timer.start()
                if self.main_timer_remaining_time:
                    self.main_timer.setInterval(self.main_timer_remaining_time)
                
                    self.main_timer.timeout.connect(self.set_normal)
            else:
                self.isPaused = True
                self.toggle_button.setIcon(QIcon(r"Files\Icons\start.png"))
                self.write_statistics()
                self.main_timer_remaining_time = self.main_timer.remainingTime()
                self.main_timer.stop()
                if self.isTimerEnabled:
                    if self.isTimeouted:
                        self.timer_remaining_time = 0
                    else:
                        self.timer_remaining_time = self.timer.remainingTime() + 1#Это будет отмечать что таймер включен
                        self.timer.stop()
        else:
            QMessageBox.warning(self, "Unable to start record", "Select a task to start a record")

    def toggle_timer(self, button, t_edit=None):
        if button.isChecked():
            text = t_edit.text()
            onlyZeros = True
            for sym in text:
                if sym != "0" and sym != ":":
                    onlyZeros = False
            if len(text) == 8 and not onlyZeros: #It's also able to do zeros check using the list
                msecs = self.calculate_msecs(text)
                if msecs >= 10000:
                    if self.isRecurring:
                        self.isTimeouted = False
                    self.isTimerEnabled = True
                    self.timers_button.setIcon(QIcon("Files\icons\hourglass_on.png"))
                    button.setIcon(QIcon("Files\icons\checkbox_on.png"))
                    self.timer_remaining_time = 0
                else:
                    QMessageBox.warning(self, "Timer is too short", "Timer must be longer or equal to 10 seconds")
                    button.setChecked(False)
            else:
                QMessageBox.warning(self, "Invalid interval", "Invalid timer interval input")
        else: 
            self.isTimerEnabled = False
            self.timers_button.setIcon(QIcon("Files\icons\hourglass_off.png"))
            button.setIcon(QIcon("Files\icons\checkbox_off.png"))

    def create_timer(self, interval):
        if self.timer_remaining_time:
            interval = self.timer_remaining_time
            self.timer_remaining_time = 0
            self.timer.timeout.connect(self.set_normal)
        else:
            if type(interval) == type(""):
                interval = self.calculate_msecs(interval)

        self.timer.setInterval(interval)
        self.timer.timeout.connect(self.send_notification)
        if not self.isRecurring:
            self.timer.setSingleShot(True)

    def set_normal(self):
        sender = self.sender()
        if sender == self.timer:
            self.timer.setInterval(self.calculate_msecs(self.timer_data[0]))
            self.timer.disconnect()
            self.timer.timeout.connect(self.send_notification)
            self.timer.start()
        else:
            self.main_timer.stop()
            self.main_timer.setInterval(1000)
            self.main_timer.timeout.disconnect()
            self.main_timer.timeout.connect(self.update_time)
            self.main_timer.start()
            self.main_timer_remaining_time = 0

    def toggle_recurring(self, button):
        if button.isChecked():
            self.isTimeouted = False
            self.isRecurring = True
            button.setIcon(QIcon(r"Files\icons\recurring_on.png"))
        else:
            self.isRecurring = False
            button.setIcon(QIcon(r"Files\icons\recurring_off.png"))

    def update_time(self):
        self.record_time = self.record_time.addSecs(1)
        self.time_label.setText(self.record_time.toString())

    def expand_line_edit(self):
        text_len = len(self.title_edit.text())
        width = self.title_edit.width()
        if text_len > 10 and width < 431:
            self.title_edit.setFixedWidth(174 + (text_len - 10) * 20)
        if width > 174 and text_len < 10:
            self.title_edit.setFixedWidth(174)
        if text_len:
            self.title_edit.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            self.toggle_button.setEnabled(True)
        else:
            self.title_edit.setAlignment(Qt.AlignmentFlag.AlignLeft)
            self.toggle_button.setEnabled(False)

    def clear_timer(self):
        if self.isRecordStarted:
            if not self.isPaused:
                self.toggle_record()
            self.title_edit.setText("")
            self.record_time = QTime.fromString("00:00:00", "hh:mm:ss")
            self.time_label.setText(self.record_time.toString())
            self.isPaused = True
            self.isRecordStarted = False
            self.stop_button.setEnabled(False)
            self.main_timer_remaining_time = 0
            self.object_manager.isSelected = False

    def send_notification(self):
        if not self.isRecurring:
            self.isTimeouted = True
        title = self.timer_data[1]
        note = self.timer_data[4]
        if not title:
            title = "Timer done"
        if not note:
            note = "(no note)"
        self.toaster.show_toast(title, note, duration=8, threaded=True, icon_path=app_icon_path)

    def write_statistics(self):
        self.interval_end_time = QTime.currentTime().toString()
        if self.interval_start_time != self.interval_end_time:
            try:
                conn = sql.connect(data_base)
                cur = conn.cursor()
                cur.execute("INSERT INTO Main_statistics (start_time, end_time, task_ID, date) VALUES (?, ?, ?, ?)", (self.interval_start_time, self.interval_end_time, self.task_ID, QDate.currentDate().toString("yyyy-MM-dd")))
                conn.commit()
                conn.close()
            except sql.Error as error:
                print(f"151: {error}")

    def calculate_msecs(self, interval_str):
        time_list = interval_str.split(":")
        return (int(time_list[0]) * 3600 + int(time_list[1]) * 60 + int(time_list[2])) * 1000

    def to_str(self, msecs):
        secs = msecs // 1000
        m, s = divmod(secs, 60)
        h, m = divmod(m, 60)

        return f'{h:d}:{m:02d}:{s:02d}'

    def closeEvent(self, event):
        if self.dialog:
            self.dialog.close()
        if not self.isPaused:
            self.toggle_record()
        config = configparser.ConfigParser()
        config.read(config_path)
        config.set("Data", "Record_time", self.record_time.toString())
        if self.object_manager.isSelected:
            config.set("Data", "Task_ID", self.task_ID)
            config.set("Data", "Task_name", self.task_name)
        else:
            config.set("Data", "Task_ID", "")
            config.set("Data", "Task_name", "")
        config.set("Data", "Remaining_time", str(self.main_timer_remaining_time))
        if self.timer_remaining_time == -1: 
            self.timer_remaining_time = 0
        config.set("Data", "Additional_timer_remaining_time", str(self.timer_remaining_time))
        config.set("Data", "Directory", self.directory)

        with open(config_path, "w") as config_file:
            config.write(config_file)

    def stay_always_on_top_sys(self):
        self.window_timer = QTimer()
        self.window_timer.setSingleShot(True)
        self.window_timer.setInterval(1)
        self.window_timer.timeout.connect(self.show_normal)
        self.window_timer.start()

    def show_normal(self):
        self.showNormal()

    def event(self, event):
        if self.isPaused:
            if event.type() == QEvent.Type.WindowStateChange and self.windowState() and Qt.WindowState.WindowMinimized:
                self.stay_always_on_top_sys()
                return True
        return super().event(event)
            
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(style_sheet)
    window = MainWindow()
    sys.exit(app.exec())