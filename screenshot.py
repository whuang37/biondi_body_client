from tkinter import *
import tkinter as tk
import pyautogui
from PIL import ImageTk
from tkinter.colorchooser import askcolor

class Toolbar(): 
    counter=  1
    DEFAULT_COLOR = 'white'
    def __init__(self, master, canvas, h , w):
        self.height = h
        self.width = w
        self.canvas = canvas
        self.counter = 1
        self.undone = []
        
        self.brush_button = tk.Button(master, text = "brush", command = self.use_brush)
        self.color_button = tk.Button(master, text = 'color', command = self.choose_color)
        self.undo_button = tk.Button(master, text = 'undo', command = self.undo)
        self.redo_button = tk.Button(master, text = 'redo', command = self.redo)
        self.text_button = tk.Button(master, text = "top-left", command = self.text)
        self.brush_button.grid(row = 0, column = 0)
        self.color_button.grid(row = 0, column = 1)
        self.undo_button.grid(row = 0, column = 2)
        self.redo_button.grid(row = 0, column = 3)
        self.text_button.grid(row = 0 , column = 4)
        self.setup()
        
        self.canvas.create_text(50, 50, text = "text right here please look", anchor = NW, fill = 'white', tag ="text")
    
    def setup(self):
        self.old_x = None
        self.old_y = None
        self.line_width = 5
        self.color = self.DEFAULT_COLOR
        self.active_button = self.brush_button
        self.canvas.bind('<B1-Motion>', self.paint)
        self.canvas.bind('<ButtonRelease-1>', self.reset)
        self.canvas.bind('<Control-z>', self.undo_bind)
        
    def use_brush(self):
        self.activate_button(self.brush_button)
        
    def choose_color(self):
        self.color = askcolor(color = self.color)[1]
        
    def activate_button(self, some_button):
        self.active_button.config(relief= RAISED)
        some_button.config(relief= SUNKEN)
        self.active_button = some_button
        

    def paint(self, event):
        self.line_width = 5
        if self.old_x and self.old_y:
            self.canvas.create_line(self.old_x, self.old_y, event.x, event.y, 
                                    width = self.line_width, fill = self.color, 
                                    capstyle = ROUND, smooth = TRUE, splinesteps = 36, tag=['line' + str(self.counter)])
        self.old_x = event.x
        self.old_y = event.y
        
    def text(self):
        if self.text_button['text'] == 'top-left':
            self.canvas.delete('text')
            self.canvas.create_text(self.width - 50, 50, text = "text right here please look", anchor = NE, fill = 'white', tag ="text")
            self.text_button.configure(text='top-right')
        elif self.text_button['text'] == 'top-right':
            self.canvas.delete('text')
            self.canvas.create_text(50, self.height - 50, text = "text right here please look", anchor = SW, fill = 'white', tag ="text")
            self.text_button.configure(text='bottom-left')
        elif self.text_button['text'] == 'bottom-left':
            self.canvas.delete('text')
            self.canvas.create_text(self.width - 50, self.height - 50, text = "text right here please look", anchor = SE, fill = 'white', tag ="text")
            self.text_button.configure(text='bottom-right')
        elif self.text_button['text'] == 'bottom-right':
            self.canvas.delete('text')
            self.canvas.create_text(50, 50, text = "text right here please look", anchor = NW, fill = 'white', tag ="text")
            self.text_button.configure(text='top-left')
            
    def undo(self):
        self.counter -= 1
        currentundone = []
        for item in self.canvas.find_withtag('line'+str(self.counter)):
            currentundone.append(self.canvas.coords(item))
        self.canvas.delete('line'+str(self.counter))
        self.undone.append(currentundone)
        
    def undo_bind(self, event):
        self.undo()
        
    def redo(self):
        try:
            currentundone = self.undone.pop()
            for coords in currentundone:
                self.canvas.create_line(coords, width = self.line_width, fill = self.color, 
                                    capstyle = ROUND, smooth = TRUE, splinesteps = 36, tag=['line' + str(self.counter)])
            self.counter += 1
        except IndexError:
            pass
    def reset(self, event):
        self.old_x, self.old_y = None, None
        self.counter += 1
class ScreenshotEditor(tk.Frame):
    def __init__(self):
        self.screenshot = tk.Toplevel(root)
        self.screenshot.withdraw()

        self.toolbar_frame = tk.Frame(self.screenshot)
        self.toolbar_frame.grid(row=0, column = 0)
        
        #self.my_toolbar = Toolbar(self.toolbar, self.canvas1)
        self.screenshot_frame = tk.Frame(self.screenshot)
        self.screenshot_frame.grid(row = 1, column = 0)

    def create_screenshot_canvas(self, img):
        
        self.screenshot.deiconify()
        root.withdraw()
        width = img.width()
        height = img.height()
        self.canvas1 = tk.Canvas(self.screenshot_frame, width = width, height = height,
                                    borderwidth = 0, highlightthickness = 0)
        self.canvas1.pack(expand=tk.YES)
        self.canvas1.create_image(0, 0, image = img, anchor = tk.NW)
        self.canvas1.img = img
        self.my_toolbar = Toolbar(self.toolbar_frame, self.canvas1, height, width)
        Tk.focus_set(self.canvas1)


class Application(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.rect = None
        self.x = self.y = 0
        self.start_x = None
        self.start_y = None
        self.curX = None
        self.curY = None

        # root.configure(background = 'red')
        # root.attributes("-transparentcolor","red")

        root.attributes("-transparent", "blue")
        root.geometry('400x50+200+200')  # set new geometry
        root.title('Lil Snippy')
        self.menu_frame = tk.Frame(master, bg="blue")
        self.menu_frame.pack(fill=tk.BOTH, expand=tk.YES)

        self.button_bar = tk.Frame(self.menu_frame,bg="")
        self.button_bar.pack(fill=tk.BOTH,expand=tk.YES)

        self.snip_button = tk.Button(self.button_bar, width=3, command=self.create_screen_canvas, background="green")
        self.snip_button.pack(expand=tk.YES)

        self.master_screen = tk.Toplevel(root)
        self.master_screen.withdraw()
        self.master_screen.attributes("-transparent", "blue")
        self.picture_frame = tk.Frame(self.master_screen, background = "blue")
        self.picture_frame.pack(fill=tk.BOTH, expand=tk.YES)
        
    def take_bounded_screenshot(self, x1, y1, x2, y2):
        im = pyautogui.screenshot(region=(x1, y1, x2, y2))
        img = ImageTk.PhotoImage(im)
        
        self.screenshot_editor = ScreenshotEditor()
        self.screenshot_editor.create_screenshot_canvas(img)
        # fileName = x.strftime("%f")
        # im.save(fileName + ".png")

    def create_screen_canvas(self):
        self.master_screen.deiconify()
        root.withdraw()

        self.screen_canvas = tk.Canvas(self.picture_frame, cursor="cross", bg="grey11")
        self.screen_canvas.pack(fill=tk.BOTH, expand=tk.YES)

        self.screen_canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.screen_canvas.bind("<B1-Motion>", self.on_move_press)
        self.screen_canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.master_screen.attributes('-fullscreen', True)
        self.master_screen.attributes('-alpha', .3)
        self.master_screen.lift()
        self.master_screen.attributes("-topmost", True)

    def on_button_release(self, event):
        self.rec_position()

        if self.start_x <= self.curX and self.start_y <= self.curY:
            print("right down")
            self.take_bounded_screenshot(self.start_x, self.start_y, self.curX - self.start_x, self.curY - self.start_y)

        elif self.start_x >= self.curX and self.start_y <= self.curY:
            print("left down")
            self.take_bounded_screenshot(self.curX, self.start_y, self.start_x - self.curX, self.curY - self.start_y)

        elif self.start_x <= self.curX and self.start_y >= self.curY:
            print("right up")
            self.take_bounded_screenshot(self.start_x, self.curY, self.curX - self.start_x, self.start_y - self.curY)

        elif self.start_x >= self.curX and self.start_y >= self.curY:
            print("left up")
            self.take_bounded_screenshot(self.curX, self.curY, self.start_x - self.curX, self.start_y - self.curY)

        self.exit_screenshot_mode()
        return event

    def exit_screenshot_mode(self):
        print("Screenshot mode exited")
        self.screen_canvas.destroy()
        self.master_screen.withdraw()
        root.deiconify()

    def exit_application(self):
        print("Application exit")
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
    app = Application(root)
    root.mainloop() 
    
