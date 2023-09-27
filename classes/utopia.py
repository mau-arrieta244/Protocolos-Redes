import classes.maquina as maquina
import time
import threading
import classes.frame as frame

class Utopia(maquina.Maquina):

    def __init__(self, pName, pId):
        super().__init__(pName, pId)
        self.capaRed = self.CapaRed()
        self.capaEnlace = self.CapaEnlace()
        self.pausa = False
        self.capaFisicaRecibidos = []


    '''
    Mostrar historial de paquetes enviados
    '''
    def mostrarEnviados(self):
        print("\n===================\n")
        print("\n     Enviados:       \n")

        for elemento in self.capaEnlace.historialEnviados:
            print("\nFrame #%d" %(elemento.sequenceNumber))
            print("Contenido: %s" %(elemento.packet))

    '''
    Mostrar historial de frames recibidos
    '''
    def mostrarRecibidos(self):
        print("\n===================\n")
        print("\n     Recibidos:       \n")
        for elemento in self.capaEnlace.historialRecibidos:
            print("\nFrame #%d" %(elemento.sequenceNumber))
            print("Contenido: %s" %(elemento.packet))

    def toLinkLayer(self):
        '''
        Obtiene paquete de capaRed, lo envía a capaEnlace
        '''
        while(True):
            if not self.pausa:
                paquete = self.capaRed.enviarPaquete()
                if paquete:
                    self.capaEnlace.paquetes.append(paquete)
                    time.sleep(1)
            else:
                pass

    def startMachine(self,maquinaDestino:maquina.Maquina):
        
        t1 = threading.Thread(target=self.capaRed.generarPaquetes)
        t2 = threading.Thread(target=self.toLinkLayer)
        t3 = threading.Thread(target=lambda:self.capaEnlace.crearFrames())
        t4 = threading.Thread(target=lambda:self.capaEnlace.toPhysicalLayer(maquinaDestino))

        t1.start()
        t2.start()
        t3.start()
        t4.start()

    def startReceiverMachine(self):
        
        t1 = threading.Thread(target=lambda:self.capaEnlace.cicloRecibidos())
        t1.start()

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
                    #print("\nUtopia Paquete generado\n")
                    time.sleep(1)
                else:
                    pass

        '''
        Retorna ultimo paquete generado en self.paquetes
        Lo utiliza Maquina para enviar a CapaEnlace.framesEnviar
        '''
        def enviarPaquete(self):
            if self.paquetes:
                #last = self.paquetes[-1]
                #self.paquetes.clear()
                packet = self.paquetes.pop(0)
                return(packet)

    class CapaEnlace:

        def __init__(self):
            self.framesEnviar = []
            self.paquetes = []
            self.capaFisicaRecibidos = []
            self.historialEnviados = []
            self.historialRecibidos = []
            self.pausa = False

        '''
        Un ciclo que revisa si ha recibido paquetes de capaRed
        Si hay paquetes, los convierte a Frames y agrega a framesEnviar []
        '''
        def crearFrames(self):
            count = 0
            while(True):
                if not self.pausa:
                    if self.paquetes:
                        #paquete = self.paquetes[0]
                        paquete = self.paquetes.pop(0)
                        newFrame = frame.Frame(count,paquete,'Data')
                        self.framesEnviar.append(newFrame)
                        #self.paquetes.clear()
                        count+=1
                        time.sleep(1)
                else:
                    pass
        
        '''
        Envia Frame formateado a maquinaDestino
        No hay errores de comunicacion
        No hay ack o nak del receiver
        '''
        def toPhysicalLayer(self,maquinaDestino:maquina.Maquina):
            while(True):
                if not self.pausa:
                    if self.framesEnviar:
                        sendingFrame = self.framesEnviar.pop(0)
                        print("\n=============================\n")
                        print("\nUtopia Paquete %d enviado!\n" %(sendingFrame.sequenceNumber))
                        maquinaDestino.capaEnlace.capaFisicaRecibidos.append(sendingFrame)
                        self.historialEnviados.append(sendingFrame)
                        time.sleep(2)
                else:
                    pass

        '''
        Un ciclo que revisa si ha recibido frames desde otra maquina
        Si hay frames, los debe decodificar y enviar a capaRed
        '''
        def cicloRecibidos(self):
            while(True):
                if not self.pausa:
                    #si hay frames recibidos
                    if self.capaFisicaRecibidos:
                        #frame recibido correctamente
                        frameRecibido = self.capaFisicaRecibidos.pop(0)
                        print("\nFrame %d recibido por maquina B ! \n" % (frameRecibido.sequenceNumber))
                        self.historialRecibidos.append(frameRecibido)
                        time.sleep(1)

                else:
                    time.sleep(1)
                    pass