
import time

class Frame():

    def __init__(self,pSequenceNumber,pPacket,pKind):
        self.sequenceNumber = pSequenceNumber
        self.packet = pPacket
        self.kind = pKind
        self.timer = True

    def startTimer(self,segundos):
            while(segundos>0):
                time.sleep(1)
                segundos-=1
            #frame "vencido"
            self.timer = False
    
    def __str__(self):
        return f"Frame #{self.sequenceNumber} - Kind: {self.kind}, Packet: {self.packet}"
    
    