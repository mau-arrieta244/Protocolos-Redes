
import time
import threading
import classes.maquina as maquina
import classes.frame as frame
from random import random

class SelectiveRepeat(maquina.Maquina):

    def __init__(self, pName, pId):
        super().__init__(pName, pId)

        self.capaRed = self.CapaRed(pName)
        self.capaEnlace = self.CapaEnlace(pName)

        #self.capaRed = self.CapaRed()
        #self.capaEnlace = self.CapaEnlace()
        self.pausa = False
        #self.capaFisicaRecibidos = []


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
                    #self.capaEnlace.framesEnviar.append(paquete)
                    time.sleep(1)
            else:
                pass

    def startMachine(self,maquinaDestino:maquina.Maquina,ventana):
        
        t1 = threading.Thread(target=self.capaRed.generarPaquetes)
        t2 = threading.Thread(target=self.toLinkLayer)
        t3 = threading.Thread(target=self.capaEnlace.crearFrames)
        t4 = threading.Thread(target=lambda:self.capaEnlace.toPhysicalLayer(maquinaDestino,ventana))

        t1.start()
        t2.start()
        t3.start()
        t4.start()

    def startReceiverMachine(self,maquinaDestino:maquina.Maquina,porcentaje):
        
        t1 = threading.Thread(target=lambda:self.capaEnlace.cicloRecibidos(maquinaDestino,porcentaje))
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
    
        def __init__(self,pName):
            self.paquetes = []
            self.framesRecibidos = []
            self.pausa = False
            self.name = pName
    

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
                    time.sleep(1)
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

        def __init__(self,pName):
            self.framesEnviar = []
            self.window = []
            self.paquetes = []
            self.capaFisicaRecibidos = []
            self.historialEnviados = []
            self.historialRecibidos = []
            self.pausa = False
            self.name = pName
        

        def sendItems(maquinaDestino:maquina.Maquina):
            pass


        def outlyingFrames(self,maquinaDestino):
            #Outlying frames? esperar nak o timeout
            #Acks llegaron? limpiar ventana
            if self.capaFisicaRecibidos:
                copia = self.capaFisicaRecibidos.copy()
                for elemento in copia:
                    #print("\nelemento: %d existe wtf" %(elemento.sequenceNumber))
                    id = elemento.sequenceNumber

                    #acknowledged
                    if(elemento.kind=='ack'):
                        #borrar de window
                        self.deleteById(id)
                        #borrar el ack
                        self.deleteRecibidosById(id)
                        #self.capaFisicaRecibidos.remove(elemento)
                        #print("\n ack  %d borrado..." %(id))
                        #print(len(self.capaFisicaRecibidos))
                        #time.sleep(1)

                    #not acknowledged
                    else:
                        resendFrame = self.getFrameById(id)
                        if(resendFrame):
                            print("\n Frame %d reenviado! \n" % (resendFrame.sequenceNumber))
                            self.historialEnviados.append(resendFrame)
                            #self.capaFisicaRecibidos.remove(elemento)
                            self.deleteRecibidosById(id)
                            #print("\n nak  %d borrado..." %(id))
                            maquinaDestino.capaEnlace.capaFisicaRecibidos.append(resendFrame)
                            #borrar el nak pero no el frame de window
                            #time.sleep(1)
                    
                time.sleep(2)
                #print("\n viene otro ciclo...")
            else:
                pass

        '''
        Por hacer:
        -Esperar ack o nak para enviar frames de acuerdo con la ventana.
        -
        '''
        def toPhysicalLayer(self,maquinaDestino:maquina.Maquina,windowSize):
            while(True):
                if not self.pausa:
                    #checkear acks o naks que hayan llegado...(missing)
                    #si window size es 2, hasta que lleguen ambos acks o naks libero window

                    #si hay frames listos
                    if self.framesEnviar:

                        
                        #vamos llenando self.window
                        #print("\n window len: "+str(len(self.window)))
                        #print("\n window size: "+str(windowSize))
                        if (len(self.window)<windowSize):
                            sendingFrame = self.framesEnviar.pop(0)
                            self.window.append(sendingFrame)
                            #time.sleep(1)

                        #ventana llena
                        else:
                            #antes de enviar, revisar de nuevo acks y naks
                            self.outlyingFrames(maquinaDestino)
                            #los envía todos pero no vacía ventana
                            buffer = self.window.copy()
                            while(buffer):
                                sendingFrame = buffer.pop(0)
                                maquinaDestino.capaEnlace.capaFisicaRecibidos.append(sendingFrame)
                                self.historialEnviados.append(sendingFrame)
                                #time.sleep()
 
                            time.sleep(2)
                            print("\n Acknowledgements:\n")
                            for elemento in self.capaFisicaRecibidos:
                                print(str(elemento.sequenceNumber)+" "+elemento.kind)
                            
                            
                            self.outlyingFrames(maquinaDestino)

                    else:
                        time.sleep(1)
                            
                            
                            

                            
                else:
                    pass
        
        
        
        
        def deleteById(self,sequenceNumber):
            for elemento in self.window:
                if elemento.sequenceNumber == sequenceNumber:
                    self.window.remove(elemento)
                    return
                
        def getFrameById(self,sequenceNumber):
            for elemento in self.window:
                if elemento.sequenceNumber == sequenceNumber:
                    return elemento
                
        def deleteRecibidosById(self,sequenceNumber):
            for elemento in self.capaFisicaRecibidos:
                if elemento.sequenceNumber == sequenceNumber:
                    self.capaFisicaRecibidos.remove(elemento)
                    return
                
                    
        
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
                        count+=1
                        time.sleep(1)
                else:
                    pass

        '''
        Un ciclo que revisa si ha recibido frames desde otra maquina
        Si hay frames, los agrega a un buffer
        Del buffer deben convertirse en paquetes y pasar en orden a la capaRed
        
        el porcentaje es porcentaje de error
        '''
        def cicloRecibidos(self,maquinaDestino:maquina.Maquina,porcentaje):
            while(True):
                if not self.pausa:
                    #si hay frames recibidos
                    if self.capaFisicaRecibidos:
                        #frame recibido correctamente
                        if random()>porcentaje:
                            frameRecibido = self.capaFisicaRecibidos.pop(0)
                            print("\n Frame %d recibido por maquina B ! \n" % (frameRecibido.sequenceNumber))
                            ackFrame = frame.Frame(frameRecibido.sequenceNumber,None,'ack')
                            maquinaDestino.capaEnlace.capaFisicaRecibidos.append(ackFrame)
                            self.historialRecibidos.append(frameRecibido)
                            #time.sleep(1)
                        #lost packets
                        else:
                            frameRecibido = self.capaFisicaRecibidos.pop(0)
                            print("\n Frame %d perdido... \n" % (frameRecibido.sequenceNumber))
                            nakFrame = frame.Frame(frameRecibido.sequenceNumber,None,'nak')
                            maquinaDestino.capaEnlace.capaFisicaRecibidos.append(nakFrame)
                            #time.sleep(1)
                        #time.sleep(1)
                        

                else:
                    time.sleep(1)
                    pass
                    
      
