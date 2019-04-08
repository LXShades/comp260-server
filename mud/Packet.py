import json
import base64

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad
from Crypto.Random import get_random_bytes


"""Packet encryption and validation manager"""
class Packet:
    """Packages the packet and returns its data as bytes

    Attributes
        data: the packet data as bytes
        encryption_key: the key to encrypt the data with
    """
    @staticmethod
    def pack(data, encryption_key, session_id, packet_id):
        try:
            iv = get_random_bytes(AES.block_size)
            cipher = AES.new(encryption_key, AES.MODE_CBC, iv)
            packet = {
                "iv": base64.b64encode(iv).decode("utf-8"),
                "data": base64.b64encode(cipher.encrypt(pad(data, AES.block_size))).decode("utf-8"),
                "packet": packet_id,
                "session": session_id
            }

            return json.dumps(packet).encode()
        except err as Exception:
            # Error encrypting packet
            return None

    """Unpacks a packet and returns its data as bytes
    
    Attributes
        data: The unencrypted packet data
        decryption_key: The key to decrypt the data with"""
    @staticmethod
    def unpack(data, decryption_key, session_id, packet_id):
        try:
            # Reconstruct the packet
            packet = json.loads(data.decode("utf-8"))

            # Verify the message
            if packet["packet"] != packet_id or packet["session"] != session_id:
                return None

            # Decrypt the message
            iv = base64.b64decode(packet["iv"])
            data = base64.b64decode(packet["data"])
            cipher = AES.new(decryption_key, AES.MODE_CBC, iv)
            data = unpad(cipher.decrypt(data), AES.block_size)

            return data
        except err as Exception:
            # Error unpacking packet -- return nothing
            return None
