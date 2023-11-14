# -*- coding: cp1251 -*-
import os, sys, math
import DataManager
from PyQt6.QtWidgets import QLabel, QFileDialog, QProgressBar, QVBoxLayout, QHBoxLayout, QWidget, QProgressBar, QPushButton, QListWidget, QMenu, QInputDialog, QMessageBox, QTreeWidgetItem, QDateEdit, QCalendarWidget, QDialog, QCheckBox, QLineEdit, QCompleter, QButtonGroup, QTreeWidget, QListWidgetItem, QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem, QGraphicsPixmapItem, QGraphicsTextItem
from PyQt6.QtGui import QPixmap, QBitmap, QPainter, QPen, QBrush, QColor, QFont, QAction, QIcon, QFontMetrics
from PyQt6.QtCore import QRectF, Qt, QSize, pyqtSignal, QDate, QTime, QUrl, QPoint, QPointF
from PyQt6.QtWebEngineWidgets import QWebEngineView
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

def getGoalImage(image_path, goal_progress, d_diff, diameter=75):
    if goal_progress > 100:
        goal_progress = 100
    image = QPixmap(image_path).scaled(diameter, diameter, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
    size = image.size()
    if size.height() > diameter or size.width() > diameter:
        image = image.copy(size.width() // 2 - (diameter / 2), size.height() // 2 - (diameter / 2), diameter, diameter)
    mask = QBitmap(diameter, diameter)
    mask.fill(Qt.GlobalColor.color0)
    painter = QPainter(mask)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(Qt.GlobalColor.color1)
    painter.drawEllipse(mask.rect())
    painter.end()

    image.setMask(mask)

    if diameter > 75:
        template = QPixmap(r"Files\Icons\big template.png")
        offset = 13
        offset2 = 22
    else:
        offset = 12
        offset2 = 20
        template = QPixmap(r"Files\Icons\template.png")

    painter.begin(template)

    painter.drawPixmap(offset, offset, image)

    painter.setPen(QPen(QColor(getGoalColor(d_diff)), 3, Qt.PenStyle.SolidLine))
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    rect = QRectF(2.0, 2.0, diameter + offset2, diameter + offset2)
    painter.drawArc(rect, 90 * 16, goal_progress * -3.6 * 16)
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
    def __init__(self, d_diff, goal_progress, isMain, state):
        super().__init__()
        if goal_progress > 100:
            self.goal_progress = 100
        else:
            self.goal_progress = goal_progress
        self.d_diff = d_diff
        
        self.isMain = isMain
        self.setOrientation(Qt.Orientation.Vertical)
        self.setTextVisible(False)
        if self.isMain:
            self.setFixedSize(14, 85)
        else:
            self.setFixedSize(14, 65)

        if state == "completed":
            self.border_color = "#FFD300"
        else:
            self.border_color = "#FFFFFF"
        self.setUpProgressBar()

    def setUpProgressBar(self):
        color = getGoalColor(int(self.d_diff))
        self.setStyleSheet("QProgressBar::chunk{background-color:" + color + "}QProgressBar{border-color:" + self.border_color + "}")
        self.setValue(self.goal_progress)

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
    def __init__(self, goal_id, goal_name, d_diff, goal_progress, isMain, isGroup, state):
        super().__init__()
        self.goal_id = goal_id
        self.goal_name = goal_name
        self.d_diff = d_diff
        self.goal_progress = goal_progress
        self.isMain = isMain
        self.isGroup = isGroup
        self.state = state
        self.arrangeWidgets()
        self.add_act = QAction("Add subgoal")
        self.add_act.triggered.connect(self.add_subgoal)
        self.delete_act = QAction("Delete goal")
        self.delete_act.triggered.connect(self.delete_goal)

    def arrangeWidgets(self):
        self.label = QLabel(self.goal_id + " " + self.goal_name)
        self.label.setFont(QFont("Calibri", 30))
        self.icon = GoalProgressBar(self.d_diff, self.goal_progress, self.isMain, self.state)

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

    #def updateWidget(self, goal_id, goal_name, d_diff, goal_progress, isGroup):
    #    self.goal_id = goal_id
    #    self.goal_name = goal_name
    #    self.d_diff = d_diff
    #    self.isGroup = isGroup
    #    self.goal_progress = goal_progress
    #    self.label.setText(self.goal_id + " " + self.goal_name)
    #    self.icon.updateGoalProgressBar(self.goal_progress, self.d_diff)

    def contextMenuEvent(self, event):
        menu = QMenu()
        if self.isGroup:
            menu.addAction(self.add_act)
        menu.addAction(self.delete_act)
        menu.exec(self.mapToGlobal(event.pos()))

class DateEditTool(QWidget):
    dateChanged = pyqtSignal()
    def __init__(self, withLineEdit=True):
        super().__init__()
        self.current_date = QDate.currentDate()
        self.date = self.current_date

        self.date_edit = QDateEdit(self.date)
        self.date_edit.userDateChanged.connect(self.change_selected_date)
        self.calendar_button = QPushButton()
        self.calendar_button.setIcon(QIcon(r"Files\icons\calendar.png"))
        self.calendar_button.setFixedSize(18, 18)
        self.calendar_button.clicked.connect(self.show_calendar)
        h_box = QHBoxLayout()
        if withLineEdit:
            h_box.addWidget(self.date_edit)
        h_box.addWidget(self.calendar_button)
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
        return self.date.toString("yyyy-MM-dd")

    def setText(self, date: str):
        date = QDate.fromString(date, "yyyy-MM-dd")
        if date:
            self.date = date
            self.date_edit.blockSignals(True)
            self.date_edit.setDate(date)
            self.date_edit.blockSignals(False)
        else:
            date = self.current_date

    def setEnabled(self, val):
        self.date_edit.setEnabled(val)
        self.calendar_button.setEnabled(val)

class SkillWidget(QWidget):
    def __init__(self, skill_name, skill_progress):
        super().__init__()
        self.skill_name = skill_name
        self.skill_progress = skill_progress

class PlotlyViewer(QWebEngineView):
    def __init__(self, fig=None):
        super().__init__()
        self.page().profile().downloadRequested.connect(self.on_downloadRequested)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
 
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
        self.cc_stats_dict = {}
        self.x = []
        self.y = []
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
                cc_stats, self.isGroup = DataManager.loadMainData("goal_custom", self.goal_id, one=True)# cc: date value, date value,|
                if cc_stats:
                    cc_stats = cc_stats.split("|")
                    for cc in cc_stats:
                        cc = cc.split(":")
                        self.cc_stats_dict[cc[0]] = cc[1].split(",")

                    self.cc_names = list(self.cc_stats_dict.keys())

                    self.showing_charact_switcher = QPushButton(self.showing_charact)
                    self.showing_charact_switcher.clicked.connect(self.switch_showing_charact)
                    self.sct_state = 1
                    h_box.addWidget(self.showing_charact_switcher)
                self.value_type = "Numeric"

            if self.graph_type == "Skills": 
                self.value_type = "Numeric"
                print(self.value_type)
            
            h_box.addWidget(remove_graph)
        h_box.setContentsMargins(10, 0, 0, 0)
        self.setLayout(h_box)

    def graph_toggled(self, state):
        color = ""
        if state == 1:
            self.toggled.emit(self.name, "", [], [], state, color)
        else:
            if self.graph_type == "Goals":
                if self.showing_charact == "h":
                    self.x, self.y = self.get_vals_for_h()
                else:
                    self.x, self.y = self.get_vals_for_charact()
            elif self.graph_type == "Skills":
                self.x, self.y = self.get_skill_vals()

            elif self.graph_type == "standard":
                self.x, self.y = self.get_graph_vals()
                color = DataManager.loadMainData("graph_color", self.name, one=True)[0]
            if self.value_mode == "All time":
                counter = 0
                y = []
                for val in self.y:
                    counter += float(val)
                    y.append(counter)
                self.y = [item for item in y]

            self.toggled.emit(self.name, self.value_type, self.x, self.y, state, color)

    def get_graph_vals(self):
        x = []
        y = []
        stat = DataManager.loadMainData("days_data", self.name)
        for s in stat:
            x.append(s[0])
            y.append(s[1])
        return x, y

    def get_skill_vals(self):
        x = []
        y = []
        stat = DataManager.loadMainData("skill_stat", self.name)
        for s in stat:
            date, time = s
            if date in x:
                y[-1] += time
            else:
                x.append(date)
                y.append(time)
        return x, y

    def get_vals_for_h(self):
        x = []
        y = []
        stat = DataManager.loadMainData("statistics", self.goal_id)
        if self.isGroup:
            stat += DataManager.loadMainData("group_statistics", self.goal_id)
        previous_date = ""
        for s in stat:
            start_time = calculate_msecs(s[0])
            end_time = calculate_msecs(s[1])
            record_time = end_time - start_time
            record_time /= 3600000
            date = s[2]
            if date not in x:
                x.append(date)
            if date == previous_date:
                y[-1] += record_time
            else:
                y.append(record_time)
            previous_date = date
        return x, y

    def get_vals_for_charact(self):
        x = []
        y = []
        stat = self.cc_stats_dict[self.showing_charact]
        for s in stat:
            s = s.split(" ")
            x.append(s[0])
            y.append(s[1])
        return x, y

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

    def getGraphData(self):
        return self.name, self.graph_type, self.value_type, self.cc_stats_dict

class ObjectManager(QWidget):
    selected = pyqtSignal(str, str, str)
    def __init__(self, parent, line_edit, init_s_filter=["Goals", "Branches", "Skills"], searching=False):
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
    def __init__(self, text, value, data_type):
        super().__init__()
        label = QLabel(text)
        self.name = text
        self.data_type = data_type
        self.delete_button = QPushButton()
        self.delete_button.setIcon(QIcon(r"Files\icons\remove.png"))
        self.delete_button.setObjectName("Tool")
        self.delete_button.setFixedSize(20, 20)
        h_box = QHBoxLayout()
        h_box.addWidget(label)
        if data_type != "displaying charact":
            self.value_edit = QLineEdit(value)
            h_box.addWidget(self.value_edit)

        h_box.addWidget(self.delete_button)
        self.setLayout(h_box)
        self.setFixedWidth(250)

    def setReadOnly(self):
        self.value_edit.setReadOnly(True)
        if self.data_type == "Skills":
            self.delete_button.setDisabled(True)

class CompleteGoalWindow(QWidget):
    completed = pyqtSignal()
    def __init__(self, parent, goal_id):
        super().__init__()
        self.setParent(parent)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(1920, 1040)
        self.painter = QPainter()

        self.goal_data = list(DataManager.loadMainData("goal", goal_id, one=True))

        if self.goal_data[7] != "completing":
            QMessageBox.warning(self, "Goal haven't been started yet", "Start completing the goal to be able to complete it")
        else:
            self.recalc_goal_values_for_comp()
            goal_image = QLabel()
            goal_image.setPixmap(getGoalImage(self.goal_data[9].split(",")[0], calculate_progress(self.goal_data[10], self.goal_data[2], self.goal_data[11]), float(self.goal_data[2]), 138))
            goal_image.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

            name_label = QLabel(self.goal_data[1])
            name_label.setFont(QFont("Calibri", 24, 700))
            name_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

            time_label = QLabel(f"Time: {self.goal_data[2]:2f} hours")
            time_label.setFont(QFont("Calibri", 24, 700))
            time_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

            ok_button = QPushButton()
            ok_button.setIcon(QIcon(f"Files\icons\complete goal.png"))
            ok_button.clicked.connect(self.complete_goal)
            ok_button.setFixedWidth(150)

            v_box = QVBoxLayout()
            v_box.addSpacing(345)
            v_box.addWidget(goal_image, alignment=Qt.AlignmentFlag.AlignHCenter)
            v_box.addWidget(name_label, alignment=Qt.AlignmentFlag.AlignHCenter)
            v_box.addWidget(time_label, alignment=Qt.AlignmentFlag.AlignHCenter)
            v_box.addWidget(ok_button, alignment=Qt.AlignmentFlag.AlignHCenter)
            v_box.addStretch()

            self.setLayout(v_box)
            self.show()

    def recalc_goal_values_for_comp(self, goal_id=""):
        if goal_id:
            goal_data = list(DataManager.loadMainData("goal", goal_id, one=True))
        else:
            goal_data = self.goal_data

        old_time = goal_data[2]
        progress, p_charact = goal_data[10].split(":")
        time = 0
        if p_charact == "Hours":
            time = float(progress)
        else:
            stats = DataManager.loadMainData("statistics", goal_data[0])
            if goal_data[13]:
                stats += DataManager.loadMainData("group_statistics", goal_data[0])
                DataManager.loadMainData("group_statistics", goal_data[0])
            if stats:
                for stat in stats:
                    start_time = calculate_msecs(stat[0])
                    end_time = calculate_msecs(stat[1])
                    record_time = end_time - start_time
                    time += record_time
                time /= 3600000

        if goal_data[12]:
            characts_str = ""
            characts_dict = {charact.split(":")[0]:sum([float(stat.split(" ")[1]) for stat in charact.split(":")[1].split(",")]) for charact in self.goal_data[12].split("|")}
        
            for charact in goal_data[11].split(","):
                name, value = charact.split(":")
                if name in characts_dict:
                    characts_str += f"{name}:{characts_dict[name]},"
                else:
                    characts_str += f"{name}:{value},"
            characts_str = characts_str.rstrip(",")
            goal_data[11] = characts_str

        used_skills = goal_data[6]
        skills_str = ""
        for skill in used_skills.split(","):
            name, value = skill.split(":")
            skill_time = time * (float(value) / old_time)
            skills_str += f"{name}:{skill_time},"
        skills_str = skills_str.rstrip(",")

        goal_data[6] = skills_str
        goal_data[2] = time
        goal_data[7] = "completed"
        goal_data.append(goal_data[0])

        if goal_id:
            DataManager.updateMainData("goal", goal_data)
        else:
            self.goal_data = goal_data
        print(goal_data)

    def complete_goal(self):
        if self.goal_data[13]:
            goal_tree = DataManager.getGoalTree(self.goal_data[0])
            for goal in goal_tree:
                if goal[0] != self.goal_data[0]:
                    self.recalc_goal_values_for_comp(goal[0])

        print(self.goal_data)
        DataManager.updateMainData("goal", self.goal_data)
        self.completed.emit()
        self.close()
        
    def paintEvent(self, event):
        self.painter.begin(self)
        brush = QBrush(QColor(0, 0, 0, 127))
        self.painter.setBrush(brush)
        self.painter.drawRect(0, 0, 1920, 1040)
        self.painter.end()

class WeekPlanView(QGraphicsView):
    def __init__(self, start_day):
        super().__init__()
        self.start_day = start_day
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 1920, 864)
        self.setScene(self.scene)
        self.scene.selectionChanged.connect(self.highlight_items)
        self.setStyleSheet("QScrollBar{width: 0px}")
        self.setFixedHeight(864)
        self.MSECSTOPIXS = 0.00001
        #Variables for creating an item
        self.creating_item = None
        self.start_point = None
        self.max_end_time = 86400000

        self.delete_act = QAction("Delete block")
        self.delete_act.triggered.connect(self.delete_block)
        self.copy_act = QAction("Copy block")
        self.copy_act.triggered.connect(self.copy_block)

        backgroud_image = QPixmap(r"Files\icons\week plan.png")
        background_item = self.scene.addPixmap(backgroud_image)
        background_item.setPos(0, 0)
        self.loadData()

    def loadData(self):
        self.blocks_dict = {}#{day_index:{block_id:block}}
        for n in range(7):
            day = self.start_day.toString("yyyy-MM-dd")
            day_records = DataManager.loadMainData("day_stats", day)
            self.blocks_dict[n] = []
            prev_end_time = ""
            prev_task_id = ""
            prev_block_i = ""
            gap_time = 0
            for record in day_records:
                #print(f"record:{record}")
                start_time, end_time, task_id = record

                current_block_i = len(self.blocks_dict[n])
                
                if prev_end_time:
                    #print(f"start:{start_time}")
                    #print(f"end:{prev_end_time}")
                    gap_time = calculate_msecs(start_time) - calculate_msecs(prev_end_time)
                if prev_task_id == task_id and gap_time < 1800000:
                    current_block_i = prev_block_i
                    block = self.blocks_dict[n][current_block_i]
                    block.end_time = end_time
                    block.gap_time += gap_time
                    #print(gap_time)
                else:
                    self.blocks_dict[n].append(TimeBlock(task_id, start_time, end_time, gap_time, n, self.blocks_dict))
                prev_end_time = end_time
                prev_task_id = task_id
                prev_block_i = current_block_i

            self.start_day = self.start_day.addDays(1)

        for blocks in self.blocks_dict.values():
            for time_block in blocks:
                time_block.updateBlockRect()
                self.scene.addItem(time_block)

    def addBlock(self, time_block):
        time_block.updateBlockRect()
        self.blocks_dict[time_block.day_index].append(time_block)
        self.scene.addItem(time_block)

    def removeBlock(self, time_block):
        self.blocks_dict[time_block.day_index].remove(time_block)
        self.scene.removeItem(time_block)

    def mouseMoveEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()
        pos = event.pos()
        if x > 112 and y <= 865:
            if self.start_point:
                if not self.creating_item and y - self.start_point.y() > 9:
                    day_index = int((x - 112) // 258)
                    start_time = math.ceil((self.start_point.y() // 9) * 9 / self.MSECSTOPIXS)

                    if self.blocks_dict[day_index]:
                        for block in self.blocks_dict[day_index]:
                            block_start_time = calculate_msecs(block.start_time)
                            if block_start_time > start_time and block_start_time < self.max_end_time:
                                self.max_end_time = block_start_time
                    else:
                        self.max_end_time = 86400000

                    if self.max_end_time - start_time > 900000: #Means there's enough space for the creating item (>= 15 mins)
                        self.creating_item = TimeBlock("", to_str(start_time), to_str(math.ceil((y // 9) * 9 / self.MSECSTOPIXS)), 0, day_index, self.blocks_dict)
                        self.creating_item.updateBlockRect()
                        self.addBlock(self.creating_item)
                elif self.creating_item:
                    end_time = math.ceil((y // 9) * 9 / self.MSECSTOPIXS)
                    if end_time <= self.max_end_time and end_time >= calculate_msecs(self.creating_item.start_time):
                        self.creating_item.end_time = to_str(end_time)
                        self.creating_item.updateBlockRect()
                        self.removeBlock(self.creating_item)
                        self.addBlock(self.creating_item)
            else:
                if isinstance(self.itemAt(x, y), QGraphicsPixmapItem) and not self.scene.mouseGrabberItem():
                    self.start_point = pos
        return super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.creating_item and self.creating_item.block_rect[2]:
            self.blocks_dict[self.creating_item.day_index].append(self.creating_item)
            self.max_end_time = 86400000
        self.creating_item = None
        self.start_point = None
        return super().mouseReleaseEvent(event)

    def mousePressEvent(self, event):
        pos = event.pos()
        if event.button() == Qt.MouseButton.RightButton and isinstance(self.itemAt(pos), TimeBlock):
            item = self.itemAt(pos)
            item.setSelected(True)
            self.menu = QMenu()
            self.menu.addAction(self.delete_act)
            self.menu.addAction(self.copy_act)
            self.menu.exec(self.mapToGlobal(pos))
        else:
            pass
        return super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            self.delete_block()
        return super().keyPressEvent(event)

    def delete_block(self):
        for item in self.scene.selectedItems():
            self.removeBlock(item)

    def copy_block(self):
        copied_blocks = []
        for block in self.scene.selectedItems():
            item_copy = TimeBlock(block.task_id, block.start_time, block.end_time, block.gap_time, block.day_index, self.blocks_dict)
            item_copy.updateBlockRect()
            self.addBlock(item_copy)
            copied_blocks.append(item_copy)
        self.scene.clearSelection()
        for block in copied_blocks:
            block.setSelected(True)
            
    def highlight_items(self):
        selected_items = self.scene.selectedItems()
        items = self.scene.items()
        for item in items:
            if isinstance(item, TimeBlock):
                if item in selected_items:
                    item.highlight()
                else:
                    item.dehighlight()

    def changeWeek(self, new_start_day):
        self.start_day = new_start_day
        self.scene.clear()
        backgroud_image = QPixmap(r"Files\icons\week plan.png")
        background_item = self.scene.addPixmap(backgroud_image)
        background_item.setPos(0, 0)
        self.loadData()

class TimeBlock(QGraphicsItem):
    def __init__(self, task_id, start_time, end_time, gap_time, day_index, blocks_dict):
        super().__init__()
        self.task_id = task_id
        self.start_time = start_time
        self.end_time = end_time
        self.gap_time = gap_time
        self.day_index = day_index
        self.block_dict = blocks_dict
        self.pen = None
        self.prev_x = 0
        self.prev_y = 0
        self.wigth = 258
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable | QGraphicsItem.GraphicsItemFlag.ItemSendsScenePositionChanges)

    def updateBlockRect(self):
        #258 - day column width, 112 - span constant
        x = self.day_index * self.wigth + 112
        y = calculate_msecs(self.start_time) * 0.00001

        height = (calculate_msecs(self.end_time) - calculate_msecs(self.start_time)) * 0.00001
        self.block_rect = [int(x), int(y), int(height)]

    def boundingRect(self):
        return QRectF(self.block_rect[0], self.block_rect[1], self.wigth, self.block_rect[2])

    def paint(self, painter, *args):
        if self.pen:
            painter.setPen(self.pen)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor("#FFD300")))
        painter.drawRoundedRect(self.block_rect[0], self.block_rect[1], self.wigth, self.block_rect[2], 15, 15)
        if self.gap_time:
            painter.setPen(QPen(QColor("#AAAAAA")))
            painter.setBrush(QBrush(QColor("#AAAAAA")))
            
            painter.drawRect(self.block_rect[0], self.block_rect[1] + 15, self.wigth, self.gap_time * 0.00001)
        
        painter.setPen(QPen(QColor("#000000")))
        if self.block_rect[2] > 9:
            font_metrics = QFontMetrics(QFont("Calibri", 16, 700))
            painter.setFont(QFont("Calibri", 16, 700))
            painter.drawText(self.block_rect[0] + 6, self.block_rect[1] + 20, self.task_id)
            painter.setFont(QFont("Calibri", 10))
            if self.block_rect[2] > 45:
                painter.drawText(self.block_rect[0] + 6, self.block_rect[1] + 35, self.start_time[:-3] + "-" + self.end_time[:-3])
            else:
                header_text_width = font_metrics.horizontalAdvance(self.task_id)
                if self.block_rect[2] > 18:
                    painter.drawText(self.block_rect[0] + 12 + header_text_width, self.block_rect[1] + 18, self.start_time[:-3] + "-" + self.end_time[:-3])
                else:
                    painter.drawText(self.block_rect[0] + 12 + header_text_width, self.block_rect[1] + 14, self.start_time[:-3] + "-" + self.end_time[:-3])
        else:
            font_metrics = QFontMetrics(QFont("Calibri", 8, 700))
            header_text_width = font_metrics.horizontalAdvance(self.task_id)
            painter.setFont(QFont("Calibri", 8, 700))
            painter.drawText(self.block_rect[0] + 6, self.block_rect[1] + 5, self.task_id)
            painter.drawText(self.block_rect[0] + 12 + header_text_width, self.block_rect[1] + 8, self.start_time[:-3] + "-" + self.end_time[:-3])

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            x = value.x()
            y = value.y()
            block_x = x + self.block_rect[0]
            block_y = y + self.block_rect[1]
            #Проверяем соответствие будущих координат стандартным правилам
            if block_x <= 0:
                x = -1 * self.block_rect[0]
            if block_x >= 1660:
                x = 1660 - self.block_rect[0]
            if block_y <= 0:
                y = -1 * self.block_rect[1]
            if block_y + self.block_rect[2] > 864:
                y = 864 - self.block_rect[1] - self.block_rect[2]
            #Корректируем координаты (шаг для x - один день, для y - 15 минут)
            x = ((x - 112) // self.wigth) * self.wigth + self.wigth
            y = y // 9 * 9

            block_x = x + self.block_rect[0]
            block_y = y + self.block_rect[1]

            day = int((block_x - 112) // self.wigth)
            
            if day > 6:
                day = 6
            
            new_start_time = to_str(math.ceil(block_y / 0.00001))
            new_end_time = to_str(math.ceil(((block_y + self.block_rect[2]) / 0.00001)))

            isFree = True
            if self.block_dict.get(day, False):
                for block in self.block_dict[day]:
                    if block != self:
                        start_time = calculate_msecs(block.start_time)
                        end_time = calculate_msecs(block.end_time)
                        cb_start_time = calculate_msecs(new_start_time)
                        cb_end_time = calculate_msecs(new_end_time)
                    
                        if (end_time > cb_start_time and cb_start_time >= start_time) or (cb_end_time > start_time and start_time >= cb_start_time) or (start_time == cb_start_time and end_time == cb_end_time):
                            isFree = False
            if isFree:
                self.prev_x = x
                self.prev_y = y
                self.start_time = new_start_time
                self.end_time = new_end_time

                if day != self.day_index:
                    self.block_dict[self.day_index].remove(self)
                    self.block_dict[day].append(self)
                    self.day_index = day

                return super().itemChange(change, QPointF(x, y))#9 - pixels for 15 mins
            else:
                return super().itemChange(change, QPointF(self.prev_x, self.prev_y))
        else:
            return super().itemChange(change, value)

    def highlight(self):
        self.pen = QPen(QColor("#FFFFFF"), 2)
        self.setZValue(1)
        self.update()

    def dehighlight(self):
        self.pen = None
        self.setZValue(0)
        self.update()
    
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

def to_str(msecs):
    secs = msecs // 1000
    m, s = divmod(secs, 60)
    h, m = divmod(m, 60)
    return f'{h:d}:{m:02d}:{s:02d}'

def calculate_progress(progress, time, characts):#Calculates progress of a goal when showing it in the goal window
    progress, p_charact = progress.split(":")
    progress = float(progress)
    if progress:
        if p_charact == "Hours":
            percents = progress / float(time) * 100
        else:
            percents = progress / float([item.split(":")[1] for item in characts.split(",") if item.split(":")[0] == p_charact][0]) * 100 #Devide progress on finish value of the charact
    else:
        percents = 0
    if percents > 100:
        percents = 100.0
    return round(percents, 2)