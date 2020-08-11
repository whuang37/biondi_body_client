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
    
    def count_body_type(self, type):
        count_query = '''SELECT COUNT(*) 
                        FROM bodies WHERE BODY_NAME = ?'''
        self.c.execute(count_query, (type,))
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
        
    def save_image(self, body_info, body_img, annotation_img):
        body_info["body_number"] = self.count_body_type(body_info["body_type"]) + 1
        body_img.save(self.folder_path + body_info["body_file_name"])
        annotation_img.save(self.folder_path + body_info["annotation_file_name"])
        
        data_values = tuple([body_info[key] for key in body_info])
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
    
    def get_image(self, body_name, body_number):
        select_query = '''SELECT *
                        FROM bodies 
                        WHERE BODY_NAME = ? AND BODY_NUMBER = ?'''
        
        self.c.execute(select_query, (body_name, body_number))
        row = self.c.fetchone()
        
        self.close()
        return row
    
    def secondary_name_grouping(self, name, params):
        if name:
            param_ph = "?"
            params.append(1)
        else: 
            param_ph = "?,?"
            params.append(0)
            params.append(1)
        return param_ph

    def query_image(self, body_param, GR_param, MAF_param, MP_param, unsure_param):
        body_param_ph = "?,"*(len(body_param)-1)+"?"
        
        GR_param_ph = self.secondary_name_grouping(GR_param, body_param)
        MAF_param_ph = self.secondary_name_grouping(MAF_param, body_param)
        MP_param_ph = self.secondary_name_grouping(MP_param, body_param)
        unsure_param_ph = self.secondary_name_grouping(unsure_param, body_param)
        
        params = tuple(body_param)
        print(params)
        group_query = '''SELECT TIME, BODY_NAME, BODY_NUMBER, X_POSITION, Y_POSITION
                        FROM bodies 
                        WHERE BODY_NAME IN ({0}) 
                        AND GR IN ({1}) 
                        AND MAF IN ({2}) 
                        AND MP IN ({3})
                        AND UNSURE IN ({4})'''.format(body_param_ph, GR_param_ph, MAF_param_ph, MP_param_ph, unsure_param_ph)
        
        self.c.execute(group_query, body_param)
        group = self.c.fetchall()
        
        self.close()
        return group
    # def query
    # def delete
    # # def export


if __name__ == "__main__":
    fm = FileManagement("")
    #print(fm.count_body_type("drop"))
    #print(fm.find_image("drop", 6))
    print(fm.query_image(["drop", "saturn", "kettlebell"], True, False, True, True,))