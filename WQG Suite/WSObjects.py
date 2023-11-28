# -*- coding: cp1251 -*-
import DataManager
import WSwidgets as ws
import WStabs as wst
from PyQt6.QtWidgets import QListWidgetItem, QPushButton, QLineEdit, QLabel, QHBoxLayout, QWidget
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QObject
from PyQt6.QtGui import QIcon

class Goal(QObject):
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
            self.goal_data = list(DataManager.loadMainData("goal", self.goal_id, one=True))
            self.isGoalExists = True
        #ID, name, time, benefit, limit_date, priority, used_skills (,), state, note, files (,), progress (,), custom_characteristics (,:), is_group, showing_in_list
        else:
            self.goal_data = ["", "", 0, "", "", "", "", "creating", "", r"Files\icons\Add an image....png", "", "", "", "", ""]
            
    def displayData(self):
        #cell_list: 1 - name lineEdit, 2 - image list, 3 - note textEdit, 4 - limit_date_label, 5 - progress_label, 6 - state_label, 7 - isgroup, 8-12 - characts lineEdits
        #list_widget_list = [self.goal_tree_list_widget, characts_list_widget, skills_list_widget]
        if self.goal_data[13]:
            isGroup = True
        else:
            isGroup = False

        goal_name = self.goal_data[1]
        images_list = self.goal_data[9].split(",")
        self.cell_list[0].setImage(images_list[0])
        self.cell_list[2].setImagesList(images_list)
        self.cell_list[5].setText("State: " + self.goal_data[7])
        self.cell_list[6].blockSignals(True)
        self.cell_list[6].setChecked(isGroup)
        self.cell_list[6].setDisabled(self.isGoalExists)
        self.cell_list[6].blockSignals(False)

        self.cell_list[1].setText(self.goal_data[1])
        note_text_edit = self.cell_list[3]
        note_text_edit.blockSignals(True)
        note_text_edit.setPlainText(self.goal_data[8])#Change textEdit's text without triggering textChanged signal
        note_text_edit.blockSignals(False)
        if self.isGoalExists:
            goal_progress = str(ws.calculate_progress(self.goal_data[10], self.goal_data[2], self.goal_data[11], self.goal_data[7]))
        else:
            goal_progress = "0"
        self.cell_list[4].setText(f"Progress: {goal_progress}%")

        #Отобразим значения стандартных характеристик
        characts_edits = self.cell_list[7:11]
        standard_characts_values = self.goal_data[2:6]
        if isGroup:
            characts_edits[0].setReadOnly(True)
        else:
            characts_edits[0].setReadOnly(False)
        for i in range(4):
            if i == 0:
                characts_edits[i].setText(str(round(float(standard_characts_values[i]), 2)))
            else:
                characts_edits[i].setText(str(standard_characts_values[i]))

        #Отобразим значения пользовательских и навыки
        characts_list_widget = self.list_widget_list[1]
        skills_list_widget = self.list_widget_list[2]

        for i in range(4, characts_list_widget.count()):
            characts_list_widget.takeItem(4)

        skills_list_widget.clear()
        characts_list_widget.addedItemsText = {}
        skills_list_widget.addedItemsText = {}
        
        custom_characts = self.goal_data[11]
        used_skills = self.goal_data[6]

        if custom_characts:
            custom_characts = custom_characts.split(",")
            for obj in custom_characts:
                obj = obj.split(":")#[charact_name, value]
                self.add_skill_or_charact(setting_mode=obj + [characts_list_widget, isGroup, "Characteristics"])
        if used_skills:
            used_skills = used_skills.split(",")
            for obj in used_skills:
                print(obj)
                obj = obj.split(":")#[skill_name, value]
                self.add_skill_or_charact(setting_mode=obj + [skills_list_widget, isGroup, "Skills"])

    def setData(self, goal_data):
        self.goal_data = goal_data
        self.goal_id = goal_data[0]
        self.isGoalExists = True