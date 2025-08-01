from tkinter import *

root = Tk()

e = Entry(root,width=50, bg="green", fg="white", borderwidth=20)
e.pack()
e.get()
# створення Label 
# myLabel1 = Label(root, text="Hello world")
# myLabel2 = Label(root, text="Learn")
# myLabel3 = Label(root, text="Python")
# myLabel2 = Label(root, text="Learn")
# виведення по рядкам стовпцям
# myLabel1.grid(row=0, column=0)
# myLabel2.grid(row=1, column=1) 
# myLabel3.grid(row=2, column=0)
#СТворення кнопок

def myClick():
    hello="Hello "+e.get()
    myLabel= Label(root,text=hello)
    myLabel.pack()
    


myButton= Button(root,text="Enter ypur name", padx="50",pady="25",command=myClick, fg="red", bg="yellow") #state="disable"
myButton.pack()
# myButton.grid()
root.mainloop() 
