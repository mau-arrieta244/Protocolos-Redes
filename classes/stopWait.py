import time
import threading
import random

class Event:
    FRAME_ARRIVAL = "frame_arrival"

class Packet:
    def __init__(self, data):
        self.data = data

class Frame:

    def __init__(self,pSequenceNumber,pPacket,pKind):
        self.sequenceNumber = pSequenceNumber
        self.packet = pPacket
        self.kind = pKind

def wait_for_event(event):
    event.wait()  # Esperar hasta que se marque el evento

class Maquina: 
    def __init__(self,pName,pId):
        self.name = pName
        self.id = pId

        self.capaRed = self.CapaRed()
        self.capaEnlace = self.CapaEnlace()

        self.pausa = False

    #CAPA DE RED 
    class CapaRed:
        def __init__(self):
            self.paquetes = []
            self.framesRecibidos = []
            self.condicionGenerarPaquetes = True

        #Genera Paquetes
        def from_network_layer(self):
            data = f"Data from network layer at time {time.time()}"
            packet = Packet(data)
            return packet
        
        def to_physical_layer(self, frame, destino):
            destino.capaEnlace.framesRecibidos.append(frame)
            if (frame.kind == 'ACK'):
                print(f"Sending ACK confirmation {frame.sequenceNumber}")
            else:
                print(f"Sending frame {frame.sequenceNumber}: {frame.packet.data}")
            time.sleep(1)

        
    class CapaEnlace:
        def __init__(self):
            self.framesEnviar = []
            self.framesRecibidos = []

        def from_physical_layer(self):
            frameRecibido = self.framesRecibidos[-1]
            ''' 
            data = f"Received frame at time {time.time()}"
            packet = Packet(data)
            frame = Frame(packet)
            '''
            return frameRecibido

        # Entrega información desde una trama entrante a la capa de red.
        def to_network_layer(self, packet):
            print("Received data in the network layer:", packet.data)


    def sender(self,event, destino):
        contFrames = 0

        while True:
            packet = self.capaRed.from_network_layer() #generar paquete
            frame = Frame(contFrames,packet,'DATA') #genera Frame con info de paquete
            contFrames += 1
            self.capaRed.to_physical_layer(frame,destino) # Enviar frame
            
            # Esperar la confirmación (ACK) del receptor
            event.wait()
            event.clear()  # Limpiar el evento para futuras esperas


    def receiver(self, event, origen):
        while True:
            if (self.capaEnlace.framesRecibidos):
                received_frame = self.capaEnlace.from_physical_layer()
                self.capaEnlace.to_network_layer(received_frame.packet)
                
                # Enviar acknowledgment (dummy frame) para despertar al emisor
                dummy_packet = Packet("ACK")
                dummy_frame = Frame(received_frame.sequenceNumber, dummy_packet,'ACK')
                self.capaRed.to_physical_layer(dummy_frame,origen)
                
                #Vaciar recibidos:
                self.capaRed.framesRecibidos = []

                # Marcar el evento para despertar al emisor
                event.set()


#EJECUCION----------------------------------------------
# Crear una bandera de evento
frame_event = threading.Event()

maquina1 = Maquina('Maquina1',1)
maquina2 = Maquina('Maquina2',2)

# Simulación de la comunicación entre sender y receiver
sender_thread = threading.Thread(target=maquina1.sender, args=(frame_event,maquina2))
receiver_thread = threading.Thread(target=maquina2.receiver, args=(frame_event,maquina1))

# Iniciar el sender y esperar un poco antes de iniciar el receiver
sender_thread.start()
time.sleep(2)  # Esperar para asegurar que el sender haya enviado al menos un frame
receiver_thread.start()
