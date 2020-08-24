import tkinter as tk
import pyautogui
from PIL import ImageTk, Image, ImageDraw, ImageFont
from tkinter.colorchooser import askcolor
from file_management import FileManagement

class ScreenshotEditor(tk.Toplevel):
    """A basic image editor for image markups.
    
    This class is used to initialize a new window with options to annotate
    the taken screenshot from LilSnippy/Image Viewer. Tools include paint brush,
    select color, move location text, undo, redo, and save
    
    Attributes:
        body_info (dict): A collection of all relevant body information for use
            in different functions.
        folder_path (str): The string directory to the selected folder for saving.
        marker_canvas (tk.Canvas): Canvas where markers are saved on the gridfile.
        im (PIL image): An image file of the screenshot.
        img (tk PhotoImage): An image file of the screenshot.
        width (int): The width of the screenshot.
        height (int): The height of the screenshot.
        new (Bool): True if the image inputted is new and False if the image inputted
        is from the Image Viewer.
        annotation (PIL image): Empty image where the annotations are saved for a separate
            file.
        draw (PIL drawing): Pillow drawing for creating markups on annotation.
        screenshot_frame (tk.Frame): Frame where the screenshot canvas is stored.
        screenshot_canvas (tk.Canvas): The canvas where the image is created and shown.
        toolbar_frame (tk.Frame): The frame where tool buttons are stored.
        old_x (int): The x position of the mouse prior. Used in drawing lines.
        old_y (int): The y position of the mouse prior. Used in drawing lines.
        line_width (int): Line width of the markup lines
        color (str): The color of the markup lines.
        text_annotation (str): The string placed on the image.
        margin (int): The distance from the end to the text position
        counter (int): The number of lines made
        undone (list): A list of lines that were undone for redoing.
        
    Typical usage example:
        ScreenshotEditor(body_info, folder_path, marker_canvas, im, new)   
    """
    def __init__(self, body_info, folder_path, marker_canvas, im, new):
        tk.Toplevel.__init__(self)
        self.body_info = body_info
        self.folder_path = folder_path
        self.marker_canvas = marker_canvas
        self.im = im
        self.img = ImageTk.PhotoImage(im)
        self.width = self.img.width()
        self.height = self.img.height()
        self.new = new
        
        self.annotation = Image.new("RGBA", (self.width, self.height))
        self.draw = ImageDraw.Draw(self.annotation) #initialize a pillow drawing that runs in the background for saving annotations
        
        self.focus_set()
        self.grab_set()
        
        self.screenshot_frame = tk.Frame(self)
        self.screenshot_frame.grid(row = 1, column = 0)
        
        self.create_screenshot_canvas()

        self.toolbar_frame = tk.Frame(self)
        self.toolbar_frame.grid(row=0, column = 0)
        
        self.create_toolbar()
        
        self.setup()

        
    def create_screenshot_canvas(self):
        """Creates the screenshot canvas.
        
        Creates a canvas where the image is stored. All lines drawn that the user 
        can see are also stored on this canvas.
        """
        self.screenshot_canvas = tk.Canvas(self.screenshot_frame, width = self.width, height = self.height,
                                    borderwidth = 0, highlightthickness = 0)
        self.screenshot_canvas.pack(expand = True)
        self.screenshot_canvas.create_image(0, 0, image = self.img, anchor = "nw")
        self.screenshot_canvas.img = self.img
        self.screenshot_canvas.focus_set()
        
    def create_toolbar(self):
        """Creates the buttons on the toolbar.
        
        Initializes and places a series of buttons which end up as the tool
        selection on the top toolbar.
        """
        self.brush_button = tk.Button(self.toolbar_frame, text = "brush", command = self.use_brush)
        self.color_button = tk.Button(self.toolbar_frame, text = 'color', command = self.choose_color)
        self.undo_button = tk.Button(self.toolbar_frame, text = 'undo', command = self.undo)
        self.redo_button = tk.Button(self.toolbar_frame, text = 'redo', command = self.redo)
        self.text_button = tk.Button(self.toolbar_frame, text = "top-left", command = self.text)
        self.save_button = tk.Button(self.toolbar_frame, text = 'save', command = self.save)
        
        self.brush_button.grid(row = 0, column = 0)
        self.color_button.grid(row = 0, column = 1)
        self.undo_button.grid(row = 0, column = 2)
        self.redo_button.grid(row = 0, column = 3)
        self.text_button.grid(row = 0 , column = 4)
        self.save_button.grid(row = 0 , column = 5)
        
    def use_brush(self):
        """Function used the activate the brush from the button"""
        self.activate_button(self.brush_button)
        
    def setup(self):
        """Initializes a series of attributes and binds.
        
        Different variables used for annotations are initialized in here. Button clicks
        are bound for drawing lines to markup the image.
        """
        self.old_x = None
        self.old_y = None
        self.line_width = 5
        self.color = 'white'
        self.active_button = self.brush_button
        self.screenshot_canvas.bind('<B1-Motion>', self.paint)
        self.screenshot_canvas.bind('<ButtonRelease-1>', self.reset)
        self.screenshot_canvas.bind('<Control-z>', self.undo_bind) # used for undoing potential lines drawn
        self.counter = 1
        self.undone = []

        self.text_annotation = self.body_info["grid_id"] + " " + str(self.body_info["x"]) + ", " + str(self.body_info["y"])
        
        # find the appropriate margin for the text
        if self.width > self.height: 
            self.margin = .05 * self.height
        else:
            self.margin = .05 * self.width
        
        # creates first text location
        self.screenshot_canvas.create_text(self.margin, self.margin, text = self.text_annotation, 
                                font =("Calibri", 14), anchor = "nw", fill = 'white', tag ="text") 
    
    def activate_button(self, some_button):
        """Keeps brush button sunken as it is used.
        
        Configures the button to maintain being sunken/raised as its used.
        
        """
        self.active_button.config(relief = "raised")
        some_button.config(relief = "sunken")
        self.active_button = some_button
        
    def choose_color(self):
        """Allows user to choose a color for lines.
        
        Initaites a color chooser for users to select a color for the annotations.
        """
        self.color = askcolor(color = self.color, parent = self.toolbar_frame)[1]

    def paint(self, event):
        """Create paint lines.
        
        Creates an annotation line for marking around where the biondi body is. used
        as a callback function when the paint tool is selected.
        """
        if self.old_x and self.old_y: # if the mouse has already been clicked
            self.screenshot_canvas.create_line(self.old_x, self.old_y, event.x, event.y, 
                                    width = self.line_width, fill = self.color, 
                                    capstyle = "round", smooth = True, splinesteps = 36, 
                                    tag=['line' + str(self.counter)]) # tagged with the line number for undoing
            # draws on the pillow annotation image for saving later
            self.draw.line((self.old_x, self.old_y, event.x, event.y), fill = self.color, 
                            width = self.line_width, joint = "curve")
        self.old_x = event.x
        self.old_y = event.y
        
    def reset(self, event):
        """Resets coordinates to create a new line.
        
        Callback function used to reset the coordinates so that paint will 
        create a new line instead of connecting back up to the old.
        """
        self.old_x, self.old_y = None, None
        self.counter += 1
        
    def text(self): # moves text around
        """Move text around the four corners
        
        Function used with the location button to move the text around the corners
        to avoid covering up bodies. Rewrites the text on the button to reflect
        the location the text is currently in.
        """
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
        self.screenshot_canvas.delete('text')
        self.screenshot_canvas.create_text(x, y, text = self.text_annotation, 
                                font =("Calibri", 14), anchor = position, 
                                fill = 'white', tag ="text")
    def undo(self): 
        """Removes previous line drawn.
        
        Used in conjunction with the undo button/bind to remove the previous line drawn.
        Adds this line's tag into a list for redoing later.
        """
        self.counter -= 1 # lowers the counter as line is being deleted
        currentundone = []
        # finds most previous line drawn to add to an undone list
        for item in self.screenshot_canvas.find_withtag('line' + str(self.counter)):
            currentundone.append(self.screenshot_canvas.coords(item)) 
        self.screenshot_canvas.delete('line'+str(self.counter)) # deletes related line
        self.undone.append(currentundone) # appends list of undone for potential redoing
        
    def undo_bind(self, event):
        """Callback function to enable undo bind."""
        self.undo() 
        
    def redo(self): #redoes in new color not old color
        """Redraws a previously undone line.
        
        Takes the previously undone line and redraws the line again with the same 
        parameters as the old line.
        
        Bugs:
            Redraws the line in the new color selected not the old color.
        """
        try:
            currentundone = self.undone.pop() 
            for coords in currentundone: #pulls from list of undoes to recreate the first one
                self.screenshot_canvas.create_line(coords, width = self.line_width, fill = self.color, 
                                    capstyle = "round", smooth = "TRUE", splinesteps = 36, tag=['line' + str(self.counter)])
            self.counter += 1
        except IndexError:
            pass # passes if no more objects are in array
        
    def save(self):
        """Commits the image and annotation to new files.
        
        Saves the image and annotation as png files with an alpha channel for merging
        later. If the image is new, it also adds it to the database.
        """
        # parameters for the PIL annotations done in tandem with the seen tkinter annotations
        self.font = ImageFont.truetype("calibrib.ttf", 20) 
        bounds = self.screenshot_canvas.bbox("text")
        self.draw.text((bounds[0], bounds[1]), fill = 'white', 
                        #takes the bottom left coordinate of text and places the text on the pillow drawing
                        font = self.font, anchor = "ne", text = self.text_annotation) 
        
        if self.new == True: # if the image is being saved from LilSnippy
            FileManagement(self.folder_path).save_image(self.body_info, self.im, self.annotation)
            from markings import GridMark
            GridMark(self.marker_canvas, self.folder_path, self.body_info)
        else: # if the annotations are being edited from Image Viewer
            self.annotation.save(self.folder_path + self.body_info["annotation_file_name"])
        
        self.destroy()
        
        all_bodies = ["drop", "crescent", "spear", "green spear", "saturn", 
                        "rod", "green rod", "ring", "kettlebell", "multi inc"]
        number = FileManagement(self.folder_path).count_bodies(all_bodies, False, False, False, False)
        if number == 300: # opens a popup at 300 biondi bodies done
            done_screen = tk.Toplevel()
            done_screen.grab_set()
            success_label = tk.Label(done_screen, text = "You have finished annotating 300 bodies.")
            success_label.pack(side = 'top')

            close_button = tk.Button(done_screen, text = "OK", command = lambda: done_screen.destroy())
            close_button.pack(side = "bottom")

class LilSnippy(tk.Frame):
    """A selection and screenshot tool.
    
    The user can select an area on the screen which is then automatically saved
    in a PIL image file.
    
    Attributes: 
        master (frame): The main frame of the application. 
        rect (tk.Canvas rectangle): A rectangle used to indicate the user's selection area.
        x (int): The x coordinate before a selection is made.
        y (int): the y coordinate before a selection is made.
        start_x (int): The x coordinate when first clicked.
        start_y (int): The y coordinate when first clicked.
        cur_x (int): The x coordinate as the mouse moves.
        cur_y (int): The y coordinate as the mouse moves.
        master_screen (tk.Window): A semi-transparent screen used to black out the rest of the
        screen other than the area being selected.
        picture_frame (tk.Frame): A frame used to change the mouse into a cross.
        body_info (dict): A dictionary of related information on the body being screenshotted.
        folder_path (str): The directory to the folder where images are saved.
        marker_canvas (tk.Canvas): The canvas on the gridfile where the markers are saved.
        
    Typical Usage Example:
        LilSnippy(master, body_info, folder_path, marker_canvas)
    """
    def __init__(self, master, body_info, folder_path, marker_canvas, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.rect = None
        self.x = self.y = 0
        self.start_x = None
        self.start_y = None
        self.cur_x = None
        self.cur_y = None

        self.master_screen = tk.Toplevel(self.master)
        self.master_screen.withdraw()
        self.master_screen.attributes("-transparent", "blue")
        self.picture_frame = tk.Frame(self.master_screen, background = "blue")
        self.picture_frame.pack(fill=tk.BOTH, expand = True)
        
        self.body_info = body_info
        self.folder_path = folder_path
        self.marker_canvas = marker_canvas
        
    def take_bounded_screenshot(self, x1, y1, x2, y2):
        """Save the screenshot as a PIL file.
        
        Using the diagonal points, this function take that area and saves it as 
        a PIL image. This image is then piped into the Screenshot Editor.
        
        Args:
            x1 (int): X coordinate of the first click.
            y1 (int): Y coordinate of the first click.
            x2 (int): X coordinate when the mouse is released.
            y2 (int): Y coordinate when the mouse is released.
        """
        im = pyautogui.screenshot(region=(x1, y1, x2, y2))
        ScreenshotEditor(self.body_info, self.folder_path, self.marker_canvas, im, True)

    def create_screen_canvas(self):
        """Initializes a screen canvas for button clicks.
        
        Creates a new canvas which then has mouse binds for recording the coordinates
        for screenshot creation. The screen is also dimmed to show the area not selected.
        """
        self.master_screen.deiconify()
        self.master.withdraw()
        
        self.screen_canvas = tk.Canvas(self.picture_frame, cursor="cross", bg="grey11")
        self.screen_canvas.pack(fill=tk.BOTH, expand= True)
        
        self.screen_canvas.focus_set()
        
        self.screen_canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.screen_canvas.bind("<B1-Motion>", self.on_move_press)
        self.screen_canvas.bind("<ButtonRelease-1>", self.on_button_release)
        
        self.master_screen.attributes('-fullscreen', True)
        self.master_screen.attributes('-alpha', .3)
        self.master_screen.lift()
        self.master_screen.attributes("-topmost", True)


    def on_button_release(self, event):
        """Takes a screenshot on the release of mouse1.
        
        A callback function used to take the coordinates when mouse 1 is lifted 
        to then take a screenshot through the take_bound_screenshot method. Checks
        where the final coordinates are to sure that it is diagonal with the starting coordinates.
        
        Returns:
            event
        """
        if self.start_x <= self.cur_x and self.start_y <= self.cur_y:
            self.take_bounded_screenshot(self.start_x, self.start_y, self.cur_x - self.start_x, self.cur_y - self.start_y)

        elif self.start_x >= self.cur_x and self.start_y <= self.cur_y:
            self.take_bounded_screenshot(self.cur_x, self.start_y, self.start_x - self.cur_x, self.cur_y - self.start_y)

        elif self.start_x <= self.cur_x and self.start_y >= self.cur_y:
            self.take_bounded_screenshot(self.start_x, self.cur_y, self.cur_x - self.start_x, self.start_y - self.cur_y)

        elif self.start_x >= self.cur_x and self.start_y >= self.cur_y:
            self.take_bounded_screenshot(self.cur_x, self.cur_y, self.start_x - self.cur_x, self.start_y - self.cur_y)

        self.exit_screenshot_mode()
        return event

    def exit_screenshot_mode(self):
        """Destroys all canvases to end screenshot capturing mode."""
        self.screen_canvas.destroy()
        self.master_screen.withdraw()
        self.master.deiconify()

    def on_button_press(self, event):
        """Records the starting mouse coordinate.
        
        When the mouse is clicked, the starting mouse coordinate is selected and saved
        to record into the rectangle for future rectangle manipulation.
        """
        self.start_x = self.screen_canvas.canvasx(event.x)
        self.start_y = self.screen_canvas.canvasy(event.y)
        self.rect = self.screen_canvas.create_rectangle(self.x, self.y, 1, 1, outline='red', width=3, fill="blue")

    def on_move_press(self, event):
        """Records the coordinates as the mouse moves.
        
        Constantly refreshes cur_x and cur_y to reflect the current mouse position
        to change the rectangle to reflect the selection area.
        """
        self.cur_x, self.cur_y = (event.x, event.y)
        # expand rectangle as you drag the mouse
        self.screen_canvas.coords(self.rect, self.start_x, self.start_y, self.cur_x, self.cur_y)

    def rec_position(self):
        """Unused function that can return the coordinates of the rectangle if needed."""
        print(self.start_x)
        print(self.start_y)
        print(self.cur_x)
        print(self.cur_y)

if __name__ == '__main__':
    help(LilSnippy)
    help(ScreenshotEditor)