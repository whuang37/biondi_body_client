import tkinter as tk
import random
from tkinter import filedialog
from PIL import Image, ImageTk
import sys
from math import floor
import screenshot


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
        self.canvas = tk.Canvas(self.master, highlightthickness=0,
                                xscrollcommand=hbar.set, yscrollcommand=vbar.set)

        self.canvas2 = self.canvas
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
        self.canvas.bind('<MouseWheel>', self.wheel)  
        self.canvas.bind("<Button-1>", self.open_popup)
        #self.canvas.bind('<Return>', self.call_screenshot)

        self.image = Image.open(path)  # open image
        self.width, self.height = self.image.size
        self.imscale = 1.0  # scale for the canvas image
        self.delta = 1.3  # zoom magnitude
        # Put image into container rectangle and use it to set proper coordinates to the image
        self.container = self.canvas.create_rectangle(0, 0, self.width, self.height, width=0)
        self.show_image()
        
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
                                            font = ("Calibri", 24), fill = 'WHITE', text = key[n])
                n += 1
                if n > num_squares:
                    break

    def call_screenshot(self):
        app = screenshot.LilSnippy(self.master)
        app.create_screen_canvas()

    def get_grid(self, x, y):
        row_num = floor(y / (self.height / self.rows))
        column_num = floor(x / (self.width / self.columns))
        print(x)
        print(y)
        print(row_num)
        print(column_num)
        key = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        return key[(row_num * self.columns) + column_num]
        
    def get_letter(self, string): #used with draw
        print(string)
        if string == "drop":
            return "d"
        elif string== "crescent":
            return "c"
        elif string== "spear":
            return "s"
        elif string== "saturn":
            return "sa"
        elif string== "rod":
            return "r"
        elif string== "ring":
            return "ri"
        elif string== "kettlebell":
            return "kb"
        elif string== "multi inc":
            return "mi"

    def draw(self, body_type, if_GR, if_MAF, if_MP, if_unsure, x, y, marker):

        self.canvas2.create_text(x,y, font = "Calibri",fill = 'WHITE', text = self.get_letter(body_type))

        if if_GR:
            print("GR")
        if if_MAF:
            print("MAF")
        if if_MP:
            print("MP")
        if if_unsure:
            print("im unsure")
            
        print(self.get_grid(x, y))
        self.canvas2.update
        marker.destroy()
        self.call_screenshot()

    def open_popup(self, event):
        x = event.x
        y = event.y 
        marker = tk.Toplevel() #create window
        marker.title("popup")
        marker.grab_set()

        '''main body name'''
        var = tk.StringVar()
        var.set("drop")
        
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
        
        dropdown1 = tk.OptionMenu(marker, var, *option_list)
        dropdown1.grid(row = 0, column = 0)

        '''secondary body names'''
        var_GR = tk.BooleanVar()
        var_MAF = tk.BooleanVar()
        var_MP = tk.BooleanVar()
        
        grC = tk.Checkbutton(marker, text = "GR", anchor ="w", variable = var_GR, onvalue = True, offvalue = False)
        mafC = tk.Checkbutton(marker, text = "MAF", anchor ="w", variable = var_MAF, onvalue = True, offvalue = False)
        mpC = tk.Checkbutton(marker, text = "MP", anchor ="w", variable = var_MP, onvalue = True, offvalue = False)

        grC.grid(row = 0, column = 1, sticky = 'w')
        mafC.grid(row = 1, column = 1, sticky = 'w')
        mpC.grid(row = 2, column = 1, sticky = 'w')
        
        var_unsure = tk.BooleanVar()
        
        unsure = tk.Checkbutton(marker, text = "UNSURE", variable = var_unsure, onvalue = True, offvalue = False)
        unsure.grid(row = 0, column = 2)
        
        '''confirm button'''
        button_ok = tk.Button(marker, text = "OK", command = lambda: self.draw(var.get(),var_GR.get(), var_MAF.get(),
                                                                                var_MP.get(), var_unsure.get(), x, y, marker))
        button_ok.grid(row = 2, column = 2)


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

    def wheel(self, event):
        ''' Zoom with mouse wheel '''
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        bbox = self.canvas.bbox(self.container)  # get image area
        if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]: pass  # Ok! Inside the image
        else: return  # zoom only inside image area
        scale = 1.0
        if event.num == 5 or event.delta == -120:  # scroll down
            i = min(self.width, self.height)
            if int(i * self.imscale) < 30: return  # image is less than 30 pixels
            self.imscale /= self.delta
            scale        /= self.delta
        if event.num == 4 or event.delta == 120:  # scroll up
            i = min(self.canvas.winfo_width(), self.canvas.winfo_height())
            if i < self.imscale: return  # 1 pixel is bigger than the visible area
            self.imscale *= self.delta
            scale        *= self.delta
        self.canvas.scale('all', x, y, scale, scale)  # rescale all canvas objects
        #self.grid_canvas.scale('all', x, y ,scale, scale)
        #self.create_grid(7, 7)
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
            


def open_image():
    path = filedialog.askopenfilename()
    i = Application(root, path=path)

if __name__ == "__main__":
    root = tk.Tk()
    find_image_button = tk.Button(root, text="Pick Image File", command = open_image)
    find_image_button.grid(column = 0, row = 0)
    root.mainloop()




# class Image_Opener(Frame):
#     def __init__(self, master, *pargs, file_name):
#         Frame.__init__(self, master, *pargs)


#         self.file_name = file_name
#         self.image = Image.open(self.file_name)
#         self.img_copy= self.image.copy()


#         self.background_image = ImageTk.PhotoImage(self.image)

#         self.background = Label(self, image=self.background_image)
#         self.background.pack(fill=BOTH, expand=YES)
#         self.background.bind('<Configure>', self.resize_image)

#     def resize_image(self,event):

#         new_width = event.width
#         new_height = event.height

#         self.image = self.img_copy.resize((new_width, new_height))

#         self.background_image = ImageTk.PhotoImage(self.image)
#         self.background.configure(image =  self.background_image)





# root = Tk()
# root.title("UCI Imaris Screenshot Tool")


# def openImage():
#     novi = Toplevel()
#     canvas = Canvas(novi, width = 500, height = 500)
#     canvas.pack(expand = YES, fill = BOTH)
#     filename = filedialog.askopenfilename()
#     currentImg = ImageTk.PhotoImage(Image.open(filename))
#     canvas.create_image(50, 10, image = currentImg, anchor = NW)
#     canvas.currentImg = currentImg


# findImageButton = Button(root, text="Pick Image File", command = openImage)
# findImageButton.pack()

# root.mainloop()