from tkinter import *
from tkinter import ttk
import threading
from PIL import ImageTk
import classes.utopia,classes.selectiveRepeat




root = Tk()
root.title('Seleccion de Protocolo')

protocolo = StringVar()

frame = Frame(root,width=800, height=600, bg="#007FFF")
frame.pack(side=TOP)

label = Label(frame,text="Seleccione un Protocolo:",font="Helvetica 15")
label.place(x=10,y=10)

screen_width = root.winfo_screenwidth()  # Width of the screen
screen_height = root.winfo_screenheight() # Height of the screen
 
# Calculate Starting X and Y coordinates for Window
x = (screen_width/2) - (800/2)
y = (screen_height/2) - (600/2)
 
root.geometry('%dx%d+%d+%d' % (800, 600, x, y))



# Create Dropdown menu ================================
options = ['Utopia','Stop and Wait']
combobox = ttk.Combobox(frame,textvariable = protocolo,
                        width=33,state="readonly")
combobox['values'] = ['Utopia','Stop and Wait','Selective Repeat']
combobox.place(x=10,y=40)





# Iniciar Simulacion Seleccionada =====================================
# Esto podría ser un Factory...  pero bruh 

def startSimulation():
    global maquina1
    global maquina2
    tipoSimulacion = combobox.get()

    match tipoSimulacion:
        case 'Utopia':
            maquina1 = classes.utopia.Utopia('Utopia_A',1)
            maquina2 = classes.utopia.Utopia('Utopia_B',2)
            maquina1.startMachine(maquina2)

        case 'StopAndWait':
            pass

        case 'PAR':
            pass

        case 'sliding':
            pass

        case 'goBack':
            pass

        case 'Selective Repeat':
            maquina1 = classes.selectiveRepeat.SelectiveRepeat('selective_A',1)
            maquina2 = classes.selectiveRepeat.SelectiveRepeat('selective_B',2)
            maquina1.startMachine(maquina2)
            maquina2.startReceiverMachine(maquina1)
            
        case _:
            print("Otra maquina")
            return
    




# Pausar Simulacion Seleccionada =====================================

def pauseSimulation():
    maquina1.pauseMachine()

# Continuar Simulacion pausada =====================================

def resumeSimulation():
    maquina1.resumeMachine()


# Boton inicio =========================================


btn = Button(frame,text="Iniciar",font="Helvetica 10",
             command= lambda:startSimulation(),
             width=15,height=2)
btn.place(x=250,y=10)


# Boton pausa =========================================


btn = Button(frame,text="Pausar",font="Helvetica 10",
             command=lambda:pauseSimulation(),
             width=15,height=2)
btn.place(x=400,y=10)


# Boton resume =========================================


btn = Button(frame,text="Resumir",font="Helvetica 10",
             command=lambda:resumeSimulation(),
             width=15,height=2)
btn.place(x=550,y=10)

# Imagenes máquina =========================================


photo = ImageTk.PhotoImage(file='images/computer.png')
img_label = Label(frame,image=photo)
img_label.photo = photo

btn2 = Button(frame,image=photo,borderwidth=0)
btn2.place(x=50,y=200)

photo2 = ImageTk.PhotoImage(file='images/server.png')
img_label2 = Label(frame,image=photo2)
img_label2.photo = photo2

btn3 = Button(frame,image=photo2,borderwidth=0)
btn3.place(x=340,y=200)


T = Text(frame, height = 5, width = 61)
T.insert(END,chars='') 
T.place(x=50,y=420)


# Main loop =========================================


mainloop()