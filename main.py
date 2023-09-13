import time
import threading

class Maquina:
    def __init__(self,pName,pId):
        
        self.name = pName
        self.id = pId
        self.capaRed = CapaRed()
        self.capaEnlace = CapaEnlace()
        self.paquetesRed_Enlace = []

    

    def toLinkLayer(self):
        while(True):
            paquete = self.capaRed.enviarPaquete()
            if paquete:
                self.paquetesRed_Enlace.append(paquete)
                #target.insert("\nPaquete recibido en enlace..\n")
                print("\nPaquete recibido en enlace..\n")
                #target.insert("\nLast packet: "+self.paquetesRed_Enlace[-1]+"\n")
                print("\nLast packet: "+self.paquetesRed_Enlace[-1]+"\n")
                time.sleep(2)
            
        
    

class CapaRed:
    
    def __init__(self):
        self.paquetes = []
        self.framesRecibidos = []
    

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
            string = str(count)+"abcd"
            self.paquetes.append(string)
            count+=1
            print("\nPaquete generado\n")
            time.sleep(4)
            

    #Retorna el primer paquete de self.paquetes
    #"envia" paquete a capa enlace
    def enviarPaquete(self):
        if self.paquetes:
            time.sleep(1)
            print("\nPaquete enviado\n")
            return self.paquetes.pop(0)
        else:
            return None
            



class CapaEnlace:

    def __init__(self):
        self.framesEnviar = []
        self.framesRecibidos = []
    
    def getFramesEnviar(self):
        return(self.framesEnviar)
    



'''
a = Maquina('A',24)

t1 = threading.Thread(target=a.capaRed.generarPaquetes)
t2 = threading.Thread(target=a.toLinkLayer)

t1.start()
t2.start()

t1.join()
t2.join()
'''

    

