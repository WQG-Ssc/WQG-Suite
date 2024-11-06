# -*- coding: cp1251 -*-
import os, configparser, subprocess, DataManager, sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QStackedWidget, QLabel, QLineEdit, QGridLayout, QPushButton, QMessageBox, QHBoxLayout, QVBoxLayout, QToolBar, QDialog, QFileDialog, QComboBox, QTextEdit
from PyQt6.QtCore import Qt, QSize, QTimer, QDate
from PyQt6.QtGui import QIcon, QFont, QPixmap, QAction, QTextCharFormat, QTextCursor
from style_sheet import style_sheet
import WSwidgets as ws
import WStabs as wstabs
import sqlite3 as sql

i_dir = r"Files\icons"
user_config_path = r"Files\config\user.ini"
main_db = r"Files\data\main.db"
other_db = r"Files\data\other.db"
changelog_path = r"Files\data\changelog.txt"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.checkDataBase()
        self.initializeUI()

    def checkDataBase(self): #Проверяем, все ли базы данных существуют
        if not os.path.exists(main_db):
            conn = sql.connect(main_db)
            cur = conn.cursor()
            cur.execute("CREATE TABLE Main_statistics (start_time TEXT, end_time TEXT, task_ID TEXT, date TEXT, busy INTEGER)")
            cur.execute("CREATE TABLE Goals (ID TEXT PRIMARY KEY NOT NULL, name TEXT, time REAL, benefit INTEGER, limit_date DATE, priority TEXT, used_skills TEXT, state TEXT, note TEXT, files TEXT, progress TEXT, custom_characteristics TEXT, cc_stats TEXT, is_group INTEGER, showing_in_list INTEGER)")
            cur.execute("CREATE TABLE Skills (name TEXT PRIMARY KEY NOT NULL, time REAL)")
            cur.execute("CREATE TABLE Branches (name TEXT PRIMARY KEY NOT NULL, custom_characteristics TEXT, sections_position TEXT)")
            cur.execute("CREATE TABLE Days (date DATE PRIMARY KEY NOT NULL, 'Mental state' TEXT, 'Physical state' TEXT, 'Day rate' INTEGER, 'Work time' REAL)")
            cur.execute("CREATE TABLE Graphs (name TEXT, value_type TEXT, color TEXT)")
            cur.execute("CREATE TABLE Characteristics (name TEXT PRIMARY KEY NOT NULL, c_type TEXT, v_type TEXT)")
            cur.execute("CREATE TABLE Skills_statistics (date DATE, task_ID TEXT)")
            cur.execute("CREATE TABLE Tasks (name TEXT, used_skills TEXT, busy INTEGER)")
            cur.execute("CREATE TABLE Plans (start_time TEXT, end_time TEXT, task_ID TEXT, date DATE, busy INTEGER)")

            cur.execute("""INSERT INTO Graphs (name, value_type, color) VALUES ('Mental state', 'Letteric', '#FF0000'), 
                        ('Physical state', 'Letteric', '#F44336'),
                        ('Work time', 'Numeric', '#FFD300'),
                        ('Day rate', 'Numeric', '#00FFFF')""")
            conn.commit()
            conn.close()
        if not os.path.exists(other_db):
            conn = sql.connect(other_db)
            cur = conn.cursor()
            cur.execute("CREATE TABLE Phrases (date DATE, name TEXT PRIMARY KEY, author TEXT)")
            cur.execute("CREATE TABLE Authors (name TEXT PRIMARY KEY NOT NULL, image TEXT)")
            cur.execute("CREATE TABLE Top12 (goal_id TEXT PRIMARY KEY)")
            conn.commit()
            conn.close()

    def initializeUI(self):
        self.setWindowTitle("WQG's Suite")
        self.setWindowIcon(QIcon("Files\Small icon.png"))
        self.anyChangesMade = False
        self.isGoalListNeedsToBeUpdated = False
        self.dialog = None
        self.dialog1 = None
        #self.showAnimation()
        self.setUpMainWindow()
        self.showMaximized()

    def showAnimation(self):
        self.dialog = ws.AnimationDialog()
        self.anim_timer = QTimer()
        self.anim_timer.setInterval(1100)
        self.anim_timer.setSingleShot(True)
        self.anim_timer.timeout.connect(self.end_animation)
        self.anim_timer.start()
        self.dialog.show()

    def end_animation(self):
        self.dialog.close()
        self.setUpMainWindow()
        self.showMaximized()

    def setUpMainWindow(self):
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        self.authorize()
        
    def authorize(self):
        if os.path.exists(user_config_path):
            config = configparser.ConfigParser()
            config.read(user_config_path)

            self.user_name = config.get("User", "Name")
            self.user_image_path = config.get("User", "Image_path")
            self.main_menu()
        else: 
            self.create_account()

    def check_password(self):
        if self.password_edit.text():
            if self.password_edit.text() == self.user_password:
                self.main_menu()
            else: QMessageBox.warning(self, 'Invalid password', 'Invalid password')

    def check_account_entry(self):
        self.user_name = self.name_edit.text()
        self.user_image_path = self.profile_image_label.image_path
        if not self.user_image_path:
            self.user_image_path = r"Files\icons\default_profile_image.png"
        if self.user_name:
            self.save_account()
        else:
            QMessageBox.warning(self, 'Empty field', 'Please, enter the account name')

    def save_account(self):
        config = configparser.ConfigParser()
        config.add_section("User")
        config.add_section("Data")
        config.set("User", "Name", self.user_name)
        config.set("User", "Image_path", self.user_image_path)
        config.set("User", "Diary_path", "")
        config.set("User", "Date_of_registration", QDate.currentDate().toString("yyyy-MM-dd"))
        config.set("Data", "last_showed_phrase", "")
        config.set("Data", "last_showed_phrase_date", "")

        with open(user_config_path, "w") as config_file:
            config.write(config_file)
        self.stacked_widget.removeWidget(self.stacked_widget.currentWidget())
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
        plans_button.clicked.connect(self.plans_window)

        buttons_h_box = QHBoxLayout()
        buttons_h_box.addSpacing(250)
        buttons_h_box.addWidget(statistics_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        buttons_h_box.addSpacing(150)
        buttons_h_box.addWidget(goals_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        buttons_h_box.addSpacing(150)
        buttons_h_box.addWidget(plans_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        buttons_h_box.addStretch()

        profile_info_box = ws.ProfileInfoBox(self.user_image_path, self.user_name)
        profile_info_box.clicked.connect(self.profile_window)
        profile_info_box.top12_button.clicked.connect(self.top_12)

        self.completing_goals_widget = ws.CompletingGoalsWidget()
        self.completing_goals_widget.recent_list_widget.itemClicked.connect(self.go_to_goal_from_dashboard)
        self.completing_goals_widget.in_progress_widget.itemClicked.connect(self.go_to_goal_from_dashboard)
        today_phrase = ws.TodayPhraseWidget()

        left_v_box = QVBoxLayout()
        left_v_box.setSpacing(0)
        left_v_box.addWidget(profile_info_box, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        left_v_box.addWidget(self.completing_goals_widget, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        left_v_box.addStretch()

        main_h_box = QHBoxLayout()
        main_h_box.addLayout(left_v_box)
        main_h_box.addLayout(buttons_h_box)
        main_h_box.addWidget(today_phrase, alignment=Qt.AlignmentFlag.AlignBottom)
        main_h_box.setContentsMargins(0, 0, 0, 30)

        container = QWidget()
        container.setLayout(main_h_box)

        self.create_toolbar()
        self.stacked_widget.addWidget(container)
        if len(sys.argv) > 1 and sys.argv[1] == "finish day":
            self.form()

    def go_to_goal_from_dashboard(self, item):
        goal_id = item.id
        self.show_object("", goal_id, "Goals", close_dialog=False)

    def profile_window(self):
        profile_tab = wstabs.ProfileTab(self.user_image_path, self.user_name)
        profile_tab.top12_button.clicked.connect(self.top_12)
        self.next_window(profile_tab)

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
        if self.stacked_widget.currentIndex() == 0:
            self.completing_goals_widget.load_data()

    def next_window(self, widget):
        self.stacked_widget.addWidget(widget)
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

    def show_object(self, text, goal_id, obj_type, close_dialog=True):
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

        if obj_type == "Skills":
            tab = wstabs.ProfileTab(self.user_image_path, self.user_name)

        self.next_window(tab)
        if close_dialog:
            self.dialog.close()

    def toggle_toolbar(self):
        if self.tool_bar.isVisible():
            self.tool_bar.hide()
        else:
            self.tool_bar.show()

    def settings(self):
        self.dialog = ws.ModalIconDialog()
        self.dialog.setWindowTitle("Settings")
        stat_edit_button = QPushButton("Edit statistics")
        stat_edit_button.clicked.connect(self.statistics_editor)
        clear_db_button = QPushButton("Clear a database")
        clear_db_button.clicked.connect(self.clear_db_dialog)
        edit_phrases_button = QPushButton("Edit phrases and authors")
        edit_phrases_button.clicked.connect(self.edit_phrases)
        edit_profile_button = QPushButton("Edit profile")
        edit_profile_button.clicked.connect(self.edit_profile)
        about_button = QPushButton("Changelog")
        about_button.clicked.connect(self.show_changelog)
        v_box = QVBoxLayout()
        v_box.setSpacing(10)
        v_box.addWidget(stat_edit_button)
        v_box.addWidget(clear_db_button)
        v_box.addWidget(edit_phrases_button)
        v_box.addWidget(edit_profile_button)
        v_box.addWidget(about_button)
        self.dialog.setLayout(v_box)
        self.dialog.show()

    def show_changelog(self):
        self.dialog1 = ws.ModalIconDialog()
        self.dialog1.setWindowTitle("Changelog")
        changelog_label = QLabel('<font face="Calibri" size="6" color="#FFD300">Changelog</font>')
        changelog_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        with open(changelog_path, "r") as file:
            changelog_text = file.read()
        changelog = QTextEdit(changelog_text)
        changelog.setReadOnly(True)
        about_button = QPushButton("About the application")
        about_button.clicked.connect(self.show_about)
        v_box = QVBoxLayout()
        v_box.addWidget(changelog_label)
        v_box.addWidget(changelog)
        v_box.addWidget(about_button)
        self.dialog1.setLayout(v_box)
        self.dialog1.show()

    def show_about(self):
        QMessageBox.about(self, "About", """<p><font  "face="Calibri" size="7">WQG's Suite</font></p><p><font  "face="Calibri" size="4">version 1.1</font></p>""")

    def edit_profile(self):
        self.dialog1 = ws.ModalIconDialog()
        parser = configparser.ConfigParser()
        parser.read(user_config_path, encoding="cp1251")
        name = parser.get("User", "Name")
        image_path = parser.get("User", "Image_path")
        self.diary_path = parser.get("User", "Diary_path")

        self.user_image = ws.AddImageLabel(ring=True)
        self.user_image.setImage(image_path)
        self.name_edit = QLineEdit(name)
        diary_button = QPushButton("Edit diary path")
        diary_button.clicked.connect(self.get_diary_path)
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.save_profile)
        v_box = QVBoxLayout()
        v_box.addWidget(self.user_image, alignment=Qt.AlignmentFlag.AlignHCenter)
        v_box.addWidget(self.name_edit)
        v_box.addWidget(diary_button)
        v_box.addWidget(ok_button)
        self.dialog1.setLayout(v_box)
        self.dialog1.show()

    def save_profile(self):
        if self.name_edit.text():
            image_path = self.user_image.image_path
            parser = configparser.ConfigParser()
            parser.read(user_config_path)
            parser.set("User", "Name", self.name_edit.text())
            parser.set("User", "Image_path", image_path)
            parser.set("User", "Diary_path", self.diary_path)
            with open(user_config_path, "w") as config_file:
                parser.write(config_file)
            self.dialog1.close()
        else:
            QMessageBox.warning(self, "Name field is empty", "Enter name to save profile")

    def get_diary_path(self):
        self.diary_path, _ = QFileDialog.getOpenFileName(self.parent(), "Select diary file", "", "Text Files(*.txt *docx)")

    def edit_phrases(self):
        self.dialog1 = wstabs.PhrasesEditor()

    def clear_db_dialog(self):
        self.dialog1 = ws.ModalIconDialog()
        self.dialog1.setWindowTitle("Clear table")
        table_combo = QComboBox()
        table_combo.addItems(["Main_statistics", "Goals", "Skills", "Branches", "Days", "Graphs", "Characteristics", "Skills_statistics", "Tasks", "Plans"])
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(lambda: self.clear_table(table_combo))
        v_box = QVBoxLayout()
        v_box.addWidget(table_combo)
        v_box.addWidget(clear_button)
        self.dialog1.setLayout(v_box)
        self.dialog1.show()

    def clear_table(self, table_combo):
        if QMessageBox.question(self, "Clear table", f"Are you sure to clear the table: {table_combo.currentText()}?") == QMessageBox.StandardButton.Yes:
            DataManager.deleteMainData("clear table", table_combo.currentText())

    def statistics_editor(self):
        self.dialog1 = wstabs.StatisticsEditor()

    def top_12(self):
        top12_tab = wstabs.Top12Tab()
        self.next_window(top12_tab)

    def statistics_window(self):
        stats_tab = wstabs.StatisticsTab()
        self.next_window(stats_tab)

    def goal_branches_window(self):
        branches_tab = wstabs.BranchesTab()
        branch_list_widget = branches_tab.branch_list_widget
        branch_list_widget.itemClicked.connect(lambda: self.goals_window(branch_list_widget.currentRow()))
        self.next_window(branches_tab)

    def goals_window(self, row): 
        self.current_branch_id = row + 1
        goals_tab = wstabs.GoalsTab(self.current_branch_id)
        goals_tab.tree_widget.itemClicked.connect(self.goal_window)
        goals_tab.add_button.clicked.connect(self.goal_window)
        goals_tab.sectionMoved.connect(self.changesMade)
        self.next_window(goals_tab)

    def goal_window(self, item=None):
        goal_tab = wstabs.GoalTab(self.current_branch_id, item)
        goal_tab.changesMade.connect(self.changesMade)
        goal_tab.changesSaved.connect(self.changesSaved)
        goal_tab.previous_window_req.connect(self.previous_window)
        goal_tab.goal_list_update_req.connect(self.goalListUpdate)
        self.next_window(goal_tab)

    def plans_window(self):
        self.tool_bar.hide()
        plans_tab = wstabs.Plans()
        plans_tab.week_plan_view.changesMade.connect(self.changesMade)
        plans_tab.changesSaved.connect(self.changesSaved)
        self.next_window(plans_tab)

    def form(self):
        self.form = wstabs.Form()

    def goalListUpdate(self):
        self.isGoalListNeedsToBeUpdated = True

    def changesMade(self):
        self.anyChangesMade = True

    def changesSaved(self):
        self.anyChangesMade = False

    def create_account(self):
        image = QLabel()
        image.setPixmap(QPixmap(i_dir + "\grad_icon.png"))

        header_label = QLabel("Welcome!")
        header_label.setFont(QFont('Calibri', 36, 700))
        subheader_label = QLabel("Create user account to start your journey")
        subheader_label.setFont(QFont('Calibri', 24))

        name_label = QLabel('Name:')
        self.profile_image_label = ws.AddImageLabel()

        self.name_edit = QLineEdit()
        self.name_edit.setFixedWidth(150)

        done_button = QPushButton()
        done_button.setIcon(QIcon(i_dir + "\Check.png"))
        done_button.setFixedSize(50, 50)
        done_button.clicked.connect(self.check_account_entry)

        grid = QGridLayout()
        grid.addWidget(self.profile_image_label, 0, 0, 0, 1)
        grid.addWidget(name_label, 0, 1, alignment=Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignHCenter)
        grid.addWidget(self.name_edit, 0, 2, alignment=Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignHCenter)

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

    def closeEvent(self, event):
        if self.dialog:
            self.dialog.close()
        if self.dialog1:
            self.dialog1.close()
        if self.anyChangesMade:
            self.stacked_widget.currentWidget().saveData()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(style_sheet)
    window = MainWindow()
    sys.exit(app.exec())