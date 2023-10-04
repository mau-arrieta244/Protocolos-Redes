import threading
import classes.frame as frame
import time
import random

# Clase para definir eventos

class Event:
    FRAME_ARRIVAL = "frame_arrival"
    CKSUM_ERR = "cksum_err"
    TIMEOUT = "timeout"

class Maquina:
    def __init__(self, pName, pId, pTasaErrores):
        self.name = pName
        self.id = pId
        self.capaRed = self.CapaRed()
        self.capaFisica = self.CapaFisica(pTasaErrores)
        self.paquetesRed_Enlace = []
        self.condicionToLinkLayer = True
        self.capaFisicaRecibidos = []
        self.pausa = False

global evento

# Clase para representar un paquete de datos
class Packet:
    def __init__(self, data):
        self.data = data


# Clase que representa una máquina que implementa el protocolo de retransmisión con confirmación positiva
class PAR(Maquina):
    def __init__(self, name, id, tasaErrores):
        super().__init__(name, id, tasaErrores)
        self.pausa = False

    # Clase para la capa de red
    class CapaRed:
        def __init__(self):
            self.paquetes = []  # Lista de paquetes generados
            self.framesRecibidos = []  # Lista de marcos recibidos
            self.generate_packets = True  # Bandera para generar paquetes
            self.pause = False  # Variable para pausar la capa de red

        # Genera un paquete de datos desde la capa de red
        def from_network_layer(self):
            data = f"Data from network layer at time {time.time()}"
            packet = Packet(data)
            return packet

        

    # Clase para la capa de enlace
    class CapaFisica:
        def __init__(self, tasaError):
            self.framesEnviar = []
            self.framesRecibidos = []
            self.framesEnviados = []
            self.frameErrores = []
            self.pausa = False
            self.tasaError = tasaError

        def CrearCapaFisica(self, tasaError):
            return self.CapaFisica(tasaError)

        def simular_error(self, tasa_error_porcentaje):
            # Generar un número aleatorio entre 0 y 99 para representar el porcentaje de error
            numero_aleatorio = random.randint(0, 99)

            # Si el número aleatorio está dentro de la tasa de error, se genera un error
            if numero_aleatorio < tasa_error_porcentaje:
                return True
            else:
                return False
        
        # Envía un marco a la capa de enlace
        def to_physical_layer(self, frame, destino):

            if (frame.kind == 'ACK'):
                print(f"Sending ACK confirmation {frame.sequenceNumber}")
                destino.capaFisica.framesRecibidos.append(frame)
                self.framesEnviados.append(frame)
                return frame.sequenceNumber
                
            else:
                print(f"----------------------------------------------------Sending frame {frame.sequenceNumber}: {frame.packet.data}----------------------------------------------------")
                destino.capaFisica.framesRecibidos.append(frame)
                self.framesEnviados.append(frame)

        # Obtiene el último marco recibido desde la capa física
        def from_physical_layer(self):
            frameRecibido = self.framesRecibidos[-1]
            if (self.simular_error(self.tasaError)):
                print(f"Error de transmision en Frame: {frameRecibido.sequenceNumber}")
                self.frameErrores.append(self.framesRecibidos.pop(-1))
                return None

            return frameRecibido

        def return_last_frame(self):
            if self.framesRecibidos:
                return self.framesRecibidos[-1]
            return None

        # Entrega información desde un paquete a la capa de red
        def to_network_layer(self, packet):
            print("Received data in the network layer:", packet.data)

    # Método del emisor
    def sender(self, frame_arrived, ACK_arrived, destination):
        sequenceNumber = 1  # Inicializa el número de secuencia
        frameEnviado = None

        while True:
            if not self.pausa:
                time.sleep(2)

                if (frameEnviado == None):
                    packet = self.capaRed.from_network_layer()  # Genera un paquete
                    newFrame = frame.Frame(sequenceNumber, packet, 'DATA')  # Crea un marco con el paquete
                    frameEnviado = newFrame
                    self.capaFisica.to_physical_layer(newFrame,destination)
                    ultimo_frame = destination.capaFisica.return_last_frame()
                    frame_arrived.set()
                else:
                    self.capaFisica.to_physical_layer(frameEnviado, destination)  # Enviar frame
                    frame_arrived.set()

                ack_received = ACK_arrived.wait(timeout=5)
                
                if ack_received:
                    frameEnviado = None
                    ackedSequenceNumber = ultimo_frame.sequenceNumber
                    if ackedSequenceNumber == sequenceNumber:
                        print("Número de acknowledgement esperado: ",sequenceNumber)
                        sequenceNumber += 1
                else:
                    print("Se agota el tiempo de espera, vuelve a enviar el frame")
                ACK_arrived.clear()  # Limpia el evento para futuras esperas

    # Método del receptor
    def receiver(self, frame_arrived, ACK_arrived, origen):
        expected_sequence_number = 1
        
        while True:
            if (not self.pausa):
                frame_arrived.wait()
                frame_arrived.clear()
                time.sleep(1)
                
                received_frame = self.capaFisica.from_physical_layer()

                if received_frame is None:
                    print("No enviar ACK")
                else:
                    if received_frame.sequenceNumber == expected_sequence_number:
                        self.capaFisica.to_network_layer(received_frame.packet)
                        expected_sequence_number += 1
                        print("Número de secuencia esperado en el receiver: ",received_frame.sequenceNumber)

                        # Enviar acknowledgment (dummy frame) para despertar al emisor
                        dummy_packet = Packet("ACK")
                        dummy_frame = frame.Frame(received_frame.sequenceNumber, dummy_packet, 'ACK')
                        self.capaFisica.to_physical_layer(dummy_frame, origen)

                        # Marcar el evento para despertar al emisor
                    ACK_arrived.set()

    def pauseMachine(self):
        self.pausa = True

    def resumeMachine(self):
        self.pausa = False

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

    # Método para pausar la máquina
    def pause_machine(self):
        self.pause = True

    # Método para reanudar la máquina
    def resume_machine(self):
        self.pause = False

    def setTasaErrores(self, tasa):
        if tasa.isdigit() and 0 <= int(tasa) <= 100:
            self.capaFisica.tasaError =  int(tasa)
            print(f'Tasa de Errores Actualizada: {int(tasa)}')
        else:
            print(f'Error al cambiar la tasa de error')

# Función para ejecutar la simulación
def startMachine(machine1, machine2):
    ACK_arrived = threading.Event()  
    frame_arrived = threading.Event()

    sender_thread = threading.Thread(target=machine1.sender, args=(frame_arrived, ACK_arrived, machine2))
    receiver_thread = threading.Thread(target=machine2.receiver, args=(frame_arrived, ACK_arrived, machine1))

    sender_thread.start()  # Iniciar el hilo del emisor
    time.sleep(5)  # Esperar para asegurar que el emisor haya enviado al menos un marco
    receiver_thread.start()  # Iniciar el hilo del receptor

"""
# Ejemplo de uso
if __name__ == "__main__":
    machine_a = PAR("Machine A", 1, 20)
    machine_b = PAR("Machine B", 2, 20)

    execution(machine_a, machine_b)  # Iniciar la simulación"""