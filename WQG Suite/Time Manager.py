# -*- coding: cp1251 -*-
import configparser, os, sys
from win10toast import ToastNotifier
import sqlite3 as sql
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QLineEdit, QHBoxLayout, QWidget, QSizePolicy, QMessageBox, QDialog, QStackedWidget, QLineEdit, QCheckBox, QFileDialog, QGraphicsLineItem
from PyQt6.QtGui import QAction, QFont, QIcon, QPen, QColor
from PyQt6.QtCore import Qt, QTime, QTimer, QSize, QDate, QEvent
import WSwidgets as ws
import DataManager, subprocess
from style_sheet import style_sheet

data_base = r"Files\data\main.db"
config_path = r"Files\config\time_manager\config.ini"
version = "0.1.1 public"
app_icon_path = os.path.abspath(r"Files\icons\Time Manager icon.ico")

style_sheet2 = """
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
    background-color: #7F6900;
    border: none;
    }
QPushButton#YellowWhite{
    background-color: #FFD300;
    color: #FFFFFF;
    border: none
    }
QPushButton::pressed#YellowWhite{
    background-color: #7F6900;
    color: #7a7a7a;
    }
QPushButton#Icon{
    background-color: black;
    color: #FFD300
    }
QPushButton#Icon::pressed{
    border: 1px solid #FFD300
    }
QLineEdit#Task{
    background-color: #000000;
    color: #FFD300;
    border: none;
    font: 16pt 'Segoe UI'
    }
QLineEdit#Timer{
    font: 12pt 'Segoe UI';
    border: none;
    }
QLineEdit#TimerTime{
    background-color: #000000;
    color: #FFD300;
    border: none;
    font: 16pt 'Segoe UI'
    }
QLabel#Title{
    color: #FFD300;
    font: 16pt 'Segoe UI'
    }"""
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.load_data()
        self.initializeUI()

    def load_data(self):
        self.day_plan_widget = None
        self.isPaused = True
        self.isTimerEnabled = False
        self.isTimeouted = False
        self.timer = None
        self.isRecordStarted = False
        self.dialog = None
        needs_restore = False
        self.toaster = ToastNotifier()
        self.timer = QTimer()
        self.task_timer = QTimer()
        self.task_timer.setSingleShot(True)
        self.task_timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.task_timer.timeout.connect(self.task_time_expired)
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.timer.timeout.connect(self.send_notification)
        self.current_date_str = QDate().currentDate().toString("yyyy-MM-dd")

        config = configparser.ConfigParser()
        if not os.path.exists(config_path):
            config = configparser.ConfigParser()
            config.add_section("Data")
            config.set("Data", "Record_time", "00:00:00")
            config.set("Data", "Additional_timer_remaining_time", "0")
            config.set("Data", "Time_block_data", ",,")
            config.set("Data", "Task_rtime", "0")
            config.set("Data", "Remaining_time", "0")
            config.set("Data", "Completed_tasks", "")
            config.set("Data", "Last_open_date", self.current_date_str)

            config.add_section("Timers")
            config.set("Timers", "Timer_1", ",,,,")

            config.add_section("Autosave")
            config.set("Autosave", "Start_time", "")
            config.set("Autosave", "End_time", "")
            config.set("Autosave", "Date", "")
            config.set("Autosave", "NeedsRestore", "False")
            config.set("Autosave", "Task_id", "")

            with open(config_path, "w") as config_file:
                config.write(config_file)

        config.read(config_path)
        self.record_time = config.get("Data", "Record_time")
        self.block_data = config.get("Data", "Time_block_data").split(",")
        tasks = config.get("Data", "Completed_tasks")
        if tasks and config.get("Data", "Last_open_date") == self.current_date_str:
            self.completed_tasks = [item.split(",") for item in tasks.split("|")]
        else:
            self.completed_tasks = []
        self.timer_data = config.get("Timers", "Timer_1").split(",")
        self.main_timer_remaining_time = config.getint("Data", "Remaining_time")
        self.isRecurring = bool(self.timer_data[2])
        self.isTimerEnabled = bool(self.timer_data[3])
        self.timer_remaining_time = config.getint("Data", "Additional_timer_remaining_time")

        needs_restore = config.getboolean("Autosave", "NeedsRestore")
        if needs_restore:
            start_time = config.get("Autosave", "Start_time")
            end_time = config.get("Autosave", "End_time")
            date = config.get("Autosave", "Date")
            task_id = config.get("Autosave", "Task_id")
            if date != self.current_date_str:
                self.block_data = ["", "", ""]
                self.record_time = "00:00:00"
                self.timer_remaining_time = 0
            self.autosaved_data = [start_time, end_time, task_id, date]
        else:
            self.autosaved_data = []

        if self.record_time != "00:00:00":
            self.isRecordStarted = True

        self.record_time = QTime.fromString(self.record_time, "hh:mm:ss")

        #Timer for autosaving
        current_time = QTime().currentTime()
        current_time_str = current_time.toString()
        self.autosave_timer = QTimer()
        self.autosave_timer.setTimerType(Qt.TimerType.PreciseTimer)

        if current_time_str[-4:] != "0:00":
            h, m, s = current_time_str.split(":")
            self.first_turn = 600000 - (int(m[1]) * 60 + int(s)) * 1000 - 1010
            self.autosave_timer.setInterval(self.first_turn)
            self.autosave_timer.setSingleShot(True)
        else:
            self.first_turn = 0
            self.autosave_timer.setInterval(598990)
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start()

    def autosave(self):
        if self.first_turn:
            self.first_turn = 0
            self.autosave_timer.stop()
            self.autosave_timer = QTimer()
            self.autosave_timer.setTimerType(Qt.TimerType.PreciseTimer)
            self.autosave_timer.setInterval(598990)
            self.autosave_timer.start()
            self.autosave_timer.timeout.connect(self.autosave)

        if not self.isPaused:
            start_time = self.interval_start_time
            end_time = QTime.currentTime().toString()
            current_time = end_time
        else:
            start_time, end_time = ["", ""]
            current_time = QTime.currentTime().toString()

        config = configparser.ConfigParser()
        config.read(config_path)
        config.set("Autosave", "Start_time", start_time)
        config.set("Autosave", "End_time", end_time)
        config.set("Autosave", "Date", QDate().currentDate().toString("yyyy-MM-dd"))
        config.set("Data", "Record_time", self.record_time.toString())
        config.set("Data", "Remaining_time", str(self.main_timer_remaining_time))
        if self.current_block:
            config.set("Data", "Time_block_data", f"{self.current_block.start_time},{self.current_block.end_time},{self.current_block.task_id}")
        config.set("Data", "Completed_tasks", "|".join([",".join(item) for item in self.completed_tasks]))
        config.set("Data", "Last_open_date", self.current_date_str)
        config.set("Data", "NeedsRestore", "True")
        if self.current_block:
            config.set("Autosave", "Task_id", self.current_block.task_id)

        if self.timer_remaining_time == -1: 
            self.timer_remaining_time = 0
        task_rtime = self.task_timer.remainingTime()
        if task_rtime == -1:
            task_rtime = 0

        config.set("Data", "Task_rtime", str(task_rtime))
        config.set("Data", "Additional_timer_remaining_time", str(self.timer_remaining_time))

        if ws.calculate_msecs(current_time) > 86390000 and self.current_block:
            self.write_statistics([start_time, end_time, self.current_date_str])
            self.interval_start_time = "00:00:00"
            self.current_date_str = QDate().fromString(self.current_date_str, "yyyy-MM-dd").addDays(1).toString("yyyy-MM-dd")

        with open(config_path, "w") as config_file:
            config.write(config_file)

    def initializeUI(self):
        self.setWindowTitle("WS Time Manager")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setFixedSize(450, 350)
        self.setWindowIcon(QIcon(app_icon_path))
        self.setUpMainWindow()

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
        self.timers_button.setObjectName("Icon")
        if self.isTimerEnabled:
            self.timers_button.setIcon(QIcon(r"Files\Icons\hourglass_on.png"))
        else:
            self.timers_button.setIcon(QIcon(r"Files\Icons\hourglass_off.png"))

        self.title_edit = QLineEdit()
        self.title_edit.setObjectName("Task")
        self.title_edit.setReadOnly(True)
        self.title_edit.setPlaceholderText("Select a task")

        info_button = QPushButton()
        info_button.setIcon(QIcon(r"Files\icons\info.png"))
        info_button.setIconSize(QSize(25, 25))
        info_button.setToolTip("Info")
        info_button.clicked.connect(self.show_info)
        info_button.setObjectName("Icon")

        self.plan_button = QPushButton()
        self.plan_button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.plan_button.setCheckable(True)
        self.plan_button.setIcon(QIcon(r"Files\icons\plan.png"))
        self.plan_button.setIconSize(QSize(25, 25))
        self.plan_button.setToolTip("Plan")
        self.plan_button.toggled.connect(self.show_plan)
        self.plan_button.setObjectName("Icon")
       
        sync_button = QPushButton()
        sync_button.clicked.connect(self.synchronize_plan)
        sync_button.setIcon(QIcon(r"Files\icons\sync.png"))
        sync_button.setIconSize(QSize(25, 25))
        sync_button.setObjectName("Icon")

        phone_button = QPushButton()
        phone_button.clicked.connect(self.continue_on_phone)
        phone_button.setIcon(QIcon(r"Files\icons\to phone.png"))
        phone_button.setIconSize(QSize(25, 25))
        phone_button.setObjectName("Icon")

        listen_button = QPushButton("listen")
        listen_button.clicked.connect(self.listen)
        listen_button.setMinimumWidth(50)

        buttons_h_box = QHBoxLayout()
        buttons_h_box.addStretch()
        buttons_h_box.addWidget(listen_button)
        buttons_h_box.addWidget(sync_button)
        buttons_h_box.addWidget(phone_button)
        buttons_h_box.addWidget(info_button)
        buttons_h_box.addWidget(self.plan_button)

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

        self.day_plan_widget = QWidget()
        self.day_plan_widget.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.day_plan_view = ws.WeekPlanView(QDate().currentDate(), week_view=False, inTimeManager=True)
        self.time_line = QGraphicsLineItem(0, 0, 256, 0)
        self.time_line.setPen(QPen(QColor("#FF0000")))
        self.time_line.setZValue(3)
        self.day_plan_view.scene.addItem(self.time_line)
        self.update_time_line(QTime.currentTime().toString("hh:mm:ss"))
        self.day_plan_view.startTask.connect(self.start_task)
        self.day_plan_view.setFixedSize(256, 325)
        complete_day_button = QPushButton("Finish day")
        complete_day_button.setObjectName("YellowWhite")
        complete_day_button.setFont(QFont('Calibri', 12, 700))
        complete_day_button.clicked.connect(self.finish_day)
        save_plan_button = QPushButton("Save plan")
        save_plan_button.setObjectName("YellowWhite")
        save_plan_button.setFont(QFont('Calibri', 12, 700))
        save_plan_button.clicked.connect(self.save_plan)

        self.open_plan_act = QAction()
        self.open_plan_act.setShortcut("Ctrl+P")
        self.open_plan_act.triggered.connect(self.open_plan_by_key)
        self.addAction(self.open_plan_act)
        self.day_plan_widget.addAction(self.open_plan_act)

        self.current_block = None
        if any(self.block_data) or self.completed_tasks:
            for block in self.day_plan_view.blocks_dict[0]:
                if block.start_time == self.block_data[0] and block.end_time == self.block_data[1] and block.task_id == self.block_data[2]:
                    self.current_block = block
                    self.title_edit.setText(self.current_block.name)
                    self.expand_line_edit()
                else:
                    for task in self.completed_tasks:
                        if task[0] == block.start_time and task[1] == block.end_time and task[2] == block.task_id:
                            block.setCompleted()

        if self.autosaved_data:
            if self.current_block:
                self.write_statistics([self.current_block.start_time, self.current_block.end_time, self.current_block.task_id, self.current_date_str])
                self.title_edit.setText(self.current_block.name)#If there's current_block means the restored data is from today
            else:
                self.write_statistics(self.autosaved_data)
            self.toggle_restore(False)

        if not self.title_edit.text():
            self.toggle_button.setEnabled(False)
        if not self.isRecordStarted:
            self.stop_button.setEnabled(False)

        plan_h_box = QHBoxLayout()
        plan_h_box.addWidget(complete_day_button)
        plan_h_box.addWidget(save_plan_button)
        plan_h_box.setContentsMargins(0, 0, 0, 0)

        plan_v_box = QVBoxLayout()
        plan_v_box.addWidget(self.day_plan_view)
        plan_v_box.addLayout(plan_h_box)
        plan_v_box.setContentsMargins(0, 0, 0, 0)
        self.day_plan_widget.setLayout(plan_v_box)
        self.stacked_widget.addWidget(container)
        self.show()
        self.title_edit.textChanged.connect(self.expand_line_edit)
        self.expand_line_edit()

    def open_plan_by_key(self):
        if self.plan_button.isChecked():
            self.plan_button.setChecked(False)
        else:
            self.plan_button.setChecked(True)

    def listen(self):
        data = DataManager.listen()
        if data:
            self.completed_tasks = data
            QMessageBox.information(self, "Success", "Success")
        else:
            QMessageBox.warning(self, "Failed to get data", "Failed to get data")

    def synchronize_plan(self):
        DataManager.synchronizePlans()

    def continue_on_phone(self):
        if not self.current_block:
            DataManager.continue_on_phone(self.completed_tasks)
        else:
            QMessageBox.warning(self, "Warning", "Finish current task to continue on the phone")

    def update_time_line(self, time):
        self.time_line.prepareGeometryChange()
        self.time_line.setPos(0, ws.calculate_msecs(time) * 0.00001)

    def save_plan(self):
        colliding_blocks = self.day_plan_view.check_blocks()
        if colliding_blocks:
            QMessageBox.warning(self, "Time blocks are colliding", f"The following blocks are colliding: {', '.join([block.name for block in colliding_blocks])}")
        else:
            DataManager.deleteMainData("Plans", self.current_date_str)
            block_list = []
            for item in self.day_plan_view.blocks_dict[0]:
                if item.task_id:
                    busy = ws.getBusyValue(item.task_id)
                    block_list.append([item.start_time, item.end_time, item.task_id, self.current_date_str, busy])
            DataManager.saveMainData("Plans", block_list)

    def finish_day(self):
        subprocess.Popen(["WQG's Suite.exe", "finish day"])

    def start_task(self, time_block):
        self.save_plan()
        if time_block.name and time_block != self.current_block and self.isPaused:
            print(DataManager.getGoalTree(time_block.task_id))
            if len(DataManager.getGoalTree(time_block.task_id)) < 2:
                if self.current_block:
                    self.clear_timer()
                self.current_block = time_block
                self.title_edit.setText(time_block.name)
                self.time_label.setText("00:00:00")
                self.task_timer.setInterval(ws.calculate_msecs(time_block.end_time) - ws.calculate_msecs(time_block.start_time))
                self.task_timer.start()
            else:
                QMessageBox.warning(self, 'Selected task is a group', 'Selected task is a group. Select an subgoal.')

    def task_time_expired(self):
        self.toaster.show_toast(f"Time expired", f"Time of {self.title_edit.text()} task expired.", duration=8, threaded=True, icon_path=app_icon_path)

    def show_plan(self, state):
        if state:
            geometry = self.geometry()
            self.day_plan_widget.setGeometry(geometry.right(), geometry.y(), 256, 350)
            self.update_time_line(QTime().currentTime().toString("hh:mm:ss"))
            self.day_plan_view.centerOn(self.time_line)
            self.day_plan_widget.show()
        else:
            self.day_plan_widget.hide()
                
    def moveEvent(self, event):
        if self.day_plan_widget.isVisible():
            geometry = self.geometry()
            self.day_plan_widget.setGeometry(geometry.right(), geometry.y(), 256, 350)

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
        2.7 If turn on the timer when the recording is enabled, timer will be enabled after restarting the recording.\n""")
        info.setObjectName("Info")
        
        v_box = QVBoxLayout()
        v_box.addWidget(title)
        v_box.addWidget(info)
        self.dialog.setLayout(v_box)
        self.dialog.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.dialog.setFixedSize(self.dialog.sizeHint())
        self.dialog.show()

    def set_timers(self):
        title = QLabel("Add timer for notifications")
        title.setObjectName("Title")
        self.timer_name_edit = QLineEdit()
        self.timer_name_edit.setPlaceholderText("Add title...")
        self.timer_name_edit.setMaxLength(25)
        self.timer_name_edit.setObjectName("Timer")

        is_rec_button = QPushButton()
        is_rec_button.setCheckable(True)
        is_rec_button.setFixedSize(22, 22)
        is_rec_button.clicked.connect(lambda: self.toggle_recurring(is_rec_button))
        is_rec_button.setObjectName("Icon")

        t_edit = QLineEdit()
        t_edit.setFixedWidth(80)
        t_edit.setInputMask("00:00:00")
        t_edit.setObjectName("TimerTime")

        self.toggle_timer_button = QPushButton()
        self.toggle_timer_button.setFixedSize(22, 22)
        self.toggle_timer_button.setCheckable(True)
        self.toggle_timer_button.clicked.connect(lambda: self.toggle_timer(self.toggle_timer_button, t_edit))
        self.toggle_timer_button.setObjectName("Icon")

        self.timer_note = QLineEdit()
        self.timer_note.setPlaceholderText("Add note...")
        self.timer_note.setObjectName("Timer")

        done_button = QPushButton("Done")
        done_button.setFixedWidth(45)
        done_button.clicked.connect(lambda: self.save_timers(t_edit))
        done_button.setObjectName("Icon")

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

        if self.timer_data[0]:
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
        if self.title_edit.text():
            self.stop_button.setEnabled(True)
        if self.isPaused:
            if len(self.current_block.task_id.split(".")) > 1:
                layers = self.current_block.task_id.split(".")
                while len(layers) > 1:
                    DataManager.updateMainData("goal_state", ["completing", ".".join(layers)])
                    layers.pop(-1)
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
            self.toggle_restore(True)
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
                    self.timer_remaining_time = self.timer.remainingTime() + 1#Это будет отмечать, что таймер включен
                    self.timer.stop()
            self.toggle_restore(False)

    def toggle_restore(self, value):
        config = configparser.ConfigParser()
        config.read(config_path)
        config.set("Autosave", "NeedsRestore", str(value))
        with open(config_path, "w") as config_file:
            config.write(config_file)

    def toggle_timer(self, button, t_edit=None):
        if button.isChecked():
            text = t_edit.text()
            onlyZeros = True
            for sym in text:
                if sym != "0" and sym != ":":
                    onlyZeros = False
            if len(text) == 8 and not onlyZeros: #It's also able to do zeros check using the list
                msecs = ws.calculate_msecs(text)
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
                interval = ws.calculate_msecs(interval)

        self.timer.setInterval(interval)
        self.timer.timeout.connect(self.send_notification)
        if not self.isRecurring:
            self.timer.setSingleShot(True)

    def set_normal(self):
        sender = self.sender()
        if sender == self.timer:
            self.timer.setInterval(ws.calculate_msecs(self.timer_data[0]))
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
        if self.day_plan_widget.isVisible():
            self.update_time_line(QTime().currentTime().toString("hh:mm:ss"))

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
            if self.current_block:
                self.current_block.setCompleted()
                current_time = QTime.currentTime() 
                if current_time.msecsSinceStartOfDay() < ws.calculate_msecs(self.current_block.end_time) and current_time.msecsSinceStartOfDay() > ws.calculate_msecs(self.current_block.start_time):
                    DataManager.updateMainData("time_block", [current_time.toString("hh:mm:ss"), self.current_block, self.current_date_str])
                    self.current_block.prepareGeometryChange()
                    self.current_block.end_time = QTime.currentTime().toString("hh:mm:ss")
                    self.current_block.updateTime()
                self.completed_tasks.append([self.current_block.start_time, self.current_block.end_time, self.current_block.task_id])
            if not self.isPaused:
                self.toggle_record()
            self.title_edit.setText("")
            self.record_time = QTime.fromString("00:00:00", "hh:mm:ss")
            self.time_label.setText("00:00:00")
            self.current_block = None
            self.isPaused = True
            self.isRecordStarted = False
            self.stop_button.setEnabled(False)
            self.main_timer_remaining_time = 0

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

    def write_statistics(self, setting_mode=None):
        if setting_mode:
            start_time = setting_mode[0]
            end_time = setting_mode[1]
            task_id = setting_mode[2]
            date = setting_mode[3]
        else:
            start_time = self.interval_start_time
            end_time = QTime.currentTime().toString()
            task_id = self.current_block.task_id
            date = self.current_date_str
        busy = ws.getBusyValue(task_id)
        try:
            conn = sql.connect(data_base)
            cur = conn.cursor()
            cur.execute("INSERT INTO Main_statistics (start_time, end_time, task_ID, date, busy) VALUES (?, ?, ?, ?, ?)", (start_time, end_time, task_id, date, busy))
            conn.commit()
            conn.close()
        except sql.Error as error:
            QMessageBox.warning(self, "Error", f"Error: {error}")

    def to_str(self, msecs):
        secs = msecs // 1000
        m, s = divmod(secs, 60)
        h, m = divmod(m, 60)
        return f'{h:02d}:{m:02d}:{s:02d}'

    def closeEvent(self, event):
        self.toggle_restore(False)
        if self.dialog:
            self.dialog.close()
        if not self.isPaused:
            self.toggle_record()
        config = configparser.ConfigParser()
        config.read(config_path)
        config.set("Data", "Record_time", self.record_time.toString())
        config.set("Data", "Completed_tasks", "|".join([",".join(item) for item in self.completed_tasks]))

        if self.current_block and self.isRecordStarted:
            config.set("Data", "Time_block_data", f"{self.current_block.start_time},{self.current_block.end_time},{self.current_block.task_id}")
            config.set("Data", "Task_rtime", str(self.task_timer.remainingTime()))
        else:
            config.set("Data", "Time_block_data", "")
        config.set("Data", "Remaining_time", str(self.main_timer_remaining_time))
        if self.timer_remaining_time == -1: 
            self.timer_remaining_time = 0
        config.set("Data", "Additional_timer_remaining_time", str(self.timer_remaining_time))
        config.set("Data", "Last_open_date", self.current_date_str)

        with open(config_path, "w") as config_file:
            config.write(config_file)
        self.day_plan_view.scene.blockSignals(True)
        self.day_plan_widget.close()

    def stay_always_on_top_sys(self):
        self.window_timer = QTimer()
        self.window_timer.setSingleShot(True)
        self.window_timer.setInterval(1)
        self.window_timer.timeout.connect(self.show_normal)
        self.window_timer.start()

    def show_normal(self):
        self.showNormal()

    def event(self, event):
        if self.day_plan_widget and self.plan_button.isChecked():
            if event.type() == QEvent.Type.Hide:
                self.day_plan_widget.hide()
            elif event.type() == QEvent.Type.Show:
                self.day_plan_widget.show()
        if self.isPaused:
            if event.type() == QEvent.Type.WindowStateChange and self.windowState() and Qt.WindowState.WindowMinimized:
                self.stay_always_on_top_sys()
                return True
        return super().event(event)
            
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(style_sheet + style_sheet2)
    window = MainWindow()
    sys.exit(app.exec())