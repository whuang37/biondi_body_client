import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from math import floor

from image_viewer import ImageViewer
from file_management import FileManagement
from markings import GridMark, Marker

class Application(tk.Frame):
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
        self.coord_label.grid(row = 4, column = 0, sticky = 'sw')

        # Create canvas and put image on it
        self.canvas = tk.Canvas(self.master, highlightthickness=0)
        self.marker_canvas = self.canvas
        self.grid_canvas = self.canvas
        
        self.canvas.grid(row=1, column=0, sticky='nswe')
        self.grid_canvas.grid(row=1, column=0, sticky='nswe')
        self.marker_canvas.grid(row=1, column=0, sticky='nswe')
        
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
        self.canvas.bind('<Button-3>', self.open_popup)
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

        self.master.geometry(str(600) + "x" + str(600))
        
        self.rows = 7
        self.columns = 7
        self.create_grid()
        
        self.initiate_markers()
        
        #tool bar
        self.toolbar = GridToolbar(self.master, self.folder_path, self.marker_canvas, self.grid_canvas)
        self.toolbar.grid(row = 0, column = 0, sticky = 'nswe' )
        
        #grid window
        grid_window = GridWindow(self.master, self.canvas, self.folder_path, self.width, self.height)
        grid_window.grid(row = 3, column = 0)
        
    def create_grid(self):
        box_width =  round(self.width / self.columns)
        box_height = round(self.height / self.rows)
        num_v_lines = self.rows - 1
        num_h_lines = self.rows - 1
        
        for i in range(0, num_v_lines):
            self.grid_canvas.create_line(box_width * (i+1), 0, box_width * (i+1), self.height,
                                        fill = "white", width = 4, tag = "line")
        for i in range(0, num_h_lines):
            self.grid_canvas.create_line(0, box_height * (i+1), self.width, box_height * (i+1),
                                        fill = "white", width = 4, tag = "line")
            
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
                                            font = ("Calibri", 24), fill = 'WHITE', text = key[n], tag = "letter")
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

    def scroll_x(self, *args, **kwargs):
        ''' Scroll canvas horizontally and redraw the image '''
        self.canvas.xview(*args, **kwargs)  # scroll horizontally

    # def move_from(self, event):
    #     ''' Remember previous coordinates for scrolling with the mouse '''
    #     self.canvas.scan_mark(event.x, event.y)

    # def move_to(self, event):
    #     ''' Drag (move) canvas to the new position '''
    #     self.canvas.scan_dragto(event.x, event.y, gain=1)
    #     self.show_image()  # redraw the image

    def verti_wheel(self, event):
        if event.num == 5 or event.delta == -120:  # scroll down
            self.canvas.yview('scroll', 20, 'units')
        if event.num == 4 or event.delta == 120:
            self.canvas.yview('scroll', -20, 'units')

    def hori_wheel(self, event):
        if event.num == 5 or event.delta == -120:  # scroll down
            self.canvas.xview('scroll', 20, 'units')
        if event.num == 4 or event.delta == 120:
            self.canvas.xview('scroll', -20, 'units')

    def show_image(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox(self.container))  # set scroll region
        image = self.image
        imagetk = ImageTk.PhotoImage(image)
        imageid = self.canvas.create_image(0,0,anchor= 'nw', image=imagetk)
        self.canvas.lower(imageid)  # set image into background
        self.canvas.imagetk = imagetk  # keep an extra reference to prevent garbage-collection

class GridWindow(tk.Frame):
    def __init__(self, master, main_canvas, folder_path, width, height):
        tk.Frame.__init__(self)
        self.master = master
        self.main_canvas = main_canvas
        self.folder_path = folder_path
        self.final_order = FileManagement(self.folder_path).get_grid()

        self.width = width
        self.height = height
        self.rows = 7
        self.columns = 7
        
        self.i = 0
        self.v = tk.StringVar()
        self.v.set(str(self.final_order[self.i][0]))
        self.text = tk.Label(self, text = "Current Grid Square:")
        self.text.grid(row = 0, column = 1)
        self.current_grid = tk.Label(self, text = self.v.get())
        self.current_grid.grid(row = 1, column = 1)

        self.forward_button = tk.Button(self, text = ">", command = self.forward)
        self.forward_button.grid(row=2, column = 2)
        

        self.backward_button = tk.Button(self, text = "<", command = self.backward)
        self.backward_button.grid(row=2, column = 0)

        self.jumpto_button = tk.Button(self, text = "Jump to", command = self.move_canvas)
        self.jumpto_button.grid(row = 2, column  = 1)
        
        self.make_check_button()

    def make_check_button(self):
        self.var_fin = tk.IntVar()
        self.var_fin.set(self.final_order[self.i][1])
        self.finished = tk.Checkbutton(self, text = "Finished", variable = self.var_fin,
                                        onvalue = 1, offvalue = 0, command = lambda y = self.final_order[self.i][0]: self.update_finished(y))
        self.finished.grid(row = 3, column = 1)
        
    def update_finished(self, grid_id):
        fin = self.var_fin.get()
        FileManagement(self.folder_path).finish_grid(grid_id, fin)
        self.final_order = FileManagement(self.folder_path).get_grid()

    def get_scrollx(self):
        total_squares = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvw"
        index = total_squares.find(self.final_order[self.i][0])
        self.w = self.width / self.columns
        return (index % self.columns) * self.w

    def get_scrolly(self):
        c = self.final_order[self.i][0]
        self.h = self.height / self.rows
        if c.islower():
            index = ord(c) - 96 + 26
        else:
            index = ord(c) - 64
        scrolly = floor(index / self.rows) * self.h
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
        if self.i < len(self.final_order) -1:
            self.i += 1 
        self.v.set(str(self.final_order[self.i][0]))
        
        self.current_grid.configure(text = self.v.get())
        self.current_grid.update()
        
        self.finished.destroy()
        self.make_check_button()

    def backward(self): 
        if self.i > 0:
            self.i -= 1 
        self.v.set((self.final_order[self.i][0]))
        self.current_grid.configure(text = self.v.get())
        self.current_grid.update()
        
        self.finished.destroy()
        self.make_check_button()

class GridToolbar(tk.Frame):
    def __init__(self, master, folder_path, marker_canvas, grid_canvas):
        tk.Frame.__init__(self)
        self.master = master
        self.folder_path = folder_path
        self.marker_canvas = marker_canvas
        self.grid_canvas = grid_canvas
        
        self.new_folder_path = tk.StringVar(value = "")
        self.case_name = tk.StringVar(value = "")
        self.grid_var = tk.BooleanVar(value = True)
        self.letter_var = tk.BooleanVar(value = True)

        
        file_b = tk.Menubutton(self, text = "File", relief = "raised")
        file_menu = tk.Menu(file_b, tearoff = False)
        file_b.configure(menu = file_menu)
        file_b.pack(side = "left")
        
        file_menu.add_command (label = "Open New Folder", command = self.open_new_folder)
        file_menu.add_command(label = "Export Images", command = self.export_images)
        file_menu.add_command(label = "Exit", command = root.quit)
        
        view_b = tk.Menubutton(self, text = "View", relief = "raised")
        view_menu = tk.Menu(view_b, tearoff = False)
        view_b.configure(menu = view_menu)
        view_b.pack(side = "left")
        
        view_menu.add_command(label = "Open Image Viewer", command = self.open_image_viewer)
        view_menu.add_command(label = "Set Window to Original Size", command = self.original_size)
        view_menu.add_checkbutton(label = "Show Grid", variable = self.grid_var, onvalue = True,
                                  offvalue = False, command = self.show_grid)
        view_menu.add_checkbutton(label = "Show Letters", variable = self.letter_var, onvalue = True,
                                  offvalue = False, command = self.show_letter)
        
        body_menu = tk.Menu(view_menu, tearoff = False)
        self.all_bodies = ["drop", "crescent", "spear", "green spear", "saturn", 
                        "rod", "green rod", "ring", "kettlebell", "multi inc"]
        self.choices = {}
        for choice in self.all_bodies:
            self.choices[choice] = tk.BooleanVar(value = True)
            body_menu.add_checkbutton(label=choice, variable=self.choices[choice], 
                                onvalue = True, offvalue = False, command = self.show_select_markers)
        view_menu.add_cascade(label = "Show Bodies", menu = body_menu)
        
        secondary_menu = tk.Menu(view_menu, tearoff = False)
        self.secondary = ["GR", "MAF", "MP", "unsure"]
        self.secondary_choices = {}
        for choice in self.secondary:
            self.secondary_choices[choice] = tk.BooleanVar(value = False)
            secondary_menu.add_checkbutton(label=choice, variable=self.secondary_choices[choice], 
                                onvalue = False, offvalue = True, command = self.show_select_markers)
        view_menu.add_cascade(label = "Show Secondary", menu = secondary_menu)
        
    def open_new_folder(self):
        path = filedialog.askdirectory()
        i = Application(root, path=path)
        
    def export_images(self):
        export = tk.Toplevel()
        export.transient(root)
        export.title("Export")
        export.geometry("300x130")
        export.columnconfigure(2, weight = 1)
        export.resizable(False, False)
        
        name = tk.Label(export, text = "Case Name:")
        name.grid(row = 1, column = 0, padx =10, pady = 10, sticky = "nsew")
        
        name_entry = tk.Entry(export, textvariable = self.case_name)
        name_entry.grid(row = 1, column = 1, padx =10, pady = 10, sticky = "nsew")
        
        folder_entry = tk.Entry(export, textvariable = self.new_folder_path)
        folder_entry.grid(row = 2, column = 0, padx =10, pady = 10, sticky = "nsew")
        
        def select_folder():
            path = filedialog.askdirectory()
            if path == "":
                return
            else:
                self.new_folder_path.set(path + "/")
                folder_entry.update()
            
        folder_button = tk.Button(export, text = "Browse", command = select_folder)
        folder_button.grid(row = 2, column = 1, padx = 10, pady = 10, sticky = "nsew")
        
        def confirm():
            if self.case_name.get() == "" or self.new_folder_path.get() == "/":
                return
            else:
                FileManagement(self.folder_path).export_case(self.new_folder_path.get(), self.case_name.get())
                export.destroy()
        
        ok_button = tk.Button(export, text = "Okay", command = confirm)
        ok_button.grid(row = 3, column = 2, padx = 10, pady = 10, sticky = "e")
        
    def open_image_viewer(self):
        ImageViewer(self.folder_path, self.marker_canvas) #TEST CLASS
    
    def original_size(self):
        self.master.geometry("600x600")
        
    def show_grid(self):
        if self.grid_var.get() == False: 
            self.grid_canvas.itemconfigure("line", state = "hidden")
        else:
            self.grid_canvas.itemconfigure("line", state = "normal")
            
    def show_letter(self):
        if self.letter_var.get() == False:
            self.grid_canvas.itemconfigure("letter", state = "hidden")
        else:
            self.grid_canvas.itemconfigure("letter", state = "normal")
            
    def _get_body_selection(self):
        body_selection = []
        for name, var in self.choices.items():
            if var.get() == True:
                body_selection.append(name)
        return body_selection
    
    def _get_secondary_selection(self):
        secondary_selection = []
        for name, var in self.secondary_choices.items():
            x = var.get()
            secondary_selection.append(x)
        return secondary_selection
            
    def show_select_markers(self):
        all_bodies = ["drop", "crescent", "spear", "green spear", "saturn", 
                        "rod", "green rod", "ring", "kettlebell", "multi inc"]
        all_data = FileManagement(self.folder_path).query_images(all_bodies, False, False, False, False)
        for i in all_data:
            self.grid_canvas.delete("m" + str(i[0]))
        
        bodies = self._get_body_selection()
        secondary_selection = self._get_secondary_selection()
        
        data = FileManagement(self.folder_path).query_images(bodies, secondary_selection[0], secondary_selection[1], 
                               secondary_selection[2], secondary_selection[3])
        for i in data:
            body_info = {}
            x = 0
            for choice in ("time", "body_name", "body_number", "x", "y"):
                body_info[choice] = i[x]
                x += 1
            GridMark(self.marker_canvas, self.folder_path, body_info)

def open_image(welcome_label1, welcome_label2, welcome_label3, button_frame):
    path = filedialog.askdirectory()
    if path == "":
        return
    welcome_label1.destroy()
    welcome_label2.destroy()
    welcome_label3.destroy()
    button_frame.destroy()
    i = Application(root, path=path)

def confirm_function(name, folder_path, file_name, nf):
    if folder_path == "" or file_name == "":
        return
    nf.destroy()

    FileManagement(folder_path + "/").initiate_folder(file_name, name)
    
    done_screen = tk.Toplevel()

    success_label1 = tk.Label(done_screen, text = "Folder sucessfully initialized!")
    success_label2 = tk.Label(done_screen, text = "Press the \"Open Previous Folder\" button to access it.")
    success_label1.grid(row = 0, column = 0, sticky = 'nswe')
    success_label2.grid(row = 2, column = 0, sticky = 'nswe')

    close_button = tk.Button(done_screen, text = "OK", command = lambda: done_screen.destroy())
    close_button.grid(row = 3, column = 0, sticky = 's')

def initiate_folder():
    nf = tk.Toplevel()
    nf.geometry("365x165")
    nf.transient(root)

    folder_path = tk.StringVar()
    folder_ebox = tk.Entry(nf, textvariable = folder_path, width = 50)
    folder_ebox.grid(row = 1, column = 0)
    
    folder_button = tk.Button(nf, text = "Browse...", command = lambda: folder_path.set(filedialog.askdirectory()))
    folder_button.grid(row = 1, column = 1)

    file_name = tk.StringVar()
    file_ebox = tk.Entry(nf, textvariable = file_name, width = 50)
    file_ebox.grid(row = 4, column = 0)

    file_button = tk.Button(nf, text = "Browse...", command = lambda: file_name.set(filedialog.askopenfilename()))
    file_button.grid(row = 4, column = 1)

    name = tk.StringVar()
    name_ebox = tk.Entry(nf, textvariable = name, width = 50)
    name_ebox.grid(row = 6, column = 0)

    confirm_button = tk.Button(nf, text = "Confirm", command = lambda: confirm_function(name.get(), folder_path.get(), file_name.get(), nf))
    confirm_button.grid(row = 8, column = 1)

    folder_label = tk.Label(nf, text = "Enter an empty folder directory:")
    folder_label.grid(row = 0, column = 0, sticky = 'w')

    file_label = tk.Label(nf, text = "Enter the grid file directory:")
    file_label.grid(row = 3, column = 0, sticky = 'w')

    name_label = tk.Label(nf, text = "Please enter you initials (eg. BJ):")
    name_label.grid(row = 5, column = 0, sticky = 'w')

    
    # folder_path = filedialog.askdirectory()
    # folder_path = folder_path + "/"
    #file_name = filedialog.askopenfilename()
    
    
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("580x100")
    root.title("Imaris Screenshot Tool")

    w1 = "Welcome to the Imaris Screenshot Tool!"
    w2 = "If you are returning to a previous session, please click on the \"Open Previous Folder\" button."
    w3 = "If you are starting a new session, please create an empty folder and select it using the \"Initiate Folder\" button."

    welcome_label1 = tk.Label(root, text = w1)
    welcome_label1.grid(row = 0, column = 2, sticky = 'nswe')
    
    welcome_label2 = tk.Label(root, text = w2)
    welcome_label2.grid(row = 2, column = 2, sticky = 'nswe')
    
    welcome_label3 = tk.Label(root, text = w3)
    welcome_label3.grid(row = 3, column = 2, sticky = 'nswe')
    
    button_frame = tk.Frame(root)
    button_frame.grid(row = 4, column = 2, sticky = 'ns')

    find_image_button = tk.Button(button_frame, text="Open Previous Folder", command = lambda: open_image(welcome_label1, welcome_label2, welcome_label3, button_frame))
    find_image_button.pack(side = "left", padx = 2 , pady = 2)
    initiate_folder_button = tk.Button(button_frame, text = "Initiate Folder", command = initiate_folder)
    initiate_folder_button.pack(side = "left", padx = 2 , pady = 2)
    root.mainloop()