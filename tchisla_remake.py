from tchisla_remake_funcs import myEval, expr_check, infos, expr_sqrt_replace
from tkinter import *
from math import isnan
from random import randint
import fractions as fr
from pygame import mixer
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

icon_path = resource_path("tchisla_remake_icon.ico")
music_path = resource_path("Laura Shigihara - Loonboon.mp3")

MLEVELS = 101
NUM_GUESSES = 10
MAINCOLOR = "pink"
CURRENT_LEVEL = 0
RULES_TO_LEVEL = False
PROGRESS_FILENAME = "progress.txt"
STARTING_PAGE = 1
STARTING_VOLUME = 50
HINTNUM = 0

def myHash(listlines):
    hashsum = 0
    generator = 1624152263628726963
    modulo = 2305843009213693951
    for line in listlines:
        for c in line:
            hashsum = (hashsum * generator + ord(c)) % modulo
    return hashsum

# Read progress
guesses = [[]]
for i in range(1, 10):
    guesses.append([[0, ""] for _ in range(MLEVELS)])
# first element - status:
#   0: didn't even try
#   1: no valid attempts
#   2: not optimal valid attempt
#   3: solved
#   4: found better than optimal O_O
# second argument - BEST valid attempt, only if status in {2, 3, 4}

inp = None
try:
    inp = open(PROGRESS_FILENAME, "r", encoding="utf-8")
    # hash check
    linesinp = inp.readlines()
    
    modified = False
    if linesinp[-1][:6] == "HASH: ":
        infilehash = linesinp[-1][6:].strip()
        for c in infilehash:
            if c not in "0123456789":
                modified = True
                break
        if not modified:
            infilehash = int(infilehash)
            calcedhash = myHash(linesinp[:-1])
            if infilehash != calcedhash:
                modified = True
    else:
        modified = True
    
    # read file
    if not modified:
        string = linesinp[0].split()
        STARTING_PAGE = int(string[1])
        MAINCOLOR = string[2]
        STARTING_VOLUME = int(string[3])
        inside_number = False
        for string in linesinp[1:-1]:
            string = string.strip()
            if string[0] == "D":
                currentdigit = int(string[-1])
            elif string[0] == "N":
                inside_number = True
                currentnumber = int(string[8:])
            elif string[0] == "B":
                guesses[currentdigit][currentnumber][1] = string[6:]
                length = guesses[currentdigit][currentnumber][1].count(str(currentdigit))
                if length > infos[currentdigit][currentnumber].minlen:
                    guesses[currentdigit][currentnumber][0] = 2
                elif length == infos[currentdigit][currentnumber].minlen:
                    guesses[currentdigit][currentnumber][0] = 3
                else:
                    guesses[currentdigit][currentnumber][0] = 4
            else:
                guesses[currentdigit][currentnumber][0] = max(guesses[currentdigit][currentnumber][0], 1)
                guesses[currentdigit][currentnumber].append(string)
                
    else:
        i = 0
        n = len(linesinp)
        inside_digit = False
        inside_number = False

        while i < n:
            string = linesinp[i].strip()
            if string[0] == "D":
                inside_digit = True
                currentdigit = int(string[-1])
                if not currentdigit:
                    inside_digit = False
            elif string[0] == "N" and inside_digit:
                inside_number = True
                currentnumber = 0
                j = -1
                power10 = 1
                while string[j] in "0123456789":
                    currentnumber += int(string[j]) * power10
                    power10 *= 10
                    j -= 1
                if currentnumber >= MLEVELS:
                    inside_number = False
            elif string[0] == "B" and inside_number and inside_digit:
                j = 1
                while string[j] not in "0123456789(+-√":
                    j += 1
                tup = myEval(string[j:], currentdigit)
                if not (tup[0] is None) and tup[2] and isinstance(tup[0], int) and tup[0] == currentnumber:
                    guesses[currentdigit][currentnumber][1] = string[j:]
                    if tup[1] > infos[currentdigit][currentnumber].minlen:
                        guesses[currentdigit][currentnumber][0] = 2
                    elif tup[1] == infos[currentdigit][currentnumber].minlen:
                        guesses[currentdigit][currentnumber][0] = 3
                    else:
                        guesses[currentdigit][currentnumber][0] = 4
            elif inside_digit and inside_number:
                tup = myEval(string, currentdigit)
                if not (tup[0] is None):
                    guesses[currentdigit][currentnumber][0] = max(guesses[currentdigit][currentnumber][0], 1)
                    guesses[currentdigit][currentnumber].append(string)
            i += 1
    inp.close()
except Exception:
    if not (inp is None):
        inp.close()

# # # # # # # # # # #
# # # GUI BEGIN # # #
# # # # # # # # # # #

class ScrollableFrame(Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = Canvas(self, bg=MAINCOLOR)
        scrollbar = Scrollbar(self, orient=VERTICAL, command=canvas.yview)
        self.scrollable_frame = Frame(canvas, bg=MAINCOLOR)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox(ALL)
            )
        )
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor=NW)

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

root = Tk()
root.geometry("900x600")
root.title("Tchisla Remake")
root.iconbitmap(icon_path)

# Main Frames
fmainmenu = Frame(root, bg=MAINCOLOR)
fmainmenu.place(relwidth=1, relheight=1)

flevelmenu = Frame(root, bg=MAINCOLOR)
flevelmenu.place(relwidth=1, relheight=1)

fthelevel = Frame(root, bg=MAINCOLOR)
fthelevel.place(relwidth=1, relheight=1)

fsettings = Frame(root, bg=MAINCOLOR)
fsettings.place(relwidth=1, relheight=1)



# Main Menu
lmaintitle = Label(fmainmenu, text="Tchisla Remake", bg=MAINCOLOR, font=("Arial", 48, "bold"), height=2)
lmaintitle.pack()

ffmenucenter = Frame(fmainmenu, bg=MAINCOLOR)
ffmenucenter.pack(expand=1)

def fshowlevelmenu():
    for i in range(MLEVELS):
        blevel[i]["bg"] = buttoncolors[guesses[CURRENT_PAGE.get()][i][0]]
        lcurrentbest[i]["text"] = " = " + guesses[CURRENT_PAGE.get()][i][1]
    flevelmenu.lift()
bmenu = Button(ffmenucenter, text="Уровни", width=15, height=3, command=fshowlevelmenu)
bmenu.pack(padx=5, pady=5)

def fshowlevel(level):
    def wrapper():
        global CURRENT_LEVEL
        global CURRENT_PAGE
        global HINTNUM
        if level == -1:
            CURRENT_PAGE.set(randint(1, 9))
            CURRENT_LEVEL = randint(0, MLEVELS-1)
            bnextlevel["command"] = fshowlevel(-1)
        else:
            CURRENT_LEVEL = level
            bnextlevel["command"] = fshowlevel((CURRENT_LEVEL+1) % MLEVELS)
        lthelevel_title1["text"] = "Уровень " + str(CURRENT_LEVEL)
        lthelevel_title2["text"] = "Выразить через " + str(CURRENT_PAGE.get())
        if guesses[CURRENT_PAGE.get()][CURRENT_LEVEL][0] > 2:
            lerror["fg"] = "green"
            lerror["text"] = "Уже решено =)"
        else:
            lerror["text"] = ""
        entry_expr.delete(0, END)
        lresult["text"] = ""
        lbest["text"] = "Лучшая попытка: " + guesses[CURRENT_PAGE.get()][CURRENT_LEVEL][1]
        for i in range(NUM_GUESSES):
            lprev[i]["text"] = ""
        i = 0
        j = len(guesses[CURRENT_PAGE.get()][CURRENT_LEVEL]) - 1
        while i < NUM_GUESSES and j >= 2:
            lprev[i]["text"] = guesses[CURRENT_PAGE.get()][CURRENT_LEVEL][j]
            i += 1
            j -= 1
        HINTNUM = 0
        lhint["text"] = ""
        fthelevel.lift()
    return wrapper
brandlevel = Button(ffmenucenter, text="Случайный уровень", width=20, height=3, command=fshowlevel(-1))
brandlevel.pack(padx=5, pady=5)

def fshowrules(tolevel):
    def wrapper():
        global RULES_TO_LEVEL
        RULES_TO_LEVEL = tolevel
        frules.lift()
    return wrapper
bmenurules = Button(ffmenucenter, text="Правила", width=15, height=3, command=fshowrules(False))
bmenurules.pack(padx=5, pady=5)

bexit = Button(fmainmenu, text="Выход", width=15, height=3, command=root.destroy)
bexit.pack(side=RIGHT, anchor=SE, padx=5, pady=5)

bsettings = Button(fmainmenu, text="Настройки", width=15, height=3, command=fsettings.lift)
bsettings.pack(side=LEFT, anchor=SW, padx=5, pady=5)

buttoncolors = [bmenu["bg"], "#edea45", "#365ec2", "#08f500", "#9700f5"]

# Settings
lsettings = Label(fsettings, text="Настройки, которые мы заслужили", bg=MAINCOLOR, font=("Arial", 24, "bold"), height=2)
lsettings.pack()

ffchangebgbox = Frame(fsettings, bg=MAINCOLOR)
ffchangebgbox.pack()

lchangebg = Label(ffchangebgbox, text="Цвет фона", bg=MAINCOLOR, font=15)
lchangebg.pack(side=LEFT, padx=20)

fffchangebg_options = Frame(ffchangebgbox, bg=MAINCOLOR)
fffchangebg_options.pack(side=LEFT)

def change_background_color(color):
    def recursively_change_bg(node):
        global MAINCOLOR
        if node["bg"] == MAINCOLOR:
            node["bg"] = color
        for child in node.children.values():
            recursively_change_bg(child)
    def wrapper():
        global MAINCOLOR
        nonlocal recursively_change_bg
        recursively_change_bg(root)
        MAINCOLOR = color
    return wrapper

maincolor = StringVar()
maincolor.set(MAINCOLOR)
available_colors = [("pink", "Розовый"),
                    ("lightblue", "Синий"),
                    ("lightgreen", "Зелёный"),
                    ("yellow", "Жёлтый"),
                    ("purple1", "Фиолетовый"),
                    ("white", "Белый"),
                    ("grey", "Серый"),
                    ("cyan", "Бирюзовый")]
bchangebg = [Radiobutton(fffchangebg_options, text=color[1], variable=maincolor, value=color[0], font=10,
                         command=change_background_color(color[0]), bg=MAINCOLOR) for color in available_colors]
for rb in bchangebg:
    rb.pack(anchor=W)

ffchange_volume = Frame(fsettings, bg=MAINCOLOR)
ffchange_volume.pack()

lchange_volume = Label(ffchange_volume, text="Громкость", bg=MAINCOLOR, font=15)
lchange_volume.pack(side=LEFT, padx=20)

volume = IntVar()
volume.set(STARTING_VOLUME)
def fchange_volume(vol):
    mixer.music.set_volume(int(vol) / 100)
scale_volume = Scale(ffchange_volume, variable=volume, length=200,
                     orient=HORIZONTAL, bg=MAINCOLOR, command=fchange_volume)
scale_volume.pack(side=LEFT)

bsettings_to_menu = Button(fsettings, text="Главное Меню", width=15, height=3, command=fmainmenu.lift)
bsettings_to_menu.pack(side=LEFT, anchor=SW, padx=5, pady=5)


# Level Menu

CURRENT_PAGE = IntVar()
CURRENT_PAGE.set(STARTING_PAGE)

llevelmenu_title = Label(flevelmenu, text="Уровни", bg=MAINCOLOR, font=("Arial", 16, "bold"), height=2)
llevelmenu_title.pack()

fftop = Frame(flevelmenu, bg=MAINCOLOR)
fftop.pack()

def fswitch_page(page):
    def wrapper():
        for i in range(MLEVELS):
            blevel[i]["bg"] = buttoncolors[guesses[page][i][0]]
            lcurrentbest[i]["text"] = guesses[page][i][1]
    return wrapper
bpages = [Radiobutton(fftop, text=i+1, variable=CURRENT_PAGE, value=i+1, command=fswitch_page(i+1),
                      bg=MAINCOLOR, font=("Arial", 20)) for i in range(9)]
for i in range(9):
    bpages[i].pack(side=LEFT, padx=7)

fflevels = ScrollableFrame(flevelmenu, bg=MAINCOLOR)
fflevels.pack(expand=1, fill=BOTH)

ffflevel = [Frame(fflevels.scrollable_frame, bg=MAINCOLOR) for i in range(MLEVELS)]
for i in range(MLEVELS):
    ffflevel[i].pack(side=TOP, anchor=NW, pady=5)

blevel = [Button(ffflevel[i], text=i, width=10, height=2, command=fshowlevel(i),
                 bg=buttoncolors[guesses[CURRENT_PAGE.get()][i][0]]) for i in range(MLEVELS)]
for i in range(MLEVELS):
    blevel[i].pack(side=LEFT, padx=15)

lcurrentbest = [Label(ffflevel[i], height=2, bg=MAINCOLOR, font=15) for i in range(MLEVELS)]
for i in range(MLEVELS):
    lcurrentbest[i].pack(side=LEFT)

blevelmenu_to_menu = Button(flevelmenu, text="Главное Меню", width=15, height=3, command=fmainmenu.lift)
blevelmenu_to_menu.pack(side=RIGHT, anchor=SE, padx=5, pady=5)

# def recursively_bind_escape_thelevel(node):
#     node.bind("<Escape>", fshowlevelmenu)
#     for child in node.children.values():
#         recursively_bind_escape_thelevel(child)
# recursively_bind_escape_thelevel(fthelevel)

# Rules
frules = Frame(root, bg=MAINCOLOR)
frules.place(relwidth=1, relheight=1)

ffrules = Frame(frules, bg=MAINCOLOR)
ffrules.pack(expand=1, fill=BOTH)

trules = Text(ffrules, bg=MAINCOLOR, wrap=WORD, height=26)
textrules = '''Цель каждого уровня:
выразить через определённую цифру с помощью операций +, -, *, /, ^, √, !,
то бишь сложения, вычитания, умножения, деления, возведения в степень, квадратного корня и факториала

Порядок операций следующий:
1) Квадратный корень √
2) Факториал !
3) Возведение в степень ^ (выполняются СЛЕВА НАПРАВО)
4) Умножение * и деление / (выполняются СЛЕВА НАПРАВО)
5) Сложение + и вычитание - (выполняются СЛЕВА НАПРАВО)

Порядок операций можно менять скобками
Можно пользоваться круглыми (), квадратными [] и фигурными {} скобками

Разрешены унарные операции сложения и вычитания,
то есть можно писать (-5), (+7) и (2^-2). В последнем случае результат будет 1/4

Можно опускать скобки после корня и перед факториалом,
то есть можно писать (√√√4), (3!!), (√4!).
Результатами этих выражений будут √(√2), 720 и 2 соответственно

Другого рода последовательно написанные операции влекут ошибку чтения

Enjoy =)
'''
#trules.tag_configure(CENTER, justify=CENTER)
trules.insert("1.0", textrules)
#trules.tag_add(CENTER, "1.0", "end")
trules["state"] = DISABLED
trules.pack(expand=1)

def fromrules():
    if RULES_TO_LEVEL:
        fthelevel.lift()
    else:
        fmainmenu.lift()
breturn_to_level = Button(frules, text="Вернуться", width=15, height=3, command=fromrules)
breturn_to_level.pack(side=LEFT, anchor=SW, padx=5, pady=5)


# The Level
frame_guesser_and_hints = Frame(fthelevel, bg=MAINCOLOR)
frame_guesser_and_hints.pack(expand=1, fill=BOTH)

ffguesser=Frame(frame_guesser_and_hints, bg=MAINCOLOR)
ffguesser.pack(side=LEFT, expand=1, fill=BOTH)

fflevelcenter = Frame(ffguesser, bg=MAINCOLOR)
fflevelcenter.pack(expand=1)

lthelevel_title1 = Label(fflevelcenter, text="Уровень " + str(CURRENT_LEVEL),
                        bg=MAINCOLOR, font=("Arial", 16, "bold"), height=1)
lthelevel_title1.pack()
lthelevel_title2 = Label(fflevelcenter, text="Выразить через " + str(CURRENT_PAGE.get()),
                        bg=MAINCOLOR, font=("Arial", 16, "bold"), height=1)
lthelevel_title2.pack()

lerror = Label(fflevelcenter, text="", height=2, bg=MAINCOLOR, font=("Arial", 12, "bold"))
lerror.pack()

fff_inlevel_buttons = Frame(fflevelcenter, bg=MAINCOLOR)
fff_inlevel_buttons.pack()

ffffentry = Frame(fff_inlevel_buttons, bg=MAINCOLOR)
ffffentry.pack(side=LEFT, padx=10)

entry_expr = Entry(ffffentry, width=50)
entry_expr.pack(pady=5)

lresult = Label(ffffentry, bg=MAINCOLOR)
lresult.pack(pady=5)

def fconvert_sqrt():
    string = expr_sqrt_replace(entry_expr.get())
    entry_expr.delete(0, END)
    entry_expr.insert(0, string)
bconvert_sqrt = Button(ffffentry, text='Преобразовать "sqrt" и "v" в символ "√"', height=3, command=fconvert_sqrt)
bconvert_sqrt.pack(pady=5)

def fcalculate(event=None):
    global guesses
    global CURRENT_LEVEL
    cp = CURRENT_PAGE.get()
    guesses[cp][CURRENT_LEVEL][0] = max(guesses[cp][CURRENT_LEVEL][0], 1)
    guesses[cp][CURRENT_LEVEL].append(expr_sqrt_replace(entry_expr.get()))
    for i in range(NUM_GUESSES-1, 0, -1):
        lprev[i]["text"] = lprev[i-1]["text"]
    lprev[0]["text"] = expr_sqrt_replace(entry_expr.get())
    tup = myEval(entry_expr.get(), cp)
    if tup[0] is None:
        lresult["text"] = ""
        lerror["fg"] = "red"
        if tup[1] == 0:
            lerror["text"] = "Пустое выражение"
        elif tup[1] == 1:
            lerror["text"] = "Недопустимый символ: " + tup[2]
        elif tup[1] == 2:
            lerror["text"] = 'Лишняя закрывающая скобка: "' + tup[2] + '"'
        elif tup[1] == 3:
            lerror["text"] = 'Недостающая закрывающая скобка: "' + tup[2] + '"'
        else:
            lerror["text"] = 'Неправильное выражение (Прочтите правила): "' + tup[2] + '"'
    else:
        if isinstance(tup[0], fr.Fraction):
            lresult["text"] = "= " + str(tup[0]) + " = " + str(float(tup[0]))
        else:
            lresult["text"] = "= " + str(tup[0])
        if tup[2]:
            if tup[0] == CURRENT_LEVEL:
                cp = CURRENT_PAGE.get()
                if guesses[cp][CURRENT_LEVEL][1]:
                    previous = myEval(guesses[cp][CURRENT_LEVEL][1], cp)
                    previous = previous[1]
                else:
                    previous = float("inf")
                if tup[1] > infos[cp][CURRENT_LEVEL].minlen:
                    lerror["fg"] = "blue"
                    lerror["text"] = "Неплохо! Но можно найти решение получше"
                    guesses[cp][CURRENT_LEVEL][0] = max(guesses[cp][CURRENT_LEVEL][0], 2)
                elif tup[1] == infos[cp][CURRENT_LEVEL].minlen:
                    lerror["fg"] = "green"
                    lerror["text"] = "Поздравляю! Вы нашли оптимальное решение!"
                    guesses[cp][CURRENT_LEVEL][0] = max(guesses[cp][CURRENT_LEVEL][0], 3)
                else:
                    lerror["fg"] = "green"
                    lerror["text"] = "Поздравляю! Стоп что??? Вы нашли решение лучше моего!!! Напишите мне"
                    guesses[cp][CURRENT_LEVEL][0] = max(guesses[cp][CURRENT_LEVEL][0], 4)

                if tup[1] < previous:
                    guesses[cp][CURRENT_LEVEL][1] = expr_sqrt_replace(entry_expr.get())
                    lbest["text"] = "Лучшая попытка: " + guesses[cp][CURRENT_LEVEL][1]
            else:
                lerror["fg"] = "red"
                lerror["text"] = "Не то число"
        else:
            lerror["fg"] = "red"
            lerror["text"] = "Выражение содержит другие цифры"
    
beval = Button(fff_inlevel_buttons, text='Вычислить', height=3, width=15,
               font=("Arial", 12, "bold"), command=fcalculate)
beval.pack(side=LEFT, padx=5, expand=1, fill=Y)
entry_expr.bind("<Return>", fcalculate)

lbest = Label(fflevelcenter, text="Лучшая попытка: ", bg=MAINCOLOR, font=("Arial", 12, "bold"))
lbest.pack()

lprevtitle = Label(fflevelcenter, text="Предыдущие попытки", bg=MAINCOLOR)
lprevtitle.pack(anchor=NW)

lprev = [Label(fflevelcenter, bg=MAINCOLOR) for i in range(NUM_GUESSES)]
for i in range(NUM_GUESSES):
    lprev[i].pack()

ffhints = Frame(frame_guesser_and_hints, bg=MAINCOLOR)
ffhints.pack(side=LEFT, expand=1, fill=Y)

fffhints = Frame(ffhints, bg=MAINCOLOR)
fffhints.pack(expand=1)

oper_to_str = {"+": "Сложение",
               "-": "Вычитание",
               "*": "Умножение",
               "/": "Деление",
               "^": "Возведение в степень",
               "√": "Квадратный корень",
               "!": "Факториал"}

def fhint():
    global HINTNUM
    global CURRENT_LEVEL
    if HINTNUM == 0:
        if infos[CURRENT_PAGE.get()][CURRENT_LEVEL].lastop:
            HINTNUM = 1
            lhint["text"] = "Оптимальное число цифр: " + str(infos[CURRENT_PAGE.get()][CURRENT_LEVEL].minlen)
        else:
            lhint["text"] = "Серьёзно?"
    elif HINTNUM == 1:
        HINTNUM = 2
        lhint["text"] = "Последняя операция: " + oper_to_str[infos[CURRENT_PAGE.get()][CURRENT_LEVEL].lastop]
    elif HINTNUM == 2:
        HINTNUM = 0
        if isinstance(infos[CURRENT_PAGE.get()][CURRENT_LEVEL].first, tuple):
            lhint["text"] = "Второй аргумент: " + str(infos[CURRENT_PAGE.get()][CURRENT_LEVEL].second)
        else:
            lhint["text"] = "Первый аргумент: " + str(infos[CURRENT_PAGE.get()][CURRENT_LEVEL].first)
bhint = Button(fffhints, text="Подсказка", height=3, width=12, command=fhint)
bhint.pack()
lhint = Label(fffhints, height=3, bg=MAINCOLOR)
lhint.pack()

fthelevelbuttons = Frame(fthelevel, bg=MAINCOLOR)
fthelevelbuttons.pack(side=TOP, fill=X)

brules = Button(fthelevelbuttons, text="Правила", width=15, height=3, command=fshowrules(True))
brules.pack(side=LEFT, padx=5, pady=5)

bnextlevel = Button(fthelevelbuttons, text="Следующий уровень", width=20, height=3)
bnextlevel.pack(side=LEFT, expand=1)

b_thelevel_to_levelmenu = Button(fthelevelbuttons, text="Уровни", width=15, height=3, command=fshowlevelmenu)
b_thelevel_to_levelmenu.pack(side=LEFT, padx=5, pady=5)



fmainmenu.lift()
mixer.init()
mixer.music.load(music_path)
mixer.music.play(loops=-1)

root.mainloop()

mixer.music.stop()
mixer.music.unload()

# # # # # # # # # #
# # # GUI END # # #
# # # # # # # # # #

# Save progress
out = open(PROGRESS_FILENAME, "w", encoding="utf-8")
string = "CONFIG: " + str(CURRENT_PAGE.get()) + " " + MAINCOLOR + " " + str(volume.get()) + "\n"
out.write(string)
infilehash = [string]
for digit in range(1, 10):
    string = "DIGIT: " + str(digit) + "\n"
    out.write(string)
    infilehash.append(string)
    for number in range(MLEVELS):
        if guesses[digit][number][0]:
            string = "NUMBER: " + str(number) + "\n"
            out.write(string)
            infilehash.append(string)
            if guesses[digit][number][0] > 1:
                string = "BEST: " + guesses[digit][number][1] + "\n"
                out.write(string)
                infilehash.append(string)
            start = max(2, len(guesses[digit][number])-NUM_GUESSES)
            for expression in guesses[digit][number][start:]:
                string = expression + "\n"
                out.write(string)
                infilehash.append(string)
infilehash = myHash(infilehash)
out.write("HASH: " + str(infilehash) + "\n")
out.close()
