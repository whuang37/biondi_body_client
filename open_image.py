import tkinter as tk
import random
from tkinter import filedialog
from PIL import Image, ImageTk
import sys
from math import floor
import screenshot


initials = tk.StringVar #global var for user initials

class AutoScrollbar(tk.Scrollbar):
    ''' A scrollbar that hides itself if it's not needed.
        Works only if you use the grid geometry manager '''
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.grid_remove()
        else:
            self.grid()
            tk.Scrollbar.set(self, lo, hi)

    def pack(self, **kw):
        raise tk.TclError('Cannot use pack with this widget')

    def place(self, **kw):
        raise tk.TclError('Cannot use place with this widget')

class Application(tk.Frame):
    ''' Advanced zoom of the image '''
    def __init__(self, mainframe, path):
        self.box = 0
        self.master = mainframe
        ''' Initialize the main Frame '''
        tk.Frame.__init__(self, master=mainframe)
        self.master.title('Zoom with mouse wheel')
        # Vertical and horizontal scrollbars for canvas
        vbar = AutoScrollbar(self.master, orient='vertical')
        hbar = AutoScrollbar(self.master, orient='horizontal')
        vbar.grid(row=0, column=1, sticky='ns')
        hbar.grid(row=1, column=0, sticky='we')
        # Create canvas and put image on it
        self.canvas = tk.Canvas(self.master, highlightthickness=0, xscrollcommand = hbar.set, yscrollcommand = vbar.set)
        self.canvas.configure(yscrollincrement = '2')
        self.canvas.configure(xscrollincrement = '2')

        self.marker_canvas = self.canvas
        self.grid_canvas = self.canvas
        
        self.canvas.grid(row=0, column=0, sticky='nswe')
        self.canvas.update()  # wait till canvas is created
        vbar.configure(command=self.scroll_y)  # bind scrollbars to the canvas
        hbar.configure(command=self.scroll_x)
        # Make the canvas expandable
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        # Bind events to the Canvas
        self.canvas.bind('<Configure>', self.show_image)  # canvas is resized
        self.canvas.bind('<ButtonPress-3>', self.move_from)
        self.canvas.bind('<B3-Motion>',     self.move_to)
        self.canvas.bind('<MouseWheel>', self.verti_wheel)
        self.canvas.bind('<Shift-MouseWheel>', self.hori_wheel)  
        self.canvas.bind("<Button-1>", self.open_popup)
        #self.canvas.bind('<Return>', self.call_screenshot)

        self.image = Image.open(path)  # open image
        self.width, self.height = self.image.size
        self.imscale = 1.0  # scale for the canvas image
        self.delta = 1.3  # zoom magnitude
        # Put image into container rectangle and use it to set proper coordinates to the image
        self.container = self.canvas.create_rectangle(0, 0, self.width, self.height, width=0)
        self.show_image()

        self.master.geometry(str(self.width) + "x" + str(self.height))
        
        self.rows = 7
        self.columns = 7
        self.create_grid()

    def create_grid(self):
        box_width =  round(self.width / self.columns)
        box_height = round(self.height / self.rows)
        num_v_lines = self.rows - 1
        num_h_lines = self.rows - 1
        
        for i in range(0, num_v_lines):
            self.grid_canvas.create_line(box_width * (i+1), 0, box_width * (i+1), self.height,
                                        fill = "white", width = 4)
        for i in range(0, num_h_lines):
            self.grid_canvas.create_line(0, box_height * (i+1), self.width, box_height * (i+1),
                                        fill = "white", width = 4)
            
        num_squares = self.rows * self.columns
        padding = 50
        key = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        n = 0
        for i in range(0, self.rows):
            for j in range(0, self.columns):
                self.grid_canvas.create_text((j + 1) * box_height - padding, (i + 1) * box_width - padding,
                                            font = ("Calibri", 24), fill = 'WHITE', text = key[n], tag = key[n])
                n += 1
                if n > num_squares:
                    break

    def open_popup(self, event):
        x = event.x
        y = event.y
        Marker(self.master, x, y, self.marker_canvas, self.height, self.width, self.columns, self.rows)
        # print(app.get_data())
        
    def scroll_y(self, *args, **kwargs):
        ''' Scroll canvas vertically and redraw the image '''
        self.canvas.yview(*args, **kwargs)  # scroll vertically
        self.show_image()  # redraw the image

    def scroll_x(self, *args, **kwargs):
        ''' Scroll canvas horizontally and redraw the image '''
        self.canvas.xview(*args, **kwargs)  # scroll horizontally
        self.show_image()  # redraw the image

    def move_from(self, event):
        ''' Remember previous coordinates for scrolling with the mouse '''
        self.canvas.scan_mark(event.x, event.y)

    def move_to(self, event):
        ''' Drag (move) canvas to the new position '''
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        self.show_image()  # redraw the image

    def verti_wheel(self, event):
        if event.num == 5 or event.delta == -120:  # scroll down
            self.canvas.yview('scroll', 20, 'units')
        if event.num == 4 or event.delta == 120:
            self.canvas.yview('scroll', -20, 'units')
        self.show_image()

    def hori_wheel(self, event):
        if event.num == 5 or event.delta == -120:  # scroll down
            self.canvas.xview('scroll', 20, 'units')
        if event.num == 4 or event.delta == 120:
            self.canvas.xview('scroll', -20, 'units')
        self.show_image()

    def show_image(self, event=None):
        ''' Show image on the Canvas '''
        bbox1 = self.canvas.bbox(self.container)  # get image area
        # Remove 1 pixel shift at the sides of the bbox1
        bbox1 = (bbox1[0] + 1, bbox1[1] + 1, bbox1[2] - 1, bbox1[3] - 1)
        bbox2 = (self.canvas.canvasx(0),  # get visible area of the canvas
                self.canvas.canvasy(0),
                self.canvas.canvasx(self.canvas.winfo_width()),
                self.canvas.canvasy(self.canvas.winfo_height()))
        bbox = [min(bbox1[0], bbox2[0]), min(bbox1[1], bbox2[1]),  # get scroll region box
                max(bbox1[2], bbox2[2]), max(bbox1[3], bbox2[3])]
        if bbox[0] == bbox2[0] and bbox[2] == bbox2[2]:  # whole image in the visible area
            bbox[0] = bbox1[0]
            bbox[2] = bbox1[2]
        if bbox[1] == bbox2[1] and bbox[3] == bbox2[3]:  # whole image in the visible area
            bbox[1] = bbox1[1]
            bbox[3] = bbox1[3]
        self.canvas.configure(scrollregion=bbox)  # set scroll region
        x1 = max(bbox2[0] - bbox1[0], 0)  # get coordinates (x1,y1,x2,y2) of the image tile
        y1 = max(bbox2[1] - bbox1[1], 0)
        x2 = min(bbox2[2], bbox1[2]) - bbox1[0]
        y2 = min(bbox2[3], bbox1[3]) - bbox1[1]
        if int(x2 - x1) > 0 and int(y2 - y1) > 0:  # show image if it in the visible area
            x = min(int(x2 / self.imscale), self.width)   # sometimes it is larger on 1 pixel...
            y = min(int(y2 / self.imscale), self.height)  # sometimes not
            image = self.image.crop((int(x1 / self.imscale), int(y1 / self.imscale), x, y))
            imagetk = ImageTk.PhotoImage(image.resize((int(x2 - x1), int(y2 - y1))))
            imageid = self.canvas.create_image(max(bbox2[0], bbox1[0]), max(bbox2[1], bbox1[1]),
                                                anchor= 'nw', image=imagetk)
            self.canvas.lower(imageid)  # set image into background
            self.canvas.imagetk = imagetk  # keep an extra reference to prevent garbage-collection
            
class Marker(tk.Frame):
    def __init__(self, master, x, y, marker_canvas, height, width, columns, rows):
        self.master = master
        self.x = x
        self.y = y
        self.marker_canvas = marker_canvas
        self.height = height
        self.width = width
        self.columns = columns
        self.rows = rows
        canvas_x = self.marker_canvas.canvasx(x)
        canvas_y = self.marker_canvas.canvasy(y)
        
        self.annotator = initials
        self.body_type = tk.StringVar()
        self.body_type.set("drop")
        self.var_GR = tk.BooleanVar()
        self.var_MAF = tk.BooleanVar()
        self.var_MP = tk.BooleanVar()
        self.var_unsure = tk.BooleanVar()
        self.grid_id = self.get_grid(canvas_x, canvas_y)
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
        button_ok = tk.Button(marker, text = "OK", command = lambda: self.draw(self.body_type.get(), x, y, marker))
        
        dropdown.grid(row = 0, column = 0)
        grC.grid(row = 0, column = 1, sticky = 'w')
        mafC.grid(row = 1, column = 1, sticky = 'w')
        mpC.grid(row = 2, column = 1, sticky = 'w')
        unsure.grid(row = 0, column = 2)
        note_entry.grid(row = 3, column = 1)
        button_ok.grid(row = 2, column = 2)

    def get_data(self):
        data = {"annotator_name": self.annotator,
                "body_type": self.body_type.get(),
                "grid_id": self.grid_id,
                "x": self.x,
                "y": self.y,
                "GR": self.var_GR.get(),
                "MAF": self.var_MAF.get(),
                "MP": self.var_MP.get(),
                "unsure": self.var_unsure.get(),
                "notes": self.notes.get(),
                }
        return data
        
    def get_grid(self, x, y):
        
        row_num = floor(y / (self.height / self.rows))
        column_num = floor(x / (self.width / self.columns))
        key = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        return key[(row_num * self.columns) + column_num]

    def get_letter(self, string): #used with draw
        body_index = {"drop": "d",
                    "crescent": "c",
                    "spear": "s",
                    "saturn": "sa",
                    "rod": "r",
                    "ring": "ri",
                    "kettlebell": "kb",
                    "multi inc": "mi"}
        return body_index[string]
    
    def call_screenshot(self, data):
        app = screenshot.LilSnippy(self.master, data)
        app.create_screen_canvas()
        
    def draw(self, body_type, x, y, marker):
        self.marker_canvas.create_text(x,y, font = "Calibri",fill = 'WHITE', text = self.get_letter(body_type), tag="marker")
        self.marker_canvas.update
        marker.destroy()
        self.call_screenshot(self.get_data())





def open_image(v):

    path = filedialog.askopenfilename()
    i = Application(root, path=path)
    initials = v

if __name__ == "__main__":
    root = tk.Tk()

    find_image_button = tk.Button(root, text="Pick Image File", command = lambda: open_image(v.get()))
    find_image_button.grid(column = 0, row = 0)

    v = tk.StringVar() #initials
    v.set("Enter Initials, eg. \"BJ\"")
    name_entry = tk.Entry(root, textvariable = v)
    name_entry.grid(column = 0, row = 1)

    root.mainloop()

