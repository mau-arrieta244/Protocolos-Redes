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

        self.capaRed = self.CapaRed(pName)
        self.capaFisica = self.CapaFisica(pName)

        self.pausa = False

    #CAPA DE RED 
    class CapaRed:
        def __init__(self,pName):
            self.paquetes = []
            self.framesRecibidos = []
            self.condicionGenerarPaquetes = True
            self.pausa = False
            self.name = pName

        #Genera Paquetes
        def from_network_layer(self):
            data = f"Data from network layer at time {time.time()} from: "+self.name
            packet = Packet(data)
            return packet
        
        
            
            time.sleep(1)

        
    class CapaFisica:
        def __init__(self,pName):
            self.name = pName
            self.framesEnviados = []
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
        
        # Entrega información desde una trama entrante a la capa de red.
        def to_network_layer(self, packet):
            print(self.name + ": Received data in the network layer: ", packet.data)

        def to_physical_layer(self, frame, destino):
            if (frame.kind == 'ACK'):
                print(self.name+ f": Sending ACK confirmation {frame.sequenceNumber}")
                destino.capaFisica.framesRecibidos.append(frame)
                self.framesEnviados.append(frame)
            else:
                print(self.name+ f": Sending frame {frame.sequenceNumber} {frame.packet.data}")
                destino.capaFisica.framesRecibidos.append(frame)
                self.framesEnviados.append(frame)

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
            
    def sender(self,frame_arrived, ACK_arrived, destino):
        contFrames = 1

        while True:
            if (not self.pausa):
                time.sleep(2)
                print(self.name + ": Generando Paquete en Capa de Red")
                packet = self.capaRed.from_network_layer() #generar paquete
                print(self.name + ": Generando DATA Frame")
                frame = Frame(contFrames,packet,'DATA') #genera Frame con info de paquete
                contFrames += 1
                
                self.capaFisica.to_physical_layer(frame,destino) # Enviar frame
                frame_arrived.set()
                print(self.name + ": Esperando confirmacion ACK")
                # Esperar la confirmación (ACK) del receptor
                ACK_arrived.wait()
                print(self.name + ": Recibe confirmacion ACK " + str(contFrames-1)+"\n")
                ACK_arrived.clear()  # Limpiar el evento para futuras esperas

    

    def receiver(self, frame_arrived, ACK_arrived, origen):
        while True:
            if (not self.pausa):
                frame_arrived.wait()
                frame_arrived.clear()
                time.sleep(2)
                received_frame = self.capaFisica.from_physical_layer()

                self.capaFisica.to_network_layer(received_frame.packet)
                
                # Enviar acknowledgment (dummy frame) para despertar al emisor
                dummy_packet = Packet("ACK")
                dummy_frame = Frame(received_frame.sequenceNumber, dummy_packet,'ACK')
                self.capaFisica.to_physical_layer(dummy_frame,origen)
                    
                # Marcar el evento para despertar al emisor
                ACK_arrived.set()

    def pauseMachine(self):
        self.pausa = True

    def resumeMachine(self):
        self.pausa = False

def startMachine(maquina1, maquina2):
    #EJECUCION----------------------------------------------
    # Crear una bandera de evento
    frame_arrived = threading.Event()
    ACK_arrived = threading.Event()

    # Simulación de la comunicación entre sender y receiver
    sender_thread = threading.Thread(target=maquina1.sender, args=(frame_arrived,ACK_arrived,maquina2))
    receiver_thread = threading.Thread(target=maquina2.receiver, args=(frame_arrived,ACK_arrived,maquina1))

    # Iniciar el sender y esperar un poco antes de iniciar el receiver
    sender_thread.start()
    time.sleep(5)  # Esperar para asegurar que el sender haya enviado al menos un frame
    receiver_thread.start()

