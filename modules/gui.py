from tkinter import *
import threading

rootWindow = Tk()
rootWindow.minsize(width=400, height=100)
rootWindow.config(background='#0080bc')

output = Label(rootWindow, text="")
output.config(font=("Lucida Sans Unicode", 20), background='#0080bc', fg='#ffffff')
output.pack()

def tkGo():
    global rootWindow
    rootWindow.mainloop()

LoadingInterrupt = False
LoadingThread = threading.Thread(target=tkGo)
LoadingThread.daemon = True
LoadingThread.start()

