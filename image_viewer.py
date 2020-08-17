import tkinter as tk
from tkinter.constants import LEFT
from PIL import Image, ImageTk
from file_management import FileManagement
from datetime import datetime

class ImageViewer(tk.Frame):
    def __init__(self, folder_path, *args, **kw):
        self.folder_path = folder_path       
        self.image_viewer = tk.Toplevel()
        self.image_viewer.columnconfigure(2, weight=1)
        self.image_viewer.rowconfigure(1, weight=1)

        # create a canvas object and a vertical scrollbar for scrolling it
        scrollbar = tk.Scrollbar(self.image_viewer, orient = "vertical")
        scrollbar.grid(row = 1, column = 1 , sticky = 'ns')
        
        
        self.button_list_canvas = tk.Canvas(self.image_viewer, bd=0, highlightthickness=0,
                        yscrollcommand=scrollbar.set)
        self.button_list_canvas.grid(row=1, column=0, sticky = 'ns')
        
        scrollbar.config(command=self.button_list_canvas.yview)
        self.button_list_canvas.xview_moveto(0)
        self.button_list_canvas.yview_moveto(0)
        
        self.make_button_frame()

        self.biondi_image_canvas = tk.Canvas(self.image_viewer, bd = 0)
        self.biondi_image_canvas.grid(row=1, column=2, sticky = 'nswe')
        
        filter_options_canvas = tk.Canvas(self.image_viewer, bd = 0)
        filter_options_canvas.grid(row=0, columnspan=3, sticky = "w")
        
        filter_bodies = tk.Menubutton(filter_options_canvas, text="Biondi Bodies", 
                                    indicatoron=True, borderwidth=1, relief="raised")
        menu = tk.Menu(filter_bodies, tearoff=False)
        filter_bodies.configure(menu=menu)
        filter_bodies.pack(padx=10, pady=10, side = tk.LEFT)

        self.choices = {}
        
        for choice in ("drop", "crescent", "spear", "green spear", "saturn", 
                        "rod", "green rod", "ring", "kettlebell", "multi inc"):
            self.choices[choice] = tk.IntVar(value=0)
            menu.add_checkbutton(label=choice, variable=self.choices[choice], 
                                onvalue=1, offvalue=0)
        
        self.var_GR = tk.BooleanVar()
        self.var_MAF = tk.BooleanVar()
        self.var_MP = tk.BooleanVar()
        self.var_unsure = tk.BooleanVar()
        
        grC = tk.Checkbutton(filter_options_canvas, text = "GR", anchor ="w", variable = self.var_GR, onvalue = True, offvalue = False)
        mafC = tk.Checkbutton(filter_options_canvas, text = "MAF", anchor ="w", variable = self.var_MAF, onvalue = True, offvalue = False)
        mpC = tk.Checkbutton(filter_options_canvas, text = "MP", anchor ="w", variable = self.var_MP, onvalue = True, offvalue = False)
        unsure = tk.Checkbutton(filter_options_canvas, text = "UNSURE", variable = self.var_unsure, onvalue = True, offvalue = False)
        apply  = tk.Button(filter_options_canvas, text = "Apply", command = lambda : self.filter())
        reset = tk.Button(filter_options_canvas, text = "Reset", command = lambda : self.reset())
        
        grC.pack(padx=10, pady = 10, side = tk.LEFT)
        mafC.pack(padx=10, pady = 10, side = tk.LEFT)
        mpC.pack(padx=10, pady = 10, side = tk.LEFT)
        unsure.pack(padx=10, pady = 10, side = tk.LEFT)
        apply.pack(padx=10, pady = 10, side = tk.LEFT)
        reset.pack(padx=10, pady = 10, side = tk.LEFT)
        
        self.all_bodies = ["drop", "crescent", "spear", "green spear", "saturn", 
                        "rod", "green rod", "ring", "kettlebell", "multi inc"]
        
        self.create_buttons(self.all_bodies, False, False, False, False)
        
    def make_button_frame(self):
        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = tk.Frame(self.button_list_canvas)
        self.interior.grid(row = 0, column = 0, sticky = "ns")
        interior_id = self.button_list_canvas.create_window(0, 0, window=interior,
                                            anchor=tk.NW)
        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            self.button_list_canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != self.button_list_canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                self.button_list_canvas.config(width=interior.winfo_reqwidth())

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != self.button_list_canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                self.button_list_canvas.itemconfigure(interior_id, width=self.button_list_canvas.winfo_width())
                
        self.button_list_canvas.bind('<Configure>', _configure_canvas)
        interior.bind('<Configure>', _configure_interior)
    
    def button_click(self, name, number):
        fm = FileManagement(self.folder_path)
        body_info = fm.get_image(name, number)

        self.make_information_frame(body_info)
        self.open_annotation_image(body_info['body file name'], body_info['annotation file name'])
        
    def make_information_frame(self, body_info):
        self.information_frame = tk.Frame(self.image_viewer)
        self.information_frame.grid(row = 3, column = 0, columnspan = 3, sticky = "nsew")
        
        x = 0
        column_widths =  ("20", "11", "12", "9", "12", "5", "5", "5", "8")
        for i in column_widths:
            if x % 2 == 0: 
                bg_color = "gray99"
            else:
                bg_color = "SystemButtonFace"
            bkgrnd = tk.Label(self.information_frame, width = i, height = "3", bg = bg_color)
            bkgrnd.grid(row = 0, column = x, rowspan = 2)
            x += 1
        
        x = 0
        for i in ("Time:", "Annotator:", "Body Type:", "Number:", "Location:", "GR:", "MAF:", "MP:", "UNSURE:"):
            if x % 2 == 0:
                bg_color = "gray99"
            else:
                bg_color = "SystemButtonFace"
            lbl = tk.Label(self.information_frame, text = i, font = ("Dosis", 10, "bold"), bg = bg_color, anchor = "w")
            lbl.grid(row = 0, column = x, sticky = "w")
            x += 1
            
        
        info = (datetime.fromtimestamp(body_info["time"]),
                body_info["annotator name"],
                body_info["body name"],
                body_info ["body number"],
                "{0} {1}, {2}".format(body_info["grid id"], body_info["x"], body_info["y"]),
                str(body_info["GR"]),
                str(body_info["MAF"]),
                str(body_info["MP"]),
                str(body_info["unsure"]))
        
        x = 0
        for i in info:
            if x % 2 == 0:
                bg_color = "gray99"
            else:
                bg_color = "SystemButtonFace"
            lbl = tk.Label(self.information_frame, text = i, font = ("Dosis", 10), bg = bg_color, anchor = "w")
            lbl.grid(row = 1, column = x, sticky = "w")
            x += 1
            
    
    def open_annotation_image(self, body_file_name, annotation_file_name):
        body_img = Image.open(self.folder_path + body_file_name)  # open image
        b_img = ImageTk.PhotoImage(body_img)
        self.biondi_image_canvas.create_image(0, 0, image = b_img, anchor = "nw")
        self.biondi_image_canvas.b_img = b_img
        
        annotation_img = Image.open(self.folder_path + annotation_file_name)  # open image
        a_img = ImageTk.PhotoImage(annotation_img)
        self.biondi_image_canvas.create_image(0, 0, image = a_img, anchor = "nw")
        self.biondi_image_canvas.a_img = a_img
        
        w, h = body_img.size
        self.image_viewer.geometry(str(w + 215) + "x" + str(h))
        
    def create_buttons(self, body_param, GR_param, MAF_param, MP_param, unsure_param):
        #self.button_list_canvas.delete("body_button")
        print("succes")
        fm = FileManagement(self.folder_path)
        data = fm.query_images(body_param, GR_param, MAF_param, MP_param, unsure_param)
        
        for i in data:
            name = i[1]
            number = i[2]
            body_name = "{} {}".format(name, number)
            btn = tk.Button(self.interior, height=1, width=20, relief=tk.FLAT, 
                            bg="gray99", fg="purple3", font="Dosis", text=body_name,
                            command= lambda i = name, x = number: self.button_click(i, x))
            btn.pack(padx=10, pady=5, side=tk.TOP)
            print("created_button")

    def refresh_button_list(self):
        self.interior.destroy()
        self.make_button_frame()
    
    def get_body_selection(self):
        body_selection = []
        for name, var in self.choices.items():
            if var.get() == 1:
                body_selection.append(name)
        return body_selection
    
    def filter(self):
        body_param = self.get_body_selection()
        GR_param = self.var_GR.get()
        MAF_param = self.var_MAF.get()
        MP_param = self.var_MP.get()
        unsure_param = self.var_unsure.get()
        
        self.refresh_button_list()
        self.create_buttons(body_param, GR_param, MAF_param, MP_param, unsure_param)

    def reset(self):
        self.refresh_button_list()
        self.create_buttons(self.all_bodies, False, False, False, False)