# -*- coding: cp1251 -*-
import calendar
import os, sys, pickle, configparser, subprocess, DataManager
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QStackedWidget, QLabel, QGraphicsScene, QLineEdit, QGridLayout, QPushButton, QMessageBox, QHBoxLayout, QVBoxLayout, QProgressBar, QCompleter, QToolBar, QDialog, QFrame, QListWidget, QListWidgetItem, QTreeWidget, QTreeWidgetItem, QGroupBox, QPlainTextEdit, QMenu, QInputDialog, QFileDialog, QDateEdit, QCalendarWidget
from PyQt6.QtCore import Qt, QPropertyAnimation, QTime, QRect, QSize, QRegularExpression
from PyQt6.QtGui import QIcon, QFont, QPixmap, QAction, QPainter, QPen, QBrush, QColor, QRegularExpressionValidator
from style_sheet import style_sheet
import WSwidgets as ws
import WSobjects as wsobj
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
            cur.execute("CREATE TABLE Main_statictics (start_time TEXT, end_time TEXT, task_ID TEXT, date TEXT)")
            cur.execute("CREATE TABLE Goals (ID TEXT PRIMARY KEY, name TEXT, total_difficulty INTEGER, time REAl, benefit INTEGER, limit_date TEXT, priority TEXT, used_skills TEXT, state INTEGER, note TEXT, files TEXT, progress TEXT, custom_characteristics TEXT)")
            cur.execute("CREATE TABLE Skills (name TEXT PRIMARY KEY, time REAL)")
            cur.execute("CREATE TABLE Branches (ID INTEGER, name TEXT PRIMARY KEY, custom_characteristics TEXT)")
            cur.execute("CREATE TABLE Days (date TEXT PRIMARY KEY, php TEXT, hp TEXT, work_time REAL, skills_xp TEXT)")
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

            time = QTime()
            current_hour = int(time.currentTime().toString().split(":")[0])
            if current_hour > 18:
                time_of_day = "evening"
            elif current_hour > 12:
                time_of_day = "afternoon"
            elif current_hour >= 0:
                time_of_day = "morning"

            header_label = QLabel(f"Good {time_of_day}, {self.user_name.split()[0]}!")
            header_label.setFont(QFont('Calibri', 36, 700))

            profile_image = QLabel()
            profile_image.setPixmap(ws.shapeImage(QSize(80, 80), self.user_image))
            password_label = QLabel("Password:")

            self.password_edit = QLineEdit()
            self.password_edit.setFixedWidth(150)

            self.enter_password_act = QAction()
            self.enter_password_act.triggered.connect(self.check_password)
            self.enter_password_act.setShortcut("Enter")

            enter_button = QPushButton()
            enter_button.setIcon(QIcon(i_dir + r"\Arrow Right.png"))
            enter_button.setFixedSize(20, 20)
            enter_button.addAction(self.enter_password_act)
            enter_button.clicked.connect(self.check_password)

            h_box = QHBoxLayout()
            h_box.addStretch()
            h_box.addWidget(password_label)
            h_box.addWidget(self.password_edit)
            h_box.addWidget(enter_button)
            h_box.addStretch()

            entry_container = QWidget()
            entry_container.setLayout(h_box)

            main_v_box = QVBoxLayout()
            main_v_box.addStretch()
            main_v_box.addWidget(header_label, alignment=Qt.AlignmentFlag.AlignHCenter)
            main_v_box.addSpacing(40)
            main_v_box.addWidget(profile_image, alignment=Qt.AlignmentFlag.AlignHCenter)
            main_v_box.addWidget(entry_container)
            main_v_box.addStretch()

            container = QWidget()
            container.setLayout(main_v_box)

            self.stacked_widget.addWidget(container)
            self.stacked_widget.setCurrentIndex(0)

        else: self.create_account()

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

        goals_button = QPushButton()
        goals_button.setIcon(QIcon(i_dir + r"\Goals.png"))
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

        user_info = [self.user_name]#Потом будет добалена информация о прогрессе

        profile_info_box = ws.ProfileInfoBox(self.user_image, user_info)
        
        main_v_box = QHBoxLayout()
        main_v_box.addWidget(profile_info_box, alignment=Qt.AlignmentFlag.AlignTop)
        main_v_box.addLayout(buttons_h_box)
        main_v_box.setContentsMargins(0, 0, 0, 0)

        container = QWidget()
        container.setLayout(main_v_box)

        self.create_toolbar()

        self.stacked_widget.addWidget(container)
        self.stacked_widget.removeWidget(self.stacked_widget.currentWidget())

    def previous_window(self):
        if self.stacked_widget.currentIndex() > 0:
            self.stacked_widget.removeWidget(self.stacked_widget.currentWidget())

    def create_toolbar(self):
        self.toggle_toolbar_act = QAction()
        self.toggle_toolbar_act.triggered.connect(self.toggle_toolbar)
        self.toggle_toolbar_act.setShortcut("F1")
        self.addAction(self.toggle_toolbar_act)

        tools = []

        toggle_button = QPushButton()
        toggle_button.setIcon(QIcon(i_dir + r"\Toggle.png"))
        toggle_button.clicked.connect(self.toggle_toolbar)
        toggle_button.setStyleSheet("border: 1px solid #FFD300")
        settings_button = QPushButton()
        settings_button.setIcon(QIcon(i_dir + r"\Settings.png"))
        settings_button.clicked.connect(self.settings)
        time_manager_button = QPushButton()
        time_manager_button.setIcon(QIcon(i_dir + r"\Fast Solution.png"))
        time_manager_button.clicked.connect(self.launch_time_manager)
        notes_button = QPushButton()
        notes_button.setIcon(QIcon(i_dir + r"\Notes.png"))
        notes_button.clicked.connect(self.notes)
        object_manager = QLineEdit()

        tools.append(toggle_button)
        tools.append(settings_button)
        tools.append(time_manager_button)
        tools.append(notes_button)

        for tool in tools:
            tool.setObjectName("Tool")
            tool.setIconSize(QSize(30, 30))

        tools.append(object_manager)
        
        self.tool_bar = QToolBar()
        for tool in tools:
            self.tool_bar.addWidget(tool)
            self.tool_bar.addSeparator()

        self.tool_bar.setOrientation(Qt.Orientation.Vertical)
        self.tool_bar.setFixedSize(58, 200)
        self.tool_bar.setMovable(False)

        self.addToolBar(Qt.ToolBarArea.RightToolBarArea, self.tool_bar)

    def launch_time_manager(self):
        time_manager = subprocess.Popen(r"WS Time Manager.exe")

    def toggle_toolbar(self):
        if self.tool_bar.isVisible():
            self.tool_bar.hide()
        else:
            self.tool_bar.show()

    def settings(self):
        self.dialog = QDialog()
        about_button = QPushButton("About")
        v_box = QVBoxLayout()
        v_box.addWidget(about_button)
        self.dialog.setLayout(v_box)
        self.dialog.show()

    def notes(self):
        self.dialog = QDialog()
        label = QLabel("In process")
        v_box = QVBoxLayout()
        v_box.addWidget(label)
        self.dialog.setLayout(v_box)
        self.dialog.show()

    def goal_branches_window(self):
        branches = DataManager.loadMainData("branches")
        self.branch_list = []

        self.branch_list_widget = QListWidget()
        self.branch_list_widget.itemClicked.connect(self.goals_window)
        h_box = QHBoxLayout()
        h_box.setContentsMargins(300, 85, 250, 85)

        if branches:
            for branch in branches:
                branch_name = branch[0]
                self.branch_list.append(branch_name)
                goal_branch = ws.GoalBranch(branch_name)
                goal_branch.deleteBranch.connect(self.delete_branch)
                goal_branch.renameBranch.connect(self.rename_branch)
                
                list_item = QListWidgetItem(self.branch_list_widget)
                list_item.setSizeHint(goal_branch.sizeHint())
                self.branch_list_widget.setItemWidget(list_item, goal_branch)
        h_box.addWidget(self.branch_list_widget)

        add_button = QPushButton()
        add_button.setIcon(QIcon(i_dir + "\Add icon.png"))
        add_button.setFixedSize(50, 50)
        add_button.clicked.connect(self.add_branch)
        add_button.setObjectName("Menu")
        h_box.addWidget(add_button, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)

        container = QWidget()
        container.setLayout(h_box)

        self.stacked_widget.addWidget(container)
        self.stacked_widget.setCurrentIndex(self.stacked_widget.currentIndex() + 1)

    def add_branch(self):
        branch_name, _ = QInputDialog.getText(self, "Add new branch", "Enter new branch name:")
        if branch_name:
            if DataManager.saveMainData("branch", branch_name) != False:
                self.branch_list.append(branch_name)

                goal_branch = ws.GoalBranch(branch_name)
                goal_branch.deleteBranch.connect(self.delete_branch)
                goal_branch.renameBranch.connect(self.rename_branch)

                list_item = QListWidgetItem(self.branch_list_widget)
                list_item.setSizeHint(goal_branch.sizeHint())
                self.branch_list_widget.setItemWidget(list_item, goal_branch)
            else:
                QMessageBox.warning(self, "Warning", "Branches cannot have the same names")

    def rename_branch(self, branch_name):
        new_name, _ = QInputDialog.getText(self, "Branch renaming", "Enter new name of the branch:")
        if new_name:
            DataManager.updateMainData("branch", [new_name, branch_name])
            branch_index = self.branch_list.index(branch_name)
            self.branch_list[branch_index] = new_name
            self.branch_list_widget.itemWidget(self.branch_list_widget.item(branch_index)).setText(new_name)

    def delete_branch(self, branch_name):
        ok = QMessageBox.question(self, "Branch deleting", "Delete branch?")
        if ok == QMessageBox.StandardButton.Yes:
            DataManager.deleteMainData("branch", branch_name)
            branch_index = self.branch_list.index(branch_name)
            self.branch_list.pop(branch_index)
            self.branch_list_widget.takeItem(branch_index)

    def goals_window(self, item):
        self.current_branch_id = str(self.branch_list_widget.currentIndex().row() + 1)

        goals = DataManager.loadMainData("goals", self.current_branch_id)

        tree_widget = QTreeWidget()
        tree_widget.setColumnWidth(0, 135)
        tree_widget.setIconSize(QSize(97, 97))
        tree_widget.setColumnCount(9)
        headers = ["", "Name", "Total difficulty", "Hours", "Benefit", "limit date", "Priority", "State", "ID"]
        tree_widget.setHeaderLabels(headers)
        tree_widget.itemClicked.connect(self.goal_window)

        for i in range(len(goals)):
            goal_info = goals[i]
            goal_info_str = list(str(item) for item in goal_info)#Преобразуем все значения в строковой тип

            goal_item = QTreeWidgetItem(tree_widget, [""] + goal_info_str[:8])
            goal_item.setSizeHint(1, QSize(100, 120))
            goal_item.setFont(1, QFont("Calibri", 18, 700))
            for i in range(2, 9):#Потом последние значение будет получатся по кол-ву характеристик
                goal_item.setFont(i, QFont("Calibri", 18))
            goal_item.setIcon(0, QIcon(ws.getGoalImage(goal_info[8].split(",")[0], goal_info[9].split(":")[0], goal_info[2]))) #Так мы получаем первое изображение из списка путей, которое является главным
            tree_widget.addTopLevelItem(goal_item)
        
        tree_widget.resizeColumnToContents(5)

        h_box = QHBoxLayout()
        h_box.setContentsMargins(300, 85, 250, 85)
        h_box.addWidget(tree_widget)
        
        add_button = QPushButton()
        add_button.setIcon(QIcon(i_dir + "\Add icon.png"))
        add_button.setFixedSize(50, 50)
        add_button.clicked.connect(self.goal_window)
        add_button.setObjectName("Menu")
        h_box.addWidget(add_button, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)

        container = QWidget()
        container.setLayout(h_box)

        self.stacked_widget.addWidget(container)
        self.stacked_widget.setCurrentIndex(self.stacked_widget.currentIndex() + 1)

    def goal_window(self, item=None):
        goal_characts = ["Total difficulty:", "Time:", "Benefit:", "Limit date:", "Priority:"]
        goal_state = "creating"
        self.areChangesMade = False
        self.goals_dict = {}

        self.goal_tree_list_widget = QListWidget()
        self.goal_tree_list_widget.setFixedWidth(475)
        self.goal_tree_list_widget.setObjectName("Tree")

        branch_name = self.branch_list_widget.itemWidget(self.branch_list_widget.currentItem()).getText()

        goal_image_label = ws.AddImageLabel(QSize(525, 325), shaping=False, default_image_path=i_dir + r"\Add an image....png")
                
        self.additional_images_label = ws.AdditionalImagesLabel()
        self.additional_images_label.imageRemoved.connect(self.setSaveEnabled)
        
        add_images_dir_button = QPushButton()
        add_images_dir_button.clicked.connect(add_images_dir_button.showMenu)
        add_images_dir_button.setIcon(QIcon(i_dir + r"\Add dir.png"))
        add_images_dir_button.setFixedSize(60, 60)
        add_images_dir_button.setIconSize(QSize(40, 40))
        add_images_dir_button.setObjectName("Tool")

        self.add_images_menu = QMenu()
        self.add_image_act = QAction("Add image or images")
        self.add_image_act.triggered.connect(self.add_image)
        
        self.set_dir_act = QAction("Add or change directory")
        self.set_dir_act.triggered.connect(self.set_dir)

        self.remove_dir_act = QAction("Remove directory")
        self.remove_dir_act.triggered.connect(self.additional_images_label.removeDir)
        self.remove_dir_act.triggered.connect(self.setSaveEnabled)

        self.add_images_menu.addAction(self.add_image_act)
        self.add_images_menu.addAction(self.set_dir_act)
        self.add_images_menu.addAction(self.remove_dir_act)
        add_images_dir_button.setMenu(self.add_images_menu)

        image_buttons_h_box = QHBoxLayout()
        image_buttons_h_box.addWidget(self.additional_images_label)
        image_buttons_h_box.addWidget(add_images_dir_button)
        image_buttons_h_box.addStretch()
        
        #Goal characteristics block
        characts_gb = QGroupBox("Characteristics")
        characts_gb.setFont(QFont('Calibri', 18))
        characts_gb.setFixedWidth(262)
        characts_list_widget = QListWidget()
        characts_list_widget.setStyleSheet("QScrollBar{width: 0px}")

        charact_edits = []

        for i in range(5): #Amount of standard goal characteristics is 5
            charact = goal_characts[i]
            charact_widget = QWidget()
            list_item = QListWidgetItem(characts_list_widget)
            h_box = QHBoxLayout()
            label = QLabel(charact)
            if charact == "Total difficulty:":
                line_edit = QLabel()
            elif charact == "Limit date:":
                line_edit = ws.DateEditTool()
                line_edit.dateChanged.connect(self.setSaveEnabled)
            elif charact == "Priority:":
                line_edit = QLineEdit()
                regex = QRegularExpression("^[A-E]$")
                validator = QRegularExpressionValidator(regex)
                line_edit.setValidator(validator)
                line_edit.textEdited.connect(self.setSaveEnabled)
            else:
                line_edit = QLineEdit()
                regex = QRegularExpression("^\d*\.?\d+$")
                validator = QRegularExpressionValidator(regex)
                line_edit.setValidator(validator)
                line_edit.textEdited.connect(self.setSaveEnabled)
            h_box.addWidget(label, alignment=Qt.AlignmentFlag.AlignLeft)
            h_box.addWidget(line_edit, alignment=Qt.AlignmentFlag.AlignRight)
            if charact == "Time:":
                self.d_diff_indicator = ws.dDiffIndicator()
                line_edit.textChanged.connect(self.update_goal_indicator)
                h_box.addWidget(self.d_diff_indicator)
            else:
                h_box.addSpacing(24)
            h_box.addSpacing(20)
            charact_widget.setLayout(h_box)
            list_item.setSizeHint(charact_widget.sizeHint())
            characts_list_widget.setItemWidget(list_item, charact_widget)
            charact_edits.append(line_edit)

        characts_v_box = QVBoxLayout()
        add_new_charact_button = QPushButton("Add new characteristics...")
        characts_v_box.addWidget(characts_list_widget, alignment=Qt.AlignmentFlag.AlignBottom)
        characts_v_box.addWidget(add_new_charact_button)
        characts_gb.setLayout(characts_v_box)

        #Used skills block
        skills_gb = QGroupBox("Skills used")
        skills_gb.setFont(QFont('Calibri', 18))
        skills_gb.setFixedWidth(262)
        skills_list_widget = QListWidget()
        skills_gb.setStyleSheet("QScrollBar{width: 0px}")
        skills_v_box = QVBoxLayout()
        skills_v_box.addStretch()

        add_skill_button = QPushButton("Add skill...")

        skills_v_box.addWidget(skills_list_widget, alignment=Qt.AlignmentFlag.AlignBottom)
        skills_v_box.addWidget(add_skill_button)
        skills_gb.setLayout(skills_v_box)

        note_text_edit = QPlainTextEdit()
        note_text_edit.setPlaceholderText("Add note...")
        note_text_edit.setFixedWidth(1000)
        note_text_edit.setStyleSheet("color: white")
        note_text_edit.textChanged.connect(self.setSaveEnabled)

        goal_name_edit = QLineEdit()
        goal_name_edit.setPlaceholderText("Add name...")
        goal_name_edit.setFixedSize(300, 45)
        goal_name_edit.setFont(QFont('Calibri', 18))
        goal_name_edit.textEdited.connect(self.setSaveEnabled)

        branch_label = QLabel("Branch: " + branch_name)
        state_label = QLabel("State: " + goal_state)
        progress_label = QLabel("Progress: ")
        progress_settings = QPushButton("...")
        progress_settings.setFixedSize(12, 12)

        v_box = QVBoxLayout()
        v_box.addWidget(goal_name_edit, alignment=Qt.AlignmentFlag.AlignLeft)
        v_box.addWidget(branch_label, alignment=Qt.AlignmentFlag.AlignLeft)
        v_box.addWidget(state_label, alignment=Qt.AlignmentFlag.AlignLeft)
        v_box.addWidget(progress_label, alignment=Qt.AlignmentFlag.AlignLeft)
        v_box.addWidget(progress_settings, alignment=Qt.AlignmentFlag.AlignLeft)
        v_box.addStretch()

        self.cell_list = [goal_image_label, goal_name_edit, self.additional_images_label, note_text_edit, progress_label, state_label] + charact_edits
        self.list_widget_list = [self.goal_tree_list_widget, characts_list_widget, skills_list_widget]

        self.save_button = QPushButton()
        self.save_button.setFixedSize(60, 60)
        self.save_button.setIconSize(QSize(30, 30))
        self.save_button.setIcon(QIcon(i_dir + r"\save goal.png"))
        self.save_button.clicked.connect(self.save_goal)
        self.save_button.setEnabled(False)

        self.id_list = []
        if item:
            goal_id = item.text(8)
            goal_name = item.text(1)
            #Отобразим дерево цели
            goal_tree = DataManager.getGoalTree(goal_id)
            for goal in goal_tree:
                self.id_list.append(goal[0])
                if goal[1] == goal_name:
                    isMain = True
                else:
                    isMain = False
                goal_tree_item = ws.GoalTreeItem(goal[0], goal[1], goal[3], goal[2].split(",")[0], isMain)
                goal_tree_item.subgoalAdded.connect(self.add_subgoal)
                goal_tree_item.goalDeleted.connect(self.delete_goal)

                list_widget_item = QListWidgetItem()
                size_hint = goal_tree_item.sizeHint()
                list_widget_item.setSizeHint(QSize(size_hint.width(), size_hint.height() + 35))
                self.goal_tree_list_widget.addItem(list_widget_item)
                self.goal_tree_list_widget.setItemWidget(list_widget_item, goal_tree_item)
        else:
            self.add_subgoal(self.current_branch_id)

        self.goal_tree_list_widget.currentItemChanged.connect(self.display_goal)
        self.goal_tree_list_widget.setCurrentRow(0)

        goal_image_label.imageAdded.connect(self.setSaveEnabled)

        if not goal_image_label.isImageAdded:
            add_images_dir_button.setEnabled(False)
            goal_image_label.imageAdded.connect(lambda: add_images_dir_button.setEnabled(True))
        goal_image_label.imageAdded.connect(lambda: self.additional_images_label.setMainImage(goal_image_label.image_path))

        gb_h_box = QHBoxLayout()
        gb_h_box.addWidget(characts_gb)
        gb_h_box.addWidget(skills_gb)
        gb_h_box.addStretch()

        middle_v_box = QVBoxLayout()
        middle_v_box.addLayout(image_buttons_h_box)
        middle_v_box.addLayout(gb_h_box)

        main_grid = QGridLayout()
        main_grid.addWidget(self.goal_tree_list_widget, 0, 0, 3, 1)
        main_grid.addWidget(goal_image_label, 0, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        main_grid.addLayout(middle_v_box, 1, 1)
        main_grid.addWidget(note_text_edit, 2, 1, 1, 2)
        main_grid.addLayout(v_box, 0, 2, alignment=Qt.AlignmentFlag.AlignLeft)
        main_grid.addWidget(self.save_button, 2, 3, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        main_grid.setColumnStretch(2, 1)

        container = QWidget()
        container.setLayout(main_grid)

        self.stacked_widget.addWidget(container)
        self.stacked_widget.setCurrentIndex(self.stacked_widget.currentIndex() + 1)

    def update_goal_indicator(self, text):
        self.d_diff_indicator.updateColor(text)

    def display_goal(self, current_item, previous):
        if self.areChangesMade and QMessageBox.question(self, "Unsaved changes", "Some changes are made. Do you want to save them?") == QMessageBox.StandardButton.Yes:
            self.save_goal(previous)
        self.areChangesMade = False
        self.current_goal_id = self.goal_tree_list_widget.itemWidget(current_item).goal_id
        if self.current_goal_id in self.goals_dict:
            self.goals_dict[self.current_goal_id].displayData()
        else:
            goal = wsobj.Goal(self.cell_list, self.list_widget_list, self.current_goal_id)
            goal.skillCharactChanged.connect(self.setSaveEnabled)
            self.goals_dict[self.current_goal_id] = goal

    def add_subgoal(self, parent_id):
        subgoal = wsobj.Goal(self.cell_list, self.list_widget_list)
        self.current_goal_id = self.getGoalID(parent_id)
        self.goals_dict[self.current_goal_id] = subgoal
        self.id_list.append(self.current_goal_id)

    def delete_goal(self, goal_id):
        DataManager.deleteMainData("goal", goal_id)
        self.id_list.remove(goal_id)
        if not self.id_list:
            self.goal_tree_list_widget.currentItemChanged.disconnect()#This will be done in this way while window system isn't ready
            self.previous_window()
        self.goals_dict.pop(goal_id)
        self.goal_tree_list_widget.takeItem(self.goal_tree_list_widget.currentRow())

    def setSaveEnabled(self):
        self.save_button.setEnabled(True)
        self.areChangesMade = True

    def add_image(self):
        image_path, _ = QFileDialog.getOpenFileNames(self, "Choose image of images", filter="Image Files (*.png *.jpg *.bmp)")
        if image_path:
            self.additional_images_label.addImages(image_path)
            self.setSaveEnabled()

    def set_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Choose a directory")
        if dir_path:
            self.additional_images_label.setDir(dir_path)
            self.setSaveEnabled()

    def save_goal(self, previous=None):
        #1 - name lineEdit, 2 - image list, 3 - note textEdit, 4 - limit_date_label, 5 - progress_label, 6 - state_label, 7-11 - characts lineEdits
        goal_name = self.cell_list[1].text()
        characts = []
        image_list = self.cell_list[2].getImagesList()
        for i in range(6, 11):
            text = self.cell_list[i].text()
            characts.append(self.cell_list[i].text())

            characts[0] = 50 #TEST

        note = self.cell_list[3].toPlainText()
        if goal_name and len(characts) == 5: #Потом будет сравниваться с кол-вом характеристик
            if self.goals_dict[self.current_goal_id].isGoalExists:
                goal_data = (self.current_goal_id, goal_name) + tuple(characts) + ("us", "state", note, image_list, "50,1", "", self.current_goal_id)
                DataManager.updateMainData("goal", goal_data)
                if previous:
                    current_widget = self.goal_tree_list_widget.itemWidget(previous)
                else:
                    current_widget = self.goal_tree_list_widget.itemWidget(self.goal_tree_list_widget.currentItem())
                current_widget.updateWidget(self.current_goal_id, goal_name, float(goal_data[3]), goal_data[11].split(",")[0])
            else:
                goal_data = (self.current_goal_id, goal_name) + tuple(characts) + ("us", "state", note, image_list, "50,1", "")
                DataManager.saveMainData("goal", goal_data)

                self.id_list.sort()
                goal_index = self.id_list.index(self.current_goal_id)
                if goal_index == 0:
                    isMain = True
                else:
                    isMain = False
                goal_tree_item = ws.GoalTreeItem(self.current_goal_id, goal_name, float(goal_data[3]), 0, isMain)
                goal_tree_item.subgoalAdded.connect(self.add_subgoal)
                goal_tree_item.goalDeleted.connect(self.delete_goal)

                list_widget_item = QListWidgetItem()
                size_hint = goal_tree_item.sizeHint()
                list_widget_item.setSizeHint(QSize(size_hint.width(), size_hint.height() + 35))

                self.goal_tree_list_widget.insertItem(goal_index, list_widget_item)
                self.goal_tree_list_widget.setItemWidget(list_widget_item, goal_tree_item)
            self.save_button.setEnabled(False)
            self.areChangesMade = False
            self.goals_dict[self.current_goal_id].setData(goal_data)
        else:
            QMessageBox.warning(self, "Fill cells to save the goal", "Not all the required cells were filled")

    def getGoalID(self, parent_id):
        depth = len(parent_id.split(".")) + 1
        
        ids = DataManager.getGoalIDs(parent_id)
        level_len = 0
        for iD in ids:
            idl = iD[0].split(".")
            if len(idl) == depth:
                level_len += 1
        return f"{parent_id}.{level_len + 1}"

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