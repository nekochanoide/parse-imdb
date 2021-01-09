from tkinter import *
from tkinter.ttk import Progressbar
from title_types import title_types
from countries import countries
from genres import genres
from tkcalendar import Calendar
from range_slider import Range_slider
import asyncio
import threading
import queue

from imdb_titles import main


def new_scrollable_listbox(host, x, label):
    frame = Frame(host)

    # for scrolling vertically
    yscrollbar = Scrollbar(frame)
    yscrollbar.pack(side=RIGHT, fill=Y)

    label = Label(frame, text=label, padx=10, pady=10)
    label.pack()
    listbox = Listbox(frame, selectmode="multiple", exportselection=0,
                      yscrollcommand=yscrollbar.set)

    # Widget expands horizontally and
    # vertically by assigning both to
    # fill option
    listbox.pack(padx=10, pady=10,
                 expand=YES, fill="both")

    for each_item in range(len(x)):
        listbox.insert(END, x[each_item])
        # listbox.itemconfig(each_item, bg="lime")

    # Attach listbox to vertical scrollbar
    yscrollbar.config(command=listbox.yview)

    return listbox, frame





def count():
    global progressbar
    a = 0
    max = 1000000000
    for i in range(max):
        a += i
        if (i % 1000000 == 0):
            progressbar["value"] = i / max
    progressbar["value"] = 1
    print(a)



def get_list_box_select(listbox):
    reslist = []
    for i in listbox.curselection():
        entrada = listbox.get(i)
        reslist.append(entrada)
    return reslist


def collect_user_params():
    params = {}
    params["title_type"] = [title_types[key]
                            for key in get_list_box_select(title_types_listbox)]
    params["genres"] = [genres[key]
                        for key in get_list_box_select(genres_listbox)]
    params["release_date"] = ",".join([release_date_from_calendar.selection.strftime("%Y-%m-%d") if release_date_from_calendar.selection else "0000-01-01",
                              release_date_to_calendar.selection.strftime("%Y-%m-%d") if release_date_to_calendar.selection else "9999-01-01"])
    params["user_rating"] = ",".join([f"{ur:.1f}" for ur in slider.getValues()])
    params["countries"] = [countries[key]
                           for key in get_list_box_select(countries_listbox)]
    return params

# Run the asyncio event loop in a worker thread.


def start_download():
    params = collect_user_params()
    worker_thread = threading.Thread(target=lambda:main(**params))
    worker_thread.setDaemon(True)
    worker_thread.start()


if __name__ == "__main__":
    root = Tk()

    root["bg"] = "#fafafa"
    root.title("Parse imdb")
    root.wm_attributes("-alpha", 0.95)
    root.geometry("600x800")

    frame = Frame(root)
    frame.pack(padx=10, pady=10)

    # title type, release_date (from, to),  genres, user_raiting, countries.

    title_types_listbox, title_types_div = new_scrollable_listbox(
        frame, list(title_types.keys()), "Title type")
    title_types_div.grid(column=0, row=0)

    genres_listbox, genres_div = new_scrollable_listbox(
        frame, list(genres.keys()), "Genres")
    genres_div.grid(column=1, row=0)

    release_date_from_label = Label(frame, text="Release date from")
    release_date_from_label.grid(column=0, row=1)
    release_date_from_calendar = Calendar(frame)
    release_date_from_calendar.grid(column=0, row=2)

    release_date_to_label = Label(frame, text="to")
    release_date_to_label.grid(column=1, row=1)
    release_date_to_calendar = Calendar(frame)
    release_date_to_calendar.grid(column=1, row=2)

    user_raiting_label = Label(frame, text="User rating")
    user_raiting_label.grid(column=0, row=3, columnspan=2)
    # https://github.com/MenxLi/tkSliderWidget
    slider = Range_slider(frame, width=400, height=60, min_val=1,
                        max_val=10, init_lis=[1, 10], show_value=True)
    slider.grid(column=0, row=4, columnspan=2)


    countries_listbox, countries_div = new_scrollable_listbox(
        frame, list(countries.keys()), "Countries")
    countries_div.grid(column=0, row=5, columnspan=2)

    progressbar = Progressbar(frame, orient=HORIZONTAL,
                            length=200, mode='determinate', maximum=1)
    
    parse_button = Button(frame, text="Parse titles", command=start_download)
    parse_button.grid(column=0, row=6, columnspan=2)

    progressbar.grid(column=0, row=7, columnspan=2)
    root.mainloop()