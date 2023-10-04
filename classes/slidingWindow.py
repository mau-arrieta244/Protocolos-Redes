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
        self.tasaErrores = pTasaErrores
        self.capaRed = self.CapaRed(pName)
        self.capaFisica = self.CapaFisica(pName,pTasaErrores)
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
        
        

    
    class CapaFisica:
        def __init__(self, pName,pTasaErrores):
            self.framesRecibidos = []
            self.framesEnviados = []
            self.frameErrores = []
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
                print(self.nombre + f" cksum_err!! Error de transmision en Frame: {frameRecibido.sequenceNumber}")
                self.frameErrores.append(self.framesRecibidos.pop(-1))
                return None
            return frameRecibido
        
        def to_physical_layer(self, frame, destino):
            if (frame.kind == 'ACK'):
                print(self.nombre + f": ACK confirmation {frame.sequenceNumber}"  +'\n' )
            else:
                print(self.nombre + f": Sending frame {frame.sequenceNumber}: {frame.packet.data}")

            destino.capaFisica.framesRecibidos.append(frame)
            self.framesEnviados.append(frame)
            
            time.sleep(1)

        def print_received_frames(self):
            print("Frames recibidos en la capa de enlace:")
            for frame in self.framesRecibidos:
                print(f"Sequence Number: {frame.sequenceNumber}, Kind: {frame.kind}, Data: {frame.packet.data}")

        # Entrega información desde una trama entrante a la capa de red.
        def to_network_layer(self, packet):
            print(self.nombre + ": Received data in the network layer:", packet.data)

    def sender(self, frame_arrived, ACK_arrived, destino):
        contFrames = 0
        frame = None
        while True:
            if not self.pausa:
                time.sleep(2)

                if (frame == None):
                    packet = self.capaRed.from_network_layer()  # generar paquete
                    frame = Frame(contFrames, packet, 'DATA')  # genera Frame con info de paquete
                    self.capaFisica.to_physical_layer(frame, destino)  # Enviar frame
                    frame_arrived.set()
                
                else:
                    self.capaFisica.to_physical_layer(frame, destino)  # Enviar frame
                    frame_arrived.set()

                # Esperar la confirmación (ACK) del receptor
                ack_received = ACK_arrived.wait(timeout=10)  # espera 5 segundos por el ACK
                ACK_arrived.clear()  # Limpiar el evento para futuras esperas
                if ack_received:
                    frame = None
                    print(self.name + " si recibe ACK " + str(contFrames))
                    contFrames = 1 - contFrames #La venta es de 1, los frames van de 0 a 1
                    
                else:
                    print(self.name +" ack_timeout!!! Se agota el tiempo de espera, vuelve a enviar el frame")

    def mostrarRecibidos(self):
            print ("---------------------------------------")
            print(self.name+": ")
            print("Frames recibidos:")
            for frame in self.capaFisica.framesRecibidos:
                if (frame.kind == 'DATA'):
                    print(f"Sequence Number: {frame.sequenceNumber}, Kind: {frame.kind}, Data: {frame.packet.data}")

            print("\n ACK recibidos:")
            for frame in self.capaFisica.framesRecibidos:
                if (frame.kind == 'ACK'):
                    print(f"Sequence Number: {frame.sequenceNumber}, Kind: {frame.kind}, Data: {frame.packet.data}")

            print("\n Recibidos con error:")
            for frame in self.capaFisica.frameErrores:
                print(f"Sequence Number: {frame.sequenceNumber}, Kind: {frame.kind}, Data: {frame.packet.data}")

    def mostrarEnviados(self):
        print ("---------------------------------------")
        print(self.name+": ")
        print("Frames Enviados:")
        for frame in self.capaFisica.framesEnviados:
            if (frame.kind == 'DATA'):
                print(f"Sequence Number: {frame.sequenceNumber}, Kind: {frame.kind}, Data: {frame.packet.data}")

        print("\n ACK Enviados:")
        for frame in self.capaFisica.framesEnviados:
            if (frame.kind == 'ACK'):
                print(f"Sequence Number: {frame.sequenceNumber}, Kind: {frame.kind}, Data: {frame.packet.data}")

    def receiver(self, frame_arrived, ACK_arrived, origen):
        contEsperado = 0
        while True:
            if not self.pausa: 
                frame_arrived.wait()
                frame_arrived.clear()
                time.sleep(1)
                received_frame = self.capaFisica.from_physical_layer()

                if received_frame is None:
                    print("No enviar ACK")
                    
                else:
                    if (received_frame.sequenceNumber == contEsperado):
                        self.capaFisica.to_network_layer(received_frame.packet)

                        # Enviar acknowledgment (dummy frame) para despertar al emisor
                        dummy_packet = Packet("ACK")
                        dummy_frame = Frame(received_frame.sequenceNumber, dummy_packet, 'ACK')
                        self.capaFisica.to_physical_layer(dummy_frame, origen)

                        contEsperado = 1 - received_frame.sequenceNumber
                        # Marcar el evento para despertar al emisor
                        ACK_arrived.set()

                   # else:
                       # print(self.name + " # de Secuencia no coincide - No enviar ACK")


    def pauseMachine(self):
        self.pausa = True

    def resumeMachine(self):
        self.pausa = False

    def setTasaErrores(self, tasa):
        if tasa.isdigit() and 0 <= int(tasa) <= 100:
            self.tasaErrores = int(tasa)
            self.capaFisica.tasaErrores =  int(tasa)
            print(f'Tasa de Errores Actualizada: {int(tasa)}')
        else:
            print(f'Error al cambiar la tasa de error')
        

def startMachine(maquina1, maquina2):
    #EJECUCION----------------------------------------------
    # Crear una bandera de evento
    frame_arrived_1 = threading.Event()
    frame_arrived_2 = threading.Event()

    ACK_arrived_1 = threading.Event()
    ACK_arrived_2 = threading.Event()

    # Simulación de la comunicación entre sender y receiver
    sender_thread = threading.Thread(target=maquina1.sender, args=(frame_arrived_1, ACK_arrived_1, maquina2))
    receiver_thread = threading.Thread(target=maquina2.receiver, args=(frame_arrived_1, ACK_arrived_1, maquina1))

    sender_thread_2 = threading.Thread(target=maquina2.sender, args=(frame_arrived_2, ACK_arrived_2, maquina1))
    receiver_thread_2 = threading.Thread(target=maquina1.receiver, args=(frame_arrived_2, ACK_arrived_2, maquina2))

    # Iniciar el sender y esperar un poco antes de iniciar el receiver
    sender_thread.start()
    time.sleep(5)  # Esperar para asegurar que el sender haya enviado al menos un frame
    receiver_thread.start()

    # Iniciar el sender y esperar un poco antes de iniciar el receiver
    sender_thread_2.start()
    time.sleep(5)  # Esperar para asegurar que el sender haya enviado al menos un frame
    receiver_thread_2.start()

