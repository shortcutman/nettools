
import itertools
import random
import socket
import struct
import sys

def internetChecksum(data):
    sum = 0
    for word in itertools.batched(data, 2):
        sum += (word[0] << 8) + word[1]

    carry = sum >> 16
    sum = (sum & 0xFFFF) + carry
    return (~sum & 0xffff).to_bytes(2, 'big')

class TCPConnection:
    source_address = 0
    destination_address = 0

    source_port = 0
    destination_port = 0
    sequence_number = 1745176383

    def __init__(self, destination, dest_port):
        self.destination_address = destination
        self.destination_port = dest_port
        self.source_port = random.randint(50000, 60000)
        self.source_address = 0x0100007f

    def flags(self, cwr=False, ece=False, urg=False, ack=False, psh=False, rst=False, syn=False, fin=False):
        flag = 0
        if cwr:
            flag |= (1 << 7)
        if ece:
            flag |= (1 << 6)
        if urg:
            flag |= (1 << 5)
        if ack:
            flag |= (1 << 4)
        if psh:
            flag |= (1 << 3)
        if rst:
            flag |= (1 << 2)
        if syn:
            flag |= (1 << 1)
        if fin:
            flag |= (1 << 0)
        return flag

    def packet(self, flags, payload):
        data_offset = (20 // 4) << 4
        window = 1024

        tcp_header_checksum = struct.pack('!HHIIBBHHH',
                             self.source_port, # 2 bytes
                             self.destination_port, # 2 bytes
                             self.sequence_number, # 4 bytes
                             0, # ack number, 4 bytes
                             data_offset, # data offset + reserved, 1 byte
                             flags, # flags, 1 byte
                             window, # window, 2 bytes
                             0, # checksum, 2 bytes
                             0) # urgent pointer, 2 bytes

        ip_pseudo_header = struct.pack('!IIBBH',
                                       self.source_address,
                                       self.destination_address,
                                       0,
                                       6,
                                       len(payload) + len(tcp_header_checksum))
        
        checksum = internetChecksum(ip_pseudo_header + tcp_header_checksum)

        tcp_header = struct.pack('!HHIIBBHBBH',
                            self.source_port, # 2 bytes
                            self.destination_port, # 2 bytes
                            self.sequence_number, # 4 bytes
                            0, # ack number, 4 bytes
                            data_offset, # data offset + reserved, 1 byte
                            flags, # flags, 1 byte
                            window, # window, 2 bytes
                            checksum[0], # checksum, 2 bytes, byte 0
                            checksum[1], # checksum, 2 bytes, byte 1
                            0) # urgent pointer, 2 bytes
        
        return tcp_header + payload #+ tcp_options

connect = TCPConnection(0x0100007f, 7777)
cFlags = connect.flags(syn=True)
pkt = connect.packet(cFlags, b'')

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname('tcp'))
    host = socket.gethostbyname('localhost')

    sock.sendto(pkt, (host, 0))

    # nothing will be received as the OS gobbles up the response
    # recvData, recvAddr = sock.recvfrom(1024)
    # print(f"recvAddr: {recvAddr}, recvData: {recvData}")

except:
    raise

