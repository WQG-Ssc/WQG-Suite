from PyQt6.QtGui import QIcon
from pathlib import Path

icon_path = r"Files/icons/plan.png"

# print(icon_path.absolute())
# print(icon_path.exists())

icon = QIcon(str(icon_path))
print("Icon is null:", icon.isNull())