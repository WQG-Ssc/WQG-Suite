import DataManager
import WSwidgets as ws
from PyQt6.QtWidgets import QListWidgetItem
from PyQt6.QtCore import QSize
class Goal:
    def __init__(self, goal_id=None):
        self.goal_id = goal_id
        if self.goal_id:
            self.self.goal_data = DataManager.loadMainData("goal", self.goal_id)

            #ѕолучим пользовательские характеристики цели
            custom_characts_values = []
            custom_characts = []
            if custom_characts:
                for charact in self.goal_data[12].split(",").split(":"):
                    custom_characts.append(charact[0])
                    custom_characts_values.append(charact[1])

            #ѕолучим остальные данные
            self.goal_id = self.goal_data[0]
            self.goal_name = self.goal_data[1]
            goal_characts_values = self.goal_data[2:7] + custom_characts_values
            used_skills = self.goal_data[7].split(",")
            goal_state = self.goal_data[8]
            images_list = self.goal_data[10].split(",")
            self.goal_progress = self.goal_data[11].split(",")[0]#ѕосле создани€ класса, убрать некоторые промежуточные переменные
            
    def arrangeData(self, widget_list):
        #ќтобразим дерево цели
        goal_tree = DataManager.getGoalTree(self.goal_id)
        for goal in goal_tree:
            if goal[1] == self.goal_name:
                isMain = True
            else:
                isMain = False
            goal_color = ws.getGoalColor(goal[3])
            goal_tree_item = ws.GoalTreeItem(self.goal_id, self.goal_name, goal_color, self.goal_progress, isMain)
            goal_tree_item.subgoalAdded.connect(self.add_subgoal)
            goal_tree_item.goalRenamed.connect(self.rename_goal)
            goal_tree_item.goalDeleted.connect(self.delete_goal)

            list_widget_item = QListWidgetItem()
            list_widget_item.setSizeHint(QSize(20, 140))
            self.goal_tree_list_widget.addItem(list_widget_item)
            self.goal_tree_list_widget.setItemWidget(list_widget_item, goal_tree_item)
            #goal_image_label.setImage(images_list[0])