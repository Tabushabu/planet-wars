import typing
from PyQt6 import QtCore
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
import sys
import run
import xml.etree.ElementTree as ET
from threading import Thread
from multiprocessing import Process
import subprocess
import os
import signal

import tkinter as tk
from tkinter.filedialog import askopenfilename
tk.Tk().withdraw() # part of the import if you are not using other tkinter functions


from PyQt6.QtWidgets import QWidget

window_x = 500
window_y = 230

# maps xml names ({name without path}.xml) to xml full paths (D:/.../({xml_name}.xml))
xml_paths_by_name = {}

# maps xml names ({name without path}.xml) to lists of behavior trees
trees_by_xml_name = {} 

class BotSelectionUI(QWidget):
    def __init__(self, bot_num):
        super().__init__()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)
        label = QLabel(f"Bot {bot_num}:", self)
        label.setMaximumWidth(30)
        main_layout.addWidget(label)

        # .xml selection
        xml_layout = QHBoxLayout()
        
        xml_label = QLabel("File:", self)
        xml_label.setMaximumWidth(25)
        xml_layout.addWidget(xml_label)
        
        self.xml_dropdown = QComboBox()
        self.xml_dropdown.addItems(xml_paths_by_name.keys())
        self.xml_dropdown.currentIndexChanged.connect(self.on_xml_index_change)
        xml_layout.addWidget(self.xml_dropdown)
        
        main_layout.addLayout(xml_layout)
        
        # behavior tree selection
        tree_layout = QHBoxLayout()
        
        tree_label = QLabel("Tree:", self)
        tree_label.setMaximumWidth(25)
        tree_layout.addWidget(tree_label)
        
        self.tree_dropdown = QComboBox()
        self.tree_dropdown.setMinimumHeight(20)
        tree_layout.addWidget(self.tree_dropdown)
        #self.bot1_tree_dropdown.addItems(trees)
        #self.bot1_tree_dropdown.currentIndexChanged.connect(self.on_bot1_tree_index_change)
        main_layout.addLayout(tree_layout)
        self.setLayout(main_layout)
        
    def on_xml_index_change(self, i):
        self.tree_dropdown.clear()
        self.tree_dropdown.addItems(trees_by_xml_name[self.xml_dropdown.currentText()])

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Game Manager")
        self.setMinimumSize(QSize(window_x, window_y))

        layout = QVBoxLayout()
        self.setLayout(layout) 
        
        bot_file_select_button = QPushButton("Select New .xml File")
        bot_file_select_button.clicked.connect(self.on_file_select)
        layout.addWidget(bot_file_select_button)

        bot_selection_layout = QHBoxLayout()

        # Bot 1
        self.bot1UI = BotSelectionUI(1)
        bot_selection_layout.addWidget(self.bot1UI)
        
        # Bot 2
        self.bot2UI = BotSelectionUI(2)
        bot_selection_layout.addWidget(self.bot2UI)
        
        layout.addLayout(bot_selection_layout)
        
        layout.addSpacing(30)
        
        centerAlign = QHBoxLayout()
        button = QPushButton("Start Game")
        button.clicked.connect(self.on_start_game_pressed)
        button.setFixedSize(QSize(140, 50))
        centerAlign.addWidget(button)
        layout.addLayout(centerAlign)
        
        self.game_process = None
        self.game_end_timer = QTimer()
        self.game_end_timer.timeout.connect(self.check_game_ended)

        
    def on_file_select(self):
        file_path, file_name = self.get_file_tree()
        if file_path == "" or file_name == "":
            return
        
        xml_paths_by_name[file_name] = file_path
        behavior_trees = get_behavior_tree_list(file_path)
        trees_by_xml_name[file_name] = behavior_trees
        
        self.bot1UI.xml_dropdown.addItem(file_name)
        self.bot2UI.xml_dropdown.addItem(file_name)

    def get_file_tree(self):
        fileTree = askopenfilename(initialdir="./", title="Select file", filetypes=(("XML files", "*.xml"),("All Files", "*.*")))
        folders = fileTree.split("/")
        file = folders.pop(-1)
        return fileTree, file

    def on_start_game_pressed(self):
        if self.bot1UI.xml_dropdown.currentIndex() == -1 or self.bot1UI.tree_dropdown.currentIndex() == -1 \
            or self.bot2UI.xml_dropdown.currentIndex() == -1 or self.bot2UI.tree_dropdown.currentIndex() == -1:
                return
        
        bot1_xml = xml_paths_by_name[self.bot1UI.xml_dropdown.currentText()]
        bot1_tree_name = self.bot1UI.tree_dropdown.currentText()
        bot2_xml = xml_paths_by_name[self.bot2UI.xml_dropdown.currentText()]
        bot2_tree_name = self.bot2UI.tree_dropdown.currentText()
        
        self.game_thread = Thread(target=run.run_game, args = (bot1_xml, bot1_tree_name, bot2_xml, bot2_tree_name, 1))
        self.game_thread.start()
        self.game_active = True
        self.game_end_timer.start(500)
        #self.spinner.start()
        
        #self.game_process = subprocess.Popen(f"python run.py {bot1_xml} {bot1_tree_name} {bot2_xml} {bot2_tree_name} 1", shell=True, )
        #self.game_process = Process(target=run.run_game, args = (bot1_xml, bot1_tree_name, bot2_xml, bot2_tree_name, 1))
        #self.game_process.start()
        
    def check_game_ended(self):
        if not self.game_thread.is_alive and self.game_active:
            self.game_active = False
            self.game_end_timer.stop()
            

def get_behavior_tree_list(xml_path):
    root = ET.parse(xml_path)
    behavior_Trees = root.findall("BehaviorTree")
    return [tree.get("ID") for tree in behavior_Trees]

app = QApplication(sys.argv)

window = MainWindow()
window.show()

try:
    app.exec()
finally:
    pass
    #if window.game_thread != None:
        #window.game_thread.join()
        #print("closing")
        #os.kill(window.game_process.pid, signal.SIGTERM)
#input()