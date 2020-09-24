#!/usr/bin/env python3

import tkinter as tk
from tkinter import *

class GUI(tk.Frame) :
    def __init__(self,master=None) :
        Frame.__init__(self,master)
        a = Button(master, text = "PUSH ME NOW PLEASE ",command=lambda: self.makeAlarm())
        a.pack()

    def makeAlarm(self) :
        print("ALARM")

root = tk.Tk()
gui = GUI(root)

gui.mainloop()