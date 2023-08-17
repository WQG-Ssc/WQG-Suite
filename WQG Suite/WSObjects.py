import DataManager
import WSwidgets as ws
from PyQt6.QtWidgets import QListWidgetItem, QPushButton, QLineEdit, QLabel, QHBoxLayout, QWidget
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QObject
from PyQt6.QtGui import QIcon

class Goal(QObject):
    skillCharactChanged = pyqtSignal()
    def __init__(self, cell_list, list_widget_list, goal_id=None):
        super().__init__()
        self.goal_id = goal_id
        self.cell_list = cell_list
        self.list_widget_list = list_widget_list
        self.loadData()
        self.displayData()

    def loadData(self):
        if self.goal_id:
            self.goal_data = DataManager.loadMainData("goal", self.goal_id)
        #ID, name, total_difficulty, time, benefit, limit_date, priority, used_skills (,), state, note, files (,), progress (,), custom_characteristics (,:)
        else:
            self.goal_data = ["", "", "", "", "", "", "", "", "", "", "", "", ""]
            
    def displayData(self):
        #cell_list: 1 - name lineEdit, 2 - image list, 3 - note textEdit, 4 - limit_date_label, 5 - progress_label, 6 - state_label, 7-11 - characts lineEdits
        #list_widget_list = [self.goal_tree_list_widget, characts_list_widget, skills_list_widget]

        goal_name = self.goal_data[1]
        images_list = self.goal_data[10].split(",")
        self.cell_list[0].setImage(images_list[0])
        self.cell_list[2].setImagesList(images_list)

        self.cell_list[1].setText(self.goal_data[1])
        self.cell_list[3].setPlainText(self.goal_data[9])
        self.cell_list[4].setText(self.goal_data[5])
        self.cell_list[5].setText("Progress: " + self.goal_data[11].split(",")[0])

        #ќтобразим значени€ стандартных характеристик
        characts_edits = self.cell_list[7:12]
        standard_characts_values = self.goal_data[2:7]
        for i in range(5):
            characts_edits[i].setText(str(standard_characts_values[i]))

        #ќтобразим значени€ пользовательских
        characts_list_widget = self.list_widget_list[1]
        
        custom_characts = self.goal_data[12]
        if custom_characts:
            custom_characts = custom_characts.split(",")
            for charact in custom_characts:
                charact = charact.split(":")#[charact_name, value]

                charact_widget = QWidget()
                h_box = QHBoxLayout()

                list_item = QListWidgetItem(characts_list_widget)

                label = QLabel(charact[0])
                remove_charact_button = QPushButton()
                line_edit = QLineEdit()
                remove_charact_button.setIcon(QIcon(r"Files\icons\remove.png"))
                remove_charact_button.setFixedSize(QSize(20, 20))
                remove_charact_button.setIconSize(QSize(20, 20))
                remove_charact_button.setObjectName("Tool")

                h_box.addWidget(label, alignment=Qt.AlignmentFlag.AlignLeft)
                h_box.addWidget(line_edit, alignment=Qt.AlignmentFlag.AlignRight)
                h_box.addWidget(remove_charact_button)
                h_box.addSpacing(20)
                charact_widget.setLayout(h_box)
                list_item.setSizeHint(charact_widget.sizeHint())
            
                characts_list_widget.addItem(list_item)
                characts_list_widget.setItemWidget(list_item, charact_widget)

        #for skill in used_skills:
        #    skill = skill.split(":")
        #    skill_widget = QWidget()
        #    skills_list_item = QListWidgetItem()
        #    label = QLabel(skill[0])
        #    p_line_edit = QLineEdit(skill[1])
        #    h_line_edit = QLineEdit()
        #    h_box = QHBoxLayout()
        #    h_box.addWidget(label, alignment=Qt.AlignmentFlag.AlignLeft)
        #    h_box.addWidget(p_line_edit, alignment=Qt.AlignmentFlag.AlignLeft)
        #    h_box.addWidget(h_line_edit, alignment=Qt.AlignmentFlag.AlignLeft)
        #    skills_list_item.setSizeHint(skills_list_widget.sizeHint())
        #    skills_list_widget.setItemWidget(skills_list_item, skills_list_widget)

    def setData(self, goal_data):
        self.goal_data = goal_data