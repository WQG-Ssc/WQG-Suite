# -*- coding: utf-8 -*-
import os, math, random, configparser
import DataManager
from PyQt6.QtWidgets import QLabel, QFileDialog, QProgressBar, QVBoxLayout, QHBoxLayout, QWidget, QProgressBar, QPushButton, QListWidget, QMenu, QMessageBox, QDateEdit, QCalendarWidget, QDialog, QCheckBox, QLineEdit, QButtonGroup, QListWidgetItem, QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsPixmapItem, QRadioButton, QTimeEdit
from PyQt6.QtGui import QPixmap, QBitmap, QPainter, QPen, QBrush, QColor, QFont, QAction, QIcon, QFontMetrics, QPainterPath, QImage, QRegularExpressionValidator, QPolygonF
from PyQt6.QtCore import QRectF, QRect, Qt, QSize, pyqtSignal, QDate, QTime, QUrl, QPoint, QPointF, QObject, QTimer, pyqtProperty, QEasingCurve, QPropertyAnimation, QRegularExpression
from PyQt6.QtWebEngineWidgets import QWebEngineView
import tempfile
from plotly.io import to_html
import plotly.graph_objs as go
import datetime as dt
user_config_file = r"Files\config\user.ini"

class AddImageLabel(QLabel):
    imageAdded = pyqtSignal()
    def __init__(self, size=QSize(80, 80), shaping=True, default_image_path=r"Files\Icons\default_profile_image.png", ring=False):
        super().__init__()
        self.size = size
        self.shaping = shaping
        self.isImageAdded = False
        self.last_dir = None
        self.image_path = ""
        self.setFixedSize(self.size)
        self.image = QPixmap(default_image_path)
        self.image = self.image.scaled(self.size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
        self.ring = ring
        if self.shaping:
            self.shape_image()
        self.setPixmap(self.image)
        if self.ring:
            self.addRing()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.underMouse():
            self.addImage()

    def addImage(self):
        height = self.size.height()
        if self.last_dir:
            image_path, _ = QFileDialog.getOpenFileName(self, 'Choose an image', self.last_dir, "Image Files (*.png *.jpg *.bmp)")
        else:
            image_path, _ = QFileDialog.getOpenFileName(self, 'Choose an image', filter="Image Files (*.png *.jpg *.bmp)")
        if image_path:
            self.image_path = image_path
            self.last_dir = os.path.dirname(self.image_path)
            self.image = QPixmap(self.image_path)
            self.sizeImage()
            size = self.image.size()
            self.isImageAdded = True
            self.imageAdded.emit()
            if self.shaping:
                if size.height() > height or size.width() > height:
                    self.image = self.image.copy(size.width() // 2 - height / 2, size.height() // 2 - height / 2, self.size.width(), height)
                self.shape_image()
            self.setPixmap(self.image)
            if self.ring: self.addRing()

    def shape_image(self):
        self.image = shapeImage(self.size, self.image)

    def sizeImage(self):
        self.image = self.image.scaled(QSize(self.size), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)

    def setImage(self, image_path):
        self.image = QPixmap(image_path)
        self.image_path = image_path
        self.sizeImage()
        if self.shaping:
            size = self.image.size()
            height = self.size.height()
            if size.height() > height or size.width() > height:
                self.image = self.image.copy(size.width() // 2 - height / 2, size.height() // 2 - height / 2, self.size.width(), height)
            self.shape_image()
        self.setPixmap(self.image)
        self.isImageAdded = True
        if self.ring: self.addRing()

    def addRing(self):
        self.setFixedSize(82, 82)
        image = QImage(82, 82, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.black)
        template = QPixmap(r"Files\icons\author template.png")
        painter = QPainter(image)
        painter.drawPixmap(1, 1, self.image)
        painter.drawPixmap(0, 0, template)
        painter.end()
        self.image = QPixmap(image)
        self.setPixmap(self.image)

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
    def __init__(self, image, name, gotoProfile=True):
        super().__init__()
        self.setFixedSize(330, 157)
        self.gotoProfile = gotoProfile
        self.painter = QPainter()
        parser = configparser.ConfigParser()
        parser.read(user_config_file)
        self.diary_path = parser.get("User", "Diary_path")

        self.profile_image = QLabel()
        size = QSize(90, 90)
        image = QPixmap(image).scaled(QSize(size), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
        image_size = image.size()
        height = size.height()
        if image_size.height() > height or image_size.width() > height:
            image = image.copy(image_size.width() // 2 - height / 2, image_size.height() // 2 - height / 2, size.width(), height)
        self.profile_image.setPixmap(shapeImage(size, image))

        self.user_name = QLabel(name)
        self.user_name.setFont(QFont('Calibri', 24))

        diary_button = QPushButton()
        diary_button.clicked.connect(self.open_diary)
        diary_button.setFixedSize(42, 20)
        diary_button.setIconSize(QSize(12, 14))
        diary_button.setIcon(QIcon(r"Files\icons\diary.png"))
        diary_button.setObjectName("Profile")
        self.top12_button = QPushButton()
        self.top12_button.setFixedSize(42, 20)
        self.top12_button.setIconSize(QSize(13, 12))
        self.top12_button.setIcon(QIcon(r"Files\icons\top 12 goals.png"))
        self.top12_button.setObjectName("Profile")
        
        user_h_box = QHBoxLayout()
        user_h_box.addSpacing(10)
        user_h_box.addWidget(self.profile_image)
        user_h_box.addSpacing(15)
        user_h_box.addWidget(self.user_name, alignment=Qt.AlignmentFlag.AlignVCenter)
        user_h_box.addStretch()

        buttons_h_box = QHBoxLayout()
        buttons_h_box.addStretch()
        buttons_h_box.setSpacing(12)
        buttons_h_box.addWidget(diary_button)
        buttons_h_box.addWidget(self.top12_button)

        main_v_box = QVBoxLayout()
        main_v_box.addLayout(user_h_box)
        main_v_box.addLayout(buttons_h_box)
        self.setLayout(main_v_box)

    def open_diary(self):
        if not self.diary_path:
            path, _ = QFileDialog.getOpenFileName(self.parent(), "Select diary file", "", "Text Files(*.txt *docx)")
            if path:
                parser = configparser.ConfigParser()
                parser.read(user_config_file)
                self.diary_path = path
                parser.set("User", "Diary_path", self.diary_path)
                with open(user_config_file, "w") as config_file:
                    parser.write(config_file)
        if self.diary_path:
            try:
                os.startfile(self.diary_path)
            except FileNotFoundError:
                QMessageBox.warning(self, "File not found", "File not found")

    def paintEvent(self, event):
        pen = QPen(QColor("#FFD300"), 2)
        brush = QBrush(Qt.BrushStyle.NoBrush)
        self.painter.begin(self)
        self.painter.setPen(pen)
        self.painter.setBrush(brush)
        self.painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.painter.drawLine(0, 157, 330, 157)
        self.painter.drawLine(330, 0, 330, 157)
        self.painter.end()

    def mousePressEvent(self, event):
        if (event.button() == Qt.MouseButton.LeftButton) and (self.profile_image.underMouse() or self.user_name.underMouse()) and self.gotoProfile:
            self.clicked.emit()

class CompletingGoalsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(330, 502)
        self.painter = QPainter()
        font24 = QFont("Calibri", 24, 700)
        recent_label = QLabel("Recently completed")
        recent_label.setFont(font24)
        self.recent_list_widget = QListWidget()
        self.in_progress_widget = QListWidget()

        for widget in [self.recent_list_widget, self.in_progress_widget]:
            widget.setIconSize(QSize(67, 67))
            widget.setStyleSheet("border: none")
            widget.setViewMode(QListWidget.ViewMode.IconMode)
            widget.setLayoutMode(QListWidget.LayoutMode.SinglePass)

        in_progress_label = QLabel("In progress")
        in_progress_label.setFont(font24)

        self.load_data()
        v_box = QVBoxLayout()
        v_box.addWidget(recent_label)
        v_box.addWidget(self.recent_list_widget)
        v_box.addWidget(in_progress_label)
        v_box.addWidget(self.in_progress_widget)
        v_box.addSpacing(112)
        self.setLayout(v_box)

    def create_item(self, goal):
        width = 86
        size = 16
        while width > 85 and size > 8:
            font = QFont("Calibri", size, 700)
            metrics = QFontMetrics(font)
            width = metrics.horizontalAdvance(goal[0])
            size -= 1

        text = metrics.elidedText(goal[0], Qt.TextElideMode.ElideRight, 85)

        if len(goal) == 3:
            item = QListWidgetItem(QIcon(getGoalImage(goal[1].split(",")[0], 100, goal[2], 56)), text)
        else:
            item = QListWidgetItem(QIcon(getGoalImage(goal[1].split(",")[0], calculate_progress(goal[2], goal[3], goal[4], "completing"), goal[3], 56)), text)
        item.setFont(font)
        item.setTextAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)
        item.setFlags(~Qt.ItemFlag.ItemIsSelectable)
        item.id = goal[-1]
        return item

    def load_data(self):
        self.recent_list_widget.clear()
        recently_completed_goals = DataManager.loadMainData("recently completed goals")
        if recently_completed_goals:
            for goal in recently_completed_goals:
                self.recent_list_widget.addItem(self.create_item(goal))

        self.in_progress_widget.clear()
        completing_goals = DataManager.loadMainData("completing goals")
        if completing_goals:
            for goal in completing_goals:
                self.in_progress_widget.addItem(self.create_item(goal))

    def paintEvent(self, event):
        self.painter.begin(self)
        self.painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.painter.setPen(QPen(QColor("#FFD300"), 2))
        self.painter.drawLine(0, 502, 330, 390)
        self.painter.drawLine(330, 0, 330, 390)
        self.painter.end()

class TodayPhraseWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.painter = QPainter()
        self.setFixedSize(450, 120)
        
        phrase, author, pixmap = self.get_today_phrase()
        icon = QLabel(self)
        icon.setPixmap(pixmap)
        author_label = QLabel(author, self)
        author_label.setFont(QFont("Calibri", 20, 700))
        author_label.setGeometry(125, 88, 310, 30)
        author_label.setFixedSize(310, 30)
        author_label.setStyleSheet("color: white")
        author_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        author_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        phrase_label = QLabel(self)
        phrase_label.setStyleSheet("color: white")
        phrase_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        phrase_label.setFixedSize(272, 52)
        phrase_label.setGeometry(145, 23, 272, 52)
        phrase_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        phrase_label.setWordWrap(True)
        font_size = 18
        height = 273
        width = 0
        while width > 272 or height > 52:
            font = QFont("Calibri", font_size, italic=True)
            text_size = QFontMetrics(font).boundingRect(QRect(0, 0, 272, 52), Qt.TextFlag.TextWordWrap, phrase)
            width = text_size.width()
            height = text_size.height()
            font_size -= 1
        phrase_label.setFont(font)
        phrase_label.setText(phrase)

    def get_today_phrase(self):
        default = False
        current_date = QDate.currentDate().toString("yyyy-MM-dd")
        parser = configparser.ConfigParser()
        parser.read(user_config_file)
        if parser.get("Data", "last_showed_phrase_date") == current_date:
            phrase_name = parser.get("Data", "last_showed_phrase")
            author = DataManager.loadOtherData("phrase author", phrase_name, one=True)[0]
            
            image = DataManager.loadOtherData("author", author, one=True)
            if image and any(image):
                image = image[0]
            else:
                image = r"Files\icons\default_profile_image.png"
        else:
            phrases = DataManager.loadOtherData("phrases for day", current_date)
            default = False
            if not phrases:
                phrases = DataManager.loadOtherData("phrases")
                if not phrases:
                    phrases = [["Add some goals to get started", "WQG's Suite"]]
                    default = True
            phrase = random.choice(phrases)
            if default:
                image = r"Files\Icon.png"
            else:
                image = DataManager.loadOtherData("author", phrase[1], one=True)
                if image and any(image):
                    image = image[0]
                else:
                    image = r"Files\icons\default_profile_image.png"
            phrase_name, author = phrase[:2]
        
        pixmap = QPixmap(image).scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
        size = pixmap.size()
        if size.width() > 120:
            pixmap = pixmap.copy((size.width() - 120) / 2, (size.height() - 120) / 2, 120, 120)

        if not default:
            parser.set("Data", "last_showed_phrase_date", current_date)
            parser.set("Data", "last_showed_phrase", phrase_name)
            with open(user_config_file, "w") as config_file:
                parser.write(config_file)

        return phrase_name, "—" + author, pixmap

    def paintEvent(self, event):
        self.painter.begin(self)
        self.painter.drawPixmap(0, 0, QPixmap(r"Files\icons\phrase background.png"))
        self.painter.end()

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
    painter.setBrush(Qt.GlobalColor.color1)
    painter.drawEllipse(mask.rect())
    painter.end()
    image.setMask(mask)

    if diameter > 75:
        template = QPixmap(r"Files\Icons\big template.png")
        offset = 11
        antialiasing = QPixmap(r"Files\Icons\antialiasing big.png")
    elif diameter == 75:
        offset = 11
        template = QPixmap(r"Files\Icons\template.png")
        antialiasing = QPixmap(r"Files\Icons\antialiasing.png")
    else:
        offset = 7
        template = QPixmap(r"Files\Icons\mini template.png")

    painter.begin(template)
    painter.drawPixmap(offset, offset, image)
    if diameter >= 75:
        painter.drawPixmap(9, 9, antialiasing)

    painter.setPen(QPen(QColor(getGoalColor(d_diff)), 3, Qt.PenStyle.SolidLine))
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    rect = QRectF(1.5, 1.5, diameter + offset * 2 - 3, diameter + offset * 2 - 3)
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
        font = QFont("Calibri", 30)
        metrics = QFontMetrics(font)
        text = metrics.elidedText(self.goal_id + " " + self.goal_name, Qt.TextElideMode.ElideRight, 420)
        self.label = QLabel(text)
        self.label.setFont(font)
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
        pass

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
            
            h_box.addWidget(remove_graph)
        h_box.setContentsMargins(10, 0, 0, 0)
        self.setLayout(h_box)

    def graph_toggled(self, state):
        color = ""
        if state == 1:
            self.toggled.emit(self.name, "", [], [], state, color)
        else:
            if self.graph_type == "Goals" or self.graph_type == "Tasks":
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
            if s[0] != "" and s[1] != "":
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
        if self.graph_type == "Goals":
            stat = DataManager.loadMainData("statistics", self.goal_id)
            if self.isGroup:
                stat += DataManager.loadMainData("group_statistics", self.goal_id)
        else:
            stat = DataManager.loadMainData("statistics", "t:" + self.name)
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
        self.select_act = QAction()
        self.select_act.setShortcuts(["Return", "Enter"])

        self.s_filter = [item for item in init_s_filter]
        self.load_data()
        self.searching = searching
        self.isSelected = False
        self.resized = False
        self.line_edit = line_edit
        self.line_edit.textChanged.connect(self.update_list)
        self.line_edit.keyPressEvent = self.move_selection
        self.list_widget = QListWidget()
        self.list_widget.addAction(self.select_act)
        self.select_act.triggered.connect(self.fill_in_by_act)
        self.list_widget.itemClicked.connect(self.fill_in)
        self.setParent(parent)
        self.setVisible(False)
        self.h = 200

        goals_button = QPushButton()
        goals_button.setObjectName("Goals")
        goals_button.setShortcut("Ctrl+G")
        branches_button = QPushButton()
        branches_button.setObjectName("Branches")
        branches_button.setShortcut("Ctrl+B")
        skills_button = QPushButton()
        skills_button.setObjectName("Skills")
        skills_button.setShortcut("Ctrl+S")
        characts_button = QPushButton()
        characts_button.setObjectName("Characteristics")
        graphs_button = QPushButton()
        graphs_button.setObjectName("Graphs")
        tasks_button = QPushButton()
        tasks_button.setObjectName("Tasks")

        h_box = QHBoxLayout()
        h_box.setContentsMargins(0, 0, 0, 0)
        buttons = [goals_button, branches_button, skills_button, characts_button, graphs_button, tasks_button]
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
                    button.setStyleSheet("QPushButton{background-color: #000000; border: none} QPushButton::checked{background-color: #000000; border: 1px solid #FFD300}")
                    h_box.addWidget(button)
                    self.filters.addButton(button)
            self.filters.buttonToggled.connect(self.filter_search)
            v_box.addLayout(h_box)

        self.s_filter = []
        self.setLayout(v_box)
        
    def move_selection(self, event):
        if event.key() == 16777237 and not self.list_widget.currentItem() and self.list_widget.count():
            self.list_widget.setCurrentRow(0)
            self.list_widget.setFocus()
        elif event.key() in (16777237, 16777235):
            self.list_widget.keyPressEvent(event)
            self.list_widget.setFocus()

        return QLineEdit.keyPressEvent(self.line_edit, event)

    def fill_in(self, item):
        text = item.text()
        goal_id = item.goal_id
        obj_type = item.obj_type

        self.line_edit.setText(text)

        self.selected.emit(text, goal_id, obj_type)
        self.isSelected = True
        self.setVisible(False)
        
    def fill_in_by_act(self):
        item = self.list_widget.currentItem()
        if item:
            self.fill_in(item)

    def update_list(self):
        self.isSelected = False
        text = self.line_edit.text()
        areResults = False
        if text and text != " ":
            if not self.resized:
                geo = self.line_edit.geometry()
                self.setGeometry(geo.x(), geo.y() + geo.height(), geo.width(), self.h)
                self.resized = True
            self.list_widget.clear()
            
            for obj_type in self.data.keys():
                if obj_type in self.s_filter or not self.s_filter:
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
            if data_type == "Authors" or data_type == "Phrases":
                names = DataManager.loadOtherData("names", data_type)
            else:
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

    def setFilter(self, s_filter):
        self.s_filter = s_filter
        buttons = self.filters.buttons()
        for button in buttons:
            if button.objectName() not in self.s_filter:
                button.setVisible(False)
            else:
                button.setVisible(True)

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
    def __init__(self, text, value, data_type, spacing=False):
        super().__init__()
        self.label = QLabel(text)
        self.name = text
        self.data_type = data_type
        self.delete_button = QPushButton()
        self.delete_button.setIcon(QIcon(r"Files\icons\remove.png"))
        self.delete_button.setObjectName("Tool")
        self.delete_button.setFixedSize(20, 20)
        h_box = QHBoxLayout()
        h_box.addWidget(self.label)
        h_box.addStretch()
        if data_type != "displaying charact":
            self.value_edit = QLineEdit(value)
            if data_type == "Skills" or data_type == "Characteristics" and DataManager.loadMainData("characteristic", text, one=True)[0] == "dynamic":
                validator = QRegularExpressionValidator(QRegularExpression("[0-9][0-9]*\.?[0-9]+$"))
                self.value_edit.setValidator(validator)
            h_box.addWidget(self.value_edit)
            metrics = QFontMetrics(self.label.font())
            text = metrics.elidedText(self.name, Qt.TextElideMode.ElideRight, 85)
            self.label.setText(text)
            h_box.addWidget(self.delete_button)
            h_box.addSpacing(18)
        self.setLayout(h_box)

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
            if QMessageBox.question(self, "Goal haven't been started yet", "Goal haven't been started yet. Are you try to enter already finished goal?") == QMessageBox.StandardButton.Yes:
                pass
        else:
            self.recalc_goal_values_for_comp()
            goal_image = QLabel()
            goal_image.setPixmap(getGoalImage(self.goal_data[9].split(",")[0], 100, float(self.goal_data[2]), 138))
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

    def complete_goal(self):
        if self.goal_data[13]:
            goal_tree = DataManager.getGoalTree(self.goal_data[0])
            for goal in goal_tree:
                if goal[0] != self.goal_data[0]:
                    self.recalc_goal_values_for_comp(goal[0])

        DataManager.updateMainData("goal", self.goal_data)
        self.completed.emit()
        self.close()
        
    def paintEvent(self, event):
        self.painter.begin(self)
        brush = QBrush(QColor(0, 0, 0, 127))
        self.painter.setBrush(brush)
        self.painter.drawRect(0, 0, 1920, 1040)
        self.painter.end()

class Object(QObject):
    switch_week_req = pyqtSignal(str)
    changes_made = pyqtSignal()
    def __init__(self):
        super().__init__()

class TimeBlock(QGraphicsItem):
    def __init__(self, task_id, start_time, end_time, gap_time, day_index, blocks_dict, gap_periods, week, used_table="", inPlan=False):
        super().__init__()
        self.object = Object()
        self.updateTaskID(task_id)
        self.start_time = start_time
        self.end_time = end_time
        self.gap_time = gap_time
        self.day_index = day_index
        self.block_dict = blocks_dict
        self.gap_periods = gap_periods
        self.used_table = used_table
        self.week = week
        self.inPlan = inPlan
        self.pen = None
        self.prev_x = 0
        self.prev_y = 0
        self.width = 258
        self.button_brush = QBrush(QColor("#000000"))
        self.selection_brush = QBrush(QColor(255, 0, 0, 0))
        self.button_pen = QPen(QColor("#FFD300"))
        if used_table != "stats" or week == False:
            self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable | QGraphicsItem.GraphicsItemFlag.ItemSendsScenePositionChanges)
        else:
            self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setZValue(1)

    def updateBlockRect(self):
        #258 - day column width, 112 - span constant
        if self.week:
            x = self.day_index * self.width + 112
        else:
            x = 0
        y = calculate_msecs(self.start_time) * 0.00001

        height = (calculate_msecs(self.end_time) - calculate_msecs(self.start_time)) * 0.00001
        self.block_rect = [int(x), int(y), int(height)]

    def updateTime(self):
        height = (calculate_msecs(self.end_time) - calculate_msecs(self.start_time)) * 0.00001
        self.block_rect[2] = height
        self.object.changes_made.emit()

    def updateTaskID(self, task_id):
        self.task_id = task_id
        if getBusyValue(self.task_id):
            self.brush = QBrush(QColor("#FFD300"))
        else:
            self.brush = QBrush(QColor("#877000"))
        if self.task_id:
            task = self.task_id.split(":")
            if len(task) > 1:
                self.name = task[1]
            else:
                self.name = self.task_id + " " + DataManager.loadMainData("goal", self.task_id, one=True)[1]
        else:
            self.name = ""
        self.object.changes_made.emit()

    def boundingRect(self):
        return QRectF(self.block_rect[0], self.block_rect[1], self.width, self.block_rect[2])

    def paint(self, painter, *args):
        painter_path = QPainterPath()
        painter_path.addRoundedRect(self.block_rect[0], self.block_rect[1], self.width, self.block_rect[2], 15, 15)
        painter.setClipPath(painter_path)
        if self.pen:
            painter.setPen(self.pen)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(self.brush)
        painter.drawRoundedRect(self.block_rect[0], self.block_rect[1], self.width, self.block_rect[2], 15, 15)
        if self.gap_periods:
            painter.setPen(QPen(QColor("#AAAAAA")))
            painter.setBrush(QBrush(QColor("#AAAAAA")))
            for period in self.gap_periods:
                y1, y2 = period
                painter.drawRect(self.block_rect[0], y1, self.width, y2)
        
        painter.setPen(QPen(QColor("#000000")))
        period = self.start_time[:-3] + "-" + self.end_time[:-3]
        time = str(round((calculate_msecs(self.end_time) - calculate_msecs(self.start_time) - self.gap_time) / 3600000, 2))
        font16 = QFont("Calibri", 16, 700)
        font14 = QFont("Calibri", 14, 700)

        font10 = QFont("Calibri", 10)
        metrics16 = QFontMetrics(font16)
        metrics8 = QFontMetrics(QFont("Calibri", 8))

        if self.block_rect[2] >= 54:
            painter.setFont(font16)
            name = metrics16.elidedText(self.name, Qt.TextElideMode.ElideRight, 176)
            painter.drawText(self.block_rect[0] + 6, self.block_rect[1] + 20, name)
            painter.setFont(font10)
            header_text_width = metrics16.horizontalAdvance(name)
            painter.drawText(self.block_rect[0] + 12 + header_text_width, self.block_rect[1] + 18, period)
            painter.setFont(font16)
            painter.drawText(self.block_rect[0] + self.width - metrics16.horizontalAdvance(time) - 5, self.block_rect[1] + self.block_rect[2] - 3, time)
        elif self.block_rect[2] >= 18:
            name = metrics16.elidedText(self.name, Qt.TextElideMode.ElideRight, 156)
            painter.setFont(font16)
            if self.block_rect[2] <= 27:
                painter.drawText(self.block_rect[0] + 6, self.block_rect[1] + 15, name)
            else:
                painter.drawText(self.block_rect[0] + 6, self.block_rect[1] + 20, name)
            header_text_width = metrics16.horizontalAdvance(name)
            if not header_text_width > 160:
                painter.setFont(font10)
                if self.block_rect[2] >= 27:
                    painter.drawText(self.block_rect[0] + 12 + header_text_width, self.block_rect[1] + 18, period)
                else:
                    painter.drawText(self.block_rect[0] + 12 + header_text_width, self.block_rect[1] + 13, period)
            painter.setFont(font16)
            painter.drawText(self.block_rect[0] + self.width - metrics16.horizontalAdvance(time) - 5, self.block_rect[1] + self.block_rect[2] - 3, time)
        elif self.block_rect[2] >= 9:
            painter.setFont(QFont("Calibri", 8))
            name = metrics8.elidedText(self.name, Qt.TextElideMode.ElideRight, 130)
            header_text_width = metrics8.horizontalAdvance(name)
            painter.drawText(self.block_rect[0] + 6, self.block_rect[1] + 8, name)
            painter.drawText(self.block_rect[0] + 10 + header_text_width, self.block_rect[1] + 8, period)
            painter.drawText(self.block_rect[0] + self.width - metrics8.horizontalAdvance(time) - 5, self.block_rect[1] + 8, time)
        else:
            name = self.name
            self.setToolTip(f"{name} period: {period} time: {time}h")

        if self.inPlan:
            metrics = QFontMetrics(font10)
            self.start_button_rect = QRect()
            if self.block_rect[2] >= 54:
                self.start_button_rect = QRect(10, self.block_rect[1] + 25, 23, 23)
                painter.drawPixmap(self.start_button_rect.x(), self.start_button_rect.y(), QPixmap(r"Files\icons\start task.png"))
            elif self.block_rect[2] >= 27:
                self.start_button_rect = QRect(metrics.horizontalAdvance(period) + metrics16.horizontalAdvance(name) + 16, self.block_rect[1] + 10, 15, 8)
                painter.drawPixmap(self.start_button_rect.x(), self.start_button_rect.y(), QPixmap(r"Files\icons\start task small.png"))
            elif self.block_rect[2] >= 18:
                self.start_button_rect = QRect(metrics.horizontalAdvance(period) + metrics16.horizontalAdvance(name) + 16, self.block_rect[1] + 5, 15, 8)
                painter.drawPixmap(self.start_button_rect.x(), self.start_button_rect.y(), QPixmap(r"Files\icons\start task small.png"))
            elif self.block_rect[2] >= 9:
                self.start_button_rect = QRect(metrics.horizontalAdvance(period) + metrics8.horizontalAdvance(name) + 16, self.block_rect[1], 15, 8)
                painter.drawPixmap(self.start_button_rect.x(), self.start_button_rect.y(), QPixmap(r"Files\icons\start task small.png"))
            self.start_button_rect.setY(self.start_button_rect.y() - self.block_rect[1])

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            x = value.x()
            y = value.y()
            block_x = x + self.block_rect[0]
            block_y = y + self.block_rect[1]
            #Проверяем соответствие будущих координат стандартным правилам
            if block_x <= 0:
                self.object.switch_week_req.emit("previous")
                x = -1 * self.block_rect[0]
            if block_x >= 1660:
                x = 1660 - self.block_rect[0]
                if block_x > 1800:
                    self.object.switch_week_req.emit("next")
            if block_y <= 0:
                y = -1 * self.block_rect[1]
            if block_y + self.block_rect[2] > 864:
                y = 864 - self.block_rect[1] - self.block_rect[2]
            #Корректируем координаты (шаг для x - один день, для y - 15 минут)
            x = ((x - 112) // self.width) * self.width + self.width
            y = y // 9 * 9
            block_x = x + self.block_rect[0]
            block_y = y + self.block_rect[1]

            if self.week:
                day = int((block_x - 112) // self.width)
                if day > 6:
                    day = 6
            else:
                day = 0
            
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

            if not self.week:
                x = 0
            if isFree:
                self.prev_x = x
                self.prev_y = y
                self.start_time = new_start_time
                self.end_time = new_end_time

                if day != self.day_index or self.start_time != new_start_time or self.end_time != new_end_time:
                    self.object.changes_made.emit()
                if day != self.day_index and self.week:
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

    def setCompleted(self):
        self.brush = QBrush(QColor("#AAAAAA"))
        self.used_table = "stats"#To make the block unabled
        self.setEnabled(False)
        self.update()

class WeekPlanView(QGraphicsView):
    switch_week_req = pyqtSignal(str, list)
    changesMade = pyqtSignal()
    startTask = pyqtSignal(TimeBlock)
    def __init__(self, start_day, week_view=True, inTimeManager=False):
        super().__init__()
        self.week_view = week_view
        self.inTimeManager = inTimeManager
        self.start_day = start_day
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.scene.selectionChanged.connect(self.highlight_items)
        self.setStyleSheet("QScrollBar{width: 0px}")
        self.setFixedHeight(864)
        self.MSECSTOPIXS = 0.00001
        self.switch_timer = QTimer()
        self.switch_timer.setInterval(500)
        self.switch_timer.setSingleShot(True)
        #Variables for creating an item
        self.creating_item = None
        self.start_point = None
        self.blocks_dict = {}
        self.max_end_time = 86400000
        self.copied_task_id = ""

        self.delete_act = QAction("Delete block")
        self.delete_act.triggered.connect(self.delete_block)
        self.delete_act.setShortcut("delete")
        self.copy_act = QAction("Copy block")
        self.copy_act.triggered.connect(self.copy_block)
        self.copy_act.setShortcut("Ctrl+C")
        self.copy_name_act = QAction("Copy name")
        self.copy_name_act.triggered.connect(self.copy_name)
        self.copy_name_act.setShortcut("Ctrl+N")
        self.paste_name_act = QAction("Paste name")
        self.paste_name_act.triggered.connect(self.paste_name)
        self.paste_name_act.setShortcut("Ctrl+E")
        self.select_all_act = QAction("Select all")
        self.select_all_act.triggered.connect(self.select_all)
        self.select_all_act.setShortcut("Ctrl+A")
        self.addActions([self.delete_act, self.copy_act, self.copy_name_act, self.paste_name_act, self.select_all_act])

        if week_view:
            self.scene.setSceneRect(0, 0, 1920, 864)
            self.pixmap = QPixmap(r"Files\icons\week plan.png")
        else:
            self.scene.setSceneRect(0, 0, 256, 864)
            self.pixmap = QPixmap(r"Files\icons\day plan.jpg")
        background_item = self.scene.addPixmap(self.pixmap)
        background_item.setPos(0, 0)
        self.loadData()

    def loadData(self, setItems=[]):
        current_date = dt.date.today()
        if self.blocks_dict:
            self.blocks_dict.clear()
        if self.week_view:
            r = 7
        else:
            r = 1
        for n in range(r):
            day = self.start_day.toString("yyyy-MM-dd")
            dtday = dt.date.fromisoformat(day)
            if self.inTimeManager:
                used_table = "plans"
            elif self.week_view:
                if dtday < current_date:
                    used_table = "stats"
                elif dtday == current_date:
                    today_completed = DataManager.loadMainData("check_today", current_date.strftime("%Y-%m-%d"))
                    if today_completed:
                        used_table = "stats"
                    else:
                        used_table = "plans"
                elif dtday > current_date:
                    used_table = "plans"
            else:
                used_table = "stats"

            if used_table == "stats":
                day_records = DataManager.loadMainData("day_stats", day)
            else:
                day_records = DataManager.loadMainData("plans", day)

            if n not in self.blocks_dict:
                self.blocks_dict[n] = []
            prev_end_time = ""
            prev_task_id = ""
            prev_block_i = ""
            for record in day_records:
                gap_time = 0
                start_time, end_time, task_id = record
                current_block_i = len(self.blocks_dict[n])
                
                if prev_end_time:
                    gap_time = calculate_msecs(start_time) - calculate_msecs(prev_end_time)
                if prev_task_id == task_id and gap_time < 1800000 and used_table == "stats" and self.week_view:#Block joining algorithm
                    current_block_i = prev_block_i
                    block = self.blocks_dict[n][current_block_i]
                    block.end_time = end_time
                    block.gap_time += gap_time
                    y1 = calculate_msecs(prev_end_time) * self.MSECSTOPIXS
                    y2 = calculate_msecs(start_time) * self.MSECSTOPIXS - y1
                    if gap_time:
                        block.gap_periods.append([y1, y2])
                else:
                    time_block = TimeBlock(task_id, start_time, end_time, 0, n, self.blocks_dict, [], self.week_view, used_table, inPlan=self.inTimeManager)
                    self.blocks_dict[n].append(time_block)
                    time_block.object.switch_week_req.connect(self.switch_week)
                    time_block.object.changes_made.connect(self.changes_made)
                prev_end_time = end_time
                prev_task_id = task_id
                prev_block_i = current_block_i

            self.start_day = self.start_day.addDays(1)

        for blocks in self.blocks_dict.values():
            for time_block in blocks:
                time_block.updateBlockRect()
                if time_block not in setItems:
                    self.scene.addItem(time_block)
        if setItems:
            for item in setItems:
                self.blocks_dict[item.day_index].append(item)

    def addBlock(self, time_block):
        time_block.updateBlockRect()
        self.blocks_dict[time_block.day_index].append(time_block)
        self.scene.addItem(time_block)

    def removeBlock(self, time_block):
        self.blocks_dict[time_block.day_index].remove(time_block)
        self.scene.removeItem(time_block)

    def mouseMoveEvent(self, event):
        pos = self.mapToScene(event.pos())
        x = pos.x()
        y = pos.y()
        if x > 112 and y <= 865 or not self.week_view and y <= 865:
            if self.start_point:
                if not self.creating_item and y - self.start_point.y() > 9:
                    if self.week_view:
                        day_index = int((x - 112) // 258)
                    else:
                        day_index = 0
                    start_time = math.ceil((self.start_point.y() // 9) * 9 / self.MSECSTOPIXS)

                    if self.blocks_dict[day_index]:
                        for block in self.blocks_dict[day_index]:
                            block_start_time = calculate_msecs(block.start_time)
                            if block_start_time > start_time and block_start_time < self.max_end_time:
                                self.max_end_time = block_start_time
                    else:
                        self.max_end_time = 86400000

                    if self.max_end_time - start_time > 900000: #Means there's enough space for the creating item (>= 15 mins)
                        self.creating_item = TimeBlock("", to_str(start_time), to_str(math.ceil((y // 9) * 9 / self.MSECSTOPIXS)), 0, day_index, self.blocks_dict, [], self.week_view, inPlan=self.inTimeManager)
                        self.creating_item.updateBlockRect()
                        self.scene.addItem(self.creating_item)
                elif self.creating_item:
                    end_time = math.ceil((y // 9) * 9 / self.MSECSTOPIXS)
                    if end_time <= self.max_end_time and end_time >= calculate_msecs(self.creating_item.start_time):
                        self.creating_item.end_time = to_str(end_time)
                        self.creating_item.prepareGeometryChange()
                        self.creating_item.updateBlockRect()
            else:
                if isinstance(self.itemAt(event.pos()), QGraphicsPixmapItem) and not self.scene.mouseGrabberItem():
                    self.start_point = pos
        return super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if self.inTimeManager:
            mapped = self.mapToScene(event.pos())
            pos = QPoint(mapped.x(), mapped.y())
            item = self.itemAt(event.pos())
            if isinstance(item, TimeBlock):
                y = pos.y() - calculate_msecs(item.start_time) * 0.00001
                x = pos.x()
                if item.start_button_rect.contains(x, y):
                    self.startTask.emit(item)
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.creating_item:
            if self.creating_item.block_rect[2]:
                self.blocks_dict[self.creating_item.day_index].append(self.creating_item)
                self.creating_item.object.switch_week_req.connect(self.switch_week)
                self.creating_item.object.changes_made.connect(self.changes_made)
        self.creating_item = None
        self.start_point = None
        self.max_end_time = 86400000
        return super().mouseReleaseEvent(event)

    def contextMenuEvent(self, event):
        pos = event.pos()
        item = self.itemAt(pos)
        if isinstance(item, TimeBlock):
            item.setSelected(True)
            self.menu = QMenu()
            self.menu.addAction(self.copy_act)
            self.menu.addAction(self.copy_name_act)
            if item.used_table != "stats" or not item.week:
                if self.copied_task_id:
                    self.menu.addAction(self.paste_name_act)
                self.menu.addAction(self.delete_act)
                self.menu.addAction(self.select_all_act)
            
            self.menu.exec(self.mapToGlobal(pos))
        return super().contextMenuEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        if isinstance(self.itemAt(event.pos()), TimeBlock):
            item = self.scene.selectedItems()
            if len(item) == 1 and (item[0].used_table != "stats" or not self.week_view):
                item = item[0]
                self.scene.clearSelection()
                self.dialog = TimeBlockDialog(item)

    def delete_block(self):
        for item in self.scene.selectedItems():
            if item.used_table != "stats" or not item.week:
                self.removeBlock(item)
        self.changesMade.emit()

    def copy_block(self):
        copied_blocks = []
        for block in self.scene.selectedItems():
            if block.used_table != "stats" or not block.week:
                item_copy = TimeBlock(block.task_id, block.start_time, block.end_time, block.gap_time, block.day_index, self.blocks_dict, [], self.week_view, inPlan=self.inTimeManager)
                item_copy.object.changes_made.connect(self.changesMade)
                item_copy.object.switch_week_req.connect(self.switch_week)
                item_copy.updateBlockRect()
                self.addBlock(item_copy)
                copied_blocks.append(item_copy)
        if copied_blocks:
            self.scene.clearSelection()
            for block in copied_blocks:
                block.setSelected(True)
            self.changesMade.emit()

    def copy_name(self):
        item = self.scene.selectedItems()
        if item: self.copied_task_id = item[0].task_id

    def paste_name(self):
        item = self.scene.selectedItems()
        if item and self.copied_task_id: item[0].updateTaskID(self.copied_task_id)

    def select_all(self):
        for day_blocks in self.blocks_dict.values():
            for block in day_blocks:
                if block.used_table != "stats":
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

    def changeWeek(self, new_start_day, exceptItems=[]):
        self.start_day = new_start_day
        for item in self.scene.items():
            if item not in exceptItems and isinstance(item, TimeBlock):
                self.scene.removeItem(item)
        self.loadData(exceptItems)

    def switch_week(self, mode):
        if not self.switch_timer.isActive() and self.week_view:
            self.switch_timer.start()
            items = self.scene.selectedItems()
            self.switch_week_req.emit(mode, items)
            self.changesMade.emit()

    def changes_made(self):
        self.changesMade.emit()
               
class TimeBlockDialog(QDialog):
    def __init__(self, time_block):
        super().__init__()
        self.setModal(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setWindowTitle("Block settings")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.goal_id = ""
        self.time_block = time_block
        self.from_te = QTimeEdit()
        self.from_te.setTime(QTime.fromString(self.time_block.start_time, "hh:mm:ss"))
        self.from_te.timeChanged.connect(self.update_time)
        self.to_te = QTimeEdit()
        self.to_te.setTime(QTime.fromString(self.time_block.end_time, "hh:mm:ss"))
        self.to_te.timeChanged.connect(self.update_time)

        start_time = calculate_msecs(self.time_block.start_time)
        end_time = calculate_msecs(self.time_block.end_time)
        self.time_label = QLabel(f"Time: {to_str(int((end_time - start_time - self.time_block.gap_time)))}")
        gap_label = QLabel(f"Gap time: {to_str(self.time_block.gap_time)}")

        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Enter name")

        type_label = QLabel("Choose type:")
        self.goal_rb = QRadioButton("Goal/skill")
        self.task_rb = QRadioButton("Task")
        self.time_rb = QRadioButton("Time name")
        self.button_group = QButtonGroup()
        self.button_group.addButton(self.goal_rb)
        self.button_group.addButton(self.task_rb)
        self.button_group.addButton(self.time_rb)
        self.button_group.buttonToggled.connect(self.toggle_mode)

        self.goal_rb_act = QAction()
        self.goal_rb_act.setShortcut("Ctrl+G")
        self.goal_rb_act.triggered.connect(self.goal_rb.click)
        self.task_rb_act = QAction()
        self.task_rb_act.setShortcut("Ctrl+T")
        self.task_rb_act.triggered.connect(self.task_rb.click)
        self.time_name_rb_act = QAction()
        self.time_name_rb_act.setShortcut("Ctrl+N")
        self.time_name_rb_act.triggered.connect(self.time_rb.click)
        self.addActions([self.goal_rb_act, self.task_rb_act, self.time_name_rb_act])

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.set_time_block)
        self.task_settings_button = QPushButton("Create or set a task")
        self.task_settings_button.clicked.connect(self.tasks_settings)

        time_h_box = QHBoxLayout()
        time_h_box.addWidget(self.from_te)
        time_h_box.addWidget(self.to_te)
        time_h_box.addStretch()

        v_box = QVBoxLayout()
        v_box.addLayout(time_h_box)
        v_box.addWidget(self.time_label)
        v_box.addWidget(gap_label)
        v_box.addWidget(self.line_edit)
        v_box.addWidget(type_label)
        v_box.addWidget(self.goal_rb)
        v_box.addWidget(self.task_rb)
        v_box.addWidget(self.time_rb)
        v_box.addWidget(ok_button)
        v_box.addWidget(self.task_settings_button)
        v_box.addStretch()
        self.setLayout(v_box)
        self.object_manager = ObjectManager(self, self.line_edit, ["Goals", "Skills", "Tasks"])
        self.object_manager.selected.connect(self.select_goal)
        self.object_manager.h = 140
        self.goal_rb.setChecked(True)#default value
        task = self.time_block.task_id.split(":")
        self.line_edit.blockSignals(True)
        if len(task) > 1:
            if task[0] == "s": self.goal_rb.setChecked(True)
            elif task[0] == "t": 
                self.task_rb.setChecked(True)
                self.object_manager.isSelected = True
            else: self.time_rb.setChecked(True)
            self.line_edit.setText(task[1])
            if task[0] == "s": task_type = "Skills"
            elif task[0] == "t": task_type = "Tasks"
            else: task_type = "Time name"
            self.select_goal(task[1], "", task_type)
        elif len(self.time_block.task_id.split(".")) > 1: 
            self.goal_rb.setChecked(True)
            goal = DataManager.loadMainData("goal", task[0], one=True)
            self.line_edit.setText(goal[1])
            self.select_goal("", task[0], "Goals")
        self.line_edit.blockSignals(False)
        self.show()

    def tasks_settings(self):
        self.dialog = QDialog()
        self.dialog.setWindowTitle("Task settings")
        self.dialog.setModal(True)
        self.dialog.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.task_line_edit = QLineEdit()
        self.task_line_edit.setPlaceholderText("Enter task name")
        self.skills_list = SkillCharactListWidget()
        self.skills_list.addedItemsText = []
        self.skills_list.setToolTip("Add used skills (give values in percentages)")
        self.skills_list.setVisible(False)
        self.busy_checkbox = QCheckBox("Busy")
        self.busy_checkbox.toggled.connect(self.toggle_skills_list)
        self.skill_edit = QLineEdit()
        self.skill_edit.setPlaceholderText("Select a skill")
        self.skill_edit.setVisible(False)
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.save_task_settings)

        if self.object_manager.isSelected:
            task_name = self.line_edit.text()
            self.task_line_edit.setText(task_name)
            self.task_line_edit.setEnabled(False)
            task = DataManager.loadMainData("task", task_name, one=True)
            if task[1]:
                for skill in task[0].split(","):
                    name, value = skill.split(":")
                    self.add_skill(name, value)
                self.busy_checkbox.setChecked(True)

        v_box = QVBoxLayout()
        v_box.addWidget(self.task_line_edit)
        v_box.addWidget(self.skill_edit)
        v_box.addWidget(self.skills_list)
        v_box.addWidget(self.busy_checkbox)
        v_box.addWidget(ok_button)
        v_box.addStretch()
        self.dialog.setLayout(v_box)
        self.dialog.show()
        self.skill_om = ObjectManager(self.dialog, self.skill_edit, ["Skills"])
        self.skill_om.selected.connect(self.add_skill)

    def save_task_settings(self):
        used_skills = ""
        if self.task_line_edit.text():
            if self.busy_checkbox.isChecked():
                for i in range(self.skills_list.count()):
                    widget = self.skills_list.itemWidget(self.skills_list.item(i))
                    skill = widget.name
                    value = widget.value_edit.text()
                    if not value:
                        return QMessageBox.warning(self, "Fill all values of skills", "Fill all values of skills")
                    used_skills += skill + ":" + value + ","
                    used_skills = used_skills.rstrip(",")
                if not used_skills:
                    return QMessageBox.warning(self, "Empty skill list", "Tasks marked as 'busy' must have defined used skills")
            busy = int(self.busy_checkbox.isChecked())
            DataManager.saveMainData("task", [used_skills, busy, self.task_line_edit.text()])
            self.line_edit.setText(self.task_line_edit.text())
            self.object_manager.isSelected = True
        self.dialog.close()

    def update_time(self):
        start_time = calculate_msecs(self.from_te.time().toString("hh:mm:ss"))
        end_time = calculate_msecs(self.to_te.time().toString("hh:mm:ss"))
        self.time_label.setText(f"Time: {to_str(int(end_time - start_time))}")

    def add_skill(self, text, value=0):
        if text not in self.skills_list.addedItemsText:
            widget = SkillCharactWidget(text, "", "Skills")
            widget.value_edit.setText(str(value))
            item = QListWidgetItem()
            item.setSizeHint(widget.sizeHint())
            widget.delete_button.clicked.connect(lambda: self.remove_skill(item))
            self.skills_list.addItem(item)
            self.skills_list.setItemWidget(item, widget)
            self.skills_list.addedItemsText.append(text)

    def remove_skill(self, item):
        self.skills_list.addedItemsText.remove(self.skills_list.itemWidget(item).name)
        self.skills_list.takeItem(self.skills_list.row(item))
        
    def select_goal(self, text, goal_id, obj_type):
        if obj_type == "Goals":
            self.goal_id = goal_id
        else:
            self.goal_id = ""

    def toggle_mode(self, button):
        if button.text() != "Task":
            self.task_settings_button.setVisible(False)

        if button.text() == "Goal/skill":
            self.object_manager.setFilter(["Goals", "Skills"])
        elif button.text() == "Time name":
            self.object_manager.setFilter([""])
        else:
            self.object_manager.setFilter(["Tasks"])
            self.task_settings_button.setVisible(True)
        self.line_edit.clear()
        self.goal_id = ""

    def toggle_skills_list(self, state):
        self.skills_list.setVisible(state)
        self.skill_edit.setVisible(state)

    def set_time_block(self):
        if self.line_edit.text():
            button = self.button_group.checkedButton()
            if button.text() == "Goal/skill" and self.object_manager.isSelected:
                if self.goal_id:
                    self.time_block.updateTaskID(self.goal_id)
                else:
                    self.time_block.updateTaskID("s:" + self.line_edit.text())
            elif button.text() == "Task" and self.object_manager.isSelected:
                self.time_block.updateTaskID("t:" + self.line_edit.text())
            elif button.text() == "Time name":
                self.time_block.updateTaskID("n:" + self.line_edit.text())
        else:
            self.time_block.updateTaskID("")

        start_time = self.from_te.time().toString("hh:mm:ss")
        end_time = self.to_te.time().toString("hh:mm:ss")

        if (calculate_msecs(end_time) - calculate_msecs(start_time)) > 0:
            if start_time != self.time_block.start_time:
                self.time_block.start_time = start_time
                self.time_block.prepareGeometryChange()
                start_value = self.time_block.block_rect[1] / 0.00001
                self.time_block.setPos(self.time_block.pos().x(), (calculate_msecs(start_time) - start_value) * 0.00001)
            if end_time != self.time_block.end_time:
                self.time_block.end_time = end_time
                self.time_block.prepareGeometryChange()
                self.time_block.updateTime()
        self.close()

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
    1201: "#00ffff"}

def calculate_msecs(interval_str):
    time_list = interval_str.split(":")
    return (int(time_list[0]) * 3600 + int(time_list[1]) * 60 + int(time_list[2])) * 1000

def to_str(msecs):
    secs = msecs // 1000
    m, s = divmod(secs, 60)
    h, m = divmod(m, 60)
    return f'{h:02d}:{m:02d}:{s:02d}'

def calculate_progress(progress, time, characts, state):#Calculates progress of a goal when showing it in the goal window
    progress, p_charact = progress.split(":")
    progress = float(progress)
    if state == "completed":
        percents = 100
    else:
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

def getBusyValue(task_id):
    task = task_id.split(":")
    if len(task) > 1:
        if task[0] == "t":
            busy = DataManager.loadMainData("task", task[1], one=True)[1]
        elif task[0] == "n":
            busy = 0
        else:
            busy = 1
    else:
        busy = 1
    return busy

class AnimationDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: transparent")
        self.setFixedSize(200, 200)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.icon_label = icon_label(self)
        self.icon_label.setPixmap(QPixmap(r"Files\Icon.png").scaled(QSize(200, 200), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))
        self.animation = QPropertyAnimation(self.icon_label, b"arc")
        self.animation.setEasingCurve(QEasingCurve.Type.InQuart)
        self.animation.setDuration(1000)
        self.animation.setStartValue(0)
        self.animation.setEndValue(360)
        self.animation.start()
        self.show()

class icon_label(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.painter = QPainter()
        self.value = 360

    def paintEvent(self, event):
        super().paintEvent(event)
        self.painter.begin(self)
        self.painter.setPen(QPen(Qt.GlobalColor.black, 9))
        self.painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.painter.drawArc(4, 4, 192, 192, 90 * 16, self.value * 16)
        self.painter.end()

    def set_color(self, value):
        self.value = 360 - value
        self.update()
    arc = pyqtProperty(int, fset=set_color)