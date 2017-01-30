from Tkinter import *

rootWindow = Tk()
rootWindow.minsize(width=400, height=100)
rootWindow.config(background='#0080bc')

output = Label(rootWindow, text="")
output.config(font=("Lucida Sans Unicode", 20), background='#0080bc', fg='#ffffff')
output.pack()

# rootWindow.mainloop() # this is called before the main loop in samplerbox.py
