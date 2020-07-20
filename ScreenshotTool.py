from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
import sys



root = Tk()
root.title("UCI Imaris Screenshot Tool")


def openImage():
    novi = Toplevel()
    canvas = Canvas(novi, width = 500, height = 500)
    canvas.pack(expand = YES, fill = BOTH)
    filename = filedialog.askopenfilename()
    currentImg = ImageTk.PhotoImage(Image.open(filename))
    canvas.create_image(50, 10, image = currentImg, anchor = NW)
    canvas.currentImg = currentImg


findImageButton = Button(root, text="Pick Image File", command = openImage)
findImageButton.pack()

root.mainloop()