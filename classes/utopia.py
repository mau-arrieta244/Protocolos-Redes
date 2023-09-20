import classes.maquina as maquina
import time

class Utopia(maquina.Maquina):

    def __init__(self, pName, pId):
        super().__init__(pName, pId)
        self.capaRed = self.CapaRed()
        self.capaEnlace = self.CapaEnlace()
        self.paquetesRed_Enlace = []
        self.condicionToLinkLayer = True

    def toLinkLayer(self):
        while(True):
            if self.condicionToLinkLayer:
                paquete = self.capaRed.enviarPaquete()
                if paquete:
                    self.paquetesRed_Enlace.append(paquete)
                    print("\nUtopia Paquete recibido en enlace..\n")
                    print("\nLast packet: "+self.paquetesRed_Enlace[-1]+"\n")
                    time.sleep(3)
            else:
                pass

    class CapaRed:
    
        def __init__(self):
            self.paquetes = []
            self.framesRecibidos = []
            self.condicionGenerarPaquetes = True
    

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
                if self.condicionGenerarPaquetes:
                    string = str(count)+"abcd"
                    self.paquetes.append(string)
                    count+=1
                    print("\nUtopia Paquete generado\n")
                    time.sleep(3)
                else:
                    pass

        #Retorna el primer paquete de self.paquetes
        #"envia" paquete a capa enlace
        def enviarPaquete(self):
            if self.paquetes:
                return(self.paquetes[-1])

    class CapaEnlace:

        def __init__(self):
            self.framesEnviar = []
            self.framesRecibidos = []
        
        def getFramesEnviar(self):
            return(self.framesEnviar)