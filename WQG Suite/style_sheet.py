# -*- coding: cp1251 -*-
style_sheet = r"""
QWidget{
    background-color: #000000;
    }
QPushButton{
    background-color: #FFD300;
    color: #000000;
    border: none
    }
QPushButton::pressed{
    background-color: #7F6900;
    border: none
    }
QPushButton#Tool{
    background-color: #000000;
    }
QPushButton#Tool::pressed{
    background-color: #7F6900
    }
QPushButton#Menu{
    background-color: #000000;
    border: none
    }
QPushButton#Menu::pressed{
    border: 1px solid #FFD300
    }
QPushButton::menu-indicator {
    height: 0px;
    width: 0px;
    }
QLabel{
    color: #FFD300;
    }
QLineEdit{
    background-color: #000000;
    color: #FFD300;
    border: 1px solid #FFD300
    }
QProgressBar{
    border: 2px solid #FFD300
    }
QToolBar{
    border: none}
QListWidget{
    border: 1px solid #FFD300;
    color: #FFD300;
    }
QListWidget#Tree::item{
    border: 1px solid #FFD300;
    }
QTreeWidget{
    border: 1px solid #FFD300;
    color: #FFD300;
    selection-background-color: #7F6900;
    selection-color: #7F6900;
    }
QTreeWidget QHeaderView::section{
    color: #FFD300;
    background-color: #000000;
    }
QTreeWidget::item{
    height: 140px
    }
QGroupBox{
    border: none
    }
QGroupBox::title{
    color: #FFD300
    }
QMenu{
    color: #FFD300
    }
QMenu::item:selected{
    background-color: #7F6900
    }
QGridBox{
    border: 1px solid #FFFFFF;
    }
QDateEdit{
    color: #FFD300;
    border: 1px solid #FFD300
    }
QDateEdit::down-button:pressed{
    background-color: #7F6900
    }
QDateEdit::up-button:pressed{
    background-color: #7F6900
    }
QCalendarWidget QAbstractItemView{
    background-color: white;
    }
QTreeWidget QHeaderView::up-arrow {
    background-color: #FFD300;
    }
QTreeWidget QHeaderView::down-arrow {
    background-color: #FFFFFF;
    }
QCheckBox{
    color: #FFD300
    }
QRadioButton{
    color: #FFD300
    }
QRadioButton::indicator::unchecked{
    image: url(C:/Users/WQG-S/OneDrive/Рабочий стол/code/WQG Suite/WQG Suite/Files/icons/rb unchecked.png)
    }
QRadioButton::indicator::checked{
    image: url(C:/Users/WQG-S/OneDrive/Рабочий стол/code/WQG Suite/WQG Suite/Files/icons/rb checked.png)
    }
QRadioButton::indicator::disabled{
    image: url(C:/Users/WQG-S/OneDrive/Рабочий стол/code/WQG Suite/WQG Suite/Files/icons/rb disabled.png)
    }
QRadioButton::disabled{
    color: gray
    }
QComboBox{
    color: #FFD300;
    border: 1px solid #FFD300;
    }
QComboBox QAbstractItemView {
    color: #FFD300
    }
"""