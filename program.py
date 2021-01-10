import json
from log import append_new_line
from tkinter import *
from tkinter.ttk import Progressbar
from title_types import title_types
from countries import countries
from genres import genres
from tkcalendar import Calendar
from range_slider import Range_slider
import threading
from multiprocessing import Manager, Value, Pool
import multiprocessing as mp

import imdb_titles


def initProcess(progress, total, curr):
    imdb_titles.progress = progress
    imdb_titles.total = total
    imdb_titles.curr = curr


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
    params["user_rating"] = ",".join(
        [f"{ur:.1f}" for ur in slider.getValues()])
    params["countries"] = [countries[key]
                           for key in get_list_box_select(countries_listbox)]
    return params


def parse_and_count(link):
    val = imdb_titles.parse_title_page(link)
    imdb_titles.curr.value = imdb_titles.curr.value + 1
    imdb_titles.progress["percent"] = imdb_titles.curr.value / \
        imdb_titles.total.value
    imdb_titles.progress["name"] = f'Парсинг тайтлов: {"{:.1f}".format(imdb_titles.progress["percent"] * 100)} %'
    return val


def work(**kwargs):
    print(kwargs)
    append_new_line("log.log", "Start with parameters:")
    append_new_line("log.log", str(kwargs))
    progress["name"] = "Получаю ссылки на все тайтлы..."
    append_new_line("log.log", "Obtaining titles links")
    progress["counting"] = False

    try:
        links = imdb_titles.obtain_all_links(**kwargs)
    except:
        progress["exception"] = True
        progress["name"] = "ОШИБКА: не удалось получить ссылки на тайтлы"
        append_new_line("log.log", "Error: can not obtain titles links")
        progress["idle"] = True
        return

    progress["name"] = "Парсинг тайтлов..."
    append_new_line("log.log", f"Titles parsing, count: {len(links)}")
    progress["counting"] = True
    progress["percent"] = 0
    total.value = len(links)
    curr.value = 0

    pool = Pool(mp.cpu_count(), initializer=initProcess,
                initargs=(progress, total, curr))
    res = pool.map_async(parse_and_count, links)

    pool.close()
    pool.join()
    try:
        titles = res.get()
    except:
        progress["exception"] = True
        progress["name"] = "ОШИБКА: парсинг неудался :("
        append_new_line("log.log", "Error: failed to parse")
        progress["idle"] = True
        return

    progress["name"] = "Запись результатов в titles.json"
    append_new_line("log.log", "Writing titles.json")
    progress["counting"] = False

    with open("titles.json", "w", encoding="utf-8") as outfile:
        try:
            json.dump(titles, outfile, ensure_ascii=False)
        except:
            progress["exception"] = True
            progress["name"] = "ОШИБКА: неудалось сохранить данные"
            append_new_line("log.log", "Error: can not save data")

    progress["idle"] = True


def start_download():
    progress["idle"] = False
    progress["exception"] = False
    params = None
    try:
        params = collect_user_params()
    except:
        params = None
        progress["exception"] = True
        progress["name"] = "ОШИБКА: оно даже не запустилось :("
        append_new_line("log.log", "Error: can not launch")

    if params:
        worker_thread = threading.Thread(target=lambda: work(**params))
        worker_thread.setDaemon(True)
        worker_thread.start()


if __name__ == "__main__":
    root = Tk()

    root["bg"] = "#fafafa"
    root.title("Parse imdb")
    root.wm_attributes("-alpha", 0.95)
    root.geometry("600x820")

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

    parse_button = Button(frame, text="Parse titles",
                          command=start_download)
    parse_button.grid(column=0, row=6, columnspan=2)

    progress_label = Label(frame, text="URMOM")
    progress_label.grid(column=0, row=7, columnspan=2)

    progressbar = Progressbar(frame, orient=HORIZONTAL,
                              length=200, mode='determinate', maximum=1)
    progressbar.grid(column=0, row=8, columnspan=2)

    manager = Manager()
    progress = manager.dict()
    total = Value("i", 0)
    curr = Value("i", 0)

    progress["name"] = ""
    progress["percent"] = 0
    progress["counting"] = False
    progress["idle"] = True
    progress["exception"] = False

    def update_progress():
        # print(progress["name"])
        # print(progress["percent"])
        # print(progress["counting"])
        progress_label["text"] = progress["name"]
        parse_button["state"] = "normal" if progress["idle"] else "disabled"
        if progress["idle"] and not progress["exception"]:
            progress["name"] = "Ожидание..."
        if (progress["counting"]):
            progressbar["mode"] = "determinate"
            progressbar["value"] = progress["percent"]
        else:
            progressbar["mode"] = "indeterminate"
            progressbar["value"] += .1

        root.after(1000, update_progress)

    root.after(1000, update_progress)
    append_new_line(
        "log.log", "=================================================")
    append_new_line("log.log", "Start program")

    def on_closing():
        append_new_line("log.log", "End program")
        append_new_line(
            "log.log", "=================================================")
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
