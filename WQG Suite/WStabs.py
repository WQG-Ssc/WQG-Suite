from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QGridLayout, QPushButton, QMessageBox, QHBoxLayout, QVBoxLayout, QDialog, QListWidget, QListWidgetItem, QTreeWidget, QTreeWidgetItem, QGroupBox, QPlainTextEdit, QMenu, QInputDialog, QFileDialog, QDateEdit, QCalendarWidget, QRadioButton, QButtonGroup, QCheckBox, QComboBox
from PyQt6.QtCore import Qt, QPropertyAnimation, QTime, QRect, QSize, QRegularExpression, pyqtSignal
from PyQt6.QtGui import QIcon, QFont, QAction, QRegularExpressionValidator
import plotly.graph_objs as go
import WSwidgets as ws
import WSobjects as wsobj
import DataManager
i_dir = r"Files\icons"

class ProfileTab(QWidget):
    def __init__(self, user_image, user_info):
        super().__init__()
        user_info_box = ws.ProfileInfoBox(user_image, user_info)
        skills_label = QLabel("Skills")
        skills_label.setFont(QFont("Calibri", 30, 700))

        self.skills_tree_widget = QTreeWidget()
        self.skills_tree_widget.setColumnCount(2)
        self.skills_tree_widget.setHeaderHidden(True)
        self.skills_tree_widget.itemDoubleClicked.connect(self.skill_settings)

        skills_data = DataManager.loadMainData("skills")
        for skill in skills_data:
            tree_widget_item = QTreeWidgetItem(self.skills_tree_widget, skill)
            tree_widget_item.setFont(0, QFont('Calibri', 24))
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
            DataManager.saveMainData("skill", skill_name)
            item = QTreeWidgetItem(self.skills_tree_widget, [skill_name, "0"])
            item.setFont(0, QFont('Calibri', 24))
            self.skills_tree_widget.addTopLevelItem(item)
            self.skills_tree_widget.resizeColumnToContents(0)

    def skill_settings(self, item):
        self.dialog = QDialog()
        self.dialog.setModal(True)
        self.dialog.setFixedSize(450, 200)
        self.dialog.setWindowTitle("Skill settings")
        rename_button = QPushButton("Rename skill")
        rename_button.clicked.connect(self.rename_skill)

        delete_button = QPushButton("Delete skill")
        delete_button.clicked.connect(self.delete_skill)

        v_box = QVBoxLayout()
        v_box.addWidget(rename_button)
        v_box.addWidget(delete_button)
        self.dialog.setLayout(v_box)
        self.dialog.show()

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

class GoalsTab(QWidget):
    def __init__(self, branch):
        super().__init__()
        self.current_branch_id = branch

        self.tree_widget = QTreeWidget()
        self.tree_widget.setColumnWidth(0, 135)
        self.tree_widget.setIconSize(QSize(97, 97))
        self.tree_widget.setColumnCount(9)
        headers = ["", "Name", "Hours", "Benefit", "limit date", "Priority", "State", "ID"]
        self.tree_widget.setHeaderLabels(headers)
        self.tree_widget.setSortingEnabled(True)

        self.updateWidget()

        h_box = QHBoxLayout()
        h_box.setContentsMargins(300, 85, 250, 85)
        h_box.addWidget(self.tree_widget)
        
        self.add_button = QPushButton()
        self.add_button.setIcon(QIcon(i_dir + "\Add icon.png"))
        self.add_button.setFixedSize(50, 50)
        self.add_button.setObjectName("Menu")
        h_box.addWidget(self.add_button, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)

        self.setLayout(h_box)

    def updateWidget(self):
        self.tree_widget.clear()
        goals = DataManager.loadMainData("goals", self.current_branch_id)
        for i in range(len(goals)):
            goal_info = goals[i]
            if goal_info[10]:
                goal_info_str = [str(item) for item in goal_info[:10]]#ѕреобразуем все значени€ в строковой тип

                goal_item = QTreeWidgetItem(self.tree_widget, [""] + goal_info_str[:7])
                goal_item.setSizeHint(1, QSize(100, 120))
                goal_item.setFont(1, QFont("Calibri", 18, 700))
                for i in range(2, 9):#ѕотом последние значение будет получатс€ по кол-ву характеристик
                    goal_item.setFont(i, QFont("Calibri", 18))
                goal_item.setIcon(0, QIcon(ws.getGoalImage(goal_info[7].split(",")[0], goal_info[8].split(":")[0], goal_info[1]))) #“ак мы получаем первое изображение из списка путей, которое €вл€етс€ главным
                self.tree_widget.addTopLevelItem(goal_item)
        self.tree_widget.resizeColumnToContents(5)

class GoalTab(QWidget):
    changesMade = pyqtSignal()
    changesSaved = pyqtSignal()
    previous_window_req = pyqtSignal()
    goal_list_update_req = pyqtSignal()
    def __init__(self, branch_id, item=None):
        super().__init__()
        self.branch_id = str(branch_id)
        self.branch_name = DataManager.loadMainData("branch", branch_id)[0]
        self.item = item

        goal_characts = ["Time:", "Benefit:", "Limit date:", "Priority:"]
        goal_state = "creating"
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
        note_text_edit.setStyleSheet("color: white")
        note_text_edit.textChanged.connect(self.setSaveEnabled)

        goal_name_edit = QLineEdit()
        goal_name_edit.setPlaceholderText("Add name...")
        goal_name_edit.setFixedSize(300, 45)
        goal_name_edit.setFont(QFont('Calibri', 18))
        goal_name_edit.textEdited.connect(self.setSaveEnabled)

        branch_label = QLabel("Branch: " + self.branch_name)
        state_label = QLabel("State: " + goal_state)
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

        self.id_list = []
        if self.item:
            goal_id = self.item.text(7)
            goal_name = self.item.text(1)
            #ќтобразим дерево цели
            goal_tree = DataManager.getGoalTree(goal_id)
            for goal in goal_tree:
                self.id_list.append(goal[0])
                if goal[1] == goal_name:
                    isMain = True
                else:
                    isMain = False
                goal_tree_item = ws.GoalTreeItem(goal[0], goal[1], goal[3], goal[2].split(":")[0], isMain)
                goal_tree_item.subgoalAdded.connect(self.add_subgoal)
                goal_tree_item.goalDeleted.connect(self.delete_goal)

                list_widget_item = QListWidgetItem()
                size_hint = goal_tree_item.sizeHint()
                list_widget_item.setSizeHint(QSize(size_hint.width(), size_hint.height() + 35))
                self.goal_tree_list_widget.addItem(list_widget_item)
                self.goal_tree_list_widget.setItemWidget(list_widget_item, goal_tree_item)
        else:
            self.add_subgoal(self.branch_id)
            self.old_goal_id = self.current_goal_id

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

        self.setLayout(main_grid)

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
        self.charact_widgets = []
        charact_edit = QLineEdit()
        charact_edit.setPlaceholderText("Enter characteristic name")

        is_showing_checkbox = QCheckBox("Showing in goal list")
        charact_type_label = QLabel("Choose characteristic type:")
        
        static_rb = QRadioButton("static")
        dynamic_rb = QRadioButton("dynamic")
        self.charact_type_group = QButtonGroup()
        self.charact_type_group.addButton(static_rb)
        self.charact_type_group.addButton(dynamic_rb)
        self.charact_type_group.buttonClicked.connect(self.update_widget)

        value_type_label = QLabel("Choose value type:")
        quantitative_rb = QRadioButton("quantitative")
        self.scale_rb = QRadioButton("scale")

        self.value_type_group = QButtonGroup()
        self.value_type_group.addButton(quantitative_rb)
        self.value_type_group.addButton(self.scale_rb)
        self.value_type_group.buttonClicked.connect(self.update_widget)

        self.v_box = QVBoxLayout()
        self.v_box.addWidget(is_showing_checkbox)
        self.v_box.addWidget(charact_edit)
        self.v_box.addWidget(charact_type_label)
        self.v_box.addWidget(static_rb)
        self.v_box.addWidget(dynamic_rb)
        self.v_box.addWidget(value_type_label)
        self.v_box.addWidget(quantitative_rb)
        self.v_box.addWidget(self.scale_rb)
        self.v_box.addStretch()

        if object_manager.isSelected:
            charact_name = line_edit.text()
            charact_edit.setText(charact_name)
            charact_info = DataManager.loadMainData("characteristics", charact_name)

            charact_edit.setReadOnly(True)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(lambda: self.save_charact(charact_edit, line_edit, is_showing_checkbox, object_manager))
        ok_v_box = QVBoxLayout()
        ok_v_box.addWidget(ok_button)
        main_v_box = QVBoxLayout()
        main_v_box.addLayout(self.v_box)
        main_v_box.addLayout(ok_v_box)
        self.dialog1.setLayout(main_v_box)
        self.dialog1.show()

    def save_charact(self, charact_edit, line_edit, is_showing_cb, obj_manager):
        charact_name = charact_edit.text()
        charact_type = self.charact_type_group.checkedButton().text()
        value_type = self.value_type_group.checkedButton().text()
        is_showing = is_showing_cb.isChecked()
        if charact_name and charact_type and value_type:
            if value_type == "quantitative":
                value = self.min_val_edit.text() + " " + self.max_val_edit.text()
            else:
                value = self.scale_vals_edit.text()
            if obj_manager.isSelected:
                DataManager.updateMainData("Characteristics", [charact_type, value_type, value, is_showing, charact_name])
            else:
                DataManager.saveMainData("Characteristics", [charact_name, charact_type, value_type, value, is_showing])
                obj_manager.isSelected = True
            self.dialog1.close()
            obj_manager.load_data()
            line_edit.setText(charact_name)
        else:
            QMessageBox.warning(self.dialog1, "Failed to create a custom characteristic", "Not all the required information were entered")

    def update_widget(self, button):
        if self.charact_widgets:
            for wid in self.charact_widgets:
                self.v_box.removeWidget(wid)
                wid.deleteLater()

        if button.text() == "dynamic":
            self.value_type_group.setExclusive(False)
            self.scale_rb.setEnabled(False)
            self.value_type_group.setExclusive(True)
        elif button.text() == "static":
            self.value_type_group.setExclusive(False)
            self.scale_rb.setEnabled(True)
            self.value_type_group.setExclusive(True)

        if button.text() == "scale":
            self.scale_vals_edit = QLineEdit()
            self.scale_vals_edit.setPlaceholderText("Set scale values")
            self.charact_widgets = [self.scale_vals_edit]
            self.v_box.addWidget(self.scale_vals_edit)
        elif button.text() == "quantitative":
            self.max_val_edit = QLineEdit()
            self.max_val_edit.setPlaceholderText("Set max value")
            self.min_val_edit = QLineEdit()
            self.min_val_edit.setPlaceholderText("Set min value")
            self.charact_widgets = [self.max_val_edit, self.min_val_edit]
            self.v_box.addWidget(self.max_val_edit)
            self.v_box.addWidget(self.min_val_edit)

    def add_skill_or_charact(self, standard_mode=[], setting_mode=[]):#Standard mode: [data_type, line_edit, list_widget, object_manager]
        if setting_mode:
            object_name, object_value, list_widget, isGroup = setting_mode
        else:
            object_value = ""
            isGroup = self.goals_dict[self.current_goal_id].goal_data[13]
            data_type, line_edit, list_widget, object_manager = standard_mode
            object_name = line_edit.text()
        if setting_mode or object_manager.isSelected and object_name not in list_widget.addedItemsText:
            widget = ws.SkillCharactWidget(object_name, object_value)
            widget.value_edit.textEdited.connect(lambda: self.skill_or_charact_changed(widget.value_edit, list_widget, object_name))
            widget.delete_button.clicked.connect(lambda: self.remove_skill_or_charact(item, object_name, list_widget))
            if standard_mode:
                self.setSaveEnabled()
            if isGroup:
                widget.setReadOnly()

            item = QListWidgetItem()
            item.setSizeHint(widget.sizeHint())

            list_widget.addItem(item)
            list_widget.addedItemsText[object_name] = object_value
            list_widget.setItemWidget(item, widget)
            if standard_mode:
                self.dialog.close()
        else:
            data_type_name = data_type[0].lower() + data_type[1:-1]
            QMessageBox.warning(self, f"Invalid {data_type_name} name", f"Choose an existing {data_type_name} from the object manager box and make sure you haven't added this {data_type_name} already.")

    def remove_skill_or_charact(self, item, object_name, list_widget):
        list_widget.takeItem(list_widget.row(item))
        list_widget.addedItemsText.pop(object_name)
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
        showing_checkbox = QCheckBox("Showing in goal list")

        self.old_checkbox_state = (self.goals_dict[self.current_goal_id].goal_data[14])
        if self.old_checkbox_state == "":
            self.old_checkbox_state = True
        showing_checkbox.setChecked(self.old_checkbox_state)

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
                charact = DataManager.loadMainData("characteristic", cc)
                if charact[0] == "dynamic": 
                    dynamic_ccs.append(cc) 

        self.old_progress_calc_mode = progress_calc_mode

        calc_combo = QComboBox()
        calc_combo.addItems(["Hours"] + dynamic_ccs)
        calc_combo.setCurrentText(progress_calc_mode)

        ok_button = QPushButton("Ok")
        ok_button.clicked.connect(lambda: self.save_goal_settings(id_edit, calc_combo, showing_checkbox))
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(lambda: self.dialog.close())

        grid = QGridLayout()
        grid.addWidget(id_label, 0, 0)
        grid.addWidget(id_edit, 0, 1)
        grid.addWidget(progress_calc_label, 1, 0)
        grid.addWidget(calc_combo, 1, 1)
        grid.addWidget(showing_checkbox, 2, 0)
        grid.addWidget(ok_button, 3, 0)
        grid.addWidget(cancel_button, 3, 1)
        self.dialog.setLayout(grid)
        self.dialog.show()

    def save_goal_settings(self, id_edit, calc_combo, checkbox):
        self.old_goal_id = self.current_goal_id
        new_id = id_edit.text()
        calc_mode = calc_combo.currentText()
        new_state = checkbox.isChecked()
        if calc_mode != self.old_progress_calc_mode:
            self.goals_dict[self.current_goal_id].goal_data[10] = self.goals_dict[self.current_goal_id].goal_data[10].split(":")[0] + ":" + calc_mode
            self.setSaveEnabled()
            #Here needs to be the function which calculates progress
        if new_id != self.current_goal_id:
            goal = self.goals_dict.pop(self.current_goal_id)
            self.goals_dict[new_id] = goal
            self.id_list[self.id_list.index(self.current_goal_id)] = new_id
            self.current_goal_id = new_id
            self.setSaveEnabled()
        if new_state != self.old_checkbox_state:
            self.goals_dict[self.current_goal_id].goal_data[14] = new_state
            self.setSaveEnabled()
        self.dialog.close()

    def update_goal_indicator(self, text):
        self.d_diff_indicator.updateColor(text)

    def display_goal(self, current_item, previous):
        if self.areChangesMade:
            question = QMessageBox.question(self, "Unsaved changes", "Some changes are made. Do you want to save them?")
            if question == QMessageBox.StandardButton.Yes:
                self.save_goal(previous)
            else:
                self.setSaveEnabled(value=False)
        self.areChangesMade = False
        self.current_goal_id = self.goal_tree_list_widget.itemWidget(current_item).goal_id
        self.old_goal_id = self.current_goal_id
        if self.current_goal_id in self.goals_dict:
            self.goals_dict[self.current_goal_id].displayData()
        else:
            goal = wsobj.Goal(self.cell_list, self.list_widget_list, self.add_skill_or_charact, self.current_goal_id)
            goal.skillCharactChanged.connect(self.setSaveEnabled)
            self.goals_dict[self.current_goal_id] = goal

    def add_subgoal(self, parent_id):
        subgoal = wsobj.Goal(self.cell_list, self.list_widget_list, self.add_skill_or_charact)
        self.current_goal_id = self.getGoalID(parent_id)
        self.goals_dict[self.current_goal_id] = subgoal
        self.id_list.append(self.current_goal_id)

    def delete_goal(self, goal_id):
        DataManager.deleteMainData("goal", goal_id)
        self.id_list.remove(goal_id)
        self.goal_list_update_req.emit()
        if not self.id_list:
            self.goal_tree_list_widget.currentItemChanged.disconnect()
            self.previous_window_req.emit()
        self.goals_dict.pop(goal_id)
        self.goal_tree_list_widget.takeItem(self.goal_tree_list_widget.currentRow())

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

    def save_goal(self, previous=None):
        #1 - name lineEdit, 2 - image list, 3 - note textEdit, 4 - limit_date_label, 5 - progress_label, 6 - state_label, 7 - isgroup, 8-12 - characts lineEdits
        goal_name = self.cell_list[1].text()
        characts = []
        image_list = self.cell_list[2].getImagesList()

        for i in range(7, 11):
            text = self.cell_list[i].text()
            if text != "":
                characts.append(self.cell_list[i].text())

        note = self.cell_list[3].toPlainText()

        is_group = int(self.cell_list[6].isChecked())
        if self.goals_dict[self.current_goal_id].goal_data[14] != "":
            is_showing_in_list = int(self.goals_dict[self.current_goal_id].goal_data[14])
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

        skill_values = [int(item) for item in skill_values if item != ""]
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

        if (goal_name and len(characts) == 4 and used_skills and full_cc_values and skills_valid) or (is_group and goal_name and len(characts) > 2):
            if self.goals_dict[self.current_goal_id].isGoalExists:
                if is_group:
                    if len(characts) < 4:
                        characts.insert(0, 0)
                    goal_data = (self.current_goal_id, goal_name) + tuple(characts) + (used_skills, self.goals_dict[self.current_goal_id].goal_data[7], note, image_list, goal_progress, custom_characts, cc_stats, is_group, is_showing_in_list, self.old_goal_id)
                else:
                    goal_data = (self.current_goal_id, goal_name) + tuple(characts) + (used_skills, self.goals_dict[self.current_goal_id].goal_data[7], note, image_list, goal_progress, custom_characts, cc_stats, is_group, is_showing_in_list, self.old_goal_id)
                DataManager.updateMainData("goal", goal_data)
                if previous:
                    current_widget = self.goal_tree_list_widget.itemWidget(previous)
                else:
                    current_widget = self.goal_tree_list_widget.itemWidget(self.goal_tree_list_widget.currentItem())
                current_widget.updateWidget(self.current_goal_id, goal_name, float(goal_data[2]), goal_data[10].split(":")[0])
            else:
                if is_group:
                    if len(characts) < 4:
                        characts.insert(0, 0)
                    goal_data = (self.current_goal_id, goal_name) + tuple(characts) + (used_skills, "creating", note, image_list, goal_progress, custom_characts, cc_stats, is_group, is_showing_in_list)
                else:
                    goal_data = (self.current_goal_id, goal_name) + tuple(characts) + (used_skills, "created", note, image_list, goal_progress, custom_characts, cc_stats, is_group, is_showing_in_list)
                DataManager.saveMainData("goal", goal_data)

                self.id_list.sort()
                goal_index = self.id_list.index(self.current_goal_id)
                if goal_index == 0:
                    isMain = True
                else:
                    isMain = False
                goal_tree_item = ws.GoalTreeItem(self.current_goal_id, goal_name, float(goal_data[2]), 0, isMain)
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
            self.save_button.setEnabled(False)
            self.areChangesMade = False
            self.changesSaved.emit()
            self.goals_dict[self.current_goal_id].setData(list(goal_data[:15]))
            if len(self.current_goal_id.split(".")) > 2:
                super_goal = ".".join(self.current_goal_id.split(".")[:-1])
                if DataManager.loadMainData("check supergoal", super_goal):
                    self.recalculateValues()
        else:
            QMessageBox.warning(self, "Fill cells to save the goal", "Not all the required cells were filled or some data were entered incorrectly")

    def recalculateValues(self):
        time_charact = self.goals_dict[self.current_goal_id].goal_data[2]
        layers = self.current_goal_id.split(".")[:-1]
        dynamic_characts = {}
        update_custom = True #Whether it is necessary to try to update a custom charact of a supergoal
        ccs = self.goals_dict[self.current_goal_id].goal_data[11].split(",")
        if ccs != [""]:
            for cc in ccs:
                cc = cc.split(":")
                dynamic_characts[cc[0]] = cc[1]

        used_skills = self.goals_dict[self.current_goal_id].goal_data[6]
        if used_skills:
            used_skills = used_skills.split(",")

        while len(layers) > 1:
            layer = ".".join(layers)
            if DataManager.loadMainData("check supergoal", layer):
                if update_custom and dynamic_characts:
                    update_custom = DataManager.recalculateValues(layer, time_charact, used_skills, dynamic_characts)
                else:
                    DataManager.recalculateValues(layer, time_charact, used_skills)
                    if layer in self.goals_dict:
                        self.goals_dict[layer].loadData()
            layers.pop(-1)

    def getGoalID(self, parent_id):
        depth = len(parent_id.split(".")) + 1
        
        ids = DataManager.getGoalIDs(parent_id) 
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
        
        standard_graphs = DataManager.loadMainData("graphs")
        for graph in standard_graphs:
            self.add_graph(graph[0], None, "standard", graph[1])
            self.standard_colors[graph[0]] = graph[2]

        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Add graph...")

        calc_settings = QPushButton("Calculations settings")

        graphs_v_box = QVBoxLayout()
        graphs_v_box.addWidget(graphs_label)
        graphs_v_box.addWidget(self.graphs_list_widget)
        graphs_v_box.addSpacing(20)
        graphs_v_box.addWidget(self.line_edit)
        graphs_v_box.addStretch()

        main_h_box = QHBoxLayout()
        main_h_box.addLayout(graphs_v_box)
        main_h_box.addWidget(self.stats_view, alignment=Qt.AlignmentFlag.AlignTop)

        self.setLayout(main_h_box)

        self.object_manager = ws.ObjectManager(self, self.line_edit, ["Goals", "Skills", "Graphs"])
        self.object_manager.selected.connect(self.add_graph)

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