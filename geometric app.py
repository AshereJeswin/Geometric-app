import sys
import random
import requests
import tempfile
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QPushButton, QLabel, QVBoxLayout, QWidget, QGraphicsPixmapItem
from PyQt6.QtGui import QPixmap, QColor, QPainter, QBrush
from PyQt6.QtCore import Qt
import tempfile

GEOMETRIC_IMAGES_URL = "https://github.com/hfg-gmuend/openmoji/raw/master/src/symbols/geometric/"

class CanvasView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)

class ImageItem(QGraphicsPixmapItem):
    def __init__(self, pixmap, parent=None):
        super().__init__(pixmap, parent)
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable)
        self.setPos(random.randint(0, 500), random.randint(0, 500))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Geometric App")
        self.canvas = CanvasView(self)
        self.setCentralWidget(self.canvas)
        self.images = []

        self.info_label = QLabel(self)
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("QLabel { background-color : white; color : black; }")
        self.info_label.setFixedHeight(50)

        self.create_buttons()

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.info_label)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def create_buttons(self):
        button1 = QPushButton("Add Image", self)
        button1.clicked.connect(self.add_image)

        button2 = QPushButton("Group Images", self)
        button2.clicked.connect(self.group_images)

        toolbar = self.addToolBar("Toolbar")
        toolbar.addWidget(button1)
        toolbar.addWidget(button2)

    def download_image(self, image_path):
        response = requests.get(image_path)
        if response.status_code == 200:
            with tempfile.NamedTemporaryFile(delete=False) as file:
                file.write(response.content)
                temp_file_path = file.name
            return temp_file_path
        return None


    def add_image(self):
        image_path = random.choice(geometric_image_paths)
        temp_image_path = self.download_image(image_path)
        if temp_image_path:
            pixmap = QPixmap(temp_image_path)
            item = ImageItem(pixmap)  # Pass the pixmap argument
            self.canvas.scene.addItem(item)
            self.images.append(item)
            self.update_info_label(item)

    def group_images(self):
        selected_items = [item for item in self.images if item.isSelected()]
        if len(selected_items) > 1:
            group_item = self.canvas.scene.createItemGroup(selected_items)
            group_item.setFlag(group_item.ItemIsMovable)
            group_item.setFlag(group_item.ItemIsSelectable)
            self.images.append(group_item)

            # Create a new ImageItem for the grouped images
            pixmap = self.get_group_pixmap(group_item)
            item = ImageItem(pixmap)
            self.canvas.scene.addItem(item)

            self.update_info_label(item)

    def get_group_pixmap(self, group_item):
        # Get the bounding rectangle that encloses all items in the group
        group_rect = group_item.boundingRect()

        # Create a new pixmap with the size of the bounding rectangle
        pixmap = QPixmap(group_rect.size().toSize())

        # Initialize the pixmap with a transparent background
        pixmap.fill(Qt.GlobalColor.transparent)

        # Create a painter to draw on the pixmap
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Translate the painter to the top-left corner of the bounding rectangle
        painter.translate(-group_rect.topLeft())

        # Render the group item onto the pixmap
        group_item.paint(painter, None, None)

        # End painting
        painter.end()

        return pixmap


    def update_info_label(self, item):
        info_text = f"Size: {item.boundingRect().width()} x {item.boundingRect().height()}  Color: {self.get_average_color(item)}"
        self.info_label.setText(info_text)

    def get_average_color(self, item):
        pixmap = item.pixmap()
        width = pixmap.width()
        height = pixmap.height()
        image = pixmap.toImage()

        total_r = 0
        total_g = 0
        total_b = 0
        total_pixels = 0  # Initialize total_pixels to avoid division by zero

        if width > 0 and height > 0:
            for y in range(height):
                for x in range(width):
                    color = QColor(image.pixel(x, y))
                    total_r += color.red()
                    total_g += color.green()
                    total_b += color.blue()
                    total_pixels += 1

        if total_pixels > 0:
            avg_r = total_r // total_pixels
            avg_g = total_g // total_pixels
            avg_b = total_b // total_pixels

            return QColor(avg_r, avg_g, avg_b)
        else:
            return QColor(10, 10, 10)  # Return default color if no pixels are found


if __name__ == "__main__":
    app = QApplication(sys.argv)

    geometric_image_paths = []

    response = requests.get(GEOMETRIC_IMAGES_URL)
    if response.status_code == 200:
        html_content = response.text
        lines = html_content.split("\n")
        for line in lines:
            if "geometric" in line and "svg" in line:
                start_index = line.find("href=")
                end_index = line.find(".svg")
                if start_index != -1 and end_index != -1:
                    image_path = line[start_index + 6:end_index + 4]
                    geometric_image_paths.append(GEOMETRIC_IMAGES_URL + image_path)

    window = MainWindow()
    window.setGeometry(100, 100, 800, 600)
    window.show()

    sys.exit(app.exec())