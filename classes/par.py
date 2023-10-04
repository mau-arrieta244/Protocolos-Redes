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

        # Envía un marco a la capa de enlace
        def to_physical_layer(self, frame, destino):

            if (frame.kind == 'ACK'):
                print(f"Sending ACK confirmation {frame.sequenceNumber}")
                return frame.sequenceNumber
            else:
                print(f"----------------------------------------------------Sending frame {frame.sequenceNumber}: {frame.packet.data}----------------------------------------------------")
                destino.capaFisica.framesRecibidos.append(frame)

    # Clase para la capa de enlace
    class CapaFisica:
        def __init__(self, tasaError):
            self.framesEnviar = []
            self.framesRecibidos = []
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

        # Obtiene el último marco recibido desde la capa física
        def from_physical_layer(self):
            frameRecibido = self.framesRecibidos[-1]
            if (self.simular_error(self.tasaError)):
                print(f"Error de transmision en Frame: {frameRecibido.sequenceNumber}")
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
    def sender(self, event, destination):
        sequenceNumber = 1  # Inicializa el número de secuencia
        while True:
            if not self.pausa:
                time.sleep(2)
                packet = self.capaRed.from_network_layer()  # Genera un paquete
                newFrame = frame.Frame(sequenceNumber, packet, 'DATA')  # Crea un marco con el paquete
                self.capaRed.to_physical_layer(newFrame,destination)
                ultimo_frame = destination.capaFisica.return_last_frame()
                ack_received = event.wait(timeout=5)
                if ack_received:
                    ackedSequenceNumber = ultimo_frame.sequenceNumber
                    if ackedSequenceNumber == sequenceNumber:
                        print("Número de acknowledgement esperado: ",sequenceNumber)
                        sequenceNumber += 1
                else:
                    print("Se agota el tiempo de espera, vuelve a enviar el frame")
                event.clear()  # Limpia el evento para futuras esperas

    # Método del receptor
    def receiver(self, event, origen):
        expected_sequence_number = 1
        while True:
            if (not self.pausa):
                if (self.capaFisica.framesRecibidos):
                    time.sleep(1)
                    received_frame = self.capaFisica.from_physical_layer()
                    self.capaFisica.framesRecibidos = []

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
                            self.capaRed.to_physical_layer(dummy_frame, origen)

                            # Marcar el evento para despertar al emisor
                        event.set()


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
    frame_event = threading.Event()  # Crear un evento

    sender_thread = threading.Thread(target=machine1.sender, args=(frame_event, machine2))
    receiver_thread = threading.Thread(target=machine2.receiver, args=(frame_event, machine1))

    sender_thread.start()  # Iniciar el hilo del emisor
    time.sleep(5)  # Esperar para asegurar que el emisor haya enviado al menos un marco
    receiver_thread.start()  # Iniciar el hilo del receptor

"""
# Ejemplo de uso
if __name__ == "__main__":
    machine_a = PAR("Machine A", 1, 20)
    machine_b = PAR("Machine B", 2, 20)

    execution(machine_a, machine_b)  # Iniciar la simulación"""