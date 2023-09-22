
import time
import threading

import random
import time

import random
import time

class Machine:
    def __init__(self, name):
        self.name = name
        self.buffer = []  # Store packets to be sent
        self.window_size = 4
        self.expected_seq_num = 0

    def send_packet(self, destination):
        if len(self.buffer) < self.window_size:
            packet = f"Packet {self.expected_seq_num}"
            print(f"{self.name} sent: {packet}")
            destination.receive_packet(packet)
            self.buffer.append(packet)
            self.expected_seq_num += 1
        else:
            print(f"{self.name}: Window is full, waiting for acknowledgments...")

    def receive_ack(self, ack_num):
        print(f"{self.name} received ACK: {ack_num}")
        if ack_num >= self.expected_seq_num:
            self.buffer = [packet for packet in self.buffer if int(packet.split()[-1]) > ack_num]
            self.expected_seq_num = ack_num + 1

    def receive_packet(self, packet):
        if random.random() < 0.8:  # Simulate packet loss
            print(f"{self.name} received: {packet}")
            time.sleep(1)  # Simulate processing delay
            ack_num = int(packet.split()[-1])
            if ack_num == self.expected_seq_num:
                self.expected_seq_num += 1
                self.send_ack(ack_num)
            else:
                self.send_ack(ack_num)  # Send duplicate ACK for already received packet
        else:
            print(f"{self.name} lost: {packet}")
            self.send_ack(self.expected_seq_num - 1)  # Retransmit last ACK

    def send_ack(self, ack_num):
        print(f"{self.name} sent ACK: {ack_num}")
        self.sender.receive_ack(ack_num)

# Create two machines
machine_A = Machine("Machine A")
machine_B = Machine("Machine B")

# Set each machine's sender reference
machine_A.sender = machine_B
machine_B.sender = machine_A

# Simulate communication
for i in range(10):
    machine_A.send_packet(machine_B)
    time.sleep(2)  # Simulate time passing
