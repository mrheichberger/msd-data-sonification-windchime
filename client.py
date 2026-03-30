# MIDI parsing and network support functions for wind chime controller
# Handles communication between Python GUI and ESP32 chime controller

import socket
import mido
import struct
import enum


class Mood(enum.Enum):
    """
    Mood enumeration for weather-responsive chime behavior
    Each mood corresponds to a specific configuration sent to the ESP32
    Values represent the mood ID sent to the hardware controller
    """
    MELANCHOLY =       6  # Cool, overcast weather
    JOYOUS =           0  # Bright, pleasant conditions  
    COZY =             1  # Comfortable indoor weather
    DISTRESSFUL_COLD = 2  # Harsh winter conditions
    DISTRESSFUL_HOT =  3  # Extreme heat conditions
    CALMING_COOL =     4  # Gentle cool weather
    CALMING_WARM =     5  # Gentle warm weather



class NotePacket():
    """
    Represents a set of MIDI notes to be played simultaneously on the wind chimes
    Includes timing information for when the notes should be triggered
    """
    def __init__(self):
        self.timestamp = 0.0  # Time delay before playing this chord
        self.notes = []        # List of MIDI note numbers to play together
        
    def __add_note(self, note:int, velocity:int):
        """Add a note to the packet if it's valid and has velocity > 0"""
        if note > 127 or note < 0:
            raise ValueError("Note must be between 0 and 127 (inclusive)")
        if velocity > 0 and not note in self.notes:
            self.notes.append(note)
        # Note: velocity is ignored since solenoids are binary (on/off)
        
    def parse_event(self, event):
        """
        Parse a MIDI event and add notes to this packet
        Returns "new packet" when a new packet should be started
        """
        if event.type == 'note_on':
            note = event.note
            # Transpose notes to fit the chime range (C4 to C6, notes 60-77)
            while note < 60:
                note += 12  # Octave up
            while note > 77:
                note -= 12  # Octave down
                
            if event.time == 0.0:
                # Note starts immediately
                self.__add_note(note, event.velocity)
                return ""
            else:
                if self.timestamp == 0.0:
                    # First note with timing
                    self.__add_note(note, event.velocity) 
                    self.timestamp = event.time
                    return ""
                else:
                    # New timing, start new packet
                    return "new packet"
                    
        if event.type == 'note_off':
            # Add note-off timing to current timestamp
            self.timestamp += event.time
        return "not note"
    def to_bytes(self):
        """
        Convert packet to binary format for transmission to ESP32
        Maps to C struct: {uint8_t notes_length, uint16_t timestamp_ms, uint8_t notes[]}
        """
        result = bytearray()
        notes_bytes = bytes(self.notes)
        result.append(len(notes_bytes))  # Number of notes
        result.extend(struct.pack(">H", int(self.timestamp*1000)))  # Timestamp in milliseconds
        result.extend(notes_bytes)  # Note numbers
        return result
        
    def __repr__(self):
        return repr(self.to_bytes()) + ", timestamp: " + str(self.timestamp)

def parse_midi_file(filename:str):
    """
    Parse a MIDI file and convert it to binary packets for the ESP32
    Returns a bytearray containing all note packets in sequence
    """
    taps = mido.MidiFile(filename)
    note_packets = []
    current_packet = NotePacket()
    
    # Process all MIDI events and group simultaneous notes
    for event in taps:
        result = current_packet.parse_event(event)
        if result == "new packet":  # Start new packet when timing changes
            note_packets.append(current_packet)
            current_packet = NotePacket()
            current_packet.parse_event(event)  # Add the new note to the new packet
            
    # Convert all packets to binary format
    binary_packets = bytearray()
    for packet in note_packets:
        for byte in packet.to_bytes():
            print(int(byte))  # Debug output
        print()  # Newline for readability
        binary_packets.extend(packet.to_bytes())
    return binary_packets

def change_config(sock:socket.socket, new_config:Mood, timber:int):
    """
    Send mood and timbre configuration to the ESP32 chime controller
    Args:
        sock: TCP socket connection to ESP32
        new_config: Mood enum value for weather-responsive behavior
        timber: Physical timbre material (0=metal, 1=rubber, 2=wood)
    """
    if timber < 0 or timber > 2:
        raise ValueError("Timber must be 0, 1, or 2")
    print("Sending config " + new_config.name)
    sock.send(b'W')  # 'W' command for weather/mood configuration
    print(new_config.value)
    sock.send(new_config.value.to_bytes(1))  # Send mood ID
    sock.send(timber.to_bytes(1))  # Send timbre material


def send_song(sock:socket.socket, song_filename:str):
    """
    Send a MIDI file to the ESP32 for playback on wind chimes
    Args:
        sock: TCP socket connection to ESP32
        song_filename: Path to MIDI file to play
    """
    print("Sending song " + song_filename)
    song = parse_midi_file(song_filename)  # Parse MIDI to binary packets
    
    sock.send(b'S')  # 'S' command for song playback
    sock.send(song)  # Send all note packets
    # TODO: Consider buffering for large files to avoid overwhelming ESP32

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    #     data = Mood.JOYOUS.value
    #     print(data.hex(" "))
        print("Connecting...")
        sock.connect(("pico22625.student.rit.edu",5000))
        print("Connected! sending song...")
        send_song(sock, "midi/lava_chicken.mid")
        print("Song sent")
    #     sock.send(b'C')
    #     sock.send(data)
        # print("Waiting for response...")
    #     print(sock.recv(1024))
