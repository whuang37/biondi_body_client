import sqlite3
import os 
from shutil import copy
from PIL import Image
from grid_tracker import GridRandomizer
class FileManagement():
    """A collection of functions used in sqlite3 data manipulation.

    Functions in this module are used for a mixture data manipulation. Body information
    is saved, then added to database where different functions will pull to perform
    actions like exporting, saving, and deleting images

    Attributes:
        folder_path (str): the directory to the selected folder where all images
            are saved
        conn: A connection to the sqlite3 database 
        c: the cursor the the previously mentioned sqlite3 database
        
    Typical usage example:
        fm = FileManagement(new_folder_path)
        bar = fm.function_bar()
    """
    
    def __init__(self, folder_path):
        self.folder_path = folder_path
        try:
            self.conn = sqlite3.connect(self.folder_path + 'body_database.db')
            self.c = self.conn.cursor()
        except sqlite3.Error as error:
            print("Error while connecting to sqlite", error)
            self.conn.close()
            self.c.close()

    def close(self):
        self.conn.commit()
        self.c.close()
        self.conn.close()
    
    def get_grid(self):
        get_grid_query = '''SELECT * FROM grid'''
        self.c.execute(get_grid_query)
        
        result = self.c.fetchall()
        return result
    
    def finish_grid(self, grid_id, state):
        finish_grid_query = '''UPDATE grid
                SET FINISHED = ? 
                WHERE GRID_ID = ?'''
        
        self.c.execute(finish_grid_query, (state, grid_id))
        self.close()
        
    def count_body_type(self, type):
        """Fetches the number of x biondi body.
        
        Retrieves the number of rows with the selected biondi body type. 
        
        Args:
            type (str): a type of biondi body. Must be same as ones entered through dict.
        
        Returns:
            c_result[0] (int): Return value with the number of selected body in the database.
        """
        
        count_query = '''SELECT COUNT(*) 
                        FROM bodies WHERE BODY_NAME = ?'''
        self.c.execute(count_query, (type,))
        c_result = self.c.fetchone()
        return c_result[0]
    
    def initiate_folder(self, img_path, name):
        """Preps a folder for biondi body analysis.
        
        Takes a folder directory and creates a new database and gridfile
        within the folder for future case analysis. 
        
        Args:
            img_path (str): the path of the grid file being initiated into a new 
                casefolder.
        """

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
        
        create_grid_query = '''CREATE TABLE IF NOT EXISTS grid (GRID_ID TEXT NOT NULL,
                                                                    FINISHED INTEGER)'''
        self.c.execute(create_grid_query)
        
        create_name_query = '''CREATE TABLE IF NOT EXISTS name (NAME TEXT NOT NULL)'''
        self.c.execute(create_name_query)
        
        randomized = GridRandomizer().get_final_order()
        random_list = []
        
        for i in randomized:
            x = (i, False)
            random_list.append(x)
            
        add_grid_query = '''INSERT INTO grid (GRID_ID, FINISHED)
                                                VALUES(?, ?)'''
        self.c.executemany(add_grid_query, random_list)
        
        add_name_query = '''INSERT INTO name (NAME) VALUES(?)'''
        self.c.execute(add_name_query, (name, ))

        self.close()
        
    def get_annotator_name(self):
        name_query = '''SELECT * FROM name'''
        self.c.execute(name_query)
        name = self.c.fetchone()
        self.close()
        return name[0]
        
                        
    def save_image(self, body_info, body_img, annotation_img):
        """Saves screenshots as image files and adds information to database.
        
        Takes the pillow images created in screenshotting and converts them to .png. 
        In doing so, adds all relevant information entered in the marker popup into
        the database for future use.
        
        Args:
            body_info (dict): a collection of information created from the marker popup.
                Dictionary values are a mixture of strings and ints, with booleans converted
                to binary when entered into the database.
            body_img (PIL img): image of just the biondi body
            annotation_img (pil img): image of just the annotation.
        """
            
        body_info["body_number"] = self.count_body_type(body_info["body_name"]) + 1
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
    
    def get_image_time(self, time):
        select_time_query = '''SELECT *
                FROM bodies 
                WHERE TIME = ?'''

        self.c.execute(select_time_query, (time,))
        row = self.c.fetchone()
        self.close()
        
        return self.convert_tuple(row)
        
    def get_image(self, body_name, body_number):
        """Fetch image information from database.
        
        Use the name and number of a specified body to find its pertinent
        information for later usage.
        
        Args:
            body_name (str): name of body. Must be as included in the dict.
            body_number (int): Number of specific body.
            
        Returns:
            row (dict): a dict of all the values included in the database in 
                the order of (time (int), annotator name (str), body name (str), 
                body number (int), x position (int),y position (int), grid id (str),
                green ring (int), multiautoflorescence (int), multiprong (int), 
                unsure (int), notes (str), body file name (str), and
                annotation file name (str). Values may be enclosed in another tuple.
        """
            
        select_query = '''SELECT *
                        FROM bodies 
                        WHERE BODY_NAME = ? AND BODY_NUMBER = ?'''
        
        self.c.execute(select_query, (body_name, body_number))
        row = self.c.fetchone()
        self.close()
        
        return self.convert_tuple(row)
    
    def convert_tuple(self, group):
        data = {}
        i = 0
        for choice in ("time", "annotator_name", "body_name", "body_number", 
                        "x", "y", "grid_id", "GR", "MAF", "MP", "unsure", 
                        "notes", "body_file_name", "annotation_file_name"):
            data[choice] = group[i]
            i += 1
            
        for choice in ("GR", "MAF", "MP", "unsure"): #can make into function later
            if data[choice] == 1:
                data[choice] = True
            else:
                data[choice] = False
        return data
    
    def secondary_name_grouping(self, name, params):
        """Get appropriate amount of placeholders.
        
        Function query_image needs to have a set of placeholders for use 
        to dictate whether it will show all bodies or just bodies with GR,
        MAF, or MP. This function creates either 1 or 2 placeholders for the 
        'IN' logic in the query. It also appends the True or False as binary 
        to scan the database appropriately.
        
        Args:
            name (bool): True or false whether the user wants just the secondary 
                annotation as True.
            params (list): List of parameters for the query in query image
            
        Returns:
            param_ph (list): Appended parameter list with GR, MAF, and MP values
                listed.
        """

        if name:
            param_ph = "?"
            params.append(1)
        else: 
            param_ph = "?,?"
            params.append(0)
            params.append(1)
        return param_ph

    def query_images(self, body_param, GR_param, MAF_param, MP_param, unsure_param):
        """Takes a set of parameters to pull all images that fall under params.
        
        Using a series of strings and bools that can be dictated through an image searcher,
        query_image can pull all the relevant bodies for listing or viewing. Takes the params
        to add the appropriate amount of placeholders for use in SQL searching.
        
        Args:
            body_param (list): a list of parameters including a list of all 
                requested biondi types which is later appended with integers
                on GR, MAF, MP, or unsure.
            GR_param (bool): True if sorting by only GR
            MAF_param (bool): True if sorting by only MAF
            MP_param (bool): True if sorting by only MP
            unsure_param (bool): True if sorting by only unsure
            
        Returns: 
            group (tuple): Tuple of time (int), body name (str), body number (int), 
                x position (int), and y position (int). Values may be included in another
                tuple 
        """
        
        body_param_ph = "?,"*(len(body_param)-1)+"?"
        
        GR_param_ph = self.secondary_name_grouping(GR_param, body_param)
        MAF_param_ph = self.secondary_name_grouping(MAF_param, body_param)
        MP_param_ph = self.secondary_name_grouping(MP_param, body_param)
        unsure_param_ph = self.secondary_name_grouping(unsure_param, body_param)
        
        group_query = '''SELECT TIME, BODY_NAME, BODY_NUMBER, X_POSITION, Y_POSITION
                        FROM bodies 
                        WHERE BODY_NAME IN ({0}) 
                        AND GR IN ({1}) 
                        AND MAF IN ({2}) 
                        AND MP IN ({3})
                        AND UNSURE IN ({4})
                        ORDER BY TIME DESC'''.format(body_param_ph, GR_param_ph, MAF_param_ph, MP_param_ph, unsure_param_ph)
        
        self.c.execute(group_query, body_param)
        group = self.c.fetchall()
        
        self.close()
        return group
    
    def edit_info(self, edited_info):
        edit_query = '''UPDATE bodies
                        SET BODY_NAME = ?,
                        GR = ?,
                        MAF = ?,
                        MP = ?, 
                        UNSURE = ?, 
                        NOTES = ? 
                        WHERE TIME = ?'''
                        
        
        self.c.execute(edit_query, edited_info)
        self.close()


                        
    def renumber_img(self, body_name, body_number):
        """Fixes body number if any discrepancies occur.
        
        Pulls a tuple of all the times sorted from oldest to newest
        of a select body type. Reiterates through the entire database
        of a select body and renumber the body numbers chronologically from
        a certain body number.
        
        Args:
            body_name (str): name of the wanted body
            body_number (int): number of the selected body where all following
                bodies would be renumbered Starts from 1. 
            
        Returns:
            bool: False if there are no bodies in the selected body type
        """
        
        renumber_query = '''UPDATE bodies 
                            SET BODY_NUMBER = ?
                            WHERE BODY_NAME = ? AND TIME = ?'''
        
        get_time_query = '''SELECT TIME 
                            from bodies where 
                            BODY_NAME = ?
                            ORDER BY TIME'''
                                        
        
        self.c.execute(get_time_query, (body_name,)) 
        time = self.c.fetchall()
        
        num_bodies = len(time)
        if num_bodies == 0:
            return False
        
        for i in range(body_number, num_bodies + 1):
            self.c.execute(renumber_query, (i, body_name, time[i-1][0]))

    def delete_img(self, body_name, body_number):
        delete_query = '''DELETE 
                        FROM bodies 
                        WHERE BODY_NAME = ? and BODY_NUMBER = ?''' 
                        
        self.c.execute(delete_query, (body_name, body_number))
        self.renumber_img(body_name, body_number)
        self.close()

    def refresh_database(self): #come back to later
        body_names = ["drop", 
                    "crescent", 
                    "spear", 
                    "green spear", 
                    "saturn", 
                    "rod", 
                    "ring", 
                    "kettlebell", 
                    "multi inc"]
        for items in body_names:
            self.renumber_img(items, 1)
            
        refresh_query = '''UPDATE bodies ORDER BY BODY_NAME, BODY_NUMBER'''
        self.c.execute(refresh_query)
        self.close()
            
            
    def merge_img(self, img, annotation, new_name):
        """Concentate annotation and body image to one png
        
        Take two image files and merge them together with the annotations 
        on top. The file is then named accordingly
        
        Args:
            img (str): name of the image file to be merged
            annotation (str): name of the annotation file to be merged
            new_name (str): the new name to be given to the new concentated
                image
        """
        
        body_img = Image.open(self.folder_path + img)
        annotation_img = Image.open(self.folder_path + annotation)
        body_img.paste(annotation_img, (0,0), annotation_img)
        body_img.save(new_name)

    def export_case(self, new_folder_path, case_name):
        """Turns all images into concentated images
        
        Iterates through all rows in the database to turn each row into
        a singular png. ALso creates a new file name in the format of
        BODY NAME_ANNOTATOR INITIALS_BODY NUMBER_GR_MAF_MP. GR, MAF, and 
        MP are optional if the body does not possess those characteristics.
        
        Args:
            new_folder_path (str): File directory where the exported case will
                be saved
        """

        all_files_query = '''SELECT ANNOTATOR_NAME, 
                            BODY_NAME, 
                            BODY_NUMBER, 
                            GR, 
                            MAF, 
                            MP, 
                            BODY_FILE_NAME, 
                            ANNOTATION_FILE_NAME
                            FROM bodies'''
                            
        self.c.execute(all_files_query)
        
        while True:
            body_info = self.c.fetchone()
            if body_info is None:
                break
            img_name = "{0}{1}_{2}_{3}_{4}".format(new_folder_path, case_name, body_info[1], body_info[0], body_info[2])
            if body_info[3] == 1:
                img_name += "_GR"
            if body_info[4] == 1:
                img_name += "_MAF"
            if body_info[5] == 1:
                img_name += "_MP"
            img_name += ".png"
            
            print(img_name)
            self.merge_img(body_info[6], body_info[7], img_name)

if __name__ == "__main__":
    fm = FileManagement("")
    #print(fm.count_body_type("saturn"))
    #fm.edit_info(("rod", 1, 1, 1, 1, "dsasd", 1597648898))
    #print(fm.get_image("crescent", 1))
    #print(fm.query_image(["saturn", "kettlebell"], False, False, False, False,))
    #fm.delete_img("multi inc", 4)
    fm.renumber_img("saturn", 1)