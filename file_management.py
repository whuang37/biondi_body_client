import sqlite3
import os 
from shutil import copy
class FileManagement():
    def __init__(self, folder_path, annotator):
        self.folder_path = folder_path
        self.annotator = annotator
        self.conn = sqlite3.connect(self.folder_path + 'body_database.db')
        self.c = self.conn.cursor()
    
    def initiate_folder(self, img_path):
        # potentially move this into main
        copy(img_path, self.folder_path + "gridfile.jpg")
        self.c.execute('''CREATE TABLE IF NOT EXISTS bodies (BODY_NAME TEXT NOT NULL, 
                                                            BODY_NUMBER INTEGER NOT NULL,
                                                            X_POSITION INTEGER NOT NULL,
                                                            Y_POSITION INTEGER NOT NULL,
                                                            GR INTEGER,
                                                            MAF INTEGER,
                                                            MP INTEGER,
                                                            UNSURE INTEGER,
                                                            NOTES TEXT,
                                                            BODY_IMAGE_NAME,
                                                            ANNOTATION_IMAGE_NAME)''')
        
    def save_image(self, body_information, body, annotation):
        