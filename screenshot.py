import tkinter as tk
import pyautogui
from PIL import ImageTk
import datetime
class ScreenshotEditor():
    def __init__(self):
        self.screenshot = tk.Toplevel(root)
        self.screenshot.withdraw()
        
        self.screenshot_frame = tk.Frame(self.screenshot)
        self.screenshot_frame.pack(expand=True)
        
    def create_screenshot_canvas(self, img):
        self.screenshot.deiconify()
        root.withdraw()

        self.canvas1 = tk.Canvas(self.screenshot_frame, width=img.width(), height = img.height(),borderwidth = 0, highlightthickness = 0 )
        self.canvas1.pack(expand=tk.YES)
        self.canvas1.create_image(0, 0, image = img, anchor = tk.NW)
        self.canvas1.img = img
class Application():
    def __init__(self, master):
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
    
