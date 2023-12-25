import statistics as stats
import datetime as dt
from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QGridLayout, QPushButton, QMessageBox, QHBoxLayout, QVBoxLayout, QDialog, QListWidget, QListWidgetItem, QTreeWidget, QTreeWidgetItem, QGroupBox, QPlainTextEdit, QMenu, QInputDialog, QFileDialog, QDateEdit, QRadioButton, QButtonGroup, QCheckBox, QComboBox, QStackedWidget, QGraphicsPixmapItem
from PyQt6.QtCore import Qt, QSize, QRegularExpression, pyqtSignal, QDate
from PyQt6.QtGui import QIcon, QFont, QAction, QRegularExpressionValidator, QFontMetrics
import plotly.graph_objs as go
import WSwidgets as ws
import WSobjects as wsobj
import DataManager, configparser, os, docx, csv
i_dir = r"Files\icons"
user_config_path = r"Files\config\user.ini"

class ProfileTab(QWidget):
    def __init__(self, user_image, user_info):
        super().__init__()
        user_info_box = ws.ProfileInfoBox(user_image, user_info)
        skills_label = QLabel("Skills")
        skills_label.setFont(QFont("Calibri", 30, 700))

        self.skills_tree_widget = QTreeWidget()
        self.skills_tree_widget.setColumnCount(2)
        self.skills_tree_widget.setHeaderHidden(True)

        skills_data = DataManager.loadMainData("skills")
        for skill in skills_data:
            tree_widget_item = QTreeWidgetItem([skill[0], str(round(skill[1], 2)) + " hours"])
            tree_widget_item.setFont(0, QFont('Calibri', 24))
            tree_widget_item.setFont(1, QFont('Calibri', 18))
            self.skills_tree_widget.addTopLevelItem(tree_widget_item)
        self.skills_tree_widget.resizeColumnToContents(0)

        add_skill_button = QPushButton()
        add_skill_button.clicked.connect(self.add_skill)
        add_skill_button.setObjectName("Menu")
        add_skill_button.setFixedSize(50, 50)
        add_skill_button.setIcon(QIcon(i_dir + r"\Add icon.png"))

        v_box = QVBoxLayout()
        v_box.addWidget(skills_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        v_box.addWidget(self.skills_tree_widget)
        
        h_box = QHBoxLayout()
        h_box.addWidget(user_info_box, alignment=Qt.AlignmentFlag.AlignTop)
        h_box.addLayout(v_box)
        h_box.addWidget(add_skill_button, alignment=Qt.AlignmentFlag.AlignBottom)
        h_box.setContentsMargins(0, 0, 0, 50)
        self.setLayout(h_box)

    def add_skill(self):
        skill_name, _ = QInputDialog.getText(self, "Skill adding", "Enter skill name:")
        if skill_name:
            if not (":" in skill_name or "," in skill_name):
                DataManager.saveMainData("skill", skill_name)
                item = QTreeWidgetItem(self.skills_tree_widget, [skill_name, "0.0 hours"])
                item.setFont(0, QFont('Calibri', 24))
                item.setFont(1, QFont('Calibri', 18))
                self.skills_tree_widget.addTopLevelItem(item)
                self.skills_tree_widget.resizeColumnToContents(0)
            else:
                QMessageBox.warning(self, "Skill name can't contain this characters: ':', ','")

class BranchesTab(QWidget):
    def __init__(self):
        super().__init__()
        branches = DataManager.loadMainData("branches")
        self.branch_list = []

        self.branch_list_widget = QListWidget()
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

        self.setLayout(h_box)

    def add_branch(self):
        branch_name, _ = QInputDialog.getText(self, "Branch adding", "Enter new branch name:")
        if branch_name:
            if DataManager.saveMainData("branch", [branch_name, ",".join(["", "Name", "Hours", "Benefit", "limit date", "Priority", "State", "ID"])]) != False:
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
            branch_index = self.branch_list.index(branch_name)
            DataManager.deleteMainData("branch", branch_index + 1)
            self.branch_list.pop(branch_index)
            self.branch_list_widget.takeItem(branch_index)

class FloatTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, text):
        super().__init__(text)

    def __lt__(self, otherItem):
        column = self.treeWidget().sortColumn()
        try:
            num = float(self.text(column))
            othernum = float(otherItem.text(column))
            return num < othernum
        except Exception:
            return self.text(column).lower() < otherItem.text(column).lower()

class GoalsTab(QWidget):
    sectionMoved = pyqtSignal()
    def __init__(self, branch):
        super().__init__()
        self.current_branch_id = branch
        self.isSubgoalsShowing = False

        self.standard_characts = ["", "Name", "Hours", "Benefit", "limit date", "Priority", "State", "ID"]
        self.tree_widget = QTreeWidget()
        self.tree_widget.setStyleSheet("QTreeWidget::item{height: 140px}")
        self.tree_widget.setIconSize(QSize(97, 97))
        self.tree_widget.setSortingEnabled(True)

        self.updateWidget()

        self.tree_widget.setColumnWidth(0, 135)
        self.tree_widget.setColumnWidth(1, 200)
        self.tree_widget.setColumnWidth(6, 120)
        self.tree_widget.setColumnWidth(4, 135)

        h_box = QHBoxLayout()
        h_box.setContentsMargins(300, 85, 250, 85)
        h_box.addWidget(self.tree_widget)

        showing_checkbox = QCheckBox()
        showing_checkbox.toggled.connect(self.toggle_subgoals_showing)
        showing_checkbox.setToolTip("Show subgoals")

        settings_button = QPushButton()
        settings_button.setIcon(QIcon(i_dir + r"\Settings.png"))
        settings_button.setObjectName("Menu")
        settings_button.setFixedSize(16, 16)
        settings_button.clicked.connect(self.characts_displaying_settings)
        
        self.add_button = QPushButton()
        self.add_button.setIcon(QIcon(i_dir + "\Add icon.png"))
        self.add_button.setFixedSize(50, 50)
        self.add_button.setObjectName("Menu")
        
        v_box = QVBoxLayout()
        v_box.setContentsMargins(0, 0, 0, 0)

        v_box.addStretch()
        v_box.addWidget(showing_checkbox, alignment=Qt.AlignmentFlag.AlignHCenter)
        v_box.addWidget(settings_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        v_box.addWidget(self.add_button)
        h_box.addLayout(v_box)

        self.setLayout(h_box)

    def characts_displaying_settings(self):
        self.dialog = QDialog()
        self.dialog.setModal(True)
        self.dialog.setFixedWidth(280)
        self.displaying_characts = []
        self.save_sections_act = QAction()
        self.addAction(self.save_sections_act)

        label = QLabel("Displaying custom characteristic")
        line_edit = QLineEdit()
        line_edit.setPlaceholderText("Enter a custom characteristic name")
        self.characts_list_widget = QListWidget()
        reset_button = QPushButton("Reset sections position")
        reset_button.clicked.connect(self.reset_sections)
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.save_displaying_characts)

        for charact in self.ccs:
            self.add_displaying_charact(charact)

        v_box = QVBoxLayout()
        v_box.addWidget(label)
        v_box.addWidget(line_edit)
        v_box.addWidget(self.characts_list_widget)
        v_box.addWidget(reset_button)
        v_box.addWidget(ok_button)
        self.dialog.setLayout(v_box)
        
        object_manager = ws.ObjectManager(self.dialog, line_edit, ["Characteristics"])
        object_manager.selected.connect(self.add_displaying_charact)
        self.dialog.show()

    def reset_sections(self):
        self.headers = self.standard_characts + self.ccs
        self.header.sectionMoved.disconnect()
        self.saveData()
        self.updateWidget()

    def toggle_subgoals_showing(self, state):
        if state:
            self.isSubgoalsShowing = True
        else:
            self.isSubgoalsShowing = False
        self.updateWidget()

    def save_displaying_characts(self):
        for charact in self.ccs:
            if charact not in self.displaying_characts:
                self.headers.remove(charact)
        for charact in self.displaying_characts:
            if charact not in self.headers:
                self.headers.append(charact)

        sections_pos = ",".join(self.headers)
        ccs = ",".join(self.displaying_characts)
        DataManager.updateMainData("displaying_characts", (ccs, sections_pos, self.current_branch_id))
        self.dialog.close()
        self.header.sectionMoved.disconnect()
        self.updateWidget()

    def add_displaying_charact(self, charact_name):
        if charact_name not in self.displaying_characts:
            widget = ws.SkillCharactWidget(charact_name, "", "displaying charact")
            item = QListWidgetItem()
            item.setSizeHint(widget.sizeHint())
            self.characts_list_widget.addItem(item)
            self.characts_list_widget.setItemWidget(item, widget)
            widget.delete_button.clicked.connect(lambda: self.remove_charact(item))
            self.displaying_characts.append(charact_name)

    def remove_charact(self, item):
        name = self.characts_list_widget.itemWidget(item).name
        self.displaying_characts.remove(name)
        self.characts_list_widget.takeItem(self.characts_list_widget.row(item))

    def updateWidget(self):
        branch = DataManager.loadMainData("branch", self.current_branch_id, one=True)
        if branch[1]:
            self.ccs = branch[1].split(",")
        else:
            self.ccs = []
        self.headers = branch[2].split(',')
        self.tree_widget.setColumnCount(len(self.headers))
        self.tree_widget.setHeaderLabels(self.headers)
        self.header = self.tree_widget.header()
        self.header.sectionMoved.connect(self.section_moved)
        font18b = QFont("Calibri", 18, 700)
        font18 = QFont("Calibri", 18)

        self.tree_widget.clear()
        goals = DataManager.loadMainData("goals", self.current_branch_id)
        for goal_info in goals:
            goal_info_dict = {}
            if goal_info[10] or self.isSubgoalsShowing:
                for i in range(len(goal_info[:7])):
                    if i == 1:
                        goal_info_dict[self.standard_characts[i + 1]] = str(round(goal_info[i], 2))
                    else:
                        goal_info_dict[self.standard_characts[i + 1]] = str(goal_info[i])
                if self.ccs and goal_info[9]:
                    for charact in goal_info[9].split(","):#Now there's all characts of the goal in goal_info_dict
                        charact_name, value = charact.split(":")
                        goal_info_dict[charact_name] = value

                goal_info_list = []
                for charact in self.headers[1:]:
                    goal_info_list.append(goal_info_dict.pop(charact, ""))

                goal_item = FloatTreeWidgetItem([""] + goal_info_list)
                goal_item.setSizeHint(1, QSize(100, 120))
                goal_item.setFont(1, font18b)
                for i in range(2, 8 + len(self.ccs)):
                    goal_item.setFont(i, font18)
                goal_item.setIcon(0, QIcon(ws.getGoalImage(goal_info[7].split(",")[0], ws.calculate_progress(goal_info[8], goal_info[1], goal_info[9], goal_info[5]), goal_info[1]))) #Так мы получаем первое изображение из списка путей, которое является главным
                self.tree_widget.addTopLevelItem(goal_item)
        self.tree_widget.resizeColumnToContents(5)

    def section_moved(self, logicI, old_index, new_index):
        section = self.headers.pop(old_index)
        self.headers.insert(new_index, section)
        self.sectionMoved.emit()

    def saveData(self):
        DataManager.updateMainData("sections_pos", [",".join(self.headers), self.current_branch_id])

class GoalTab(QWidget):
    changesMade = pyqtSignal()
    changesSaved = pyqtSignal()
    previous_window_req = pyqtSignal()
    goal_list_update_req = pyqtSignal()
    def __init__(self, branch_id, item=None, goal_id=None):
        super().__init__()
        self.branch_id = str(branch_id)
        self.branch_name, _, sections_pos = DataManager.loadMainData("branch", branch_id, one=True)
        sections_pos = sections_pos.split(",")

        goal_characts = ["Time:", "Benefit:", "Limit date:", "Priority:"]
        self.areChangesMade = False
        self.goals_dict = {}

        self.goal_tree_list_widget = QListWidget()
        self.goal_tree_list_widget.setFixedWidth(475)
        self.goal_tree_list_widget.setObjectName("Tree")

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
        characts_list_widget = ws.SkillCharactListWidget()
        characts_list_widget.setStyleSheet("QScrollBar{width: 0px}")

        charact_edits = []
        for i in range(4): #Amount of standard goal characteristics is 4
            charact = goal_characts[i]
            charact_widget = QWidget()
            list_item = QListWidgetItem(characts_list_widget)
            h_box = QHBoxLayout()
            label = QLabel(charact)
            if charact == "Limit date:":
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
                regex = QRegularExpression("[0-9][0-9]*\.?[0-9]+$")
                validator = QRegularExpressionValidator(regex)
                line_edit.setValidator(validator)
                line_edit.textEdited.connect(self.setSaveEnabled)
            h_box.addWidget(label, alignment=Qt.AlignmentFlag.AlignLeft)
            h_box.addStretch()
            h_box.addWidget(line_edit)
            if charact == "Time:":
                self.d_diff_indicator = ws.dDiffIndicator()
                line_edit.textChanged.connect(self.update_goal_indicator)
                h_box.addWidget(self.d_diff_indicator)
                h_box.addSpacing(6)
            else:
                h_box.addSpacing(24)
            h_box.addSpacing(20)
            charact_widget.setLayout(h_box)
            list_item.setSizeHint(charact_widget.sizeHint())
            characts_list_widget.setItemWidget(list_item, charact_widget)
            charact_edits.append(line_edit)

        characts_v_box = QVBoxLayout()
        add_new_charact_button = QPushButton("Add new characteristics...")
        add_new_charact_button.clicked.connect(lambda: self.add_skill_or_charact_dialog("Characteristics", characts_list_widget))
        characts_v_box.addWidget(characts_list_widget, alignment=Qt.AlignmentFlag.AlignBottom)
        characts_v_box.addWidget(add_new_charact_button)
        characts_gb.setLayout(characts_v_box)

        #Used skills block
        skills_gb = QGroupBox("Skills used")
        skills_gb.setFont(QFont('Calibri', 18))
        skills_gb.setFixedWidth(262)
        skills_list_widget = ws.SkillCharactListWidget()
        skills_gb.setStyleSheet("QScrollBar{width: 0px}")
        skills_v_box = QVBoxLayout()
        skills_v_box.addStretch()

        add_skill_button = QPushButton("Add skill...")
        add_skill_button.clicked.connect(lambda: self.add_skill_or_charact_dialog("Skills", skills_list_widget))

        skills_v_box.addWidget(skills_list_widget, alignment=Qt.AlignmentFlag.AlignBottom)
        skills_v_box.addWidget(add_skill_button)
        skills_gb.setLayout(skills_v_box)

        note_text_edit = QPlainTextEdit()
        note_text_edit.setPlaceholderText("Add note...")
        note_text_edit.setFixedWidth(1000)
        note_text_edit.textChanged.connect(self.setSaveEnabled)

        goal_name_edit = QLineEdit()
        goal_name_edit.setPlaceholderText("Add name...")
        goal_name_edit.setFixedSize(300, 45)
        goal_name_edit.setFont(QFont('Calibri', 18))
        goal_name_edit.textEdited.connect(self.setSaveEnabled)

        branch_label = QLabel("Branch: " + self.branch_name)
        state_label = QLabel("State: ")
        progress_label = QLabel("Progress: ")
        group_checkbox = QCheckBox("Group")
        group_checkbox.stateChanged.connect(self.setSaveEnabled)
        other_settings = QPushButton("...")
        other_settings.clicked.connect(self.goal_settings)
        other_settings.setFixedSize(12, 12)

        v_box = QVBoxLayout()
        v_box.addWidget(goal_name_edit, alignment=Qt.AlignmentFlag.AlignLeft)
        v_box.addWidget(branch_label, alignment=Qt.AlignmentFlag.AlignLeft)
        v_box.addWidget(state_label, alignment=Qt.AlignmentFlag.AlignLeft)
        v_box.addWidget(progress_label, alignment=Qt.AlignmentFlag.AlignLeft)
        v_box.addWidget(group_checkbox, alignment=Qt.AlignmentFlag.AlignLeft)
        v_box.addWidget(other_settings, alignment=Qt.AlignmentFlag.AlignLeft)
        v_box.addStretch()

        self.cell_list = [goal_image_label, goal_name_edit, self.additional_images_label, note_text_edit, progress_label, state_label, group_checkbox] + charact_edits
        self.list_widget_list = [self.goal_tree_list_widget, characts_list_widget, skills_list_widget]

        self.save_button = QPushButton()
        self.save_button.setFixedSize(60, 60)
        self.save_button.setIconSize(QSize(30, 30))
        self.save_button.setIcon(QIcon(i_dir + r"\save goal.png"))
        self.save_button.clicked.connect(self.save_goal)
        self.save_button.setEnabled(False)

        self.complete_button = QPushButton()
        self.complete_button.setFixedSize(60, 60)
        self.complete_button.setIconSize(QSize(30, 30))
        self.complete_button.setIcon(QIcon(i_dir + r"\complete goal.png"))
        self.complete_button.clicked.connect(self.complete_goal)
        self.complete_button.setEnabled(False)

        self.id_list = []
        if item or goal_id:
            if goal_id:
                self.main_goal_id = goal_id
            else:
                self.main_goal_id = item.text(sections_pos.index("ID"))
            self.update_goal_tree()
        else:
            self.add_subgoal(self.branch_id)
            self.old_goal_id = self.current_goal_id
            self.main_goal_id = self.current_goal_id

        self.goal_tree_list_widget.currentItemChanged.connect(self.display_goal)
        self.goal_tree_list_widget.setCurrentRow(0)

        goal_image_label.imageAdded.connect(self.setSaveEnabled)

        if not goal_image_label.isImageAdded:
            add_images_dir_button.setEnabled(False)
            goal_image_label.imageAdded.connect(lambda: add_images_dir_button.setEnabled(True))
        goal_image_label.imageAdded.connect(lambda: self.additional_images_label.setMainImage(goal_image_label.image_path))

        buttons_v_box = QVBoxLayout()
        buttons_v_box.addStretch()
        buttons_v_box.addWidget(self.save_button, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        buttons_v_box.addWidget(self.complete_button, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)

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
        main_grid.addLayout(buttons_v_box, 2, 3)
        main_grid.setColumnStretch(2, 1)

        self.setLayout(main_grid)

    def update_goal_tree(self):
        self.goal_tree_list_widget.blockSignals(True)
        self.goal_tree_list_widget.clear()
        self.id_list = []

        goal_tree = DataManager.getGoalTree(self.main_goal_id)
        for goal in goal_tree:
            self.id_list.append(goal[0])
            if goal[0] == self.main_goal_id:
                isMain = True
            else:
                isMain = False
            goal_tree_item = ws.GoalTreeItem(goal[0], goal[1], goal[3], ws.calculate_progress(goal[2], goal[3], goal[4], goal[6]), isMain, goal[5], goal[6])
            goal_tree_item.subgoalAdded.connect(self.add_subgoal)
            goal_tree_item.goalDeleted.connect(self.delete_goal)

            list_widget_item = QListWidgetItem()
            size_hint = goal_tree_item.sizeHint()
            list_widget_item.setSizeHint(QSize(size_hint.width(), size_hint.height() + 35))
            self.goal_tree_list_widget.addItem(list_widget_item)
            self.goal_tree_list_widget.setItemWidget(list_widget_item, goal_tree_item)
        self.goal_tree_list_widget.blockSignals(False)

    def add_skill_or_charact_dialog(self, data_type, list_widget):
        if data_type == "Skills" and self.goals_dict[self.current_goal_id].goal_data[13]:
            QMessageBox.warning(self, "Unable to add skill to this goal", "The goal has group type. Its used skills will be automatically added.")
        else:
            data_type_name = data_type[0].lower() + data_type[1:-1]
            self.dialog = QDialog()
            self.dialog.setWindowFlag(Qt.WindowType.FramelessWindowHint)
            self.dialog.setFixedHeight(275)
            self.dialog.setModal(True)
            line_edit = QLineEdit()
            line_edit.setPlaceholderText(f"Enter {data_type_name} name...")
            object_manager = ws.ObjectManager(self.dialog, line_edit, [data_type])
            ok_button = QPushButton()
            enter_act = QAction()
            enter_act.triggered.connect(ok_button.click)
            ok_button.addAction(enter_act)
            ok_button.clicked.connect(lambda: self.add_skill_or_charact([data_type, line_edit, list_widget, object_manager]))
            ok_button.setIcon(QIcon(i_dir + r"\Arrow Right.png"))
            ok_button.setFixedSize(20, 20)
            h_box = QHBoxLayout()
            h_box.addWidget(line_edit)
            h_box.addWidget(ok_button)
            v_box = QVBoxLayout()
            v_box.addLayout(h_box)
            v_box.addStretch()
            if data_type == "Characteristics":
                charact_button = QPushButton("Add new or change existing characteristic")
                charact_button.clicked.connect(lambda: self.charact_settings(line_edit, object_manager))
                v_box.addWidget(charact_button)
            self.dialog.setLayout(v_box)
            self.dialog.show()

    def charact_settings(self, line_edit, object_manager):
        self.dialog1 = QDialog()
        self.dialog1.setWindowTitle("Characteristic settings")
        self.dialog1.setModal(True)
        charact_name = ""
        charact_edit = QLineEdit()
        charact_edit.setPlaceholderText("Enter characteristic name")
        validator = QRegularExpressionValidator(QRegularExpression("[^,:|]*"))
        charact_edit.setValidator(validator)

        charact_type_label = QLabel("Choose characteristic type:")
        static_rb = QRadioButton("static")
        dynamic_rb = QRadioButton("dynamic")

        self.charact_type_group = QButtonGroup()
        self.charact_type_group.addButton(static_rb)
        self.charact_type_group.addButton(dynamic_rb)

        v_box = QVBoxLayout()
        v_box.addWidget(charact_edit)
        v_box.addWidget(charact_type_label)
        v_box.addWidget(static_rb)
        v_box.addWidget(dynamic_rb)
        v_box.addStretch()

        if object_manager.isSelected:
            charact_name = line_edit.text()
            charact_edit.setText(charact_name)
            charact_info = DataManager.loadMainData("characteristic", charact_name, one=True)

            if charact_info[0] == "static":
                static_rb.setChecked(True)
            else:
                dynamic_rb.setChecked(True)

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(lambda: self.delete_charact(charact_name, object_manager))
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(lambda: self.save_charact(charact_edit, line_edit, object_manager))
        ok_h_box = QHBoxLayout()
        ok_h_box.addWidget(delete_button)
        ok_h_box.addWidget(ok_button)
        main_v_box = QVBoxLayout()
        main_v_box.addLayout(v_box)
        main_v_box.addLayout(ok_h_box)
        self.dialog1.setLayout(main_v_box)
        self.dialog1.show()

    def delete_charact(self, charact_name, obj_manager):
        if charact_name:
            DataManager.deleteMainData("characteristic", charact_name)
            obj_manager.load_data()
            obj_manager.update_list()
            self.dialog1.close()

    def save_charact(self, charact_edit, line_edit, obj_manager):
        charact_name = charact_edit.text()
        old_charact_name = line_edit.text()
        charact_type = ""
        if self.charact_type_group.checkedButton():
            charact_type = self.charact_type_group.checkedButton().text()
        value_type = ""
        if charact_name and charact_type:
            if obj_manager.isSelected:
                DataManager.updateMainData("Characteristics", [charact_name, charact_type, value_type, old_charact_name])
            else:
                DataManager.saveMainData("Characteristics", [charact_name, charact_type, value_type])
                obj_manager.isSelected = True
            self.dialog1.close()
            obj_manager.load_data()
            line_edit.setText(charact_name)
        else:
            QMessageBox.warning(self.dialog1, "Warning", "Not all the required information were entered")

    def add_skill_or_charact(self, standard_mode=[], setting_mode=[]):
        if setting_mode:
            object_name, object_value, list_widget, isGroup, data_type = setting_mode
        else:
            object_value = ""
            isGroup = self.goals_dict[self.current_goal_id].goal_data[13]
            data_type, line_edit, list_widget, object_manager = standard_mode
            object_name = line_edit.text()
        if setting_mode or object_manager.isSelected and object_name not in list_widget.addedItemsText:
            item = QListWidgetItem()
            if object_value.replace(".", "").isdigit():
                object_value = str(round(float(object_value), 1))
            widget = ws.SkillCharactWidget(object_name, object_value, data_type, spacing=True)
            widget.value_edit.textEdited.connect(lambda: self.skill_or_charact_changed(widget.value_edit, list_widget, object_name))
            widget.delete_button.clicked.connect(lambda: self.remove_skill_or_charact(item, object_name, list_widget, data_type))
            item.setSizeHint(widget.sizeHint())
            if standard_mode:
                self.setSaveEnabled()
            
            if data_type == "Characteristics":
                c_type = DataManager.loadMainData("characteristic", object_name, one=True)[0]
                if c_type == "dynamic" and isGroup:
                    widget.setReadOnly()
                if c_type == "dynamic" and not setting_mode:
                    self.goals_dict[self.current_goal_id].goal_data[12] += f"{object_name}:{QDate.currentDate().toString('yyyy-MM-dd')} 0"

            elif isGroup and data_type == "Skills":
                widget.setReadOnly()

            list_widget.addItem(item)
            list_widget.addedItemsText[object_name] = object_value
            list_widget.setItemWidget(item, widget)
            if standard_mode:
                self.dialog.close()
        else:
            data_type_name = data_type[0].lower() + data_type[1:-1]
            QMessageBox.warning(self, f"Invalid {data_type_name} name", f"Choose an existing {data_type_name} from the object manager box and make sure you haven't added this {data_type_name} already.")

    def remove_skill_or_charact(self, item, object_name, list_widget, data_type):
        list_widget.takeItem(list_widget.row(item))
        list_widget.addedItemsText.pop(object_name)
        if data_type == "Characteristics":
            c_type = DataManager.loadMainData("characteristic", object_name, one=True)[0]
            if c_type == "dynamic":#Delete charact stats
                self.goals_dict[self.current_goal_id].goal_data[12] = "|".join([item for item in self.goals_dict[self.current_goal_id].goal_data[12].split("|") if item.split(":")[0] != object_name])
        self.setSaveEnabled()

    def skill_or_charact_changed(self, line_edit, list_widget, name):
        list_widget.addedItemsText[name] = line_edit.text()
        self.setSaveEnabled()

    def goal_settings(self):
        self.dialog = QDialog()
        self.dialog.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.dialog.setModal(True)

        id_label = QLabel("Set goal id:")
        id_edit = QLineEdit(self.current_goal_id)
        progress_calc_label = QLabel("How to calculate goal progress:")

        cc = self.goals_dict[self.current_goal_id].goal_data[11]
        progress_calc_mode = "Hours"
        dynamic_ccs = []

        if cc:
            calc_mode = self.goals_dict[self.current_goal_id].goal_data[10]
            if calc_mode:
                progress_calc_mode = calc_mode.split(":")[1]
            else:
                self.goals_dict[self.current_goal_id].goal_data[10] = "0:" + progress_calc_mode
            ccs = [item.split(":")[0] for item in cc.split(",")]
            
            for cc in ccs:
                charact = DataManager.loadMainData("characteristic", cc, one=True)
                if charact[0] == "dynamic": 
                    dynamic_ccs.append(cc) 

        self.old_progress_calc_mode = progress_calc_mode

        calc_combo = QComboBox()
        calc_combo.addItems(["Hours"] + dynamic_ccs)
        calc_combo.setCurrentText(progress_calc_mode)

        ok_button = QPushButton("Ok")
        ok_button.clicked.connect(lambda: self.save_goal_settings(id_edit, calc_combo))
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(lambda: self.dialog.close())

        grid = QGridLayout()
        grid.addWidget(id_label, 0, 0)
        grid.addWidget(id_edit, 0, 1)
        grid.addWidget(progress_calc_label, 1, 0)
        grid.addWidget(calc_combo, 1, 1)
        grid.addWidget(ok_button, 2, 0)
        grid.addWidget(cancel_button, 2, 1)
        self.dialog.setLayout(grid)
        self.dialog.show()

    def save_goal_settings(self, id_edit, calc_combo):
        self.old_goal_id = self.current_goal_id
        new_id = id_edit.text()
        calc_mode = calc_combo.currentText()
        if calc_mode != self.old_progress_calc_mode:
            self.goals_dict[self.current_goal_id].goal_data[10] = DataManager.recalculateProgress(self.current_goal_id, calc_mode, self.goals_dict[self.current_goal_id].goal_data[13], returning=True)
            self.setSaveEnabled()

        if new_id != self.current_goal_id:
            DataManager.updateMainData("goal_id", [new_id, self.current_goal_id])
            goal = self.goals_dict.pop(self.current_goal_id)
            self.goals_dict[new_id] = goal
            self.id_list[self.id_list.index(self.current_goal_id)] = new_id
            self.current_goal_id = new_id
            self.setSaveEnabled()
        self.dialog.close()

    def update_goal_indicator(self, text):
        self.d_diff_indicator.updateColor(text)

    def display_goal(self, current_item, previous):
        if self.areChangesMade:
            c_i = self.goal_tree_list_widget.itemWidget(current_item).goal_id
            question = QMessageBox.question(self, "Unsaved changes", "Some changes are made. Do you want to save them?")
            if question == QMessageBox.StandardButton.Yes:
                self.save_goal(previous)
            else:
                self.setSaveEnabled(value=False)
            self.current_goal_id = c_i
        else:
            self.current_goal_id = self.goal_tree_list_widget.itemWidget(current_item).goal_id
        self.areChangesMade = False
        self.old_goal_id = self.current_goal_id
        if self.current_goal_id in self.goals_dict:
            self.goals_dict[self.current_goal_id].displayData()
        else:
            goal = wsobj.Goal(self.cell_list, self.list_widget_list, self.add_skill_or_charact, self.current_goal_id)
            self.goals_dict[self.current_goal_id] = goal
        if self.goals_dict[self.current_goal_id].goal_data[7] != "completed":
            self.complete_button.setEnabled(True)
        else:
            self.complete_button.setEnabled(False)

    def add_subgoal(self, parent_id):
        subgoal = wsobj.Goal(self.cell_list, self.list_widget_list, self.add_skill_or_charact)
        self.current_goal_id = self.getGoalID(parent_id)
        self.goals_dict[self.current_goal_id] = subgoal
        self.id_list.append(self.current_goal_id)
        self.goal_tree_list_widget.blockSignals(True)
        self.goal_tree_list_widget.setCurrentRow(-1)
        self.goal_tree_list_widget.blockSignals(False)

    def delete_goal(self, goal_id):
        isGroup = self.goals_dict[self.current_goal_id].goal_data[13]
        DataManager.deleteMainData("goal", goal_id, isGroup)
        DataManager.deleteMainData("statistics", goal_id, isGroup)
        DataManager.deleteMainData("skills_stats", goal_id, isGroup)
        if len(self.current_goal_id.split(".")) > 2 and not isGroup:
            self.recalculateValues()
        id_list = [item for item in self.id_list]
        for iD in id_list:
            if iD.startswith(goal_id + ".") or iD == goal_id:
                self.goals_dict.pop(iD, "")
                self.id_list.remove(iD)
        self.goal_list_update_req.emit()
        if not self.id_list:
            self.previous_window_req.emit()
        else:
            self.update_goal_tree()

    def setSaveEnabled(self, *args, value=True):
        self.save_button.setEnabled(value)
        self.areChangesMade = value
        if value:
            self.changesMade.emit()
            self.goal_list_update_req.emit()

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

    def complete_goal(self):
        if QMessageBox.question(self, "Goal completing", "Complete goal?") == QMessageBox.StandardButton.Yes:
            self.widget = ws.CompleteGoalWindow(self, self.current_goal_id)
            self.widget.completed.connect(self.update_window)

    def update_window(self):
        self.update_goal_tree()
        self.goals_dict[self.current_goal_id].loadData()
        self.goals_dict[self.current_goal_id].displayData()
        self.goal_list_update_req.emit()

    def save_goal(self, previous=None):
        #1 - name lineEdit, 2 - image list, 3 - note textEdit, 4 - limit_date_label, 5 - progress_label, 6 - state_label, 7 - isgroup, 8-12 - characts lineEdits
        goal_name = self.cell_list[1].text()
        characts = []
        image_list = self.cell_list[2].getImagesList()

        #Get custom characts values
        for i in range(7, 11):
            text = self.cell_list[i].text()
            if i == 7 and float(text) != 0.0:
                characts.append(self.cell_list[i].text())
            elif i != 7:
                characts.append(self.cell_list[i].text())

        note = self.cell_list[3].toPlainText()

        is_group = int(self.cell_list[6].isChecked())
        if len(self.current_goal_id.split(".")) > 2:
            is_showing_in_list = 0
        else:
            is_showing_in_list = 1

        used_skills = ""
        custom_characts = ""
        skills_list_wid = self.list_widget_list[2]
        skill_values = []

        skills = list(skills_list_wid.addedItemsText.keys())
        for skill in skills:
            skill_value = skills_list_wid.addedItemsText[skill]
            used_skills += f"{skill}:{skill_value},"
            skill_values.append(skill_value)

        skill_values = [float(item) for item in skill_values if item != ""]
        if len(skill_values) > 1 and sum(skill_values) == float(characts[0]):
            skills_valid = True
        elif len(skill_values) == 1 and sum(skill_values) <= float(characts[0]):
            skills_valid = True
        else:
            skills_valid = False

        used_skills = used_skills.rstrip(",")

        cc_list_widget = self.list_widget_list[1]
        full_cc_values = True

        for cc in cc_list_widget.addedItemsText.keys():
            c_value = cc_list_widget.addedItemsText[cc]
            if not c_value:
                full_cc_values = False
                c_value = 0
            custom_characts += f"{cc}:{c_value},"
        custom_characts = custom_characts.rstrip(",")

        if self.goals_dict[self.current_goal_id].goal_data[12]:
            cc_stats = self.goals_dict[self.current_goal_id].goal_data[12]
        else:
            cc_stats = ""

        goal_progress = self.goals_dict[self.current_goal_id].goal_data[10]
        if not goal_progress:
            goal_progress = "0:Hours"
        elif goal_progress.split(":")[1] != "Hours" and goal_progress.split(":")[1] not in cc_list_widget.addedItemsText:#Means the charact by which was calculating progress was deleted
            self.goals_dict[self.current_goal_id].goal_data[10] = DataManager.recalculateProgress(self.current_goal_id, "Hours", self.goals_dict[self.current_goal_id].goal_data[13], returning=True)
            goal_progress = self.goals_dict[self.current_goal_id].goal_data[10]

        if (goal_name and len(characts) == 4 and used_skills and full_cc_values and skills_valid) or (is_group and goal_name and len(characts) > 2):
            if self.goals_dict[self.current_goal_id].isGoalExists:
                if is_group:
                    if len(characts) < 4:#Валидность определяется по длине списка, поэтому вставить значение 0 изначально нельзя
                        characts.insert(0, 0)
                    goal_data = (self.current_goal_id, goal_name) + tuple(characts) + (used_skills, self.goals_dict[self.current_goal_id].goal_data[7], note, image_list, goal_progress, custom_characts, cc_stats, is_group, is_showing_in_list, self.old_goal_id)
                else:
                    goal_data = (self.current_goal_id, goal_name) + tuple(characts) + (used_skills, self.goals_dict[self.current_goal_id].goal_data[7], note, image_list, goal_progress, custom_characts, cc_stats, is_group, is_showing_in_list, self.old_goal_id)
                DataManager.updateMainData("goal", goal_data)
            else:
                if is_group:
                    if len(characts) < 4:
                        characts.insert(0, 0)
                    else:
                        characts[0] = 0
                    used_skills = ""
                    goal_data = (self.current_goal_id, goal_name) + tuple(characts) + (used_skills, "created", note, image_list, goal_progress, custom_characts, cc_stats, is_group, is_showing_in_list)
                else:
                    goal_data = (self.current_goal_id, goal_name) + tuple(characts) + (used_skills, "created", note, image_list, goal_progress, custom_characts, cc_stats, is_group, is_showing_in_list)
                DataManager.saveMainData("goal", goal_data)

                self.id_list.sort()
                goal_index = self.id_list.index(self.current_goal_id)
                if goal_index == 0:
                    isMain = True
                else:
                    isMain = False
                goal_tree_item = ws.GoalTreeItem(self.current_goal_id, goal_name, 0, 0, isMain, is_group, self.goals_dict[self.current_goal_id].goal_data[7])
                goal_tree_item.subgoalAdded.connect(self.add_subgoal)
                goal_tree_item.goalDeleted.connect(self.delete_goal)

                list_widget_item = QListWidgetItem()
                size_hint = goal_tree_item.sizeHint()
                list_widget_item.setSizeHint(QSize(size_hint.width(), size_hint.height() + 35))

                self.goal_tree_list_widget.insertItem(goal_index, list_widget_item)
                self.goal_tree_list_widget.setItemWidget(list_widget_item, goal_tree_item)
                self.goal_tree_list_widget.blockSignals(True)
                self.goal_tree_list_widget.setCurrentItem(list_widget_item)
                self.goal_tree_list_widget.blockSignals(False)
                self.complete_button.setEnabled(True)

            self.save_button.setEnabled(False)
            self.areChangesMade = False
            self.changesSaved.emit()
            self.goals_dict[self.current_goal_id].setData(list(goal_data[:15]))
            if len(self.current_goal_id.split(".")) > 2 and not is_group:
                self.recalculateValues()
            self.update_goal_tree()
        else:
            QMessageBox.warning(self, "Fill cells to save the goal", "Not all the required cells were filled or some data were entered incorrectly")

    def recalculateValues(self):
        layers = self.current_goal_id.split(".")

        while len(layers) > 2:
            DataManager.recalculateValues(layers)
            supergoal_id = ".".join(layers[:-1])
            if supergoal_id in self.goals_dict:
                self.goals_dict[supergoal_id].loadData()
            layers.pop(-1)

    def getGoalID(self, parent_id):
        depth = len(parent_id.split(".")) + 1
        
        ids = DataManager.loadMainData("get_goal_ids", parent_id)
        level_len = 0
        for iD in ids:
            idl = iD[0].split(".")
            if len(idl) == depth:
                level_len += 1
        return f"{parent_id}.{level_len + 1}"

    def saveData(self):
        if QMessageBox.question(self, "Unsaved changes", "Some changes are made. Do you want to save them?") == QMessageBox.StandardButton.Yes:
            self.save_goal()

class StatisticsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.traces = []
        self.graphs = {"Goals":[], "Skills":[], "standard":[]}
        self.standard_colors = {}
        self.from_date = ""
        self.to_date = ""

        self.fig = go.Figure()
        self.fig.update_layout(
        xaxis=dict(gridcolor='#444444', color='white', title='Dates', type='date'),
        yaxis=dict(title='Numeric', gridcolor='#444444', color='#FFFFFF', type='linear'),
        yaxis2=dict(title='Letteric', overlaying='y', gridcolor='#444444', color='#FFD300', type="category", categoryorder="category descending"),
        yaxis3=dict(title='%', overlaying='y', side='right', gridcolor='#444444', color='#00FFFF'),
        paper_bgcolor='black',
        plot_bgcolor='black',
        legend_font_color='white')

        self.stats_view = ws.PlotlyViewer(self.fig)
        self.stats_view.setFixedSize(1500, 825)
        graphs_label = QLabel("Graphs")
        graphs_label.setFont(QFont("Calibri", 24))
        self.graphs_list_widget = QListWidget()
        self.graphs_list_widget.itemClicked.connect(self.display_graph_stats)
        
        standard_graphs = DataManager.loadMainData("graphs")
        for graph in standard_graphs:
            self.add_graph(graph[0], None, "standard", graph[1])
            self.standard_colors[graph[0]] = graph[2]

        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Add graph...")

        self.graph_tree_widget = QTreeWidget()
        self.graph_tree_widget.setColumnCount(3)
        self.graph_tree_widget.setHeaderLabels(["", "Average per day", "Total"])
        self.graph_tree_widget.setFixedWidth(400)
        self.graph_tree_widget.setColumnWidth(1, 120)

        date_checkbox = QCheckBox()
        date_checkbox.stateChanged.connect(self.toggle_date_selection)
        
        from_label = QLabel("From:")
        to_label = QLabel("to")
        self.from_det = ws.DateEditTool()
        self.from_det.dateChanged.connect(self.changeFromDate)
        self.to_det = ws.DateEditTool()
        self.to_det.dateChanged.connect(self.changeToDate)
        self.toggle_date_selection(0)

        date_h_box = QHBoxLayout()
        date_h_box.addWidget(date_checkbox)
        date_h_box.addWidget(from_label)
        date_h_box.addWidget(self.from_det)
        date_h_box.addWidget(to_label)
        date_h_box.addWidget(self.to_det)
        date_h_box.addStretch()

        graphs_v_box = QVBoxLayout()
        graphs_v_box.addWidget(graphs_label)
        graphs_v_box.addWidget(self.graphs_list_widget)
        graphs_v_box.addSpacing(20)
        graphs_v_box.addWidget(self.line_edit)
        graphs_v_box.addStretch()

        gview_v_box = QVBoxLayout()
        gview_v_box.addWidget(self.stats_view, alignment=Qt.AlignmentFlag.AlignTop)
        gview_v_box.addWidget(self.graph_tree_widget, alignment=Qt.AlignmentFlag.AlignTop)
        gview_v_box.addLayout(date_h_box)

        main_h_box = QHBoxLayout()
        main_h_box.addLayout(graphs_v_box)
        main_h_box.addLayout(gview_v_box)

        self.setLayout(main_h_box)

        self.object_manager = ws.ObjectManager(self, self.line_edit, ["Goals", "Skills"])
        self.object_manager.selected.connect(self.add_graph)

    def toggle_date_selection(self, state):
        if state:
            self.from_det.setEnabled(True)
            self.to_det.setEnabled(True)
            self.from_date = self.from_det.text()
            self.to_date = self.to_det.text()
        else:
            self.from_det.setEnabled(False)
            self.to_det.setEnabled(False)
            self.from_date = ""
            self.to_date = ""
        self.display_graph_stats(self.graphs_list_widget.currentItem())

    def changeFromDate(self):
        self.from_date = self.from_det.text()
        self.display_graph_stats(self.graphs_list_widget.currentItem())

    def changeToDate(self):
        self.to_date = self.to_det.text()
        self.display_graph_stats(self.graphs_list_widget.currentItem())
        
    def display_graph_stats(self, item):
        self.graph_tree_widget.clear()
        if item:
            widget = self.graphs_list_widget.itemWidget(item)
            graph_name, graph_type, value_type, cc_stats = widget.getGraphData()
        
            self.graph_tree_widget.setHeaderLabels([graph_name, "Average per day", "Total"])
            if graph_type == "Goals":
                x, y = widget.get_vals_for_h()
                self.addItem("Hours", x, y)
                x = []
                y = []
                for name, xy in cc_stats.items():
                    for stat in xy:
                        x_val, y_val = stat.split(" ")
                        x.append(x_val)
                        y.append(float(y_val))
                    self.addItem(name, x, y)
            elif graph_type == "Skills":
                x, y = widget.get_skill_vals()
                self.addItem(graph_name, x, y)
            elif graph_type == "standard":
                if value_type != "Letteric":
                    x, y = widget.get_graph_vals()
                    if value_type == "Numeric" and graph_name == "Work time":
                        self.addItem(graph_name, x, y)
                    else:
                        self.addItem(graph_name, x, y, hideSumVal=True)
            self.graph_tree_widget.resizeColumnToContents(0)

    def addItem(self, name, x, y, hideSumVal=False):
        if self.from_date:
            year, m, d = [int(item) for item in self.from_date.split("-")]
            year1, m1, d1 = [int(item) for item in self.to_date.split("-")]
            minTime = dt.date(year, m, d)
            maxTime = dt.date(year1, m1, d1)

            y_vals = []
            for i in range(len(x)):
                year, m, d = [int(item) for item in x[i].split("-")]
                date = dt.date(year, m, d)
                if date >= minTime and date <= maxTime:
                    y_vals.append(y[i])
        else:
            y_vals = y

        if y_vals and any(y_vals):
            average = round(stats.mean(y_vals), 2)
            total = round(sum(y_vals), 2)
        else:
            average = 0
            total = 0

        if hideSumVal:
            item = QTreeWidgetItem([name, str(average), ""])
        else:
            item = QTreeWidgetItem([name, str(average), str(total)])
        item.setFont(1, QFont("Segoe UI", 10))
        item.setFont(2, QFont("Segoe UI", 10))
        self.graph_tree_widget.addTopLevelItem(item)

    def display_graph(self, graph_name, value_type, x, y, state, color):
        if state == 2:
            if value_type == "Numeric":
                yaxis = "y"
            elif value_type == "Letteric":
                yaxis = "y2"
            elif value_type == "%":
                yaxis = "y3"

            if color:
                self.fig.add_trace(go.Scatter(x=x, y=y, name=graph_name, yaxis=yaxis, line=dict(color=color)))
            else:
                self.fig.add_trace(go.Scatter(x=x, y=y, name=graph_name, yaxis=yaxis))
            self.traces.append(graph_name)
            self.stats_view.set_figure(self.fig)
        else:
            data = list(self.fig.data)
            data.pop(self.traces.index(graph_name))
            self.fig.data = data
            self.traces.remove(graph_name)
            self.stats_view.set_figure(self.fig)

    def add_graph(self, name, goal_id, obj_type, value_type=None):
        if not value_type:
            self.line_edit.clear()
        if (obj_type == "Goals" and goal_id not in self.graphs[obj_type]) or (obj_type != "Goals" and name not in self.graphs[obj_type]):
            if obj_type == "Goals":
                self.graphs[obj_type].append(goal_id)
            else:
                self.graphs[obj_type].append(name)
            widget = ws.GraphItem(name, obj_type, goal_id, value_type)
            widget.toggled.connect(self.display_graph)
            widget.removed.connect(self.remove_graph)
            item = QListWidgetItem()
            item.setSizeHint(widget.sizeHint())
            self.graphs_list_widget.addItem(item)
            self.graphs_list_widget.setItemWidget(item, widget)
            self.graphs_list_widget.setCurrentItem(item)

    def remove_graph(self, graph_widget):
        for i in range(self.graphs_list_widget.count()):
            item = self.graphs_list_widget.item(i)
            widget = self.graphs_list_widget.itemWidget(item)
            if widget.name == graph_widget.name and widget.graph_type == graph_widget.graph_type:
                self.graphs_list_widget.takeItem(i)
                if graph_widget.graph_type == "Goals":
                    self.graphs[widget.graph_type].remove(graph_widget.goal_id)
                else:
                    self.graphs[widget.graph_type].remove(graph_widget.name)
                if widget.show_checkbox.isChecked():
                    self.display_graph(graph_widget.name, None, None, None, 1, None)
                break

class Form(QDialog):
    def __init__(self):
        super().__init__()
        self.goals_with_dccs = []
        parser = configparser.ConfigParser()
        parser.read(r"Files\config\user.ini")
        self.FormFillingDate = parser.get("Data", "FormFillingDate")
        self.current_date = QDate().currentDate().toString("yyyy-MM-dd")
        if self.FormFillingDate != self.current_date:
            self.setModal(True)
            self.setWindowFlag(Qt.WindowType.FramelessWindowHint)

            today_records = DataManager.loadMainData("day_stats", self.current_date)
            self.records_dict = {}
            if today_records:
                for record in today_records:
                    start_time = ws.calculate_msecs(record[0])
                    end_time = ws.calculate_msecs(record[1])
                    record_time = end_time - start_time
                    if record[2] in self.records_dict:
                        self.records_dict[record[2]] += record_time
                    else:
                        self.records_dict[record[2]] = record_time

            today_label = QLabel("Today")
            today_label.setFont(QFont("Calibri", 24, 700))

            regex = QRegularExpression("[A-E]")
            validator = QRegularExpressionValidator(regex)
            m_state_label = QLabel("Mental state:")
        
            m_state_line_edit = QLineEdit()
            m_state_line_edit.setValidator(validator)
            p_state_label = QLabel("Psysical state:")
            p_state_line_edit = QLineEdit()
            p_state_line_edit.setValidator(validator)

            regex = QRegularExpression("[1-9]|10")
            validator = QRegularExpressionValidator(regex)
            day_rate_label = QLabel("Day rate:")
            day_rate_line_edit = QLineEdit()
            day_rate_line_edit.setValidator(validator)

            self.day_stats_edits = [m_state_line_edit, p_state_line_edit, day_rate_line_edit]

            change_label = QLabel("Change of dynamic characts")
            self.change_list_widget = QListWidget()
            self.day_note = QPlainTextEdit()
            self.day_note.setPlaceholderText("How was your day?")

            ok_button = QPushButton("OK")
            ok_button.clicked.connect(self.save_day_data)

            self.line_edit_dict = {}
            self.goal_ccs_dict = {}
        
            for task in self.records_dict:
                if len(task.split(".")) > 1:
                    self.add_goal_item(task)

            self.day_plan_view = ws.WeekPlanView(QDate().currentDate(), False)
            self.day_plan_view.changesMade.connect(self.check_plan)

            self.time_label = QLabel()
            self.time_label.setFont(QFont("Calibri", 14))
            self.check_plan()

            grid = QGridLayout()
            grid.addWidget(m_state_label, 0, 0)
            grid.addWidget(m_state_line_edit, 0, 1)
            grid.addWidget(p_state_label, 1, 0)
            grid.addWidget(p_state_line_edit, 1, 1)
            grid.addWidget(day_rate_label, 2, 0)
            grid.addWidget(day_rate_line_edit, 2, 1)

            v_box = QVBoxLayout()
            v_box.addWidget(today_label)
            v_box.addLayout(grid)
            v_box.addWidget(self.change_list_widget)
            v_box.addWidget(self.day_note)
            v_box.addWidget(ok_button)

            plan_v_box = QVBoxLayout()
            plan_v_box.addWidget(self.day_plan_view)
            plan_v_box.addWidget(self.time_label)

            main_h_box = QHBoxLayout()
            main_h_box.addLayout(v_box)
            main_h_box.addLayout(plan_v_box)

            self.setLayout(main_h_box)
            self.show()
        else:
            QMessageBox.warning(self, "Form is already filled", "Form is already filled")

    def add_goal_item(self, task):
        if task not in self.goals_with_dccs:
            dynamic_ccs = []
            goal = list(DataManager.loadMainData("goal", task, one=True))
            goal_name = goal[1]
            ccs = goal[11]
            if ccs:
                ccs = ccs.split(",")
                dynamic_ccs = [item.split(":")[0] for item in ccs if DataManager.loadMainData("characteristic", item.split(":")[0], one=True)[0] == "dynamic"]
            if dynamic_ccs:
                widget = QWidget()
                h_box = QHBoxLayout()
                label = QLabel(goal_name)
                h_box.addWidget(label)
                for cc in dynamic_ccs:
                    charact_label = QLabel(cc + ":")
                    line_edit = QLineEdit()
                    line_edit.setFixedWidth(20)
                    if goal[0] in self.line_edit_dict:
                        self.line_edit_dict[goal[0]].append(line_edit)
                        self.goal_ccs_dict[goal[0]].append(cc)
                    else:
                        self.line_edit_dict[goal[0]] = [line_edit]
                        self.goal_ccs_dict[goal[0]] = [cc]
                    h_box.addWidget(charact_label)
                    h_box.addWidget(line_edit)
                
                h_box.addStretch()
                widget.setLayout(h_box)
                item = QListWidgetItem()
                item.setSizeHint(widget.sizeHint())
                self.change_list_widget.addItem(item)
                self.change_list_widget.setItemWidget(item, widget)
                self.goals_with_dccs.append(task)

    def save_day_data(self):
        day_stats = [item.text() for item in self.day_stats_edits if item.text() != ""]

        if len(day_stats) == 3:
            DataManager.deleteMainData("stats", self.current_date)
            DataManager.deleteMainData("plans", self.current_date)
            self.records_dict = {}
            for item in self.day_plan_view.blocks_dict[0]:
                if item.task_id in self.records_dict:
                    self.records_dict[item.task_id] += ws.calculate_msecs(item.end_time) - ws.calculate_msecs(item.start_time)
                else:
                    self.records_dict[item.task_id] = ws.calculate_msecs(item.end_time) - ws.calculate_msecs(item.start_time)
                busy = ws.getBusyValue(item.task_id)
                DataManager.saveMainData("statistics", [item.start_time, item.end_time, item.task_id, self.current_date, busy])

            DataManager.saveMainData("day", [self.current_date] + day_stats + [float(self.time_label.text().replace("Time: ", ""))])
            for goal_id in self.records_dict.keys():
                if len(goal_id.split(".")) > 1:
                    needs_calc = False
                    cc_stats_str = ""
                    goal_data = list(DataManager.loadMainData("goal", goal_id, one=True))

                    value, p_charact = goal_data[10].split(":")
                    goal_cc_stats = goal_data[12]
                    value = float(value)

                    if p_charact == "Hours":
                        value += self.records_dict[goal_id] / 3600000

                    if goal_id in self.line_edit_dict:
                        for edit in self.line_edit_dict[goal_id]:
                            if edit.text():
                                needs_calc = True

                        if needs_calc:
                            for stat in goal_cc_stats.split("|"):
                                cc_name, stats = stat.split(":")

                                if cc_name in self.goal_ccs_dict[goal_id]:
                                    index = self.goal_ccs_dict[goal_id].index(cc_name)
                                    cc_stats_str += f"{cc_name}:{stats},{self.current_date} {self.line_edit_dict[goal_id][index].text()}|"
                                else:
                                    cc_stats_str += stat
                                if cc_name == p_charact:
                                    value += float(self.line_edit_dict[goal_id][index].text())
                            cc_stats_str = cc_stats_str.rstrip("|")
                        else:
                            cc_stats_str = goal_cc_stats

                    DataManager.updateMainData("goal_characts", [cc_stats_str, f"{value}:{p_charact}", "completing", goal_id])
                    if len(goal_id.split(".")) > 2:
                        layers = goal_id.split(".")
                        while len(layers) > 2:
                            DataManager.recalculateValues(layers)
                            supergoal_id = ".".join(layers[:-1])
                            layers.pop(-1)

            for task_id in self.records_dict:
                DataManager.addSkillStat(task_id, self.records_dict[task_id] / 3600000, self.current_date)

            DataManager.recalculateSkills()
            parser = configparser.ConfigParser()
            parser.read(user_config_path)
            diary_path = parser.get("User", "diary_path")
            parser.set("Data", "FormFillingDate", self.current_date)

            if self.day_note.toPlainText():
                ok = True
                doc = None
                while not doc and ok:
                    if not diary_path:
                        diary_path, _ = QFileDialog.getOpenFileName(self, "Select diary to save notes", filter="Text Files(*.txt *.docx)")
                        if diary_path:
                            parser.set("User", "diary_path", diary_path)
                    if diary_path:
                        file_format = os.path.splitext(diary_path)[1]
                        if file_format == ".txt":
                            with open(diary_path, "a") as diary:
                                diary.write(self.current_date + "\n" + self.day_note.toPlainText() + "\n")
                            ok = False
                        elif file_format == ".docx":
                            try:
                                doc = docx.Document(diary_path)
                            except Exception:
                                if not QMessageBox.question(self, "Error", "File not exists. If you're sure that it exists try to add some text in it. Do you want to try again?") == QMessageBox.StandardButton.Yes:
                                    ok = False
                                else:
                                    diary_path = None
                            if doc:
                                text_lines = [self.current_date] + self.day_note.toPlainText().split("\n")
                                for line in text_lines:
                                    doc.add_paragraph(line)
                                doc.save(diary_path)

            with open(user_config_path, "w") as config_file:
                parser.write(config_file)
            self.close()
        else: 
            QMessageBox.warning(self, "Fill all cells to save the form", "Fill all cells to save the form")

    def check_plan(self):
        time = 0
        items = self.day_plan_view.scene.items()
        for item in items:
            if not isinstance(item, QGraphicsPixmapItem):
                if len(item.task_id.split(".")) > 1:
                    self.add_goal_item(item.task_id)
                if ws.getBusyValue(item.task_id):
                    time += ws.calculate_msecs(item.end_time) - ws.calculate_msecs(item.start_time) - item.gap_time
        time /= 3600000
        self.time_label.setText(f"Time: {time}")

class StatisticsEditor(QDialog):
    def __init__(self):
        super().__init__()
        self.setModal(True)
        self.setFixedHeight(300)
        self.setWindowTitle("Statistics editor")
        self.current_date = QDate().currentDate()
        label = QLabel("What to edit?")

        self.stacked_widget = QStackedWidget()

        self.edit_mode = QComboBox()
        self.edit_mode.addItems(["Goal custom characteristic statistics", "Day info", "load main statistics"])#"Day schedule"
        self.edit_mode.activated.connect(self.switch_tab)
        ok_button = QPushButton("Write")
        ok_button.clicked.connect(self.save_data)

        main_v_box = QVBoxLayout()
        main_v_box.addWidget(label, alignment=Qt.AlignmentFlag.AlignHCenter)
        main_v_box.addWidget(self.edit_mode, alignment=Qt.AlignmentFlag.AlignHCenter)
        main_v_box.addWidget(self.stacked_widget)
        main_v_box.addWidget(ok_button)

        self.goal_id = ""
        self.stats = []

        #First tab
        self.characts_list = ws.SkillCharactListWidget()
        label = QLabel("Form: date value, date value")
        goal_edit = QLineEdit()
        goal_edit.setPlaceholderText("Select a goal")
        goal_edit.textEdited.connect(self.clear_list)

        v_box1 = QVBoxLayout()
        v_box1.addWidget(label)
        v_box1.addWidget(goal_edit)
        v_box1.addWidget(self.characts_list)

        #Second tab
        self.date_edit = QDateEdit(self.current_date)
        self.date_edit.dateChanged.connect(self.load_day)

        regex = QRegularExpression("[A-E]")
        validator = QRegularExpressionValidator(regex)
        m_state_label = QLabel("Mental state:")
        
        m_state_line_edit = QLineEdit()
        m_state_line_edit.setValidator(validator)
        p_state_label = QLabel("Psysical state:")
        p_state_line_edit = QLineEdit()
        p_state_line_edit.setValidator(validator)

        regex = QRegularExpression("[1-9]|10")
        day_rate_label = QLabel("Day rate:")
        day_rate_line_edit = QLineEdit()
        day_rate_line_edit.setValidator(QRegularExpressionValidator(regex))

        work_time_edit = QLineEdit()
        work_time_label = QLabel("Work time:")
        regex = QRegularExpression("[0-9][0-9]*\.?[0-9]+$")
        work_time_edit.setValidator(QRegularExpressionValidator(regex))

        from_csv = QPushButton("from .csv in form: ms, ps, dr, wt, date")
        from_csv.clicked.connect(self.load_stats)

        grid2 = QGridLayout()
        grid2.addWidget(self.date_edit, 0, 0)
        grid2.addWidget(m_state_label, 1, 0)
        grid2.addWidget(m_state_line_edit, 1, 1)
        grid2.addWidget(p_state_label, 2, 0)
        grid2.addWidget(p_state_line_edit, 2, 1)
        grid2.addWidget(day_rate_label, 3, 0)
        grid2.addWidget(day_rate_line_edit, 3, 1)
        grid2.addWidget(work_time_label, 4, 0)
        grid2.addWidget(work_time_edit, 4, 1)
        grid2.addWidget(from_csv, 5, 0, 1, 0)
        self.second_tab_cells = [m_state_line_edit, p_state_line_edit, day_rate_line_edit, work_time_edit]

        self.load_day(self.current_date)

        #Third tab
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["start, end, task_ID, date", "time, task_ID, date"])
        load_button = QPushButton("load from .csv file")
        load_button.clicked.connect(self.load_stats)
        v_box3 = QVBoxLayout()
        v_box3.addWidget(self.mode_combo)
        v_box3.addWidget(load_button)
        v_box3.addStretch()

        layouts = [grid2, v_box3]

        cont = QWidget()
        cont.setLayout(v_box1)
        self.object_manager = ws.ObjectManager(cont, goal_edit, ["Goals"])
        self.object_manager.selected.connect(self.goal_selected)
        self.stacked_widget.addWidget(cont)
        
        for layout in layouts:
            cont = QWidget()
            cont.setLayout(layout)
            self.stacked_widget.addWidget(cont)
        
        self.setLayout(main_v_box)
        self.show()

    def switch_tab(self, i):
        self.stacked_widget.setCurrentIndex(i)
        self.stats = []

    def load_day(self, date):
        day = DataManager.loadMainData("day_data", date.toString("yyyy-MM-dd"), one=True)
        if day:
            for i in range(len(self.second_tab_cells)):
                d = day[i]
                if not d:
                    d = ""
                else: d = str(d)
                self.second_tab_cells[i].setText(d)
        else:
            for cell in self.second_tab_cells:
                cell.setText("")

    def clear_list(self):
        self.characts_list.clear()
        self.characts_list.addedItemsText = {}

    def load_stats(self):
        file_name, ok = QFileDialog.getOpenFileName(self, filter="CSV files (*.csv)")
        if ok and file_name:
            with open(file_name, "r") as file:
                file = csv.reader(file, delimiter=";")
                self.stats = [item for item in file]

    def goal_selected(self, text, iD):
        self.goal_id = iD
        self.characts_list.clear()
        stats = DataManager.loadMainData("goal_custom", self.goal_id, one=True)[0]
        if stats:
            stats_dict = {charact.split(":")[0]:charact.split(":")[1] for charact in stats.split("|")}
            for charact in stats_dict:
                widget = QWidget()
                charact_label = QLabel(charact + ":")
                line_edit = QLineEdit(stats_dict[charact])
                h_box = QHBoxLayout()
                h_box.addWidget(charact_label)
                h_box.addWidget(line_edit)
                widget.setLayout(h_box)

                item = QListWidgetItem()
                item.setSizeHint(widget.sizeHint())
                self.characts_list.addItem(item)
                self.characts_list.setItemWidget(item, widget)
                self.characts_list.addedItemsText[charact] = line_edit

    def save_data(self):
        try:
            success = None
            index = self.edit_mode.currentIndex()
            if index == 0 and self.goal_id:
                stats_str = ""
                for cell, edit in self.characts_list.addedItemsText.items():
                    stats_str += f"{cell}:{edit.text()}"
                success = DataManager.updateMainData("goal_characts_stats", [stats_str, self.goal_id])
                layers = self.goal_id.split(".")

                if len(layers) == 2:
                    goal = DataManager.loadMainData("goal", self.goal_id, one=True)
                    DataManager.recalculateProgress(self.goal_id, goal[10].split(":")[1])
                else:
                    while len(layers) > 2:
                        DataManager.recalculateValues(layers)
                        supergoal_id = ".".join(layers[:-1])
                        layers.pop(-1)

            if index == 1:
                if self.stats:
                    for day_stats in self.stats:
                        if len(day_stats) == 5:
                            if any(day_stats):
                                success = DataManager.saveMainData("day_data", day_stats)
                        else:
                            success = False
                else:
                    isDataEntered = True
                    for edit in self.second_tab_cells:
                        if not edit.text():
                            isDataEntered = False
                    if isDataEntered:
                        success = DataManager.saveMainData("day_data", [item.text() for item in self.second_tab_cells] + [self.date_edit.date().toString("yyyy-MM-dd")])
                    else:
                        QMessageBox.warning(self, "Not all the cells are filled", "Fill all the cells to save data")

            if index == 2 and self.stats:
                task_id_list = []
                mode = self.mode_combo.currentIndex()
                if mode == 0:
                    for day_stat in self.stats:
                        if len(day_stat) == 4:
                            if any(day_stat):
                                task_id_list.append(day_stat[2])
                                DataManager.addSkillStat(day_stat[2], (ws.calculate_msecs(day_stat[1]) - ws.calculate_msecs(day_stat[0])) / 3600000, day_stat[3])
                                day_stat.append(1)#busy value
                                success = DataManager.saveMainData("statistics", day_stat)
                        else:
                            success = False
                else:
                    time_dict = {}
                    for day_stat in self.stats:
                        if len(day_stat) == 3:
                            if any(day_stat):
                                date = day_stat[2]
                                if date in time_dict:
                                    start_time = time_dict[date]
                                else:
                                    start_time = "0:00:00"

                                task_id_list.append(day_stat[1])
                                end_time = ws.to_str(int(ws.calculate_msecs(start_time) + (float(day_stat[0]) * 3600000)))
                                time_dict[date] = end_time
                                DataManager.addSkillStat(day_stat[1], float(day_stat[0]), date)
                                success = DataManager.saveMainData("statistics", [start_time, end_time, day_stat[1], date, 1])
                        else:
                            success = False
                task_id_list = list(set(task_id_list))

                #Recalculate progress of goals
                for task_id in task_id_list:
                    if len(task_id.split(".")) > 1: #determinating if task_id is goal_id or not
                        goal_data = DataManager.loadMainData("goal", task_id, one=True)
                        DataManager.recalculateProgress(task_id, goal_data[10].split(":")[1], goal_data[13])
                        DataManager.updateMainData("goal_state", ["completing", task_id])

                        if len(task_id.split(".")) > 2:
                            layers = task_id.split(".")
                            while len(layers) > 2:
                                goal_id = ".".join(layers[:-1])
                                goal_data = DataManager.loadMainData("goal", goal_id, one=True)
                                DataManager.updateMainData("goal_state", ["completing", task_id])
                                DataManager.recalculateProgress(goal_id, goal_data[10].split(":")[1], goal_data[13])
                                layers.pop(-1)

                DataManager.recalculateSkills()
                if QMessageBox.question(self, "Question", "Is it necessary to recalculate days work time?") == QMessageBox.StandardButton.Yes:
                    DataManager.recalculateDaysWorkTime()
            if success == True:
                QMessageBox.information(self, "Data has been written", "Data has been written")
            elif success == False:
                QMessageBox.warning(self, "An error occured", "Data has not been written")
        except Exception as error:
            QMessageBox.critical(self, "An error occured", f"Error: {error}")

class Plans(QWidget):
    changesSaved = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.date_edit_tool = ws.DateEditTool(False)
        self.date_edit_tool.dateChanged.connect(self.change_current_date)
        self.current_date = dt.date.today()
        
        self.months = ["January","February","March","April","May","June","July","August","September","October","November","December"]
        self.current_date = self.current_date - dt.timedelta(days=self.current_date.weekday())
        end_of_week = self.current_date + dt.timedelta(days=6)
        self.date_label = QLabel(f"{self.current_date.day}-{end_of_week.day} {self.months[self.current_date.month - 1]} {self.current_date.year}")
        
        self.date_label.setFont(QFont("Calibri", 24, 700))
        next_week_button = QPushButton()
        next_week_button.setFixedSize(18, 34)
        next_week_button.setIconSize(QSize(18, 34))
        next_week_button.setObjectName("Tool")
        next_week_button.setIcon(QIcon(i_dir + r"\next week.png"))
        next_week_button.clicked.connect(self.next_week)
        next_week_button.setShortcut(Qt.Key.Key_Right)
        prev_week_button = QPushButton()
        prev_week_button.setFixedSize(18, 34)
        prev_week_button.setIconSize(QSize(18, 34))
        prev_week_button.setObjectName("Tool")
        prev_week_button.setIcon(QIcon(i_dir + r"\prev week.png"))
        prev_week_button.setShortcut(Qt.Key.Key_Left)
        prev_week_button.clicked.connect(self.prev_week)

        week_day = QDate(self.current_date.year, self.current_date.month, self.current_date.day)
        self.week_plan_view = ws.WeekPlanView(week_day)
        self.week_plan_view.switch_week_req.connect(self.move_item_to_week)

        self.day_labels = []
        self.time_labels = []
        days_h_box = QHBoxLayout()
        days_h_box.addSpacing(115)
        time_h_box = QHBoxLayout()

        recalc_time_button = QPushButton()
        recalc_time_button.setShortcut("Ctrl+R")
        recalc_time_button.setIcon(QIcon(i_dir + r"\recurring_on.png"))
        recalc_time_button.setObjectName("Tool")
        recalc_time_button.setFixedSize(17, 17)
        recalc_time_button.clicked.connect(self.recalculate_time)
        time_h_box.addSpacing(50)
        time_h_box.addWidget(recalc_time_button)
        time_h_box.addSpacing(40)
        
        for n in range(7):
            label = QLabel(f"{self.months[week_day.month() - 1]} {week_day.day()}")
            label.setFont(QFont("Calibri", 20))
            time_label = QLabel("0 hours")
            time_label.setFont(QFont("Calibri", 18))
            week_day = week_day.addDays(1)
            self.day_labels.append(label)
            days_h_box.addWidget(label, alignment=Qt.AlignmentFlag.AlignHCenter)
            self.time_labels.append(time_label)
            time_h_box.addWidget(time_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        save_button = QPushButton()
        save_button.setIcon(QIcon(i_dir + r"\Tasks.png"))
        save_button.setStyleSheet("QPushButton{border: 1px solid #FFD300; background-color: #000000} QPushButton::pressed{border: 1px solid #FFD300; background-color: #7F6900}")
        save_button.setFixedWidth(75)
        save_button.setShortcut("Ctrl+S")
        save_button.clicked.connect(self.save_plan)

        header_h_box = QHBoxLayout()
        header_h_box.addWidget(self.date_label)
        header_h_box.addWidget(prev_week_button)
        header_h_box.addWidget(next_week_button)
        header_h_box.addWidget(self.date_edit_tool)
        header_h_box.addWidget(save_button)
        header_h_box.addStretch()

        main_v_box = QVBoxLayout()
        main_v_box.addLayout(header_h_box)
        main_v_box.addLayout(days_h_box)
        main_v_box.addWidget(self.week_plan_view)
        main_v_box.addLayout(time_h_box)
        main_v_box.addStretch()
        main_v_box.setContentsMargins(0, 0, 0, 0)
        self.recalculate_time()
        self.setLayout(main_v_box)

    def recalculate_time(self):
        blocks_dict = self.week_plan_view.blocks_dict
        for i in range(7):
            time = 0
            for item in blocks_dict[i]:
                if ws.getBusyValue(item.task_id):
                    time += (ws.calculate_msecs(item.end_time) - ws.calculate_msecs(item.start_time)) / 3600000
            self.time_labels[i].setText(str(round(time, 2)) + " hours")

    def move_item_to_week(self, mode, items):
        self.save_plan(exceptItems=items)
        if mode == "previous":
            self.current_date = self.current_date - dt.timedelta(weeks=1)
        else:
            self.current_date = self.current_date + dt.timedelta(weeks=1)
        self.update_plan(items)

    def next_week(self):
        self.current_date = self.current_date + dt.timedelta(weeks=1)
        self.update_plan()

    def prev_week(self):
        self.current_date = self.current_date - dt.timedelta(weeks=1)
        self.update_plan()

    def change_current_date(self):
        date = self.date_edit_tool.date
        new_date = dt.date(date.year(), date.month(), date.day())
        if new_date.weekday != 0:
            new_date = new_date - dt.timedelta(days=new_date.weekday())
        self.current_date = new_date
        self.update_plan()
        
    def update_plan(self, exceptItems=[]):
        self.week_plan_view.changeWeek(QDate(self.current_date.year, self.current_date.month, self.current_date.day), exceptItems)
        self.update_labels()
        
    def update_labels(self):
        self.recalculate_time()
        end_of_week = self.current_date + dt.timedelta(days=6)
        current_month_name = self.months[self.current_date.month - 1]
        self.date_label.setText(f"{self.current_date.day}-{end_of_week.day} {current_month_name} {self.current_date.year}")

        week_day = QDate(self.current_date.year, self.current_date.month, self.current_date.day)
        for label in self.day_labels:
            label.setText(f"{self.months[week_day.month() - 1]} {week_day.day()}")
            week_day = week_day.addDays(1)

    def save_plan(self, *args, exceptItems=[]):
        blocks_dict = self.week_plan_view.blocks_dict
        for i in blocks_dict:
            day = self.current_date + dt.timedelta(days=i)
            DataManager.deleteMainData("Plans", day.strftime("%Y-%m-%d"))
            for block in blocks_dict[i]:
                if block.task_id and block not in exceptItems:
                    busy = ws.getBusyValue(block.task_id)
                    DataManager.saveMainData("Plans", [block.start_time, block.end_time, block.task_id, day.strftime("%Y-%m-%d"), busy])
        if not exceptItems:
            self.changesSaved.emit()

    def saveData(self):
        if QMessageBox.question(self, "Unsaved changes", "Some changes were made. Save changes?") == QMessageBox.StandardButton.Yes:
            self.save_plan()

class PhrasesEditor(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Edit phrases and authors")
        self.setMinimumHeight(350)
        label = QLabel("Edit phrases and authors")
        label.setFont(QFont("Calibri", 20))
        edit_authors_button = QPushButton()
        edit_authors_button.setFixedSize(20, 20)
        edit_authors_button.setIcon(QIcon(i_dir + r"\add icon black"))
        edit_authors_button.clicked.connect(self.edit_authors)
        self.date_checkbox = QCheckBox()
        self.date_checkbox.toggled.connect(self.toggle_date_edit)
        self.date_edit = ws.DateEditTool()
        self.toggle_date_edit(False)
        self.author_edit = QLineEdit()
        self.author_edit.setFixedWidth(100)
        self.phrase_edit = QLineEdit()
        self.phrase_edit.setFixedWidth(200)
        add_phrase_button = QPushButton()
        add_phrase_button.setIcon(QIcon(i_dir + r"\Arrow Right.png"))
        add_phrase_button.setFixedSize(20, 20)
        add_phrase_button.clicked.connect(self.add_phrase)
        delete_button = QPushButton("Delete phrase")
        delete_button.clicked.connect(self.delete_phrase)
        ok_button = QPushButton("OK")
        ok_button.setFixedWidth(20)
        ok_button.clicked.connect(self.close)

        parser = configparser.ConfigParser()
        parser.read(user_config_path)
        self.last_showed_phrase = parser.get("Data", "last_showed_phrase")

        h_box = QHBoxLayout()
        h_box.addWidget(edit_authors_button)
        h_box.addWidget(self.date_checkbox)
        h_box.addWidget(self.date_edit)
        h_box.addWidget(self.author_edit)
        h_box.addWidget(self.phrase_edit)
        h_box.addWidget(add_phrase_button)

        v_box = QVBoxLayout()
        v_box.addWidget(label, alignment=Qt.AlignmentFlag.AlignHCenter)
        v_box.addSpacing(20)
        v_box.addLayout(h_box)
        v_box.addStretch()
        v_box.addWidget(delete_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        v_box.addWidget(ok_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.setLayout(v_box)
        self.show()
        self.authors_om = ws.ObjectManager(self, self.author_edit, ["Authors"])
        self.phrases_om = ws.ObjectManager(self, self.phrase_edit, ["Phrases"])
        self.phrases_om.selected.connect(self.phrase_selected)

    def edit_authors(self):
        self.dialog1 = QDialog()
        self.dialog1.setModal(True)
        self.dialog1.setWindowTitle("Edit authors")
        self.author_image = ws.AddImageLabel(ring=True)
        self.name_edit = QLineEdit()
        self.dialog1.setFixedSize(200, 250)
        delete_button = QPushButton("Delete author")
        delete_button.clicked.connect(self.delete_author)
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.save_author)
        v_box = QVBoxLayout()
        v_box.addWidget(self.author_image, alignment=Qt.AlignmentFlag.AlignHCenter)
        v_box.addWidget(self.name_edit)
        v_box.addStretch()
        v_box.addWidget(delete_button)
        v_box.addWidget(ok_button)
        self.dialog1.setLayout(v_box)
        self.dialog1.show()
        self.authors_om1 = ws.ObjectManager(self.dialog1, self.name_edit, ["Authors"])
        self.authors_om1.selected.connect(self.show_author_image)
        self.authors_om1.h = 100

    def show_author_image(self, text, *args):
        image = DataManager.loadOtherData("author", text, one=True)[0]
        if image:
            self.author_image.setImage(image)

    def save_author(self):
        text = self.name_edit.text()
        metrics = QFontMetrics(QFont("Calibri", 20, 700))
        if metrics.horizontalAdvance(text) < 311 and text:
            if self.authors_om1.isSelected:
                DataManager.updateOtherData("author", self.author_image.image_path, text)
            else:
                DataManager.saveOtherData("author", text, self.author_image.image_path)
            self.dialog1.close()
            self.authors_om.load_data()
        else:
            QMessageBox.warning(self, "Warning", "Author's name is too long or name is not entered")

    def delete_author(self):
        if self.authors_om1.isSelected and QMessageBox.question(self.dialog1, "Delete author", "Are you sure to delete this author?") == QMessageBox.StandardButton.Yes:
            DataManager.deleteOtherData("author", self.name_edit.text())
        self.dialog1.close()
        self.phrases_om.load_data()
        self.authors_om.load_data()

    def toggle_date_edit(self, state):
        if state:
            self.date_edit.setEnabled(True)
        else:
            self.date_edit.setEnabled(False)

    def add_phrase(self):
        phrase = self.phrase_edit.text().rstrip()
        if phrase and self.author_edit.text() and self.authors_om.isSelected:
            if len(phrase) < 241:
                if self.date_checkbox.isChecked():
                    date = self.date_edit.text()
                else:
                    date = None
                DataManager.saveOtherData("phrase", date, phrase, self.author_edit.text())
                self.author_edit.clear()
                self.phrase_edit.clear()
                self.phrases_om.load_data()
            else:
                QMessageBox.warning(self, "Warning", "Phrase must be shorter than 240 characters")

    def delete_phrase(self):
        if self.phrase_edit.text() == self.last_showed_phrase:
            parser = configparser.ConfigParser()
            parser.read(user_config_path)
            parser.set("Data", "last_showed_phrase", "")
            parser.set("Data", "last_showed_phrase_date", "")
            with open(user_config_path, "w") as config_file:
                parser.write(config_file)
        if self.phrases_om.isSelected:
            DataManager.deleteOtherData("phrase", self.phrase_edit.text())
        self.author_edit.clear()
        self.phrase_edit.clear()
        self.phrases_om.load_data()

    def phrase_selected(self, text, goal_id, obj_type):
        self.author_edit.blockSignals(True)
        date = DataManager.loadOtherData("phrase date", text, one=True)
        if any(date):
            date = date[0]
            self.date_edit.setEnabled(True)
            self.date_edit.setText(date)
        else:
            self.date_edit.setEnabled(False)
        self.author_edit.setText(DataManager.loadOtherData("phrase author", text, one=True)[0])
        self.author_edit.blockSignals(False)

class Top12Tab(QWidget):
    def __init__(self):
        super().__init__()
        self.tree_widget = QTreeWidget()
        self.tree_widget.setFont(QFont("Calibri", 18))
        self.tree_widget.setHeaderLabels(["Number", "", "Name", "Time", "Date of completion", "ID"])
        self.tree_widget.setStyleSheet("QTreeWidget::item{height: 140px}")
        self.tree_widget.setIconSize(QSize(97, 97))
        self.tree_widget.setSortingEnabled(True)
        self.remove_act = QAction("Remove goal")
        self.remove_act.triggered.connect(self.remove_goal)
        self.font = QFont("Calibri", 18, 700)
        self.tree_widget.setColumnWidth(0, 75)
        self.tree_widget.setColumnWidth(1, 120)
        self.tree_widget.setColumnWidth(4, 200)
        for goal in DataManager.loadOtherData("top 12"):
            goal_info = DataManager.loadMainData("goal", goal[1], one=True)
            image_path = goal_info[9]
            if image_path:
                image_path = image_path.split(",")[0]
            goal_info = [goal[0], goal_info[1], goal_info[2], goal_info[4], goal[1]]
            self.add_item(goal_info, image_path)

        add_button = QPushButton()
        add_button.setIcon(QIcon(i_dir + "\Add icon.png"))
        add_button.setFixedSize(50, 50)
        add_button.setObjectName("Menu")
        add_button.clicked.connect(self.add_goal)
        
        h_box = QHBoxLayout()
        h_box.setContentsMargins(300, 85, 250, 85)
        h_box.addWidget(self.tree_widget)
        h_box.addWidget(add_button, alignment=Qt.AlignmentFlag.AlignBottom)#baseline
        self.setLayout(h_box)

    def add_item(self, goal_info, image_path, save=False):
        image = ws.getGoalImage(image_path, 100, goal_info[2])
        goal_info = list(map(str, goal_info))
        goal_info.insert(1, "")
        goal_item = QTreeWidgetItem(self.tree_widget, goal_info)
        goal_item.setFont(2, self.font)
        goal_item.setIcon(1, QIcon(image))
        goal_item.setSizeHint(1, QSize(100, 120))
        self.tree_widget.addTopLevelItem(goal_item)
        if save:
            DataManager.saveOtherData("top goal", goal_info[5])

    def add_goal(self):
        if self.tree_widget.topLevelItemCount() == 12:
            QMessageBox.warning(self, "The list fully filled", "The list has maximum amount of goals")
        else:
            self.dialog = QDialog()
            self.dialog.setModal(True)
            self.dialog.setMinimumHeight(150)
            self.dialog.setWindowTitle(f"Add top {self.tree_widget.topLevelItemCount() + 1} goal")
            self.goal_edit = QLineEdit()
            self.goal_edit.setPlaceholderText("Enter goal name")
            v_box = QVBoxLayout()
            v_box.addWidget(self.goal_edit)
            v_box.addStretch()
            self.dialog.setLayout(v_box)
            self.dialog.show()
            self.object_manager = ws.ObjectManager(self.dialog, self.goal_edit, ["Goals"])
            self.object_manager.h = 100
            self.object_manager.selected.connect(self.goal_selected)

    def goal_selected(self, text, goal_id, obj_type):
        goal = DataManager.loadMainData("goal", goal_id, one=True)
        new = True
        for i in range(self.tree_widget.topLevelItemCount()):
            item = self.tree_widget.topLevelItem(i)
            if item.text(5) == goal_id:
                new = False
        if new and goal[7] == "completed":
            self.add_item([self.tree_widget.topLevelItemCount() + 1, goal[1], goal[2], goal[4], goal[0]], goal[9].split(",")[0], True)
        else:
            QMessageBox.warning(self, "Warning", "The goal already added to the list or goal is incompleted")
        self.dialog.close()

    def contextMenuEvent(self, event):
        self.item = self.tree_widget.itemAt(self.tree_widget.mapFromGlobal(event.pos()))
        if isinstance(self.item, QTreeWidgetItem):
            self.menu = QMenu()
            self.menu.addAction(self.remove_act)
            self.menu.exec(event.pos())

    def remove_goal(self):
        self.tree_widget.takeTopLevelItem(self.tree_widget.indexOfTopLevelItem(self.item))
        DataManager.deleteOtherData("top goal", self.item.text(5))