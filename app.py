import sys
import random
import os
import requests
from PyQt6.QtCore import Qt, QPoint,QRect
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget,QDialog ,QVBoxLayout, QPushButton, QLabel

# directory to store the downloaded geometric images
IMAGE_DIRECTORY = "geometric_images"

# Url for the geometric images repository
REPO_URL = "https://github.com/hfg-gmuend/openmoji/raw/master/color/svg/{}"

class GeometricImage(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.image_path = ""
        self.move_started = False
        self.offset = QPoint()

    def set_image(self, image_path):
        self.image_path = image_path
        pixmap = QPixmap(image_path)
        self.setPixmap(pixmap)
        self.resize(pixmap.size())

    def mousePressEvent(self, event):
        self.move_started = True
        self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.move_started and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.mapToParent(event.pos() - self.offset))

    def mouseReleaseEvent(self, event):
        self.move_started = False

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Viewer")
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.setGeometry(QRect(100,100,400,200))

        self.layout = QVBoxLayout(self.central_widget)
        self.canvas = QWidget(self.central_widget)
        self.canvas.setObjectName("canvas")
        self.layout.addWidget(self.canvas)

        self.image_labels = []

        self.download_button = QPushButton("Download Image", self.central_widget)
        self.download_button.clicked.connect(self.download_image)
        self.layout.addWidget(self.download_button)

        self.group_button = QPushButton("Group Images", self.central_widget)
        self.group_button.clicked.connect(self.group_images)
        self.layout.addWidget(self.group_button)

        self.size_button = QPushButton("Change Size")
        self.size_button.clicked.connect(self.change_selected_images_size)
        self.layout.addWidget(self.size_button)

        if not os.path.exists(IMAGE_DIRECTORY):
            os.makedirs(IMAGE_DIRECTORY)

    def download_image(self):
        image_filename = f"geometric_{random.randint(1, 100)}.svg"
        image_path = os.path.join(IMAGE_DIRECTORY, image_filename)
        image_url = REPO_URL.format(image_filename)
        response = requests.get(image_url)
        with open(image_path, "wb") as f:
            f.write(response.content)

        image_label = GeometricImage(self.canvas)
        image_label.set_image(image_path)
        image_label.show()
        self.image_labels.append(image_label)
        
    def change_selected_images_size(self, new_size):
        for _, _, image_size, _ in self.selected_images:
            image_size.setWidth(new_size[0])
            image_size.setHeight(new_size[1])
        self.update()

    def group_images(self):                                                 #For grouping the images
        group_label = QLabel(self.canvas)
        group_label.setStyleSheet("background-color: rgba(0, 0, 255, 100);")
        group_pixmap = QPixmap(self.canvas.size())
        group_label.setPixmap(group_pixmap)
        group_label.move(0, 0)
        group_label.resize(self.canvas.size())
        group_label.show()

        painter = QPainter(group_pixmap)
        for image_label in self.image_labels:
            image_position = image_label.pos()
            painter.drawPixmap(image_position, image_label.pixmap())

        painter.end()
        self.image_labels = []

class SizeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Change Size")

        layout = QVBoxLayout()

        self.width_label = QLabel("Width:")
        self.width_spinbox = QSpinBox()
        self.width_spinbox.setRange(10, 500)

        self.height_label = QLabel("Height:")
        self.height_spinbox = QSpinBox()
        self.height_spinbox.setRange(10, 500)

        buttons_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.ok_button)
        buttons_layout.addWidget(self.cancel_button)

        layout.addWidget(self.width_label)
        layout.addWidget(self.width_spinbox)
        layout.addWidget(self.height_label)
        layout.addWidget(self.height_spinbox)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def get_size(self):
        return (self.width_spinbox.value(), self.height_spinbox.value())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
