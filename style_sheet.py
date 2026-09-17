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
QPushButton#Profile{
    border: 1px solid #FFD300; 
    background-color: #000000
    }
QPushButton#Profile::pressed{
    background-color: #7F6900;
    border: 1px solid #FFD300;
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
    image: url(Files/icons/asc.png);
    }
QTreeWidget QHeaderView::down-arrow {
    image: url(Files/icons/desc.png);
    }
QCheckBox{
    color: #FFD300
    }
QRadioButton{
    color: #FFD300
    }
QRadioButton::indicator::unchecked{
    image: url(Files/icons/rb unchecked.png)
    }
QRadioButton::indicator::checked{
    image: url(Files/icons/rb checked.png)
    }
QRadioButton::indicator::disabled{
    image: url(Files/icons/rb disabled.png)
    }
QRadioButton::indicator::checked::disabled{
    image: url(Files/icons/rb disabled checked.png)
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
QTimeEdit{
    color: #FFD300;
    border: 1px solid #FFD300;
    }
QPlainTextEdit{
    color: white
    }

QScrollBar:vertical {
    border: 1px solid #FFD300;
    background: black;
    width: 8px;
    margin: 0 0 0 0;
}
QScrollBar::handle:vertical {
    background: #FFD300;
    border: 1px solid black;
    min-height: 5px;
}
QScrollBar::add-line:vertical {
    height: 0px;
}
QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
    height: 0px;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

QScrollBar:horizontal {
    border: 1px solid #FFD300;
    background: black;
    height: 8px;
    margin: 0 0 0 0;
}

QScrollBar::handle:horizontal {
    background: #FFD300;
    border: 1px solid black;
    min-width: 5px;
}

QScrollBar::add-line:horizontal {
    width: 0px;
}

QScrollBar::sub-line:horizontal {
    width: 0px;
}

QScrollBar::left-arrow:horizontal, QScrollBar::right-arrow:horizontal {
    width: 0px;
}

QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: none;
}
QToolTip{
    background-color: #000000;
    border: none;
}
QInputDialog QSpinBox{
    color: #FFD300;
}
"""
#QScrollBar:horizontal{
#    border: 1px solid #FFD300;
#    background: black;
#    height: 5px;
#    margin: 0px 5px 0 5px;
#}
#QScrollBar::handle:horizontal {
#    background: #FFD300;
#    min-width: 20px;
#}
#QScrollBar::add-line:horizontal {
#    border: 1px solid #FFD300;
#    background: black;
#    width: 20px;
#    subcontrol-position: right;
#    subcontrol-origin: margin;
#}

#QScrollBar::sub-line:horizontal {
#    border: 1px solid #FFD300;
#    background: black;
#    width: 20px;
#    subcontrol-position: left;
#    subcontrol-origin: margin;
#}
