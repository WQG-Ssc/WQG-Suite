# -*- coding: cp1251 -*-
import os, sys, configparser, subprocess, DataManager
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QStackedWidget, QLabel, QGraphicsScene, QLineEdit, QGridLayout, QPushButton, QMessageBox, QHBoxLayout, QVBoxLayout, QToolBar, QDialog, QListWidget, QListWidgetItem, QTreeWidget, QTreeWidgetItem, QGroupBox, QPlainTextEdit, QMenu, QInputDialog, QFileDialog, QDateEdit, QCalendarWidget
from PyQt6.QtCore import Qt, QPropertyAnimation, QTime, QRect, QSize, QRegularExpression, QDate
from PyQt6.QtGui import QIcon, QFont, QPixmap, QAction, QPainter, QPen, QBrush, QColor, QRegularExpressionValidator
from style_sheet import style_sheet
import WSwidgets as ws
import WSobjects as wsobj
import WStabs as wstabs
import sqlite3 as sql

i_dir = r"Files\icons"
user_config_path = r"Files\config\user.ini"
main_db = r"Files\data\main_test.db"
other_db = r"Files\data\other.db"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.checkDataBase()
        self.initializeUI()

    def checkDataBase(self): #Проверяем, все ли базы данных существуют
        if not os.path.exists(main_db):
            conn = sql.connect(main_db)
            cur = conn.cursor()
            cur.execute("CREATE TABLE Main_statistics (start_time TEXT, end_time TEXT, task_ID TEXT, date TEXT)")
            cur.execute("CREATE TABLE Goals (ID TEXT PRIMARY KEY NOT NULL, name TEXT, time REAL, benefit INTEGER, limit_date TEXT, priority TEXT, used_skills TEXT, state INTEGER, note TEXT, files TEXT, progress TEXT, custom_characteristics TEXT, cc_stats TEXT, type TEXT, showing_in_list INTEGER)")
            cur.execute("CREATE TABLE Skills (name TEXT PRIMARY KEY NOT NULL, time REAL)")
            cur.execute("CREATE TABLE Branches (name TEXT PRIMARY KEY NOT NULL, custom_characteristics TEXT, sections_position TEXT)")
            cur.execute("CREATE TABLE Days (date TEXT PRIMARY KEY NOT NULL, 'Mental state' TEXT, 'Physical state' TEXT, 'Day rate' INTEGER, 'Work time' REAL, 'Shedule completing' INTEGER, 'Shedule completing accuracy' INTEGER)")
            cur.execute("CREATE TABLE Graphs (name TEXT, value_type TEXT, color TEXT)")
            cur.execute("CREATE TABLE Characteristics (name TEXT PRIMARY KEY NOT NULL, c_type TEXT, v_type TEXT)")
            cur.execute("CREATE TABLE Skills_statistics (date TEXT, task_ID TEXT)")

            cur.execute("""INSERT INTO Graphs (name, value_type, color) VALUES ('Mental state', 'Letteric', '#FF0000'), 
                        ('Physical state', 'Letteric', '#F44336'), 
                        ('Work time', 'Numeric', '#FFD300'),
                        ('Shedule completing', '%', '#143484'),
                        ('Shedule completing accuracy', '%', '#009F65'),
                        ('Day rating', 'Numeric', '00FFFF')""")

            conn.commit()
            conn.close()
        if not os.path.exists(other_db):
            conn = sql.connect(other_db)
            cur = conn.cursor()
            cur.execute("CREATE TABLE Phrases (date TEXT, author TEXT, phrase TEXT)")
            cur.execute("CREATE TABLE Authors (author TEXT PRIMARY KEY, images TEXT)")
            conn.commit()
            conn.close()

    def initializeUI(self):
        self.setWindowTitle("WQG's Suite")
        self.setWindowIcon(QIcon("Files\Icon.png"))
        self.FormFillingDate = ""
        self.anyChangesMade = False
        self.isGoalListNeedsToBeUpdated = False
        self.showAnimation()
        self.setUpMainWindow()

        self.showMaximized()

    def showAnimation(self):
        pass
        #label = QLabel()
        #label.setPixmap(QPixmap(images["Start Window"]))

        #painter = QPainter()
        #for alpha in range(0.0, 1.0, 0.1):
        #    pen = QPen(QColor(0, 0, 0, alpha))
        #    brush = QBrush(QColor(0, 0, 0, alpha))
        #    painter.setBrush(brush)
        #    painter.drawRect(QRect(0, 0, 1080, 1920))
        #    painter.end()

    def setUpMainWindow(self):
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        self.authorize()
        
    def authorize(self):
        if os.path.exists(user_config_path):
            config = configparser.ConfigParser()
            config.read(user_config_path)

            self.user_name = config.get("User", "Name")
            self.user_password = config.get("User", "Password")
            self.user_image = QPixmap(r"Files/icons/User/Profile_picture.png")
            self.FormFillingDate = config.get("Data", "FormFillingDate")

            self.main_menu()

        #    time = QTime()
        #    current_hour = int(time.currentTime().toString().split(":")[0])
        #    if current_hour > 18:
        #        time_of_day = "evening"
        #    elif current_hour > 12:
        #        time_of_day = "afternoon"
        #    elif current_hour >= 0:
        #        time_of_day = "morning"

        #    header_label = QLabel(f"Good {time_of_day}, {self.user_name.split()[0]}!")
        #    header_label.setFont(QFont('Calibri', 36, 700))

        #    profile_image = QLabel()
        #    profile_image.setPixmap(ws.shapeImage(QSize(80, 80), self.user_image))
        #    password_label = QLabel("Password:")

        #    self.password_edit = QLineEdit()
        #    self.password_edit.setFixedWidth(150)

        #    self.enter_password_act = QAction()
        #    self.enter_password_act.triggered.connect(self.check_password)
        #    self.enter_password_act.setShortcut("Enter")

        #    enter_button = QPushButton()
        #    enter_button.setIcon(QIcon(i_dir + r"\Arrow Right.png"))
        #    enter_button.setFixedSize(20, 20)
        #    enter_button.addAction(self.enter_password_act)
        #    enter_button.clicked.connect(self.check_password)

        #    h_box = QHBoxLayout()
        #    h_box.addStretch()
        #    h_box.addWidget(password_label)
        #    h_box.addWidget(self.password_edit)
        #    h_box.addWidget(enter_button)
        #    h_box.addStretch()

        #    entry_container = QWidget()
        #    entry_container.setLayout(h_box)

        #    main_v_box = QVBoxLayout()
        #    main_v_box.addStretch()
        #    main_v_box.addWidget(header_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        #    main_v_box.addSpacing(40)
        #    main_v_box.addWidget(profile_image, alignment=Qt.AlignmentFlag.AlignHCenter)
        #    main_v_box.addWidget(entry_container)
        #    main_v_box.addStretch()

        #    container = QWidget()
        #    container.setLayout(main_v_box)

        #    self.stacked_widget.addWidget(container)
        #    self.stacked_widget.setCurrentIndex(0)

        #else: self.create_account()

    def check_password(self):
        if self.password_edit.text():

            if self.password_edit.text() == self.user_password:
                self.main_menu()
            else: QMessageBox.warning(self, 'Invalid password', 'Invalid password')

    def check_account_entry(self): #Проверяет, вся ли информация аккаунта введена
        self.user_name = self.name_edit.text()
        self.user_password = self.password_edit.text()
        if self.user_name and self.user_password:
            self.save_account()
        else:
            QMessageBox.warning(self, 'Empty fields', 'Enter all user information')

    def save_account(self): #Создаёт файл настроек
        config = configparser.ConfigParser()
        config.add_section("User")
        config.set("User", "Name", self.user_name)
        config.set("User", "Password", self.user_password)
        config.set("Data", "FormFillingDate", "")

        with open(user_config_path, "w") as config_file:
            config.write(config_file)

        image = self.profile_image_label.pixmap()
        image.save(r"Files/icons/User/Profile_picture.png")

        self.main_menu()

    def main_menu(self):
        self.previous_window_act = QAction()
        self.previous_window_act.triggered.connect(self.previous_window)
        self.previous_window_act.setShortcut("Esc")
        self.addAction(self.previous_window_act)

        statistics_button = QPushButton()
        statistics_button.setIcon(QIcon(i_dir + r"\Statistics.png"))
        statistics_button.setFixedSize(205, 110)
        statistics_button.setObjectName("Menu")
        statistics_button.setIconSize(QSize(205, 80))
        statistics_button.clicked.connect(self.statistics_window)

        goals_button = QPushButton()
        goals_button.setIcon(QIcon(i_dir + r"\Goals tab.png"))
        goals_button.setFixedSize(129, 110)
        goals_button.setObjectName("Menu")
        goals_button.setIconSize(QSize(129, 100))
        goals_button.clicked.connect(self.goal_branches_window)

        plans_button = QPushButton()
        plans_button.setIcon(QIcon(i_dir + r"\Plans.png"))
        plans_button.setFixedSize(119, 110)
        plans_button.setObjectName("Menu")
        plans_button.setIconSize(QSize(119, 107))

        home_button = QPushButton()
        home_button.setIcon(QIcon(i_dir + r"\Home.png"))
        home_button.setFixedSize(138, 110)
        home_button.setObjectName("Menu")
        home_button.setIconSize(QSize(138, 95))

        buttons_h_box = QHBoxLayout()
        buttons_h_box.addSpacing(62)
        buttons_h_box.addWidget(statistics_button, alignment=Qt.AlignmentFlag.AlignVCenter)
        buttons_h_box.addSpacing(155)
        buttons_h_box.addWidget(goals_button, alignment=Qt.AlignmentFlag.AlignVCenter)
        buttons_h_box.addSpacing(155)
        buttons_h_box.addWidget(plans_button, alignment=Qt.AlignmentFlag.AlignVCenter)
        buttons_h_box.addSpacing(155)
        buttons_h_box.addWidget(home_button, alignment=Qt.AlignmentFlag.AlignVCenter)
        buttons_h_box.addStretch()

        self.user_info = [self.user_name]#Потом будет добалена информация о прогрессе

        profile_info_box = ws.ProfileInfoBox(self.user_image, self.user_info)
        profile_info_box.clicked.connect(self.profile_window)
        
        main_v_box = QHBoxLayout()
        main_v_box.addWidget(profile_info_box, alignment=Qt.AlignmentFlag.AlignTop)
        main_v_box.addLayout(buttons_h_box)
        main_v_box.setContentsMargins(0, 0, 0, 0)

        container = QWidget()
        container.setLayout(main_v_box)

        self.create_toolbar()

        self.stacked_widget.addWidget(container)
        #self.stacked_widget.removeWidget(self.stacked_widget.currentWidget())

    def profile_window(self):
        profile_tab = wstabs.ProfileTab(self.user_image, self.user_info)
        self.stacked_widget.addWidget(profile_tab)
        self.next_window()

    def previous_window(self):
        if self.stacked_widget.currentIndex() > 0:
            current_widget = self.stacked_widget.currentWidget()
            if self.anyChangesMade:
                current_widget.saveData()
                self.anyChangesMade = False
            if self.isGoalListNeedsToBeUpdated:
                prev_widget = self.stacked_widget.widget(self.stacked_widget.currentIndex() - 1)
                prev_widget.updateWidget()
                self.isGoalListNeedsToBeUpdated = False
            self.stacked_widget.removeWidget(current_widget)
            current_widget.deleteLater()

    def next_window(self):
        self.stacked_widget.setCurrentIndex(self.stacked_widget.currentIndex() + 1)

    def create_toolbar(self):
        self.tool_bar = QToolBar()
        self.toggle_toolbar_act = QAction()
        self.toggle_toolbar_act.triggered.connect(self.toggle_toolbar)
        self.toggle_toolbar_act.setShortcut("F1")
        self.addAction(self.toggle_toolbar_act)

        toggle_button = QPushButton()
        toggle_button.setIcon(QIcon(i_dir + r"\Toggle.png"))
        toggle_button.clicked.connect(self.toggle_toolbar)
        toggle_button.setStyleSheet("border: 1px solid #FFD300")
        settings_button = QPushButton()
        settings_button.setIcon(QIcon(i_dir + r"\Settings.png"))
        settings_button.clicked.connect(self.settings)
        time_manager_button = QPushButton()
        time_manager_button.setIcon(QIcon(i_dir + r"\Time Manager icon.png"))
        time_manager_button.clicked.connect(lambda: subprocess.Popen("WS Time Manager.exe"))
        obj_manager_button = QPushButton()
        obj_manager_button.setIcon(QIcon(i_dir + r"\search.png"))
        obj_manager_button.clicked.connect(self.open_obj_manager)
        obj_manager_button.setShortcut('F3')
        finish_day_button = QPushButton()
        finish_day_button.setIcon(QIcon(i_dir + r"\finish day.png"))
        finish_day_button.clicked.connect(self.form)

        tools = [toggle_button, settings_button, obj_manager_button, finish_day_button, time_manager_button]

        for tool in tools:
            tool.setObjectName("Tool")
            tool.setIconSize(QSize(30, 30))
            self.tool_bar.addWidget(tool)
            self.tool_bar.addSeparator()

        self.tool_bar.setOrientation(Qt.Orientation.Vertical)
        self.tool_bar.setFixedSize(58, 200)
        self.tool_bar.setMovable(False)

        self.addToolBar(Qt.ToolBarArea.RightToolBarArea, self.tool_bar)

    def open_obj_manager(self):
        self.dialog = QDialog()
        self.dialog.setModal(True)
        self.dialog.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.dialog.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        line_edit = QLineEdit(self.dialog)
        line_edit.setStyleSheet("border-radius: 15px")
        line_edit.setPlaceholderText("Search object...")
        line_edit.setFont(QFont("Calibri", 18))
        self.dialog.setMinimumSize(line_edit.sizeHint().width(), line_edit.sizeHint().height() + 200)
        
        obj_manager = ws.ObjectManager(self.dialog, line_edit)
        obj_manager.selected.connect(self.show_object)
        obj_manager.setStyleSheet("background-color: #000000")
        self.dialog.show()

    def show_object(self, text, goal_id, obj_type):
        if obj_type == "Goals":
            tab = wstabs.GoalTab(goal_id.split(".")[0], goal_id=goal_id)
            tab.changesMade.connect(self.changesMade)
            tab.changesSaved.connect(self.changesSaved)
            tab.previous_window_req.connect(self.previous_window)

        if obj_type == "Branches":
            self.current_branch_id = DataManager.loadMainData("branch_id", text, one=True)[0]
            tab = wstabs.GoalsTab(self.current_branch_id)
            tab.tree_widget.itemClicked.connect(self.goal_window)
            tab.add_button.clicked.connect(self.goal_window)
            tab.sectionMoved.connect(self.changesMade)

            self.stacked_widget.addWidget(tab)
            self.next_window()

        if obj_type == "Skills":
            tab = wstabs.ProfileTab(self.user_image, self.user_info)

        self.stacked_widget.addWidget(tab)
        self.next_window()
        self.dialog.close()

    def toggle_toolbar(self):
        if self.tool_bar.isVisible():
            self.tool_bar.hide()
        else:
            self.tool_bar.show()

    def settings(self):
        self.dialog = QDialog()
        stat_edit_button = QPushButton("Edit statistics")
        stat_edit_button.clicked.connect(self.statistics_editor)
        v_box = QVBoxLayout()
        v_box.addWidget(stat_edit_button)
        self.dialog.setLayout(v_box)
        self.dialog.show()

    def notes(self):
        self.dialog = QDialog()
        label = QLabel("In process")
        v_box = QVBoxLayout()
        v_box.addWidget(label)
        self.dialog.setLayout(v_box)
        self.dialog.show()

    def statistics_editor(self):
        self.dialog = wstabs.StatisticsEditor()

    def statistics_window(self):
        stats_tab = wstabs.StatisticsTab()
        self.stacked_widget.addWidget(stats_tab)
        self.next_window()

    def goal_branches_window(self):
        branches_tab = wstabs.BranchesTab()
        branch_list_widget = branches_tab.branch_list_widget
        branch_list_widget.itemClicked.connect(lambda: self.goals_window(branch_list_widget.currentRow()))
        self.stacked_widget.addWidget(branches_tab)
        self.next_window()

    def goals_window(self, row): 
        self.current_branch_id = row + 1
        goals_tab = wstabs.GoalsTab(self.current_branch_id)
        goals_tab.tree_widget.itemClicked.connect(self.goal_window)
        goals_tab.add_button.clicked.connect(self.goal_window)
        goals_tab.sectionMoved.connect(self.changesMade)

        self.stacked_widget.addWidget(goals_tab)
        self.next_window()

    def goal_window(self, item=None):
        goal_tab = wstabs.GoalTab(self.current_branch_id, item)
        goal_tab.changesMade.connect(self.changesMade)
        goal_tab.changesSaved.connect(self.changesSaved)
        goal_tab.previous_window_req.connect(self.previous_window)
        goal_tab.goal_list_update_req.connect(self.goalListUpdate)

        self.stacked_widget.addWidget(goal_tab)
        self.next_window()

    def form(self):
        self.form = wstabs.Form(self.FormFillingDate)

    def goalListUpdate(self):
        self.isGoalListNeedsToBeUpdated = True

    def changesMade(self):
        self.anyChangesMade = True

    def changesSaved(self):
        self.anyChangesMade = False

    def create_account(self):
        image = QLabel()
        image.setPixmap(QPixmap(i_dir + "\Grad Icon.png"))

        header_label = QLabel("Welcome!")
        header_label.setFont(QFont('Calibri', 36, 700))
        subheader_label = QLabel("Create user account to start your journey")
        subheader_label.setFont(QFont('Calibri', 24))

        name_label = QLabel('Name:')
        password_label = QLabel('Password:')
        self.profile_image_label = ws.AddImageLabel()

        self.name_edit = QLineEdit()
        self.name_edit.setFixedWidth(150)
        self.password_edit = QLineEdit()
        self.password_edit.setFixedWidth(150)

        done_button = QPushButton()
        done_button.setIcon(QIcon(i_dir + "\Check.png"))
        done_button.setFixedSize(50, 50)
        done_button.clicked.connect(self.check_account_entry)

        grid = QGridLayout()
        grid.addWidget(self.profile_image_label, 0, 0, 0, 1)
        grid.addWidget(name_label, 0, 1, alignment=Qt.AlignmentFlag.AlignRight)
        grid.addWidget(self.name_edit, 0, 2, alignment=Qt.AlignmentFlag.AlignLeft)
        grid.addWidget(password_label, 1, 1, alignment=Qt.AlignmentFlag.AlignRight)
        grid.addWidget(self.password_edit, 1, 2, alignment=Qt.AlignmentFlag.AlignLeft)

        info_container = QWidget()
        info_container.setLayout(grid)

        v_box = QVBoxLayout()
        v_box.addSpacing(50)
        v_box.addWidget(image, alignment=Qt.AlignmentFlag.AlignCenter)
        v_box.addWidget(header_label, alignment=Qt.AlignmentFlag.AlignCenter)
        v_box.addWidget(subheader_label, alignment=Qt.AlignmentFlag.AlignCenter)
        v_box.addSpacing(100)
        v_box.addWidget(info_container, alignment=Qt.AlignmentFlag.AlignCenter)
        v_box.addStretch()
        v_box.addWidget(done_button, alignment=Qt.AlignmentFlag.AlignRight)

        container = QWidget()
        container.setLayout(v_box)
        self.stacked_widget.addWidget(container)
        self.stacked_widget.setCurrentIndex(0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(style_sheet)
    window = MainWindow()
    sys.exit(app.exec())