import tkinter as tk
from image_viewer import ImageViewer
from file_management import FileManagement

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
