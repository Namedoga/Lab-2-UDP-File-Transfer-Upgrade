# This program was modified by othniel / n01105862
import socket
import argparse
import struct  # IMPROVEMENT: unpack sequence numbers + create ACKs

CHUNK_SIZE = 4096
HEADER_SIZE = 4  # IMPROVEMENT: 4-byte sequence number header

def run_server(port, output_file):
    # 1. Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 2. Bind the socket to the port
    server_address = ('', port)
    print(f"[*] Server listening on port {port}")
    print(f"[*] Server will save each received file as 'received_<ip>_<port>.jpg' based on sender.")
    sock.bind(server_address)

    # 3. Keep listening for new transfers
    try:
        while True:
            f = None
            sender_filename = None
            expected_seq = 0  # IMPROVEMENT: track the next expected sequence number
            recv_buffer = {}


            while True:
                packet, addr = sock.recvfrom(CHUNK_SIZE + HEADER_SIZE)

                # IMPROVEMENT: If packet is only 4 bytes, treat it as EOF (seq header only)
                if len(packet) <= HEADER_SIZE:
                    print(f"[*] End of file signal received from {addr}. Closing.")
                    break

                # IMPROVEMENT: Extract seq number and payload
                seq_num = struct.unpack("!I", packet[:HEADER_SIZE])[0]
                data = packet[HEADER_SIZE:]

                if f is None:
                    print("==== Start of reception ====")
                    ip, sender_port = addr
                    sender_filename = f"received_{ip.replace('.', '_')}_{sender_port}.jpg"
                    f = open(sender_filename, 'wb')
                    print(f"[*] First packet received from {addr}. File opened for writing as '{sender_filename}'.")

            if seq_num == expected_seq:
                 f.write(data)
                 expected_seq += 1
                 
                 while expected_seq in recv_buffer:
                      f.write(recv_buffer.pop(expected_seq))
                      expected_seq += 1
            elif seq_num > expected_seq:
                      recv_buffer[seq_num] = data
            ack_num = expected_seq - 1
            ack_packet = struct.pack("!I", ack_num)
            sock.sendto(ack_packet, addr)

            if f:
                f.close()
            print("==== End of reception ====")

    except KeyboardInterrupt:
        print("\n[!] Server stopped manually.")
    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        sock.close()
        print("[*] Server socket closed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reliable UDP File Receiver (Part 1: loss)")
    parser.add_argument("--port", type=int, default=12001, help="Port to listen on")
    parser.add_argument("--output", type=str, default="received_file.jpg", help="File path to save data (not used for per-sender naming)")
    args = parser.parse_args()

    try:
        run_server(args.port, args.output)
    except KeyboardInterrupt:
        print("\n[!] Server stopped manually.")
    except Exception as e:
        print(f"[!] Error: {e}")
