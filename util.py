import struct
import zlib

# Constants
MAX_NUM_CLIENTS = 10
CHUNK_SIZE = 512

def make_message(msg_type, content):
    """Format a message string with type and length."""
    length = len(content)
    return f"{msg_type} {length} {content}"

def make_packet(packet_type, seqno, data):
    """Format a packet with a pseudo-header and CRC32 checksum."""
    header = f"{packet_type} {seqno} "
    checksum = zlib.crc32((header + data).encode())
    return f"{header}{data} {checksum}"
