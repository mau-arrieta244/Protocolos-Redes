
import time
import threading
import classes.maquina as maquina
import classes.frame as frame

class SelectiveRepeat(maquina.Maquina):

    def __init__(self, pName, pId):
        super().__init__(pName, pId)
        self.capaRed = self.CapaRed()
        self.capaEnlace = self.CapaEnlace()
        self.pausa = False
        self.capaFisicaRecibidos = []

    def toLinkLayer(self):
        '''
        Obtiene paquete de capaRed, lo envía a capaEnlace
        '''
        while(True):
            if not self.pausa:
                paquete = self.capaRed.enviarPaquete()
                if paquete:
                    self.capaEnlace.paquetes.append(paquete)
                    #self.capaEnlace.framesEnviar.append(paquete)
                    time.sleep(3)
            else:
                pass

    def startMachine(self,maquinaDestino:maquina.Maquina):
        
        t1 = threading.Thread(target=self.capaRed.generarPaquetes)
        t2 = threading.Thread(target=self.toLinkLayer)
        t3 = threading.Thread(target=self.capaEnlace.crearFrames)
        t4 = threading.Thread(target=lambda:self.capaEnlace.toPhysicalLayer(maquinaDestino))

        t1.start()
        t2.start()
        t3.start()
        t4.start()

    def pauseMachine(self):
        
        self.pausa = True
        self.capaRed.pausa = True
        self.capaEnlace.pausa = True

    def resumeMachine(self):
        
        self.pausa = False
        self.capaRed.pausa = False
        self.capaEnlace.pausa = False
        

    class CapaRed:
    
        def __init__(self):
            self.paquetes = []
            self.framesRecibidos = []
            self.pausa = False
    

        '''
        Genera paquetes con strings aleatorios
        Los almacena en self.paquetes
        De self.paquetes se enviaran a CapaEnlace
        En CapaEnlace se convierten en Frames
        En CapaEnlace se almacenan en framesEnviar
        '''
        def generarPaquetes(self):
            count = 0
            while(True):
                if not self.pausa:
                    string = str(count)+"abcd"
                    self.paquetes.append(string)
                    count+=1
                    #print('\nCondicion paquetes:'+str(self.pausa))
                    #print("\nUtopia Paquete generado\n")
                    time.sleep(3)
                else:
                    pass

        '''
        Retorna ultimo paquete generado en self.paquetes
        Lo utiliza Maquina para enviar a CapaEnlace.framesEnviar
        '''
        def enviarPaquete(self):
            if self.paquetes:
                last = self.paquetes[-1]
                self.paquetes.clear()
                return(last)

    class CapaEnlace:

        def __init__(self):
            self.framesEnviar = []
            self.paquetes = []
            self.pausa = False
        
        '''
        Por hacer:
        -esperar ack o nak para enviar frames de acuerdo con la ventana.
        -comunicarme tambien con capa red, pasarle los paquetes recibidos, en  orden
        '''
        def toPhysicalLayer(self,maquinaDestino:maquina.Maquina):
            while(True):
                if not self.pausa:
                    if self.framesEnviar:
                        sendingFrame = self.framesEnviar[0]
                        maquinaDestino.capaFisicaRecibidos.append(sendingFrame)
                        self.framesEnviar.clear()
                        print("\n=============================\n")
                        print("\nSelective Repeat Frame recibido en otra maquina!\n")
                        print("\nLast Frame: "+maquinaDestino.capaFisicaRecibidos[-1].packet+"\n")
                        print("\n=============================\n")
                        time.sleep(3)
                else:
                    pass
        '''
        Un ciclo que revisa si ha recibido paquetes de capaRed
        Si hay paquetes, los convierte a Frames y agrega a framesEnviar []
        '''
        def crearFrames(self):
            count = 0
            while(True):
                if not self.pausa:
                    if self.paquetes:
                        paquete = self.paquetes[0]
                        newFrame = frame.Frame(count,paquete,'Data')
                        self.framesEnviar.append(newFrame)
                        self.paquetes.clear()
                        time.sleep(2)
                else:
                    pass
