
// use std::os::unix::net::SocketAddr;
use std::net::{SocketAddr, ToSocketAddrs};
use std::mem::{MaybeUninit};
use socket2::{Socket, Domain, Type, Protocol, SockAddr};

fn main() {
    println!("Hello, world!");
    ping(&String::from("www.google.com"));
}

struct ICMPHeader {
    icmp_type: u8,
    code: u8,
    checksum: u16,
    rest_of_header: u32
}

impl ICMPHeader {
    fn as_bytes(&self) -> Vec<u8> {
        let mut bytes = Vec::new();
        bytes.push(self.icmp_type);
        bytes.push(self.code);
        bytes.extend_from_slice(&self.checksum.to_be_bytes());
        bytes
    }
}

fn calculate_internet_checksum(bytes: &Vec<u8>) -> u16 {
    let mut sum: u32 = 0;

    for bit in bytes.chunks(2) {
        println!("2 bytes: {:?}", bit);

        sum += ((bit[0] as u32) << 8) + (bit[1] as u32);
    }

    let carry = sum >> 16;
    sum = (sum & 0xffff) + carry;
    (!sum & 0xffff) as u16
}

fn ping(addr: &String) {
    let mut header = ICMPHeader {
        icmp_type: 8,
        code: 0,
        checksum: 0,
        rest_of_header: 0
    };

    let mut bytes_before_checksum: Vec<u8> = Vec::new();
    bytes_before_checksum.extend(&header.as_bytes());
    bytes_before_checksum.extend(vec![1, 1, 1, 1, 1, 1, 1, 1]);
    println!("ICMP Packet: {:?}", bytes_before_checksum);

    let cs = calculate_internet_checksum(&bytes_before_checksum);
    println!("Checksum: {:?}", cs.to_be_bytes());
    header.checksum = cs;

    let mut fullbytes: Vec<u8> = Vec::new();
    fullbytes.extend(&header.as_bytes());
    fullbytes.extend(vec![1, 1, 1, 1, 1, 1, 1, 1]);

    let socket = Socket::new(Domain::IPV4, Type::RAW, Some(Protocol::ICMPV4)).unwrap();
    let address = "www.google.com:0".to_socket_addrs().unwrap().next().unwrap();
    let connectResult = socket.connect(&SockAddr::from(address)).unwrap();
    let sendResult = socket.send(&fullbytes);

    let mut buf = Vec::with_capacity(4096);
    let received = socket.recv(buf.spare_capacity_mut());
    unsafe {
        buf.set_len(received.unwrap());
    }

    println!("{:02x?}", buf);

}