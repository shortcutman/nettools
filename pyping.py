import itertools
import select
import socket
import struct

def internetChecksum(data):
    sum = 0
    for word in itertools.batched(data, 2):
        sum += (word[0] << 8) + word[1]

    print(hex(sum))
    carry = sum >> 16
    sum = (sum & 0xFFFF) + carry
    return (~sum & 0xffff).to_bytes(2, 'big')

def ping(addr):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname('icmp'))
        host = socket.gethostbyname(addr) # translate to ip address

        # from RFC 792
        # type (8 for echo request), code (always 0 under echo request), checksum (0 to start), identifier, sequence number
        icmp_header = struct.pack('bbHHh', 8, 0, 0, 0, 0)
        data = b'A' * 32
        print(icmp_header)
        checksum = internetChecksum(icmp_header + data)
        icmp_header = struct.pack('bbBBHh', 8, 0, checksum[0], checksum[1], 0, 0)
        packet = icmp_header + data
        sock.sendto(packet, (host, 1))

        selections = select.select([sock], [], [], 2)
        recvData, recvAddr = sock.recvfrom(1024)
        print(recvAddr)
        
    except socket.error as e:
        raise

ping("www.google.com")