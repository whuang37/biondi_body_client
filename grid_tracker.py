import tkinter as tk
from PIL import Image, ImageTk
import random


class Grid_Randomizer():
    def __init__(self):

        self.set1a = ["A", "C", "E", "G", "O", "Q", "S", "U", "c", "e", "g", "i", "q", "s", "u", "w"] #16
        self.set1b = ["I", "K", "M", "W", "Y", "a", "k", "m", "o"] #9
        self.set2a = ["B", "D", "F", "P", "R", "T", "d", "f", "h", "r", "t", "v"] #12
        self.set2b = ["H", "J", "L", "N", "V", "X", "Z", "b", "j", "l", "n", "p"] #12

        random.shuffle(self.set1a)
        random.shuffle(self.set1b)
        random.shuffle(self.set2a)
        random.shuffle(self.set2b)

        self.which_set = random.randint(1,2) # set 1 or 2
        self.which_subset1 = random.randint(1,2) # 1 = a, 2 = b for set 1
        self.which_subset2 = random.randint(1,2) # for set 2

        self.final_order = []
        



    def set_order_from_prev(self, final): #takes an array, but can be changed later to take a string
        self.final_order = final

    def set_final_order(self):
        set1 = []
        set2 = []
        
        #orders subsets
        if self.which_subset1 == 1:
            set1.extend(self.set1a)
            set1.extend(self.set1b)
        else:
            set1.extend(self.set1b)
            set1.extend(self.set1a)

        if self.which_subset2 == 1:
            set2.extend(self.set2a)
            set2.extend(self.set2b)
        else:
            set2.extend(self.set2b)
            set2.extend(self.set2a)

        #orders sets
        if self.which_set == 1:
            self.final_order.extend(set1)
            self.final_order.extend(set2)
        else:
            self.final_order.extend(set2)
            self.final_order.extend(set1)

    def get_final_order(self):
        return self.final_order

    
class Grid_Window():
    def __init__(self, master):
        self.master = master
        master.title("Grid Tool") 

if __name__ == "__main__":
    #root = tk.Tk()
    gr = Grid_Randomizer()
    gr.set_final_order()
    #root.mainloop()
    
    



        