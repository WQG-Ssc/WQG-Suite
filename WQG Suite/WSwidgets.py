# -*- coding: cp1251 -*-
import os, sys
import DataManager
from PyQt6.QtWidgets import QLabel, QFileDialog, QProgressBar, QVBoxLayout, QHBoxLayout, QWidget, QProgressBar, QPushButton, QListWidget, QMenu, QInputDialog, QMessageBox, QTreeWidgetItem, QDateEdit, QCalendarWidget, QDialog, QCheckBox, QLineEdit, QCompleter, QButtonGroup, QTreeWidget, QListWidgetItem
from PyQt6.QtGui import QPixmap, QBitmap, QPainter, QPen, QBrush, QColor, QFont, QAction, QIcon
from PyQt6.QtCore import QRectF, Qt, QSize, pyqtSignal, QDate, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from typing import Union
import tempfile
from plotly.io import to_html
import plotly.graph_objs as go

class AddImageLabel(QLabel):
    imageAdded = pyqtSignal()
    def __init__(self, size=QSize(80, 80), shaping=True, default_image_path=r"Files\Icons\default_profile_image.png"):
        super().__init__()

        self.size = size
        self.shaping = shaping

        self.isImageAdded = False
        self.last_dir = None
        self.setFixedSize(self.size)

        self.image = QPixmap(default_image_path)
        self.image = self.image.scaled(QSize(self.size), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)

        self.setPixmap(self.image)

        if self.shaping:
            self.setPixmap(shapeImage(self.size(), self.image()))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.underMouse():
            self.addImage()

    def addImage(self):
        height = self.size.height()
        if self.last_dir:
            self.image_path, _ = QFileDialog.getOpenFileName(self, 'Choose an image', self.last_dir, "Image Files (*.png *.jpg *.bmp)")
        else:
            self.image_path, _ = QFileDialog.getOpenFileName(self, 'Choose an image', r'C:\Users\WQG-S\OneDrive\Рабочий стол\code\Mountain Quiz\images', "Image Files (*.png *.jpg *.bmp)")
        if self.image_path:
            self.last_dir = os.path.dirname(self.image_path)
            self.image = QPixmap(self.image_path)
            self.sizeImage()
            size = self.image.size()
            self.isImageAdded = True
            self.imageAdded.emit()
            if self.shaping:
                if size.height() > height or size.width() > height:
                    self.image = self.image.copy(size.width() // 2 - height / 2, size.height() // 2 - height / 2, self.size.width(), height)
                self.setPixmap(shapeImage(self.size, self.image))
            else:
                self.setPixmap(self.image)

    def shapeImage(self):
        mask = QBitmap(self.size)
        mask.fill(Qt.GlobalColor.color0)
        painter = QPainter(mask)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setBrush(Qt.GlobalColor.color1)
        painter.drawEllipse(mask.rect())
        painter.end()

        self.image.setMask(mask)

        self.setPixmap(self.image)

    def sizeImage(self):
        self.image = self.image.scaled(QSize(self.size), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)

    def setImage(self, image_path):
        self.image = QPixmap(image_path)
        self.sizeImage()
        if self.shaping:
            self.shapeImage()
        self.setPixmap(self.image)
        self.isImageAdded = True

def shapeImage(size, image):
    mask = QBitmap(size)
    mask.fill(Qt.GlobalColor.color0)
    painter = QPainter(mask)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setBrush(Qt.GlobalColor.color1)
    painter.drawEllipse(mask.rect())
    painter.end()

    image.setMask(mask)
    return image

class ProfileInfoBox(QWidget):
    clicked = pyqtSignal()
    def __init__(self, image, info, gotoProfile=True):
        super().__init__()
        self.setFixedSize(365, 480)
        self.arrangeWidgets(image, info)
        self.gotoProfile = gotoProfile

    def arrangeWidgets(self, image, info):
        self.profile_image = QLabel()
        self.profile_image.setPixmap(shapeImage(QSize(80, 80), image))

        self.user_name = QLabel(info[0])
        self.user_name.setFont(QFont('Calibri', 24))

        lvl_bar = QProgressBar()
        lvl_bar.setFixedSize(155, 32)
        year_bar = QProgressBar()
        year_bar.setFixedSize(300, 28)
        month_bar = QProgressBar()
        month_bar.setFixedSize(300, 28)
        day_bar = QProgressBar()
        day_bar.setFixedSize(300, 28)

        v_box = QVBoxLayout()
        v_box.addWidget(self.user_name, alignment=Qt.AlignmentFlag.AlignLeft)
        v_box.addWidget(lvl_bar, alignment=Qt.AlignmentFlag.AlignLeft)
        
        h_box = QHBoxLayout()
        h_box.addWidget(self.profile_image)
        h_box.addLayout(v_box)
        h_box.addStretch()
        
        main_v_box = QVBoxLayout()
        main_v_box.addLayout(h_box)
        main_v_box.addSpacing(42)
        main_v_box.addWidget(year_bar)
        main_v_box.addSpacing(26)
        main_v_box.addWidget(month_bar)
        main_v_box.addSpacing(26)
        main_v_box.addWidget(day_bar)
        main_v_box.addStretch()

        self.setLayout(main_v_box)

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(QColor("#FFD300"), 2, Qt.PenStyle.SolidLine)
        brush = QBrush(Qt.BrushStyle.NoBrush)

        painter.setPen(pen)
        painter.setBrush(brush)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.drawLine(364, 370, 364, 0)
        painter.drawLine(0, 476, 364, 370)
        
        painter.end()

    def mousePressEvent(self, event):
        if (event.button() == Qt.MouseButton.LeftButton) and (self.profile_image.underMouse() or self.user_name.underMouse()) and self.gotoProfile:
            self.clicked.emit()

class GoalBranch(QWidget):
    deleteBranch = pyqtSignal(str)
    renameBranch = pyqtSignal(str)

    def __init__(self, branch_name):
        super().__init__()
        self.branch_name = branch_name
        self.rename_act = QAction("Rename branch")
        self.rename_act.triggered.connect(lambda: self.renameBranch.emit(self.branch_name))
        self.delete_act = QAction("Delete branch")
        self.delete_act.triggered.connect(lambda: self.deleteBranch.emit(self.branch_name))
        self.arrangeWidgets()

    def setText(self, text):
        self.title.setText(text)
        self.branch_name = text

    def getText(self):
        return self.branch_name

    def arrangeWidgets(self):
        self.title = QLabel(self.branch_name)
        self.title.setFont(QFont("Calibri", 24))

        main_h_box = QHBoxLayout()
        main_h_box.addWidget(self.title)
        main_h_box.addStretch()
        self.setLayout(main_h_box)

    def contextMenuEvent(self, event):
        menu = QMenu()
        menu.addAction(self.rename_act)
        menu.addAction(self.delete_act)

        action = menu.exec(self.mapToGlobal(event.pos()))

def getGoalImage(image_path, goal_progress, d_diff):
    image = QPixmap(image_path).scaled(75, 75, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
    size = image.size()
    if size.height() > 75 or size.width() > 75:
        image = image.copy(size.width() // 2 - 36.5, size.height() // 2 - 36.5, 75, 75)
    mask = QBitmap(75, 75)
    mask.fill(Qt.GlobalColor.color0)
    painter = QPainter(mask)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(Qt.GlobalColor.color1)
    painter.drawEllipse(mask.rect())
    painter.end()

    image.setMask(mask)

    template = QPixmap(r"Files\Icons\template.png")

    painter.begin(template)
    painter.drawPixmap(12, 12, image)

    painter.setPen(QPen(QColor(getGoalColor(d_diff)), 3, Qt.PenStyle.SolidLine))
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    rect = QRectF(2.0, 2.0, 95.0, 95.0)
    painter.drawArc(rect, 90 * 16, -120 * 16)
    painter.end()

    return template

class dDiffIndicator(QLabel):
    def __init__(self):
        super().__init__()
        self.template = QPixmap(r"Files\icons\diff indicator template.png")

    def updateColor(self, text):
        if text:
            d_diff = float(text)
        else:
            d_diff = 0
        color = getGoalColor(d_diff)

        painter = QPainter()
        painter.begin(self.template)
        pen = QPen(QColor(color), 1, Qt.PenStyle.SolidLine)
        brush = QBrush(QColor(color), Qt.BrushStyle.SolidPattern)
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.drawEllipse(2, 2, 8, 8)
        painter.end()
        self.setPixmap(self.template)

class GoalProgressBar(QProgressBar):
    def __init__(self, d_diff, goal_progress, isMain):
        super().__init__()
        self.goal_progress = goal_progress
        self.d_diff = d_diff
        
        self.isMain = isMain
        self.setOrientation(Qt.Orientation.Vertical)
        self.setTextVisible(False)
        if self.isMain:
            self.setFixedSize(14, 85)
        else:
            self.setFixedSize(14, 65)
        self.setUpProgressBar()

    def setUpProgressBar(self):
        color = getGoalColor(self.d_diff)
        self.setStyleSheet("QProgressBar::chunk{background-color:" + color + "}")
        self.setValue(int(self.goal_progress))

    def updateGoalProgressBar(self, goal_progress, d_diff):
        self.goal_progress = goal_progress
        self.d_diff = d_diff
        self.setUpProgressBar()
        
class AdditionalImagesLabel(QLabel):
    imageRemoved = pyqtSignal()
    def __init__(self):
        super().__init__()
        
        self.images_list = []
        self.images_from_dir = []
        self.directory = None
        self.setFixedSize(60, 60)
        
        self.setStyleSheet("border: 1px solid #FFD300")
        self.setFont(QFont('Calibri', 18))

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def setImagesList(self, images_list):
        self.images_list = images_list
        self.images_from_dir = []
        if len(self.images_list) > 1:
            maybe_dir = self.images_list[1].split("#")
            if maybe_dir[0] == "dir":
                self.directory = maybe_dir[1]
                self.images_list.pop(1)
                self.getImagesFromDir()
        self.displayImagesAmount()

    def displayImagesAmount(self):
        self.images_amount = len(self.images_list) + len(self.images_from_dir)
        if self.images_amount < 2:
            self.setText("+")
        else:
            self.setText("+" + str(self.images_amount - 1))

    def getImagesList(self):
        if self.directory:
            self.images_list.insert(1, "dir#" + self.directory)#Приводим к формату: image,dir:dir,image,...
            images = ",".join(self.images_list)
        else:
            images = ",".join(self.images_list)
        return images

    def addImages(self, images):
        self.images_list += images
        self.displayImagesAmount()

    def setMainImage(self, image):
        if self.images_list:
            self.images_list[0] = image
        else:
            self.images_list.append(image)

    def setDir(self, dir_path):
        self.directory = dir_path
        self.getImagesFromDir()
        self.displayImagesAmount()

    def getImagesFromDir(self):
        self.images_from_dir = []
        file_list = os.listdir(self.directory)

        for file in file_list:
            if file.endswith(".png") or file.endswith(".jpg"):
                self.images_from_dir.append(file)

    def removeDir(self):
        self.directory = None
        self.images_from_dir = []
        self.displayImagesAmount()

    def image_removed(self, image_index):
        self.images_list.pop(image_index)
        self.imageRemoved.emit()
        self.displayImagesAmount()

    def mousePressEvent(self, event):
        if self.underMouse() and event.button() == Qt.MouseButton.LeftButton and self.images_list:
            self.images_window = AddtionalImagesWindow(self.images_list, self.images_from_dir, self.directory)
            self.images_window.imageRemoved.connect(self.image_removed)

class AddtionalImagesWindow(QWidget):
    imageRemoved = pyqtSignal(int)
    def __init__(self, images_list, images_from_dir=[], directory=""):
        super().__init__()
        self.setMinimumSize(100, 100)
        self.images_list = images_list
        self.images_from_dir = images_from_dir
        self.current_image_index = 0
        self.directory = directory
        self.setUpWindow()

    def setUpWindow(self):
        self.non_dir_images_amount = len(self.images_list)
        self.all_images_amount = self.non_dir_images_amount + len(self.images_from_dir)
        self.all_images = self.images_list + self.images_from_dir

        self.image = QPixmap(self.all_images[0])

        self.image_label = QLabel()
        self.image_label.setPixmap(self.scaleImage(self.image))
        self.count_label = QLabel("1/" + str(self.all_images_amount))
        self.previous_button = QPushButton()
        self.previous_button.setIcon(QIcon(r"Files\icons\arrow previous.png"))
        self.previous_button.setFixedSize(self.previous_button.iconSize())
        self.previous_button.clicked.connect(self.previous_image)
        self.next_button = QPushButton()
        self.next_button.setIcon(QIcon(r"Files\icons\arrow next.png"))
        self.next_button.setFixedSize(self.next_button.iconSize())
        self.next_button.clicked.connect(self.next_image)
        if self.all_images_amount < 2:
            self.next_button.setEnabled(False)
            self.previous_button.setEnabled(False)
        self.remove_button = QPushButton()
        self.remove_button.setEnabled(False)
        self.remove_button.setIcon(QIcon(r"Files\icons\remove.png"))
        self.remove_button.clicked.connect(self.remove_image)
        self.remove_button.setObjectName("Tool")
        self.remove_button.setFixedSize(QSize(16, 16))

        button_h_box = QHBoxLayout()
        button_h_box.addStretch()
        button_h_box.addSpacing(20)
        button_h_box.addWidget(self.previous_button)
        button_h_box.addWidget(self.count_label)
        button_h_box.addWidget(self.next_button)
        button_h_box.addStretch()
        button_h_box.addWidget(self.remove_button)

        main_v_box = QVBoxLayout()
        main_v_box.addWidget(self.image_label)
        main_v_box.addLayout(button_h_box)

        self.setLayout(main_v_box)
        self.show()

    def previous_image(self):
        if self.current_image_index == 0:
            self.current_image_index = self.all_images_amount - 1
        else:
            self.current_image_index -= 1

        self.setImage()

        self.count_label.setText(f'{self.current_image_index + 1}/{self.all_images_amount}')
        self.image_label.setPixmap(self.scaleImage(self.image))

    def next_image(self):
        if self.current_image_index + 1 == self.all_images_amount:
            self.current_image_index = 0
        else:
            self.current_image_index += 1

        self.setImage()

        self.image_label.setPixmap(self.scaleImage(self.image))
        self.count_label.setText((f'{self.current_image_index + 1}/{self.all_images_amount}'))

    def setImage(self):
        if self.current_image_index >= self.non_dir_images_amount: #По кол-ву изображений из директории и индекса текущего изображения определяет, относительный или абсолютный путь
            self.image = QPixmap(os.path.join(self.directory, self.all_images[self.current_image_index]))
            self.remove_button.setEnabled(False)
        else:
            if self.current_image_index == 0:
                self.remove_button.setEnabled(False)
            else:
                self.remove_button.setEnabled(True)
            self.image = QPixmap(self.all_images[self.current_image_index])

    def scaleImage(self, pixmap):
        return pixmap.scaled(self.image_label.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)

    def remove_image(self):
        self.all_images.pop(self.current_image_index)
        self.imageRemoved.emit(self.current_image_index)
        self.all_images_amount -= 1
        self.non_dir_images_amount -= 1
        self.count_label.setText(f"{self.current_image_index}/{self.all_images_amount}")
        if self.all_images_amount == 1:
            self.next_button.setEnabled(False)
            self.previous_button.setEnabled(False)
        self.previous_image()
        
    def resizeEvent(self, event):
        self.image_label.setPixmap(self.scaleImage(self.image))

class GoalTreeItem(QWidget):
    subgoalAdded = pyqtSignal(str)
    goalDeleted = pyqtSignal(str)
    def __init__(self, goal_id, goal_name, d_diff, goal_progress, isMain):
        super().__init__()
        self.goal_id = goal_id
        self.goal_name = goal_name
        self.d_diff = d_diff
        self.goal_progress = goal_progress
        self.isMain = isMain
        self.arrangeWidgets()
        self.add_act = QAction("Add subgoal")
        self.add_act.triggered.connect(self.add_subgoal)
        self.delete_act = QAction("Delete goal")
        self.delete_act.triggered.connect(self.delete_goal)

    def arrangeWidgets(self):
        self.label = QLabel(self.goal_id + " " + self.goal_name)
        self.label.setFont(QFont("Calibri", 30))
        self.icon = GoalProgressBar(self.d_diff, self.goal_progress, self.isMain)

        h_box = QHBoxLayout()
        h_box.addWidget(self.label)
        h_box.addStretch()
        h_box.addWidget(self.icon)
        self.setLayout(h_box)

    def add_subgoal(self):
        self.subgoalAdded.emit(self.goal_id)

    def delete_goal(self):
        if QMessageBox.question(self, "Delete goal", "Do you want to delete this goal?") == QMessageBox.StandardButton.Yes:
            self.goalDeleted.emit(self.goal_id)

    def updateWidget(self, goal_id, goal_name, d_diff, goal_progress):
        self.goal_id = goal_id
        self.goal_name = goal_name
        self.d_diff = d_diff
        self.goal_progress = goal_progress
        self.label.setText(self.goal_id + " " + self.goal_name)
        self.icon.updateGoalProgressBar(self.goal_progress, self.d_diff)

    def contextMenuEvent(self, event):
        menu = QMenu()
        menu.addAction(self.add_act)
        menu.addAction(self.delete_act)
        menu.exec(self.mapToGlobal(event.pos()))

class DateEditTool(QWidget):
    dateChanged = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.current_date = QDate.currentDate()
        self.date = self.current_date

        self.date_edit = QDateEdit(self.date)
        self.date_edit.userDateChanged.connect(self.change_selected_date)
        calendar_button = QPushButton()
        calendar_button.setIcon(QIcon(r"Files\icons\calendar.png"))
        calendar_button.setFixedSize(18, 18)
        calendar_button.clicked.connect(self.show_calendar)
        h_box = QHBoxLayout()
        h_box.addWidget(self.date_edit)
        h_box.addWidget(calendar_button)
        self.setLayout(h_box)

    def show_calendar(self):
        self.dialog = QDialog()
        self.dialog.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.dialog.setModal(True)
        calendar = QCalendarWidget()
        calendar.setSelectedDate(self.date)
        calendar.clicked.connect(self.close_calendar)
        v_box = QVBoxLayout()
        v_box.addWidget(calendar)
        self.dialog.setLayout(v_box)
        self.dialog.show()

    def close_calendar(self, date):
        self.dialog.close()
        self.date_edit.setDate(date)
        self.date = date

    def change_selected_date(self, date):
        self.date = date
        self.dateChanged.emit()

    def text(self):
        return self.date.toString("dd/MM/yyyy")

    def setText(self, date: str):
        date = QDate.fromString(date, "dd/MM/yyyy")
        if date:
            self.date = date
            self.date_edit.blockSignals(True)
            self.date_edit.setDate(date)
            self.date_edit.blockSignals(False)
        else:
            date = self.current_date

class SkillWidget(QWidget):
    def __init__(self, skill_name, skill_progress):
        super().__init__()
        self.skill_name = skill_name
        self.skill_progress = skill_progress
        self.arrangeWidgets()

    def arrangeWidgets(self):
        pass

class PlotlyViewer(QWebEngineView):
    def __init__(self, fig=None):
        super().__init__()
        self.page().profile().downloadRequested.connect(self.on_downloadRequested)
 
        self.temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False)
        self.set_figure(fig)
 
    def set_figure(self, fig=None):
        self.temp_file.seek(0)
        if fig is None:
            fig = go.Figure()
        fig.update_xaxes(showspikes=True)
        fig.update_yaxes(showspikes=True)
        html = to_html(fig, config={"responsive": True, 'scrollZoom': True})
        html += "\n<style>body{margin: 0;} \n.plot-container,.main-svg,.svg-container{width:100% !important; height:100% !important;}</style>"
 
        self.temp_file.write(html)
        self.temp_file.truncate()
        self.temp_file.seek(0)
        self.load(QUrl.fromLocalFile(self.temp_file.name))

    def closeEvent(self, event):
        self.temp_file.close()
        os.unlink(self.temp_file.name)
        super().closeEvent(event)
 
    def on_downloadRequested(self, download):
        pass#dialog = QFileDialog()path, _ = dialog.getSaveFileName(self, "Save File", os.path.join(os.getcwd(), "statistics.png"), "*.png")if path:    download.setPath(path)    download.accept()

class GraphItem(QWidget):
    toggled = pyqtSignal(str, str, list, list, int, str)
    removed = pyqtSignal(QWidget)
    def __init__(self, name, graph_type, goal_id, value_type):
        super().__init__()
        self.name = name
        self.goal_id = goal_id
        self.value_type = value_type
        self.graph_type = graph_type
        self.value_mode = "Per day"
        self.showing_charact = "h"
        self.show_checkbox = QCheckBox(self.name)
        self.show_checkbox.stateChanged.connect(self.graph_toggled)
        h_box = QHBoxLayout()
        h_box.addWidget(self.show_checkbox, alignment=Qt.AlignmentFlag.AlignLeft)

        if self.graph_type != "standard" or (self.graph_type == "standard" and self.name == "Work time"):
            self.value_mode_switcher = QPushButton(self.value_mode)
            self.value_mode_switcher.setCheckable(True)
            self.value_mode_switcher.toggled.connect(self.switch_val_mode)
            h_box.addWidget(self.value_mode_switcher, alignment=Qt.AlignmentFlag.AlignRight)

        if self.graph_type != "standard":
            remove_graph = QPushButton()
            remove_graph.clicked.connect(lambda: self.removed.emit(self))
            remove_graph.setIcon(QIcon(r"Files\icons\remove.png"))
            remove_graph.setFixedSize(13, 13)
            remove_graph.setIconSize(QSize(13, 13))
            remove_graph.setObjectName("Tool")

            if self.graph_type == "Goals":
                cc_stats = DataManager.loadMainData("goal_custom", self.goal_id)[0]# cc: date value, date value,|
                cc_stats = cc_stats.split("|")
                self.cc_stats_dict = {}
                for cc in cc_stats:
                    cc = cc.split(":")
                    self.cc_stats_dict[cc[0]] = cc[1].split(",")

                self.cc_names = list(self.cc_stats_dict.keys())

                self.showing_charact_switcher = QPushButton(self.showing_charact)
                self.showing_charact_switcher.clicked.connect(self.switch_showing_charact)
                self.sct_state = 1
                h_box.addWidget(self.showing_charact_switcher)
            self.value_type = "Numeric"
            
            h_box.addWidget(remove_graph)
        h_box.setContentsMargins(10, 0, 0, 0)
        self.setLayout(h_box)

    def graph_toggled(self, state):
        color = ""
        if state == 1:
            self.toggled.emit(self.name, "", [], [], state, color)
        else:
            self.x = []
            self.y = []
            if self.graph_type == "Goals":
                if self.showing_charact == "h":
                    stat = DataManager.loadMainData("statistics", self.goal_id)
                    previous_date = ""
                    for s in stat:
                        start_time = calculate_msecs(s[0])
                        end_time = calculate_msecs(s[1])
                        record_time = end_time - start_time
                        record_time /= 3600000
                        date = s[2]
                        if date not in self.x:
                            self.x.append(date)
                        if date == previous_date:
                            self.y[-1] += record_time
                        else:
                            self.y.append(record_time)
                        previous_date = date
                else:
                    stat = self.cc_stats_dict[self.showing_charact]
                    for s in stat:
                        s = s.split(" ")
                        self.x.append(s[0])
                        self.y.append(s[1])
            elif self.graph_type == "Skills":
                stat = DataManager.loadMainData("skill_stat", self.name)
                for s in stat:
                    self.x.append(s[0])
                    self.y.append(s[1])
            elif self.graph_type == "standard":
                stat = DataManager.loadMainData("day_stats", self.name)
                for s in stat:
                    self.x.append(s[0])
                    self.y.append(s[1])
                color = DataManager.loadMainData("graph_color", self.name)[0]
            if self.value_mode == "All time":
                counter = 0
                y = []
                for val in self.y:
                    counter += float(val)
                    y.append(counter)
                self.y = [item for item in y]

            self.toggled.emit(self.name, self.value_type, self.x, self.y, state, color)

    def switch_val_mode(self, state):
        if state:
            self.value_mode_switcher.setText("All time")
            self.value_mode = "All time"
        else:
            self.value_mode_switcher.setText("Per day")
            self.value_mode = "Per day"
        if self.show_checkbox.isChecked():
            self.graph_toggled(1)#Delete graph and then display updated
            self.graph_toggled(2)

    def switch_showing_charact(self):
        if self.sct_state == len(self.cc_names) + 1:
            self.sct_state = 1
        else:
            self.sct_state += 1
        if self.sct_state == 1:
            self.showing_charact = "h"
            self.showing_charact_switcher.setText(self.showing_charact)
        else:
            self.showing_charact = self.cc_names[self.sct_state - 2]
            self.showing_charact_switcher.setText(self.showing_charact)
        if self.show_checkbox.isChecked():
            self.graph_toggled(1)
            self.graph_toggled(2)

class ObjectManager(QWidget):
    selected = pyqtSignal(str, str, str)
    def __init__(self, parent, line_edit, init_s_filter=["Goals", "Branches", "Skills", "Characteristics", "Graphs"], searching=False):
        super().__init__()
        self.s_filter = [item for item in init_s_filter]

        self.load_data()
        self.searching = searching
        self.isSelected = False
        self.resized = False
        self.line_edit = line_edit
        self.line_edit.textChanged.connect(self.update_list)
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.fill_in)
        self.setParent(parent)
        self.setVisible(False)

        goals_button = QPushButton()
        goals_button.setObjectName("Goals")
        branches_button = QPushButton()
        branches_button.setObjectName("Branches")
        skills_button = QPushButton()
        skills_button.setObjectName("Skills")
        characts_button = QPushButton()
        characts_button.setObjectName("Characteristics")
        graphs_button = QPushButton()
        graphs_button.setObjectName("Graphs")

        h_box = QHBoxLayout()
        h_box.setContentsMargins(0, 0, 0, 0)
        buttons = [goals_button, branches_button, skills_button, characts_button, graphs_button]
        self.filters = QButtonGroup()
        self.filters.setExclusive(False)
        
        v_box = QVBoxLayout()
        v_box.setContentsMargins(0, 0, 0, 0)
        v_box.addWidget(self.list_widget)

        if len(init_s_filter) > 1:
            for button in buttons:
                if button.objectName() in init_s_filter:
                    button.setIcon(QIcon(os.path.join(r'Files\icons', f"{button.objectName()}.png")))
                    button.setToolTip(button.objectName())
                    button.setCheckable(True)
                    button.setChecked(True)
                    button.setStyleSheet("QPushButton{background-color: #000000; border: none} QPushButton::checked{background-color: #000000; border: 1px solid #FFD300}")
                    h_box.addWidget(button)
                    self.filters.addButton(button)
            self.filters.buttonToggled.connect(self.filter_search)
            v_box.addLayout(h_box)

        self.setLayout(v_box)

    def fill_in(self, item):
        text = item.text()
        goal_id = item.goal_id
        obj_type = item.obj_type

        self.line_edit.setText(text)

        self.selected.emit(text, goal_id, obj_type)
        self.isSelected = True
        self.setVisible(False)

    def update_list(self):
        self.isSelected = False
        text = self.line_edit.text()
        areResults = False
        if text and text != " ":
            if not self.resized:
                geo = self.line_edit.geometry()
                self.setGeometry(geo.x(), geo.y() + geo.height(), geo.width(), 200)
                self.resized = True
            self.list_widget.clear()
            
            for obj_type in self.data.keys():
                if obj_type in self.s_filter:
                    for data in self.data[obj_type]:
                        if text.upper() in data.upper():
                            icon = QIcon(os.path.join(r'Files\icons', f"{obj_type}.png"))
                            item = ListWidgetItem(icon, data)
                            item.obj_type = obj_type
                            if obj_type == "Goals":
                                item.goal_id = self.goals_ids[self.data[obj_type].index(data)]
                            
                            self.list_widget.addItem(item)
                            areResults = True
                if areResults:
                    self.setVisible(True)
        else:
            self.setVisible(False)

    def load_data(self):
        self.data = {}
        for data_type in self.s_filter:
            names = DataManager.loadMainData("names", data_type)
            if names:
                if data_type == "Goals":
                    self.goals_ids = [item[1] for item in names]
                names = [item[0] for item in names]
                self.data[data_type] = names

    def filter_search(self, button, toggled):
        if toggled:
            self.s_filter.append(button.objectName())
        else:
            self.s_filter.remove(button.objectName())
        self.update_list()

class SkillCharactListWidget(QListWidget):
    def __init__(self):
        super().__init__()
        self.addedItemsText = {}

class ListWidgetItem(QListWidgetItem):
    def __init__(self, icon, text):
        super().__init__()
        self.obj_type = ""
        self.goal_id = ""
        self.setIcon(icon)
        self.setText(text)

class SkillCharactWidget(QWidget):
    def __init__(self, text, value):
        super().__init__()
        label = QLabel(text)
        self.delete_button = QPushButton()
            
        self.delete_button.setIcon(QIcon(r"Files\icons\remove.png"))
        self.delete_button.setObjectName("Tool")
        self.delete_button.setFixedSize(20, 20)
        h_box = QHBoxLayout()
        self.value_edit = QLineEdit(value)

        h_box.addWidget(label)
        h_box.addWidget(self.value_edit)

        h_box.addWidget(self.delete_button)
        self.setLayout(h_box)
        self.setFixedWidth(250)

    def setReadOnly(self):
        self.value_edit.setReadOnly(True)

def getGoalColor(d_diff):
    previous_key = -1
    keys = color_scale.keys()
    if d_diff > 1200:
        color_key = 1201
    for key in keys:
        if key >= d_diff > previous_key:
            color_key = key
            break
        previous_key = key
    return color_scale[color_key]

color_scale = {
    0.5: "#15ff00",
    1: "#43ff00",
    2: "#7dff00",
    3: "#b3ff00",
    5: "#d4fd00",
    10: "#eafb00",
    15: "#f7f500",
    20: "#ffea00",
    30: "#ffda00",
    40: "#ffc900",
    50: "#ffaf00",
    75: "#ff8b00",
    100: "#ff5b00",
    150: "#ff2600",
    200: "#ff0100",
    300: "#de0038",
    400: "#a70094",
    500: "#7100e7",
    750: "#4d2bff",
    1000: "#347cff",
    1200: "#20d3ff",
    1201: "#00ffff"
}

def calculate_msecs(interval_str):
    time_list = interval_str.split(":")
    return (int(time_list[0]) * 3600 + int(time_list[1]) * 60 + int(time_list[2])) * 1000