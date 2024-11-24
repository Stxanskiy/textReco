from PyQt5.QtWidgets import (
    QApplication, QLabel, QMainWindow, QPushButton, QFileDialog,
    QScrollArea, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QComboBox
)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QPixmap, QGuiApplication, QFont, QIcon
from PIL import Image
import pytesseract
import sys

# Укажи путь к Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class OCRApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OCR: Распознавание текста")
        self.setWindowIcon(QIcon("icon.png"))  # Добавьте иконку приложения
        self.is_dark_theme = False

        self.setup_ui()
        self.load_styles()
        self.showMaximized()

    def setup_ui(self):
        """Инициализация пользовательского интерфейса"""
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Главный контейнер
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Верхняя панель
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(10, 10, 10, 10)

        self.header_label = QLabel("OCR: Распознавание текста", self)
        self.header_label.setObjectName("header")
        self.header_label.setFont(QFont("Arial", 20, QFont.Bold))
        self.header_label.setAlignment(Qt.AlignLeft)

        self.language_selector = QComboBox(self)
        self.language_selector.addItems(["English", "Russian", "French", "German"])  # Добавьте нужные языки
        self.language_selector.setObjectName("languageSelector")
        self.language_selector.setFixedWidth(150)

        self.theme_button = QPushButton("", self)
        self.theme_button.setObjectName("themeButton")
        self.theme_button.setIconSize(QSize(24, 24))
        self.theme_button.setFixedSize(40, 40)
        self.theme_button.clicked.connect(self.toggle_theme)

        header_layout.addWidget(self.header_label)
        header_layout.addWidget(self.language_selector)
        header_layout.addStretch()
        header_layout.addWidget(self.theme_button)
        main_layout.addLayout(header_layout)

        # Контентное тело
        content_layout = QVBoxLayout()
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        content_widget.setContentsMargins(20, 20, 20, 20)

        self.image_label = QLabel("Кликните или перетащите изображение", self)
        self.image_label.setObjectName("imageLabel")
        self.image_label.setCursor(Qt.PointingHandCursor)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFrameShape(QFrame.Box)
        self.image_label.setMinimumHeight(300)
        self.image_label.mousePressEvent = self.open_file_dialog
        content_layout.addWidget(self.image_label)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setObjectName("scrollResultArea")
        self.scroll_area.setWidgetResizable(True)
        self.result_widget = QLabel("Результат распознавания появится здесь.", self)
        self.result_widget.setObjectName("resultLabel")
        self.result_widget.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.result_widget.setWordWrap(True)
        self.result_widget.setMinimumHeight(100)

        self.scroll_area.setWidget(self.result_widget)
        self.scroll_area.setMinimumHeight(150)
        content_layout.addWidget(self.scroll_area)

        # Нижняя панель кнопок
        button_layout = QHBoxLayout()
        self.copy_button = QPushButton("Cкопировать текст", self)
        self.copy_button.setFixedWidth(200)
        self.copy_button.setEnabled(False)
        self.copy_button.clicked.connect(self.copy_text)
        button_layout.addWidget(self.copy_button, alignment=Qt.AlignRight)

        content_layout.addLayout(button_layout)
        main_layout.addWidget(content_widget)

        # Перетаскивание файлов
        self.setAcceptDrops(True)

    def load_styles(self):
        """Загрузка стилей"""
        try:
            theme = "styles/dark_theme.css" if self.is_dark_theme else "styles/light_theme.css"
            with open("styles/styles.css", "r") as base_styles, open(theme, "r") as theme_styles:
                self.setStyleSheet(base_styles.read() + "\n" + theme_styles.read())
        except FileNotFoundError:
            print("Файлы стилей не найдены, используется базовый стиль.")
        # Обновление иконки после смены темы
        self.theme_button.setIcon(QIcon("icons/sun.png" if self.is_dark_theme else "icons/moon.png"))

    def dragEnterEvent(self, event):
        """Обработка перетаскивания файла"""
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Обработка сброса файла"""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.process_image(file_path)

    def open_file_dialog(self, event=None):
        """Открытие файла через диалог"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите изображение", "", "Изображения (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.process_image(file_path)

    def process_image(self, file_path):
        """Обработка изображения и распознавание текста"""
        self.result_widget.setText("Обработка изображения...")
        QTimer.singleShot(100, lambda: self.recognize_text(file_path))

    def recognize_text(self, file_path):
        """Распознавание текста с использованием Tesseract"""
        try:
            pixmap = QPixmap(file_path)
            self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio))

            image = Image.open(file_path)
            selected_language = self.language_selector.currentText()
            lang_map = {
                "Английский": "eng",
                "Русский": "rus",
                "Французский": "fra",
                "Немецкий": "deu"
            }
            tesseract_lang = lang_map.get(selected_language, "eng")

            text = pytesseract.image_to_string(image, lang=tesseract_lang)

            self.result_widget.setText(text if text else "Текст не распознан")
            self.copy_button.setEnabled(True)
        except Exception as e:
            self.result_widget.setText(f"Ошибка: {e}")

    def copy_text(self):
        """Копирование текста в буфер обмена"""
        text = self.result_widget.text()
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(text)

    def toggle_theme(self):
        """Переключение темы оформления"""
        self.is_dark_theme = not self.is_dark_theme
        self.load_styles()


if __name__ == "__main__":
    app = QApplication([])
    window = OCRApp()
    window.show()
    sys.exit(app.exec())
