from tkinter import *


def new_scrollable_listbox(host, x):
    frame = Frame(host)
    frame.pack(padx=10, pady=10)

    # for scrolling vertically
    yscrollbar = Scrollbar(frame)
    yscrollbar.pack(side=RIGHT, fill=Y)

    label = Label(frame,
                  text="Select the languages below :  ",
                  padx=10, pady=10)
    label.pack()
    listbox = Listbox(frame, selectmode="multiple",
                      yscrollcommand=yscrollbar.set)

    # Widget expands horizontally and
    # vertically by assigning both to
    # fill option
    listbox.pack(padx=10, pady=10,
                 expand=YES, fill="both")

    for each_item in range(len(x)):
        listbox.insert(END, x[each_item])
        listbox.itemconfig(each_item, bg="lime")

    # Attach listbox to vertical scrollbar
    yscrollbar.config(command=listbox.yview)

    return listbox, frame


window = Tk()
window.title('Multiple selection')

x = ["C", "C++", "C#", "Java", "Python",
     "R", "Go", "Ruby", "JavaScript", "Swift",
     "SQL", "Perl", "XML"]

# # for scrolling vertically
# yscrollbar = Scrollbar(window)
# yscrollbar.pack(side=RIGHT, fill=Y)

# label = Label(window,
#               text="Select the languages below :  ",
#               font=("Times New Roman", 10),
#               padx=10, pady=10)
# label.pack()
# listbox = Listbox(window, selectmode="multiple",
#                   yscrollcommand=yscrollbar.set)

# # Widget expands horizontally and
# # vertically by assigning both to
# # fill option
# listbox.pack(padx=10, pady=10,
#              expand=YES, fill="both")



# for each_item in range(len(x)):
#     listbox.insert(END, x[each_item])
#     listbox.itemconfig(each_item, bg="lime")

# # Attach listbox to vertical scrollbar
# yscrollbar.config(command=listbox.yview)


listbox, frame = new_scrollable_listbox(window, x)

def select():
    reslist = list()
    seleccion = listbox.curselection()
    for i in seleccion:
        entrada = listbox.get(i)
        reslist.append(entrada)
    for val in reslist:
        print(val)


btn = Button(window, text="Choices", command=select)
btn.pack()

window.mainloop()
