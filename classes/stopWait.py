import time
import threading
import random
import classes.maquina as maquina

class Event:
    FRAME_ARRIVAL = "frame_arrival"


class Packet:
    def __init__(self, data):
        self.data = data

class Frame():

    def __init__(self,pSequenceNumber,pPacket,pKind):
        self.sequenceNumber = pSequenceNumber
        self.packet = pPacket
        self.kind = pKind

def wait_for_event(event):
    event.wait()  # Esperar hasta que se marque el evento

class StopWait(maquina.Maquina): 
    def __init__(self,pName,pId):
        super().__init__(pName, pId)

        self.capaRed = self.CapaRed()
        self.capaEnlace = self.CapaEnlace()

        self.pausa = False

    #CAPA DE RED 
    class CapaRed:
        def __init__(self):
            self.paquetes = []
            self.framesRecibidos = []
            self.condicionGenerarPaquetes = True
            self.pausa = False

        #Genera Paquetes
        def from_network_layer(self):
            data = f"Data from network layer at time {time.time()}"
            packet = Packet(data)
            return packet
        
        def to_physical_layer(self, frame, destino):
            
            if (frame.kind == 'ACK'):
                print(f"Sending ACK confirmation {frame.sequenceNumber}")
            else:
                print(f"Sending frame {frame.sequenceNumber}: {frame.packet.data}")
                destino.capaEnlace.framesRecibidos.append(frame)
            
            time.sleep(1)

        
    class CapaEnlace:
        def __init__(self):
            self.framesEnviar = []
            self.framesRecibidos = []
            self.pausa = False

        def from_physical_layer(self):
            frameRecibido = self.framesRecibidos[-1]
            ''' 
            data = f"Received frame at time {time.time()}"
            packet = Packet(data)
            frame = Frame(packet)
            '''
            return frameRecibido
        
        def print_received_frames(self):
            print("Frames recibidos en la capa de enlace:")
            for frame in self.framesRecibidos:
                print(f"Sequence Number: {frame.sequenceNumber}, Kind: {frame.kind}, Data: {frame.packet.data}")

        # Entrega información desde una trama entrante a la capa de red.
        def to_network_layer(self, packet):
            print("Received data in the network layer:", packet.data)


    def sender(self,event, destino):
        contFrames = 1

        while True:
            if (not self.pausa):
                time.sleep(2)
                packet = self.capaRed.from_network_layer() #generar paquete
                frame = Frame(contFrames,packet,'DATA') #genera Frame con info de paquete
                contFrames += 1
                self.capaRed.to_physical_layer(frame,destino) # Enviar frame
                
                # Esperar la confirmación (ACK) del receptor
                event.wait()
                event.clear()  # Limpiar el evento para futuras esperas

    

    def receiver(self, event, origen):
        while True:
            if (not self.pausa):
                if (self.capaEnlace.framesRecibidos):
                    time.sleep(1)
                    received_frame = self.capaEnlace.from_physical_layer()
                    #Vaciar recibidos:
                    self.capaEnlace.framesRecibidos = []

                    self.capaEnlace.to_network_layer(received_frame.packet)
                    
                    # Enviar acknowledgment (dummy frame) para despertar al emisor
                    dummy_packet = Packet("ACK")
                    dummy_frame = Frame(received_frame.sequenceNumber, dummy_packet,'ACK')
                    self.capaRed.to_physical_layer(dummy_frame,origen)
                    
                    # Marcar el evento para despertar al emisor
                    event.set()

    def pauseMachine(self):
        self.pausa = True

    def resumeMachine(self):
        self.pausa = False

def ejecucion(maquina1, maquina2):
    #EJECUCION----------------------------------------------
    # Crear una bandera de evento
    frame_event = threading.Event()

    # Simulación de la comunicación entre sender y receiver
    sender_thread = threading.Thread(target=maquina1.sender, args=(frame_event,maquina2))
    receiver_thread = threading.Thread(target=maquina2.receiver, args=(frame_event,maquina1))

    # Iniciar el sender y esperar un poco antes de iniciar el receiver
    sender_thread.start()
    time.sleep(5)  # Esperar para asegurar que el sender haya enviado al menos un frame
    receiver_thread.start()

