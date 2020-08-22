import tkinter as tk
from image_viewer import ImageViewer
from screenshot import LilSnippy
from file_management import FileManagement
from time import time
from math import floor
class Marker(tk.Frame):
    def __init__(self, master, x, y, marker_canvas, height, width, columns, rows, folder_path):
        self.master = master
        self.x = x
        self.y = y
        self.marker_canvas = marker_canvas
        self.height = height
        self.width = width
        self.columns = columns
        self.rows = rows
        self.canvas_x = self.marker_canvas.canvasx(x)
        self.canvas_y = self.marker_canvas.canvasy(y)
        
        self.annotator = "wh"
        self.body_type = tk.StringVar()
        self.body_type.set("drop")
        self.var_GR = tk.BooleanVar()
        self.var_MAF = tk.BooleanVar()
        self.var_MP = tk.BooleanVar()
        self.var_unsure = tk.BooleanVar()
        self.grid_id = self.get_grid(self.canvas_x, self.canvas_y)
        self.notes = tk.StringVar()
        
        marker = tk.Toplevel() #create window
        marker.title("popup")
        marker.grab_set()
        
        option_list = [
            "drop", 
            "crescent", 
            "spear", 
            "green spear", 
            "saturn", 
            "rod", 
            "green rod",  
            "ring", 
            "kettlebell", 
            "multi inc"
        ]
        
        dropdown = tk.OptionMenu(marker, self.body_type, *option_list)
        grC = tk.Checkbutton(marker, text = "GR", anchor ="w", variable = self.var_GR, onvalue = True, offvalue = False)
        mafC = tk.Checkbutton(marker, text = "MAF", anchor ="w", variable = self.var_MAF, onvalue = True, offvalue = False)
        mpC = tk.Checkbutton(marker, text = "MP", anchor ="w", variable = self.var_MP, onvalue = True, offvalue = False)
        unsure = tk.Checkbutton(marker, text = "UNSURE", variable = self.var_unsure, onvalue = True, offvalue = False)
        note_entry = tk.Entry(marker, textvariable = self.notes)
        button_ok = tk.Button(marker, text = "OK", command = lambda: self.draw(marker))
        
        dropdown.grid(row = 0, column = 0)
        grC.grid(row = 0, column = 1, sticky = 'w')
        mafC.grid(row = 1, column = 1, sticky = 'w')
        mpC.grid(row = 2, column = 1, sticky = 'w')
        unsure.grid(row = 0, column = 2)
        note_entry.grid(row = 3, column = 1)
        button_ok.grid(row = 2, column = 2)
        
        self.folder_path = folder_path

    def get_data(self):
        time_added = int(time())
        body_file_name = str(self.body_type.get()) + "_" + str(time_added)
        annotation_file_name = body_file_name + "_ANNOTATION"
        fm = FileManagement(self.folder_path)
        
        data = {"time": time_added,
                "annotator_name": self.annotator,
                "body_name": self.body_type.get(),
                "body_number": fm.count_body_type(self.body_type.get()) + 1,
                "x": self.canvas_x,
                "y": self.canvas_y,
                "grid_id": self.grid_id,
                "GR": self.var_GR.get(),
                "MAF": self.var_MAF.get(),
                "MP": self.var_MP.get(),
                "unsure": self.var_unsure.get(),
                "notes": self.notes.get(),
                "body_file_name": body_file_name + ".png",
                "annotation_file_name": annotation_file_name + ".png"
                }
        return data
        
    def get_grid(self, x, y):
        
        row_num = floor(y / (self.height / self.rows))
        column_num = floor(x / (self.width / self.columns))
        key = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        return key[(row_num * self.columns) + column_num]

    
    def call_screenshot(self, data):
        app = LilSnippy(self.master, data, self.folder_path, self.marker_canvas)
        app.create_screen_canvas()
        
    def draw(self, marker):
        data = self.get_data()
        marker.destroy()
        self.call_screenshot(data)


class GridMark():
    def __init__(self, marker_canvas, folder_path, body_info):
        self.marker_canvas = marker_canvas
        self.folder_path = folder_path
        self.body_name = body_info["body_name"]
        self.body_number = body_info["body_number"]
        self.x = body_info["x"]
        self.y = body_info["y"]
        self.time = body_info["time"]
        self.tag = "m" + str(self.time)
        self.marker_canvas.create_text(self.x, self.y, font = ("Calibri", 24, "bold"), fill = 'WHITE', activefill = "red",
                                       text = self.get_letter(self.body_name), tag = self.tag)
        
        self.marker_canvas.tag_bind(self.tag, '<ButtonPress-1>', self.on_click)
        self.marker_canvas.update 
        
    def on_click(self, event):
        time = self.time
        ImageViewer(self.folder_path, self.marker_canvas).open_file(time)
        
    def get_letter(self, string): #used with draw
        body_index = {"drop": "d",
                    "crescent": "c",
                    "spear": "s",
                    "green spear": "grs",
                    "saturn": "sa",
                    "rod": "r",
                    "ring": "ri",
                    "kettlebell": "kb",
                    "multi inc": "mi"}
        return body_index[string]

