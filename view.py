from tkinter import *
from tkinter import ttk
import threading
from PIL import ImageTk
import classes.utopia,classes.maquina



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
combobox['values'] = ['Utopia','Stop and Wait']
combobox.place(x=10,y=40)




# Iniciar Simulacion Seleccionada =====================================
# Esto podría ser un Factory...  pero bruh 

def startSimulation():
    tipoSimulacion = combobox.get()
    print("\ntipo sim: "+tipoSimulacion)

    match tipoSimulacion:
        case 'Utopia':
            a = classes.utopia.Utopia('a',1)
            t1 = threading.Thread(target=a.capaRed.generarPaquetes)
            t2 = threading.Thread(target=a.toLinkLayer)

            t1.start()
            t2.start()
        case _:
            print("Otra maquina")


    

# Pausar Simulacion Seleccionada =====================================

def pauseSimulation(maquina):
    maquina.condicionToLinkLayer = False
    maquina.CapaRed.condicionGenerarPaquetes = False


# Continuar Simulacion pausada =====================================

def resumeSimulation(maquina):
    maquina.condicionToLinkLayer = True
    maquina.CapaRed.condicionGenerarPaquetes = True


# Boton inicio =========================================


btn = Button(frame,text="Iniciar",font="Helvetica 10",
             command= lambda:startSimulation(),
             width=15,height=2)
btn.place(x=250,y=10)


# Boton pausa =========================================


btn = Button(frame,text="Pausar",font="Helvetica 10",
             command=lambda:pauseSimulation(a),
             width=15,height=2)
btn.place(x=400,y=10)


# Boton resume =========================================


btn = Button(frame,text="Resumir",font="Helvetica 10",
             command=lambda:resumeSimulation(a),
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