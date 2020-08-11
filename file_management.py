import sqlite3
import os 
from shutil import copy
from PIL import Image
class FileManagement():
    def __init__(self, folder_path):
        self.folder_path = folder_path
        try:
            self.conn = sqlite3.connect(self.folder_path + 'body_database.db')
            self.c = self.conn.cursor()
            
            create_table_query = '''CREATE TABLE IF NOT EXISTS bodies (TIME INTEGER NOT NULL,
                                                    ANNOTATOR_NAME TEXT,
                                                    BODY_NAME TEXT NOT NULL, 
                                                    BODY_NUMBER INTEGER NOT NULL,
                                                    X_POSITION INTEGER NOT NULL,
                                                    Y_POSITION INTEGER NOT NULL,
                                                    GRID_ID TEXT NOT NULL,
                                                    GR INTEGER,
                                                    MAF INTEGER,
                                                    MP INTEGER,
                                                    UNSURE INTEGER,
                                                    NOTES TEXT,
                                                    BODY_FILE_NAME,
                                                    ANNOTATION_FILE_NAME)'''
        
            self.c.execute(create_table_query)
        
        except sqlite3.Error as error:
            print("Error while connecting to sqlite", error)
            self.conn.close()
            self.c.close()

    def close(self):
        self.conn.commit()
        self.c.close()
        self.conn.close()
    
    def count(self, column, type):
        count_query = '''SELECT COUNT(*) FROM bodies WHERE ? = ?'''
        self.c.execute(count_query, (column, type))
        c_result = self.c.fetchone()
        return c_result[0]
    
    def initiate_folder(self, img_path):
        # potentially move this into main
        copy(img_path, self.folder_path + "gridfile.jpg")
        create_table_query = '''CREATE TABLE IF NOT EXISTS bodies (TIME INTEGER NOT NULL,
                                                            ANNOTATOR_NAME TEXT,
                                                            BODY_NAME TEXT NOT NULL, 
                                                            BODY_NUMBER INTEGER NOT NULL,
                                                            X_POSITION INTEGER NOT NULL,
                                                            Y_POSITION INTEGER NOT NULL,
                                                            GRID_ID TEXT NOT NULL,
                                                            GR INTEGER,
                                                            MAF INTEGER,
                                                            MP INTEGER,
                                                            UNSURE INTEGER,
                                                            NOTES TEXT,
                                                            BODY_FILE_NAME TEXT,
                                                            ANNOTATION_FILE_NAME TEXT)'''
        
        self.c.execute(create_table_query)
        self.close()
        
    def save_image(self, body_information, body_img, annotation_img):
        body_information["body_number"] = self.count("BODY_NAME", body_information["body_type"]) + 1
        body_img.save(self.folder_path + body_information["body_file_name"])
        annotation_img.save(self.folder_path + body_information["annotation_file_name"])
        
        data_values = tuple([body_information[key] for key in body_information])
        insert_query = '''INSERT INTO bodies (TIME, 
                                            ANNOTATOR_NAME, 
                                            BODY_NAME, 
                                            BODY_NUMBER, 
                                            X_POSITION, 
                                            Y_POSITION, 
                                            GRID_ID, 
                                            GR, 
                                            MAF, 
                                            MP, 
                                            UNSURE, 
                                            NOTES, 
                                            BODY_FILE_NAME, 
                                            ANNOTATION_FILE_NAME) 
                                            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        
        self.c.execute(insert_query, data_values)
        self.close()
    # def query
    # def delete
    # def export
