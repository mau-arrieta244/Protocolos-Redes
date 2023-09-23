import classes.maquina as maquina
import time
import threading

class StopWait(maquina.Maquina):

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
                    self.capaEnlace.framesEnviar.append(paquete)
                    time.sleep(3)
            else:
                pass

    def startMachine(self,maquinaDestino:maquina.Maquina):
        
        t1 = threading.Thread(target=self.capaRed.generarPaquetes)
        t2 = threading.Thread(target=self.toLinkLayer)
        t3 = threading.Thread(target=lambda:self.capaEnlace.toPhysicalLayer(maquinaDestino))
        t1.start()
        t2.start()
        t3.start()

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
                    print('\nCondicion paquetes:'+str(self.pausa))
                    print("\nUtopia Paquete generado\n")
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
            self.pausa = False
        
        '''
        Importante!! acordarme que aca hay que mandar un FRAME formateado , no un paquete suelto.
        '''
        def toPhysicalLayer(self,maquinaDestino:maquina.Maquina):
            while(True):
                if not self.pausa:
                    if self.framesEnviar:
                        paquete = self.framesEnviar[0]
                        maquinaDestino.capaFisicaRecibidos.append(paquete)
                        print("\n=============================\n")
                        print("\nUtopia Paquete recibido en otra maquina!\n")
                        print("\nLast packet: "+maquinaDestino.capaFisicaRecibidos[-1]+"\n")
                        print("\n=============================\n")
                        self.framesEnviar.clear()
                        time.sleep(3)
                else:
                    pass