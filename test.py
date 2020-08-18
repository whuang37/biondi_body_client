from tkinter import *
from PIL import Image, ImageTk
import random

root=Tk()
frame=Frame(root)
frame.pack(expand=True, fill=BOTH) #.grid(row=0,column=0)
canvas=Canvas(frame,bg='#FFFFFF',scrollregion=(0,0,2438,2444))
canvas.configure(scrollregion=canvas.bbox("all"))
body_img = Image.open("gridfile.jpg")  # open image

def random_place(event):
    canvas.xview_moveto(random.uniform(0,1))
    canvas.yview_moveto(random.uniform(0, 1))
    
b_img = ImageTk.PhotoImage(body_img)
canvas.create_image(0, 0, image = b_img, anchor = "nw")
canvas.b_img = b_img

canvas.bind('<Button-1>', random_place)

hbar=Scrollbar(frame,orient=HORIZONTAL)
hbar.pack(side=BOTTOM,fill=X)
hbar.config(command=canvas.xview)
vbar=Scrollbar(frame,orient=VERTICAL)
vbar.pack(side=RIGHT,fill=Y)
vbar.config(command=canvas.yview)
canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
canvas.pack(side=LEFT,expand=True,fill=BOTH)
root.mainloop()