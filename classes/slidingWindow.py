import time
import threading
import random

class Event:
    FRAME_ARRIVAL = "frame_arrival"
    CKSUM_ERR = "cksum_err"

class Maquina:
    def __init__(self,pName,pId, pTasaErrores):
        self.name = pName
        self.id = pId
        self.capaRed = self.CapaRed(pName)
        self.capaEnlace = self.CapaEnlace(pName,pTasaErrores)
        self.paquetesRed_Enlace = []
        self.condicionToLinkLayer = True
        self.capaFisicaRecibidos = []
        self.pausa = False
        

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

class SlidingWindow(Maquina): 
    def __init__(self,pName,pId, pTasaErrores):
        super().__init__(pName, pId, pTasaErrores)
        self.pausa = False

    #CAPA DE RED 
    class CapaRed:
        def __init__(self, pName):
            self.paquetes = []
            self.framesRecibidos = []
            self.condicionGenerarPaquetes = True
            self.pausa = False
            self.nombre = pName

        #Genera Paquetes
        def from_network_layer(self):
            data = f"Data from network layer at time {time.time()}"
            packet = Packet(data)
            return packet
        
        def to_physical_layer(self, frame, destino):
            if (frame.kind == 'ACK'):
                print(self.nombre + f": ACK confirmation {frame.sequenceNumber}"  +'\n' )
            else:
                print(self.nombre + f": Sending frame {frame.sequenceNumber}: {frame.packet.data}")
                destino.capaEnlace.framesRecibidos.append(frame)
            
            time.sleep(1)

    
    class CapaEnlace:
        def __init__(self, pName,pTasaErrores):
            self.framesEnviar = []
            self.framesRecibidos = []
            self.pausa = False
            self.nombre = pName
            self.tasaErrores = pTasaErrores

        def simular_error(self,tasa_error_porcentaje):
            # Generar un número aleatorio entre 0 y 99 para representar el porcentaje de error
            numero_aleatorio = random.randint(0, 99)

            # Si el número aleatorio está dentro de la tasa de error, se genera un error
            if numero_aleatorio < tasa_error_porcentaje:
                return True
            else:
                return False
    
        def from_physical_layer(self):
            frameRecibido = self.framesRecibidos[-1]
            #Generar error!
            if (self.simular_error(self.tasaErrores)):
                print(f"Error de transmision en Frame: {frameRecibido.sequenceNumber}")
                return None
            return frameRecibido
        
        def print_received_frames(self):
            print("Frames recibidos en la capa de enlace:")
            for frame in self.framesRecibidos:
                print(f"Sequence Number: {frame.sequenceNumber}, Kind: {frame.kind}, Data: {frame.packet.data}")

        # Entrega información desde una trama entrante a la capa de red.
        def to_network_layer(self, packet):
            print(self.nombre + ": Received data in the network layer:", packet.data)

    def sender(self, event, destino):
        contFrames = 1

        while True:
            if not self.pausa:
                time.sleep(2)
                packet = self.capaRed.from_network_layer()  # generar paquete
                frame = Frame(contFrames, packet, 'DATA')  # genera Frame con info de paquete
                self.capaRed.to_physical_layer(frame, destino)  # Enviar frame

                # Esperar la confirmación (ACK) del receptor
                ack_received = event.wait(timeout=10)  # espera 5 segundos por el ACK
                if ack_received:
                    contFrames += 1
                    print(self.name + " si recibe ACK " + str(contFrames - 1))
                else:
                    print("Se agota el tiempo de espera, vuelve a enviar el frame")
                event.clear()  # Limpiar el evento para futuras esperas


    def receiver(self, event, origen):
        while True:
            if not self.pausa:
                if self.capaEnlace.framesRecibidos:
                    time.sleep(1)
                    received_frame = self.capaEnlace.from_physical_layer()
                    self.capaEnlace.framesRecibidos = []

                    if received_frame is None:
                        print("No enviar ACK")
                        
                    else:
                        self.capaEnlace.to_network_layer(received_frame.packet)

                        # Enviar acknowledgment (dummy frame) para despertar al emisor
                        dummy_packet = Packet("ACK")
                        dummy_frame = Frame(received_frame.sequenceNumber, dummy_packet, 'ACK')
                        self.capaRed.to_physical_layer(dummy_frame, origen)

                        # Marcar el evento para despertar al emisor
                        event.set()


    def pauseMachine(self):
        self.pausa = True

    def resumeMachine(self):
        self.pausa = False

def ejecucion(maquina1, maquina2):
    #EJECUCION----------------------------------------------
    # Crear una bandera de evento
    frame_event_1 = threading.Event()
    frame_event_2 = threading.Event()

    # Simulación de la comunicación entre sender y receiver
    sender_thread = threading.Thread(target=maquina1.sender, args=(frame_event_1,maquina2))
    receiver_thread = threading.Thread(target=maquina2.receiver, args=(frame_event_1,maquina1))

    #sender_thread_2 = threading.Thread(target=maquina2.sender, args=(frame_event_2,maquina1))
    #receiver_thread_2 = threading.Thread(target=maquina1.receiver, args=(frame_event_2,maquina2))

    # Iniciar el sender y esperar un poco antes de iniciar el receiver
    sender_thread.start()
    time.sleep(5)  # Esperar para asegurar que el sender haya enviado al menos un frame
    receiver_thread.start()

    # Iniciar el sender y esperar un poco antes de iniciar el receiver
    #sender_thread_2.start()
    #time.sleep(5)  # Esperar para asegurar que el sender haya enviado al menos un frame
    #receiver_thread_2.start()

