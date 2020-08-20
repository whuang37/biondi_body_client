import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from math import floor
from screenshot import LilSnippy
from time import time
from image_viewer import ImageViewer
from file_management import FileManagement
from markings import GridMark
import grid_tracker



class Grid_Window(tk.Frame):
    def __init__(self, master, main_canvas, final_order, width, height):
        self.master = master
        self.main_canvas = main_canvas
        self.final_order = final_order
        self.total_squares = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvw"

        self.width = height
        self.height = height
        
        self.i = 0
        self.gw = tk.Toplevel()
        self.gw.geometry("150x75")
        self.v = tk.StringVar()
        self.v.set(str(self.final_order[self.i]))
        self.text = tk.Label(self.gw, text = "Current Grid Square:")
        self.text.grid(row = 0, column = 1)
        self.current_grid = tk.Label(self.gw, text = self.v.get())
        self.current_grid.grid(row = 1, column = 1)


        self.forward_button = tk.Button(self.gw, text = ">", command = self.forward)
        self.forward_button.grid(row=2, column = 2)
        

        self.backward_button = tk.Button(self.gw, text = "<", command = self.backward)
        self.backward_button.grid(row=2, column = 0)

        self.jumpto_button = tk.Button(self.gw, text = "Jump to", command = self.move_canvas)
        self.jumpto_button.grid(row = 2, column  = 1)

    def get_scrollx(self):
        index = self.total_squares.find(self.final_order[self.i])
        w = self.width/7
        return (index % 7) * w

    def get_scrolly(self):
        row1 = "ABCDEFG"
        row2 = "HIJKLMN"
        row3 = "OPQRSTU"
        row4 = "VWXYZab"
        row5 = "cdefghi"
        row6 = "jklmnop"
        row7 = "qrstuvw"
        scrolly = 0
        h = self.height/7
        
        if row2.find(self.final_order[self.i]) != -1:
            scrolly = h
        if row3.find(self.final_order[self.i]) != -1:
            scrolly = h * 2
        if row4.find(self.final_order[self.i]) != -1:
            scrolly = h * 3 
        if row5.find(self.final_order[self.i]) != -1:
            scrolly = h * 4
        if row6.find(self.final_order[self.i]) != -1:
            scrolly = h * 5
        if row7.find(self.final_order[self.i]) != -1:
            scrolly = h * 6 

        return scrolly        

    def move_canvas(self):
        scrollx = self.get_scrollx()
        scrolly = self.get_scrolly()

        offsetx = +1 if scrollx >= 0 else 0
        offsety = +1 if scrolly >= 0 else 0
        self.main_canvas.xview_moveto(float(scrollx + offsetx)/self.width)
        self.main_canvas.yview_moveto(float(scrolly + offsety)/self.height)
        self.master.geometry("600x600")
        
    def forward(self):
        self.i += 1 
        self.v.set(str(self.final_order[self.i]))
        self.current_grid.configure(text = self.v.get())
        self.current_grid.update()

    def backward(self): 
        self.i -= 1 
        self.v.set((self.final_order[self.i]))
        self.current_grid.configure(text = self.v.get())
        self.current_grid.update()

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
    ''' Advanced zoom of the image  we did this yep cock'''
    def __init__(self, mainframe, path):
        self.box = 0
        self.master = mainframe

        ''' Initialize the main Frame '''
        tk.Frame.__init__(self, master=mainframe)
        self.master.title('Zoom with mouse wheel')
        # Vertical and horizontal scrollbars for canvas

        #coord bar
        self.mousex = tk.IntVar()
        self.mousey = tk.IntVar()
        self.mousex.set(0)
        self.mousey.set(0)
        self.coord_label = tk.Label(self.master, text = "X: " + str(self.mousex.get()) + "  " + "Y: " + str(self.mousey.get())) 
        self.coord_label.grid(row = 3, column = 0, sticky = 'sw')

        #tool bar
        self.toolbar = tk.Frame(self.master, bg = "gray")
        self.toolbar.grid(row = 0, column = 0, sticky = 'nswe' )

        self.gt = grid_tracker.GridRandomizer()
        self.gt.set_final_order()
        self.final_order = self.gt.get_final_order()
        self.gridw_button = tk.Button(self.toolbar, text = "Open Grid", command = self.open_grid_window)
        self.gridw_button.pack(side = "left", padx = 2 , pady = 2)

        self.open_new_button = tk.Button(self.toolbar, text = "Open New Folder", command = self.open_new_folder)
        self.open_new_button.pack(side = "left", padx = 2, pady = 2)
        
        self.image_viewer_button = tk.Button(self.toolbar, text = "Image Viewer", command = self.open_image_viewer)
        self.image_viewer_button.pack(side = "left", padx = 2, pady = 2)



        # Create canvas and put image on it
        self.canvas = tk.Canvas(self.master, highlightthickness=0)
        

        self.marker_canvas = self.canvas
        self.grid_canvas = self.canvas
        
        self.canvas.grid(row=1, column=0, sticky='nswe')
        self.canvas.update()  # wait till canvas is created

        vbar = tk.Scrollbar(self.master, orient='vertical', command = self.canvas.yview)
        hbar = tk.Scrollbar(self.master, orient='horizontal', command = self.canvas.xview)
        vbar.grid(row=1, column=1, sticky='ns')
        hbar.grid(row=2, column=0, sticky='we')
        self.canvas.configure(xscrollcommand = hbar.set, yscrollcommand = vbar.set, xscrollincrement = '2', yscrollincrement = '2')
        self.canvas.update()

        # Make the canvas expandable
        self.master.rowconfigure(1, weight=1)
        self.master.columnconfigure(0, weight=1)
        # Bind events to the Canvas
        #self.canvas.bind('<Configure>', self.show_image)  # canvas is resized
        #self.canvas.bind('<ButtonPress-3>', self.move_from)
        #self.canvas.bind('<B3-Motion>', self.move_to)
        self.canvas.bind('<MouseWheel>', self.verti_wheel)
        self.canvas.bind('<Shift-MouseWheel>', self.hori_wheel)  
        self.canvas.bind('<Button-2>', self.open_popup)
        self.canvas.bind('<Motion>', self.update_coords)
        #self.canvas.bind('<Return>', self.call_screenshot)

        self.folder_path = path + "/"
        self.image = Image.open(self.folder_path + "gridfile.jpg")  # open image
        self.width, self.height = self.image.size
        self.imscale = 1.0  # scale for the canvas image
        self.delta = 1.3  # zoom magnitude
        # Put image into container rectangle and use it to set proper coordinates to the image
        self.container = self.canvas.create_rectangle(0, 0, self.width, self.height, width=0)

        self.show_image()

        self.master.geometry(str(500) + "x" + str(500))
        
        self.rows = 7
        self.columns = 7
        self.create_grid()
        
        self.initiate_markers()
        
    def open_image_viewer(self):
        ImageViewer(self.folder_path, self.marker_canvas) #TEST CLASS
        
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
        
        if round(box_width / 5) > round(box_height / 5):
            padding = round(box_height / 5)
        else:
            padding = round(box_width / 5)
            
        key = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        n = 0
        for i in range(0, self.rows):
            for j in range(0, self.columns):
                self.grid_canvas.create_text((j + 1) * box_height - padding, (i + 1) * box_width - padding,
                                            font = ("Calibri", 24), fill = 'WHITE', text = key[n], tag = key[n])
                n += 1
                if n > num_squares:
                    break
   
    def initiate_markers(self):
        all_bodies = ["drop", "crescent", "spear", "green spear", "saturn", 
                        "rod", "green rod", "ring", "kettlebell", "multi inc"]
        fm = FileManagement(self.folder_path)
        data = fm.query_images(all_bodies, False, False, False, False)
        for i in data:
            body_info = {}
            x = 0
            for choice in ("time", "body_name", "body_number", "x", "y"):
                body_info[choice] = i[x]
                x += 1
            GridMark(self.marker_canvas, self.folder_path, body_info)
    
    def open_grid_window(self):
        Grid_Window(self.master, self.canvas, self.final_order, self.width, self.height)

    def open_new_folder(self):
        path = filedialog.askdirectory()
        i = Application(root, path=path)

    def update_coords(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.mousex.set(x)
        self.mousey.set(y)

        self.coord_label.configure(text = "X: " + str(self.mousex.get()) + "  " + "Y: " + str(self.mousey.get()))
        self.coord_label.update()

    def open_popup(self, event):
        x = event.x
        y = event.y
        Marker(self.master, x, y, self.marker_canvas, self.height, self.width, self.columns, self.rows, self.folder_path)
        
    def scroll_y(self, *args, **kwargs):
        ''' Scroll canvas vertically and redraw the image '''
        self.canvas.yview(*args, **kwargs)  # scroll vertically
        #self.show_image()  # redraw the image

    def scroll_x(self, *args, **kwargs):
        ''' Scroll canvas horizontally and redraw the image '''
        self.canvas.xview(*args, **kwargs)  # scroll horizontally
        #self.show_image()  # redraw the image

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
        #self.show_image()

    def hori_wheel(self, event):
        if event.num == 5 or event.delta == -120:  # scroll down
            self.canvas.xview('scroll', 20, 'units')
        if event.num == 4 or event.delta == 120:
            self.canvas.xview('scroll', -20, 'units')
        #self.show_image()

    def show_image(self, event=None):
        ''' Show image on the Canvas '''
        # bbox1 = self.canvas.bbox(self.container)  # get image area
        # Remove 1 pixel shift at the sides of the bbox1
        # bbox1 = (bbox1[0] + 1, bbox1[1] + 1, bbox1[2] - 1, bbox1[3] - 1)
        # bbox2 = (self.canvas.canvasx(0),  # get visible area of the canvas
        #         self.canvas.canvasy(0),
        #         self.canvas.canvasx(self.canvas.winfo_width()),
        #         self.canvas.canvasy(self.canvas.winfo_height()))
        # bbox = [min(bbox1[0], bbox2[0]), min(bbox1[1], bbox2[1]),  # get scroll region box
        #         max(bbox1[2], bbox2[2]), max(bbox1[3], bbox2[3])]
        # if bbox[0] == bbox2[0] and bbox[2] == bbox2[2]:  # whole image in the visible area
        #     bbox[0] = bbox1[0]
        #     bbox[2] = bbox1[2]
        # if bbox[1] == bbox2[1] and bbox[3] == bbox2[3]:  # whole image in the visible area
        #     bbox[1] = bbox1[1]
        #     bbox[3] = bbox1[3]
        self.canvas.configure(scrollregion=self.canvas.bbox(self.container))  # set scroll region
        # x1 = max(bbox2[0] - bbox1[0], 0)  # get coordinates (x1,y1,x2,y2) of the image tile
        # y1 = max(bbox2[1] - bbox1[1], 0)
        # x2 = min(bbox2[2], bbox1[2]) - bbox1[0]
        # y2 = min(bbox2[3], bbox1[3]) - bbox1[1]
        # if int(x2 - x1) > 0 and int(y2 - y1) > 0:  # show image if it in the visible area
        #     x = min(int(x2 / self.imscale), self.width)   # sometimes it is larger on 1 pixel...
        #     y = min(int(y2 / self.imscale), self.height)  # sometimes not
        image = self.image
        imagetk = ImageTk.PhotoImage(image)
        imageid = self.canvas.create_image(0,0,anchor= 'nw', image=imagetk)
        self.canvas.lower(imageid)  # set image into background
        self.canvas.imagetk = imagetk  # keep an extra reference to prevent garbage-collection
            
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


def open_image():
    path = filedialog.askdirectory()
    i = Application(root, path=path)
    
def initiate_folder():
    folder_path = filedialog.askdirectory()
    folder_path = folder_path + "/"
    file_name = filedialog.askopenfilename()
    FileManagement(folder_path).initiate_folder(file_name)
    
if __name__ == "__main__":
    root = tk.Tk()

    find_image_button = tk.Button(root, text="Pick Image File", command = open_image)
    find_image_button.grid(column = 0, row = 0)
    initiate_folder_button = tk.Button(root, text = "Initiate Folder", command = initiate_folder)
    initiate_folder_button.grid(column = 0, row = 1)
    root.mainloop()