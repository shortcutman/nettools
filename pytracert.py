import itertools
import select
import socket
import struct
import time

def internetChecksum(data):
    sum = 0
    for word in itertools.batched(data, 2):
        sum += (word[0] << 8) + word[1]

    carry = sum >> 16
    sum = (sum & 0xFFFF) + carry
    return (~sum & 0xffff).to_bytes(2, 'big')

def tracert_ping(addr, ttl):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname('icmp'))
        sock.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
        host = socket.gethostbyname(addr) # translate to ip address

        # from RFC 792
        # type (8 for echo request), code (always 0 under echo request), checksum (0 to start), identifier, sequence number
        icmp_header = struct.pack('bbHHh', 8, 0, 0, 0, 0)
        data = b'A' * 32
        checksum = internetChecksum(icmp_header + data)
        icmp_header = struct.pack('bbBBHh', 8, 0, checksum[0], checksum[1], 0, 0)
        packet = icmp_header + data

        kq = select.kqueue()
        kevent = select.kevent(sock, select.KQ_FILTER_READ, select.KQ_EV_ADD | select.KQ_EV_CLEAR)

        start = time.time()

        for i in range(3):
            sock.sendto(packet, (host, 0))
            kreturn = kq.control([kevent], 2)
            if len(kreturn) > 0:
                break
            print(f"Hop {ttl} *")

        recvData, recvAddr = sock.recvfrom(1024)
        end = time.time()
        roundTripTime = end - start
        print(f"Elapsed: {roundTripTime}s")

        result = False

        icmpReplyPacket = recvData[20:] # we get full ip header back
        if icmpReplyPacket[0] == 0:
            print(f"Final destination {recvAddr} elapsed {roundTripTime}")
            result = True
        elif icmpReplyPacket[0] == 11 and icmpReplyPacket[1] == 0:
            print(f"Hop {ttl} addr {recvAddr} elapsed {roundTripTime}]")
        else:
            print(f"Hop {ttl} other response")

        sock.close()
        return result
        
    except socket.error as e:
        raise

ttl = 0
while True:
    found = tracert_ping("www.google.com", ttl)
    if found:
        break
    else:
        ttl += 1
