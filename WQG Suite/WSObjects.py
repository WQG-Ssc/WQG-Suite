# -*- coding: cp1251 -*-
import DataManager
import WSwidgets as ws
from PyQt6.QtWidgets import QListWidgetItem, QPushButton, QLineEdit, QLabel, QHBoxLayout, QWidget
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QObject
from PyQt6.QtGui import QIcon

class Goal(QObject):
    skillCharactChanged = pyqtSignal()
    def __init__(self, cell_list, list_widget_list, add_skill_or_charact, goal_id=None):
        super().__init__()
        self.goal_id = goal_id
        self.cell_list = cell_list
        self.list_widget_list = list_widget_list
        self.add_skill_or_charact = add_skill_or_charact
        self.isGoalExists = False
        self.loadData()
        self.displayData()

    def loadData(self):
        if self.goal_id:
            self.goal_data = DataManager.loadMainData("goal", self.goal_id)
            self.isGoalExists = True
        #ID, name, total_difficulty, time, benefit, limit_date, priority, used_skills (,), state, note, files (,), progress (,), custom_characteristics (,:)
        else:
            self.goal_data = ["", "", "", "", "", "", "", "", "", "", r"Files\icons\Add an image....png", "", ""]
            
    def displayData(self):
        #cell_list: 1 - name lineEdit, 2 - image list, 3 - note textEdit, 4 - limit_date_label, 5 - progress_label, 6 - state_label, 7-11 - characts lineEdits
        #list_widget_list = [self.goal_tree_list_widget, characts_list_widget, skills_list_widget]
        goal_name = self.goal_data[1]
        images_list = self.goal_data[10].split(",")
        self.cell_list[0].setImage(images_list[0])
        self.cell_list[2].setImagesList(images_list)

        self.cell_list[1].setText(self.goal_data[1])
        note_text_edit = self.cell_list[3]
        note_text_edit.blockSignals(True)
        note_text_edit.setPlainText(self.goal_data[9])#Change textEdit's text without triggering textChanged signal
        note_text_edit.blockSignals(False)
        self.cell_list[4].setText("Progress: " + self.goal_data[11].split(",")[0])

        #Отобразим значения стандартных характеристик
        characts_edits = self.cell_list[6:11]
        standard_characts_values = self.goal_data[2:7]
        for i in range(5):
            characts_edits[i].setText(str(standard_characts_values[i]))

        #Отобразим значения пользовательских и навыки
        characts_list_widget = self.list_widget_list[1]
        skills_list_widget = self.list_widget_list[2]
        
        custom_characts = self.goal_data[12]
        used_skills = self.goal_data[7]

        if custom_characts:
            custom_characts = custom_characts.split(",")
            for obj in custom_characts:
                obj = obj.split(":")#[charact_name, value]
                self.add_skill_or_charact(setting_mode=obj + [characts_list_widget])
        if used_skills:
            used_skills = used_skills.split(",")
            for obj in used_skills:
                obj = obj.split(":")#[skill_name, value]
                self.add_skill_or_charact(setting_mode=obj + [skills_list_widget])

    def setData(self, goal_data):
        self.goal_data = goal_data
        self.isGoalExists = True