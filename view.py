from tkinter import *
from tkinter import ttk
from PIL import ImageTk,Image


root = Tk()
root.title('Seleccion de Protocolo')

protocolo = StringVar()

frame = Frame(root,width=600, height=400, bg="#007FFF")
frame.pack(side=TOP)

label = Label(frame,text="Seleccione un Protocolo:",font="Helvetica 28")
label.place(x=90,y=80)

screen_width = root.winfo_screenwidth()  # Width of the screen
screen_height = root.winfo_screenheight() # Height of the screen
 
# Calculate Starting X and Y coordinates for Window
x = (screen_width/2) - (600/2)
y = (screen_height/2) - (400/2)
 
root.geometry('%dx%d+%d+%d' % (600, 400, x, y))

def clicked(opcion):
    print("Opcion seleccionada fue: "+opcion)

# Create Dropdown menu ================================
options = ['Utopia','Stop and Wait']
combobox = ttk.Combobox(frame,textvariable = protocolo,
                        width=65,state="readonly")
combobox['values'] = ['Utopia','Stop and Wait']
combobox.place(x=90,y=150)



#Segunda Ventana =====================================
def startSimulation():
    top = Toplevel()
    top.title('Protocolo')
    top.geometry('%dx%d+%d+%d' % (600, 400, x, y))
    frame2 = Frame(top,width=600, height=400, bg="#007FFF")
    frame2.pack(side=TOP)

    label2 = Label(frame2,text="Protocolo: "+combobox.get(),
                  font="Helvetica 20")
    label2.place(x=20,y=20)

    #compuImage = Image.open("computer.png")
    photo = ImageTk.PhotoImage(file='images/computer.png')
    img_label = Label(frame2,image=photo)
    img_label.photo = photo

    btn2 = Button(frame2,image=photo,borderwidth=0)
    btn2.place(x=50,y=70)

    photo2 = ImageTk.PhotoImage(file='images/server.png')
    img_label2 = Label(frame2,image=photo2)
    img_label2.photo = photo2

    btn3 = Button(frame2,image=photo2,borderwidth=0)
    btn3.place(x=340,y=70)


#======================================================


btn = Button(frame,text="Iniciar",font="Helvetica 12",
             command=startSimulation,
             width=15,height=5)
btn.place(x=90,y=190)

#======================================================


mainloop()