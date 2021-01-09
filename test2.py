#-*- coding: utf-8 -*-
# Python version 3.4
# The use of the ttk module is optional, you can use regular tkinter widgets

from tkinter import *
from tkinter import ttk
from tkcalendar import Calendar

main = Tk()
main.title("Multiple Choice Listbox")
main.geometry("+50+150")
frame = ttk.Frame(main, padding=(3, 3, 12, 12))
frame.grid(column=0, row=0, sticky=(N, S, E, W))

ttkcal = Calendar(frame)
ttkcal.grid(column=0, row=0, columnspan=2)

def select():
    print(ttkcal.selection)

btn = ttk.Button(frame, text="Choices", command=select)
btn.grid(column=0, row=1)

main.mainloop()