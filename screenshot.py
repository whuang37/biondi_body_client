import tkinter as tk
import pyautogui
from PIL import ImageTk, Image, ImageDraw, ImageFont
from tkinter.colorchooser import askcolor
from file_management import FileManagement

class Toolbar(): # creates the toolbar and its related functions
    counter =  1
    DEFAULT_COLOR = 'white'
    def __init__(self, master, canvas, im, h , w, body_info, folder_path, marker_canvas, new):
        self.new = new
        self.master = master
        self.height = h
        self.width = w
        self.text_annotation = body_info["grid_id"] + " " + str(body_info["x"]) + ", " + str(body_info["y"])
        if self.width > self.height: # find the appropriate margin for the text
            self.margin = .05 * self.height
        else:
            self.margin = .05 * self.width
        
        self.im = im
        self.annotation = Image.new("RGBA", (self.width, self.height))
        self.draw = ImageDraw.Draw(self.annotation) #initialize a pillow drawing that runs in the background for saving annotations
        
        self.canvas = canvas
        self.counter = 1
        self.undone = [] 
        
        self.brush_button = tk.Button(master, text = "brush", command = self.use_brush)
        self.color_button = tk.Button(master, text = 'color', command = self.choose_color)
        self.undo_button = tk.Button(master, text = 'undo', command = self.undo)
        self.redo_button = tk.Button(master, text = 'redo', command = self.redo)
        self.text_button = tk.Button(master, text = "top-left", command = self.text)
        self.save_button = tk.Button(master, text = 'save', command = self.save)
        self.brush_button.grid(row = 0, column = 0)
        self.color_button.grid(row = 0, column = 1)
        self.undo_button.grid(row = 0, column = 2)
        self.redo_button.grid(row = 0, column = 3)
        self.text_button.grid(row = 0 , column = 4)
        self.save_button.grid(row = 0 , column = 5)
        self.setup()
        
        self.body_info = body_info
        self.folder_path = folder_path
        self.canvas.create_text(self.margin, self.margin, text = self.text_annotation, 
                                font =("Calibri", 14), anchor = "nw", fill = 'white', tag ="text") # creates text location
        
        self.marker_canvas = marker_canvas
        
    
    def setup(self):
        self.old_x = None
        self.old_y = None
        self.line_width = 5
        self.color = self.DEFAULT_COLOR
        self.active_button = self.brush_button
        self.canvas.bind('<B1-Motion>', self.paint)
        self.canvas.bind('<ButtonRelease-1>', self.reset)
        self.canvas.bind('<Control-z>', self.undo_bind) # used for undoing potential lines drawn
        
    def use_brush(self):
        self.activate_button(self.brush_button)
        
    def choose_color(self):
        self.color = askcolor(color = self.color, parent = self.master)[1]
        
    def activate_button(self, some_button): # keeps brush button sunken as its used
        self.active_button.config(relief = "raised")
        some_button.config(relief = "sunken")
        self.active_button = some_button
        

    def paint(self, event): # creates the paint lines
        self.line_width = 5
        if self.old_x and self.old_y:
            self.canvas.create_line(self.old_x, self.old_y, event.x, event.y, 
                                    width = self.line_width, fill = self.color, 
                                    capstyle = "round", smooth = True, splinesteps = 36, 
                                    tag=['line' + str(self.counter)])
            self.draw.line((self.old_x, self.old_y, event.x, event.y), fill = self.color, 
                            width = self.line_width, joint = "curve")
        self.old_x = event.x
        self.old_y = event.y
        
    def reset(self, event): # resets coordinates to create a new line
        self.old_x, self.old_y = None, None
        self.counter += 1
        
    def text(self): # moves text around
        if self.text_button['text'] == 'top-left':
            self.text_position(self.width - self.margin, self.margin, "ne")
            self.text_button.configure(text='top-right')
        elif self.text_button['text'] == 'top-right':
            self.text_position(self.margin, self.height - self.margin, "sw")
            self.text_button.configure(text='bottom-left')
        elif self.text_button['text'] == 'bottom-left':
            self.text_position(self.width - self.margin, self.height - self.margin, "se")
            self.text_button.configure(text='bottom-right')
        elif self.text_button['text'] == 'bottom-right':
            self.text_position(self.margin, self.margin, "nw")
            self.text_button.configure(text='top-left')
        
    def text_position(self, x, y, position):
        self.canvas.delete('text')
        self.canvas.create_text(x, y, text = self.text_annotation, 
                                font =("Calibri", 14), anchor = position, 
                                fill = 'white', tag ="text")
    def undo(self): 
        self.counter -= 1
        currentundone = []
        for item in self.canvas.find_withtag('line' + str(self.counter)):
            currentundone.append(self.canvas.coords(item)) 
        self.canvas.delete('line'+str(self.counter)) # deletes related line
        self.undone.append(currentundone) # appends list of undone for potential redoing
        
    def undo_bind(self, event): # enables ctrl-z bind to work
        self.undo() 
        
    def redo(self): #redoes in new color not old color
        try:
            currentundone = self.undone.pop() 
            for coords in currentundone: #pulls from list of undoes to recreate the first one
                self.canvas.create_line(coords, width = self.line_width, fill = self.color, 
                                    capstyle = "round", smooth = "TRUE", splinesteps = 36, tag=['line' + str(self.counter)])
            self.counter += 1
        except IndexError:
            pass # passes if no more objects are in array
        
    def save(self):
        self.font = ImageFont.truetype("calibrib.ttf", 20) 
        bounds = self.canvas.bbox("text")
        self.draw.text((bounds[0], bounds[1]), fill = 'white', 
                        font = self.font, anchor = "ne", text = self.text_annotation) #takes the bottom left coordinate of text and places the text on the pillow drawing
        
        if self.new == True:
            fm = FileManagement(self.folder_path)
            fm.save_image(self.body_info, self.im, self.annotation)
            from markings import GridMark
            GridMark(self.marker_canvas, self.folder_path, self.body_info)
        else: 
            self.annotation.save(self.folder_path + self.body_info["annotation_file_name"])

class ScreenshotEditor(tk.Frame):
    def __init__(self, body_info, folder_path, marker_canvas, new):
        self.screenshot = tk.Toplevel()
        self.screenshot.withdraw()

        self.toolbar_frame = tk.Frame(self.screenshot)
        self.toolbar_frame.grid(row=0, column = 0)
        
        self.screenshot_frame = tk.Frame(self.screenshot)
        self.screenshot_frame.grid(row = 1, column = 0)
        
        self.body_info = body_info
        self.folder_path = folder_path
        self.new = new
        self.marker_canvas = marker_canvas

    def create_screenshot_canvas(self, im):
        
        self.screenshot.deiconify()
        img = ImageTk.PhotoImage(im)
        width = img.width()
        height = img.height()
        
        self.screenshot_canvas = tk.Canvas(self.screenshot_frame, width = width, height = height,
                                    borderwidth = 0, highlightthickness = 0)
        self.screenshot_canvas.pack(expand=tk.YES)
        self.screenshot_canvas.create_image(0, 0, image = img, anchor = "nw")
        self.screenshot_canvas.img = img
        self.my_toolbar = Toolbar(self.toolbar_frame, self.screenshot_canvas, im, height, width,
                                    self.body_info, self.folder_path, self.marker_canvas, self.new)
        self.screenshot_canvas.focus_set()


class LilSnippy(tk.Frame):
    def __init__(self, master, body_info, folder_path, marker_canvas, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.rect = None
        self.x = self.y = 0
        self.start_x = None
        self.start_y = None
        self.curX = None
        self.curY = None

        self.master_screen = tk.Toplevel(self.master)
        self.master_screen.withdraw()
        self.master_screen.attributes("-transparent", "blue")
        self.picture_frame = tk.Frame(self.master_screen, background = "blue")
        self.picture_frame.pack(fill=tk.BOTH, expand=tk.YES)
        
        self.body_info = body_info
        self.folder_path = folder_path
        self.marker_canvas = marker_canvas
    def take_bounded_screenshot(self, x1, y1, x2, y2):
        im = pyautogui.screenshot(region=(x1, y1, x2, y2))
        
        self.screenshot_editor = ScreenshotEditor(self.body_info, self.folder_path, self.marker_canvas, True)
        self.screenshot_editor.create_screenshot_canvas(im)

    def create_screen_canvas(self):
        self.master_screen.deiconify()
        self.master.withdraw()
        
        self.screen_canvas = tk.Canvas(self.picture_frame, cursor="cross", bg="grey11")
        self.screen_canvas.pack(fill=tk.BOTH, expand= tk.YES)
        
        self.screen_canvas.focus_set()
        
        self.screen_canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.screen_canvas.bind("<B1-Motion>", self.on_move_press)
        self.screen_canvas.bind("<ButtonRelease-1>", self.on_button_release)
        
        buttontest = tk.Button(self.screen_canvas, text = "Pick Image File", command = self.on_button_press)
        buttontest.pack()
        
        self.master_screen.attributes('-fullscreen', True)
        self.master_screen.attributes('-alpha', .3)
        self.master_screen.lift()
        self.master_screen.attributes("-topmost", True)


    def on_button_release(self, event):
        self.rec_position()

        if self.start_x <= self.curX and self.start_y <= self.curY:
            self.take_bounded_screenshot(self.start_x, self.start_y, self.curX - self.start_x, self.curY - self.start_y)

        elif self.start_x >= self.curX and self.start_y <= self.curY:
            self.take_bounded_screenshot(self.curX, self.start_y, self.start_x - self.curX, self.curY - self.start_y)

        elif self.start_x <= self.curX and self.start_y >= self.curY:
            self.take_bounded_screenshot(self.start_x, self.curY, self.curX - self.start_x, self.start_y - self.curY)

        elif self.start_x >= self.curX and self.start_y >= self.curY:
            self.take_bounded_screenshot(self.curX, self.curY, self.start_x - self.curX, self.start_y - self.curY)

        self.exit_screenshot_mode()
        return event

    def exit_screenshot_mode(self):
        self.screen_canvas.destroy()
        self.master_screen.withdraw()
        self.master.deiconify()

    def exit_application(self): # not used yet
        root.quit()

    def on_button_press(self, event):
        # save mouse drag start position
        self.start_x = self.screen_canvas.canvasx(event.x)
        self.start_y = self.screen_canvas.canvasy(event.y)
        self.rect = self.screen_canvas.create_rectangle(self.x, self.y, 1, 1, outline='red', width=3, fill="blue")

    def on_move_press(self, event):
        self.curX, self.curY = (event.x, event.y)
        # expand rectangle as you drag the mouse
        self.screen_canvas.coords(self.rect, self.start_x, self.start_y, self.curX, self.curY)

    def rec_position(self):
        print(self.start_x)
        print(self.start_y)
        print(self.curX)
        print(self.curY)

if __name__ == '__main__':
    root = tk.Tk()
    app = LilSnippy(root)
    app.create_screen_canvas()
    root.mainloop() 
    
    
