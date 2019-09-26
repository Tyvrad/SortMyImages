import sys
import pyexiv2
import time
import datetime

from PySide2.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QFileDialog, QProgressBar, QListWidgetItem
from PySide2.QtCore import QDir, QFile, Qt
from PySide2 import QtUiTools

# This application organizes images from a source directory and sorts them in a target directory grouped into folders.
# One folder per day

G_VERSION_NUMBER = "0.1a"

window = None
dict_photos = dict()


class progress_window(QWidget):

    def set_min(self, value):
        self.progress.setMinimum(value)

    def set_max(self, value):
        self.progress.setMaximum(value)

    def set_value(self, value):
        self.progress.setValue(value)
        QApplication.processEvents()

    def set_text(self, text):
        self.lbl_text.setText(text)

    def setup_ui(self):
        self.lbl_text = QLabel("Hello World!")
        self.progress = QProgressBar()
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)
        self.progress.setValue(50)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.lbl_text)
        self.layout.addWidget(self.progress)

        self.setLayout(self.layout)

    def __init__(self):
        QWidget.__init__(self, parent=None)

        self.setWindowTitle("Progress")

        self.setup_ui()
        self.show()


def load_mainwindow():
    loader = QtUiTools.QUiLoader()
    uifile = QFile("forms/window.ui")
    uifile.open(QFile.ReadOnly)
    window = loader.load(uifile, None)
    uifile.close()

    return window


def select_src_directory():
    str_directory = QFileDialog.getExistingDirectory(window, "Select source directory", window.edit_src_dir.text())
    window.edit_src_dir.setText(str_directory)


def select_target_directory():
    str_directory = QFileDialog.getExistingDirectory(window, "Select target directory", window.edit_target_dir.text())
    window.edit_target_dir.setText(str_directory)


def update_directory_info():
    global dict_photos
    # Get list of all entries in directory and count files with supported file name extension
    dir = QDir(window.edit_src_dir.text())
    list_files = dir.entryInfoList()

    # Clear data from previous runs
    dict_photos = dict()
    window.list_files.clear()
    QApplication.processEvents()

    QApplication.setOverrideCursor(Qt.WaitCursor)

    # Actual scanning of selected directory
    start = time.time()
    for entry in list_files:
        # lbl_current_file.setText("Current file: {0}".format(entry.absoluteFilePath()))
        if entry.isFile():
            # Processing and capture time extraction
            print("Processing: {0}".format(entry.absoluteFilePath()))
            md = pyexiv2.ImageMetadata(entry.absoluteFilePath())

            try:
                md.read()
                capture_time = md['Exif.Photo.DateTimeOriginal'].value
                print("Photo taken: {0}".format(capture_time))

                dict_photos[entry.absoluteFilePath()] = capture_time
            except:
                print("Skipping file")

    QApplication.setOverrideCursor(Qt.ArrowCursor)

    print("\n\n")
    end = time.time()
    duration = end-start
    print("Processing took {:2.4f}s".format(duration))

    window.lbl_dir_info.setText("Directory contains {0} images".format(len(dict_photos)))
    print("Valid image files: {0}/{1}".format(len(dict_photos), len(list_files)))

    if len(dict_photos) > 0:
        update_file_list()


def update_file_list():
    for entry in dict_photos:
        window.list_files.addItem(QListWidgetItem(entry))


def update_example():
    str_separator = window.cmb_separator.currentText()

    new_example = "Example: 2010{0}01{0}01".format(str_separator)
    window.lbl_example.setText(new_example)


def organize_files():
    separator = window.cmb_separator.currentText()

    target_dir = QDir(window.edit_target_dir.text())
    list_target_dirs = target_dir.entryList()

    progress = progress_window()
    progress.set_max(window.list_files.count())

    for index in range(window.list_files.count()):
        progress.set_value(index)

        #
        # STEP 1: Create target directory if necessary
        #

        # Get folder name for file
        fn_src = window.list_files.item(index).text()
        progress.set_text("Processing \"{0}\"".format(fn_src))

        md = pyexiv2.ImageMetadata(fn_src)

        image_ts = datetime.date
        try:
            md.read()
            image_ts = md['Exif.Photo.DateTimeOriginal'].value

        except:
            print("Cannot open file \"{0}\"".format(fn_src))
            continue

        # Makes sure the day and month are always two digits
        def correct_format(number):
            if number < 10:
                return "0" + str(number)
            else:
                return str(number)

        folder_name_trg = str(image_ts.year) + separator + correct_format(image_ts.month) + separator + correct_format(image_ts.day)
        dir_name_trg = target_dir.absolutePath() + QDir.separator() + folder_name_trg

        # Create folder for day if necessary
        target_folder = QDir(dir_name_trg)
        if not target_folder.exists():
            QDir.mkdir(target_dir, dir_name_trg)
            print("Created directory \"{0}\"".format(dir_name_trg))

        #
        # STEP 2: Move file
        #

        # absolute file name of the new file
        fn_trg_abs = dir_name_trg + QDir.separator() + fn_src.split(QDir.separator())[-1]
        file_trg = QFile(fn_trg_abs)

        # Don't overwrite existing files
        if file_trg.exists():
            print("Skipping file \"{0}\"".format(file_trg.fileName()))
            continue

        QFile.copy(fn_src, fn_trg_abs)
        print("Copied file from \"{0}\" to \"{1}\"".format(fn_src, fn_trg_abs))

    print("Finished!")


def toggle_organize_btn():
    str_dir_src = window.edit_src_dir.text()
    dir_src = QDir(str_dir_src)
    str_dir_target = window.edit_target_dir.text()
    dir_trg = QDir(str_dir_target)

    # Double check as initializing a QDir with an empty string results in it pointing to the current dir
    if dir_src.exists() and dir_trg.exists() and len(str_dir_src) > 0 and len(str_dir_target) > 0:
        window.btn_organize_files.setEnabled(True)
    else:
        window.btn_organize_files.setEnabled(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Load main window
    window = load_mainwindow()
    window.setWindowTitle("SortMyImages {0}".format(G_VERSION_NUMBER))

    # Connect signal-slots
    window.btn_browse_src_dir.clicked.connect(select_src_directory)
    window.btn_browse_target_dir.clicked.connect(select_target_directory)

    window.edit_src_dir.textChanged.connect(update_directory_info)
    window.btn_organize_files.clicked.connect(organize_files)
    window.cmb_separator.currentTextChanged.connect(update_example)

    # Check for activity of organize button
    window.edit_src_dir.textChanged.connect(toggle_organize_btn)
    window.edit_target_dir.textChanged.connect(toggle_organize_btn)

    window.show()

    sys.exit(app.exec_())
