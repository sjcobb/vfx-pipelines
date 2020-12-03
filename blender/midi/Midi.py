'''
Created on 19.03.2011

@author: kaiwegner
'''
import sys
import string

import io

import sys, string, types


class EnumException(Exception):
    pass

class Enumeration:
    #
    # __init__ 
    #
    def __init__(self, enumList):
        lookup          = { } # tuple
        reverseLookup   = { } # tuple
        i               = 0   # integer
        uniqueNames     = [ ] # list
        uniqueValues    = [ ] # list
        #
        # Loop through emuerated list passed as parameter
        # X contains current index
        #
        for x in enumList:
            if type(x) == tuple:
                #
                # Tuple type, set x and i to current enumeration
                # X as a string (should be unique), I as a value
                #
                x, i = x
            if type(x) != str:
                # Error if x is not a sting
                raise EnumException("enum name is not a string: " + x)
            if type(i) != int:
                # Error is i is not an integer
                raise EnumException("enum value is not an integer: " + i)
            if x in uniqueNames:
                # Error if x string is not unique
                raise EnumException("enum name is not unique: " + x)
            if i in uniqueValues:
                raise EnumException("enum value is not unique for " + x)
            #
            # Add Name (x) to uniqueName list
            #
            uniqueNames.append(x)
            #
            # Add value (i) to uniqueValues list
            #
            uniqueValues.append(i)
            lookup[x]        = i
            reverseLookup[i] = x
            i                = i + 1
        self.lookup = lookup
        self.reverseLookup = reverseLookup
    #
    # __add__ method
    #
    def __add__(self, other):
        lst = [ ] # temp list
        #
        # Loop thorugh keys (index k)
        #
        for k in self.lookup.keys():
            lst.append((k, self.lookup[k]))
        for k in other.lookup.keys():
            lst.append((k, other.lookup[k]))
        return Enumeration(lst)
    #
    # hasattr (has attribute) method
    #
    def hasattr(self, attr):
        return attr in self.lookup
    #
    # has_value method
    def has_value(self, attr):
        return attr in self.reverseLookup
    #
    # __getattr__ method
    #
    def __getattr__(self, attr):
        if not attr in self.lookup:
            raise AttributeError
        return self.lookup[attr]
    #
    # whatis method
    #
    def whatis(self, value):
        return self.reverseLookup[value]
#
# Channel voice messages:
# Bits 7-4 indicate channel message event type (8-E), if F, then this is a system exteneded message
# Bits 3-0 indicate channel number (in data 0-15, for MIDI channels 1-16)
#
channelVoiceMessages = Enumeration([("NOTE_OFF",                0x80),
                                    ("NOTE_ON",                 0x90),
                                    ("POLYPHONIC_KEY_PRESSURE", 0xA0),  # Key Aftertouch
                                    ("CONTROLLER_CHANGE",       0xB0),
                                    ("PROGRAM_CHANGE",          0xC0),
                                    ("CHANNEL_KEY_PRESSURE",    0xD0),
                                    ("PITCH_BEND",              0xE0)]) # Pitch Wheel
#
# Channel mode messages for data for program change or controller change channel voice message
#
channelModeMessages = Enumeration([ ("ALL_SOUND_OFF",           0x78),
                                    ("RESET_ALL_CONTROLLERS",   0x79),
                                    ("LOCAL_CONTROL",           0x7A),
                                    ("ALL_NOTES_OFF",           0x7B),
                                    ("OMNI_MODE_OFF",           0x7C),
                                    ("OMNI_MODE_ON",            0x7D),
                                    ("MONO_MODE_ON",            0x7E),
                                    ("POLY_MODE_ON",            0x7F)])
#
# MIDI meta events
#
metaEvents = Enumeration([          ("SEQUENCE_NUMBER",         0x00),
                                    ("TEXT_EVENT",              0x01),
                                    ("COPYRIGHT_NOTICE",        0x02),
                                    ("SEQUENCE_TRACK_NAME",     0x03),
                                    ("INSTRUMENT_NAME",         0x04),
                                    ("LYRIC",                   0x05),
                                    ("MARKER",                  0x06),
                                    ("CUE_POINT",               0x07),
                                    ("MIDI_CHANNEL_PREFIX",     0x20),
                                    ("MIDI_PORT",               0x21),
                                    ("END_OF_TRACK",            0x2F),
                                    ("SET_TEMPO",               0x51),
                                    ("SMTPE_OFFSET",            0x54),
                                    ("TIME_SIGNATURE",          0x58),
                                    ("KEY_SIGNATURE",           0x59),
                                    ("SEQUENCER_SPECIFIC_META_EVENT", 0x7F)])

#
# Class MidiEvent
#
# - __init__    (self,track)
# - __cmp__     (self, other time) Compare self time wit other time
#

class MidiEvent:

    def __init__(self, track):
        self.track    = track   # track integer
        self.time     = None    # time (relative time in ticks)
        self.type     = None    # Type (e.g. note on, note off, etc.)
        self.channel  = None    # Channel
        self.pitch    = None    # Pitch (MIDI note, 0-127)
        self.velocity = None    # Velocity (MIDI note "volume", 0-127)
        self.data     = None    # data integer
    #
    # __cmp__ compare other time with self time
    #
    def __cmp__(self, other):
        # assert self.time != None and other.time != None
        return cmp(self.time, other.time)

    def __repr__(self):
        #
        # Build string with initial data for
        #  - Type (MIDI command)
        #  - Time (MIDI time, relative time in ticks)
        #  - Track
        #  - Channel
        #
        r = ("<MidiEvent %s, t=%s, track=%s, channel=%s" %
             (self.type,
              repr(self.time),
              self.track.index,
              repr(self.channel)))
        #
        # If present, add to string
        #  - Pitch (if present, MIDI note 0-127)
        #  - Data  (if present, MIDI data, (varies by MIDI event))
        #  - Velocity (if present, MID velocity (volume) 0-127
        #     
        for attrib in ["pitch", "data", "velocity"]:
            if getattr(self, attrib) != None:
                r = r + ", " + attrib + "=" + repr(getattr(self, attrib))
        #
        # Terminate string with '>' end bracket and return completed 
        # string with MIDI event
        #
        return r + ">"

    def read(self, time, dbytes):
        global runningStatus
        self.time = time
        # do we need to use running status?
        #print("byte 0 : ",dbytes[0])
        #
        # Test if most significant bit set in firt byte (index 0 of dbytes)    
        #
        if not (int(dbytes[0]) & 0x80):
            #
            # Most significant bit (7) is set
            #
            dbytes = str.encode(chr(runningStatus))[1:] + dbytes
        #
        # Get first byte from passed dbytes data
        #
        runningStatus = x = dbytes[0]
        x = int(x)          # Set X as integer of first byte (incdex 0) of MIDI data from dbytes
        y = x & 0xF0        # Set Y to current MIDI data from file with lower 4 bits masked
        z = int(dbytes[1])  # Set Z as integer of next byte (index 1) of MIDI data 
        #
        # Test if any bits 7-4 (upper bits is set)
        #
        if channelVoiceMessages.has_value(y):
            #
            # Channel message has value y 
            # (most signifcant bits in byte)
            # This means this is a channel voice messge MIDI event
            # First Get channel data
            #
            self.channel = (x & 0x0F) + 1
            # Get type from upper 4 bits of byte 
            self.type = channelVoiceMessages.whatis(y)
            # if Type is program change or channel 
            # return value associated with program
            # change or channel pressure
            #
            if (self.type == "PROGRAM_CHANGE" or
                self.type == "CHANNEL_KEY_PRESSURE"):
                #
                # Channel voice messge is program change or
                # channel key pressure
                #    
                self.data = z
                return dbytes[2:]
            else:
                #
                # MIDI File entry type not program change
                # or channel key pressure
                # Get pitch velocity and channel values
                #
                self.pitch    = z
                self.velocity = int(dbytes[2])
                channel       = self.track.channels[self.channel - 1]
                #
                # Test if NOTE off entry
                # NOTE: Note off also interpreted for Note on with 0 velocity
                #
                if (self.type == "NOTE_OFF" or
                    (self.velocity == 0 and self.type == "NOTE_ON")):
                    #
                    # Note Off event, process it
                    #
                    channel.noteOff(self.pitch, self.time)
                # Not Note Off, check for 
                elif self.type == "NOTE_ON":
                    #
                    # Note On event, process it
                    #
                    channel.noteOn(self.pitch, self.time, self.velocity)
                return dbytes[3:]
        #
        # Event is not a channel voice message, test if it is a channel mode message 
        # A channel mode message is a 0xBX first, followed by second byte (z)
        # with what mode message it is
        #
        elif y == 0xB0 and channelModeMessages.has_value(z):
            #
            # Mode message found in channel mode message table
            # Get channel from first byte, bits 3-0
            #
            self.channel = (x & 0x0F) + 1
            #
            # Get type string from channelModeMesssage table 
            #
            self.type = channelModeMessages.whatis(z)
            if self.type == "LOCAL_CONTROL":
                self.data = (int(dbytes[2]) == 0x7F)
            elif self.type == "MONO_MODE_ON":
                self.data = int(dbytes[2])
            #
            # return advanced MIDI data bytes string
            #
            return dbytes[3:]
        #
        # y is not a channel mode message, test if it is a SYSEX event
        #
        elif x == 0xF0 or x == 0xF7:
            self.type = {0xF0: "F0_SYSEX_EVENT",
                         0xF7: "F7_SYSEX_EVENT"}[x]
            #
            # Get length (varible length field) from MIDI data string and advance MIDI data string
            #
            length, dbytes = getVariableLengthNumber(dbytes[1:])
            #
            # Get data to self based on length just read from MIDI data string
            #
            self.data = dbytes[:length]
            #
            # Return advanced MIDI data string
            #
            return dbytes[length:]
        #
        # y is not a SYSEX event, check if if is a meta event
        #
        elif x == 0xFF:
            #
            # Meta event, test if z value (2nd byte) is in metaEvents table
            #
            if not metaEvents.has_value(z):
                print("Unknown meta event: FF %02X" % z)
                sys.stdout.flush()
                print("Unknown midi event type")
            self.type      = metaEvents.whatis(z)
            length, dbytes = getVariableLengthNumber(dbytes[2:])
            self.data      = dbytes[:length]
            return dbytes[length:]
        #
        # If none of the above, then we don't know and probably don't
        # care what this MIDI event is.
        #
        print( "Unknown midi event type " , x)
        return dbytes[2:] 

    def write(self):
        #
        # Create system extended event dictionarey (0xF0 and 0xF7 supported)
        # 
        sysex_event_dict = {"F0_SYSEX_EVENT": 0xF0,
                            "F7_SYSEX_EVENT": 0xF7}
        #
        # Test if write of Channel voice message
        #
        if channelVoiceMessages.hasattr(self.type):
            # 
            # Valid/supported Channel voice messsage:
            # 
            x = chr((self.channel - 1) +
                    getattr(channelVoiceMessages, self.type))
            if (self.type != "PROGRAM_CHANGE" and
                self.type != "CHANNEL_KEY_PRESSURE"):
                data = chr(self.pitch) + chr(self.velocity)
            else:
                data = chr(self.data)
            return x + data

        elif channelModeMessages.hasattr(self.type):
            x = getattr(channelModeMessages, self.type)
            x = (chr(0xB0 + (self.channel - 1)) +
                 chr(x) +
                 chr(self.data))
            return x

        elif sysex_event_dict.has_key(self.type):
            str = chr(sysex_event_dict[self.type])
            str = str + putVariableLengthNumber(len(self.data))
            return str + self.data

        elif metaEvents.hasattr(self.type):
            str = chr(0xFF) + chr(getattr(metaEvents, self.type))
            str = str + putVariableLengthNumber(len(self.data))
            return str + self.data

        else:
            print( "unknown midi event type: " + self.type)

"""
register_note() is a hook that can be overloaded from a script that
imports this module. Here is how you might do that, if you wanted to
store the notes as tuples in a list. Including the distinction
between track and channel offers more flexibility in assigning voices.

import midi
notelist = [ ]
def register_note(t, c, p, v, t1, t2):
    notelist.append((t, c, p, v, t1, t2))
midi.register_note = register_note
"""

def register_note(track_index, 
                  channel_index, 
                  pitch, 
                  velocity,
                  keyDownTime, 
                  keyUpTime
                 ):
    pass


# Define for Show Note string in hex
def showstr(str, n=16):
    for x in str[:n]:
        print ('%02x' % ord(x)),
    print
#
# Get number from a set of bytes of requested length
# 
def getNumber(bytes, length):
    #
    # MIDI uses big-endian for everything
    #
    sum = 0
    for i in range(length):
        sum = (sum << 8) + int(bytes[i])
    return sum, bytes[length:]

#
# Get a number from a variable length MIDI data event
#
def getVariableLengthNumber(bytes):
    sum = 0
    i   = 0
    #
    # Loop and get number from variable byte field
    # Number is in bits 6-0 of each byte and
    # the variable length number is terminated
    # when bit 7 is zero
    #
    while 1:
        x = int(bytes[i])               # Get current byte as integer
        i = i + 1                       # increment index
        sum = (sum << 7) + (x & 0x7F)   # Add bits 6-0 to current sum
        if not (x & 0x80):              # Test if last byte (bit 7 is zero)
            return sum, bytes[i:]       # If last byte, then return read/calculated number

def putNumber(num, length):
    # MIDI uses big-endian for everything
    lst = [ ]
    for i in range(length):
        n = 8 * (length - 1 - i)
        lst.append(chr((num >> n) & 0xFF))
    return string.join(lst, "")

def putVariableLengthNumber(x):
    lst = [ ]
    while 1:
        y, x = x & 0x7F, x >> 7
        lst.append(chr(y + 0x80))
        if x == 0:
            break
    lst.reverse()
    lst[-1] = chr(ord(lst[-1]) & 0x7f)
    return string.join(lst, "")

#
# MidiChannel class
#   - __init__    (self, track, index)
#   - __repr__    (self)
#   - noteOn      (self, pitch (0-127), time (relative ticks), velocity (0-127))
#   - noteOff     (self, pitch (0-127), time (relative ticks))
#
class MidiChannel:

    """A channel (together with a track) provides the continuity connecting
    a NOTE_ON event with its corresponding NOTE_OFF event. Together, those
    define the beginning and ending times for a Note."""

    def __init__(self, track, index):
        self.index   = index
        self.track   = track
        self.pitches = { }

    def __repr__(self):
        return "<MIDI channel %d>" % self.index

    def noteOn(self, pitch, time, velocity):
        self.pitches[pitch] = (time, velocity)

    def noteOff(self, pitch, time):
        if pitch in self.pitches:
            keyDownTime, velocity = self.pitches[pitch]
            register_note(self.track.index, self.index, pitch, velocity,
                          keyDownTime, time)
            del self.pitches[pitch]
        # The case where the pitch isn't in the dictionary is illegal,
        # I think, but we probably better just ignore it.

#
# Class DeltaTime
#
# Methods/operators:
# read 
# write
#
class DeltaTime(MidiEvent):

    type = "DeltaTime"
    #
    # Read Delta time from string as variable length data from MIDI data string
    # return that number and MIDI data past that number (advanced string "newstr")
    #
    def read(self, oldstr):
        self.time, newstr = getVariableLengthNumber(oldstr)
        return self.time, newstr
    #
    # Write Delta time to string as variable length data MIDI data field
    # return string advanced to current end of string
    #
    def write(self):
        str = putVariableLengthNumber(self.time)
        return str

#
# Class MidiTrack
#   - __init__      (self,index)  Init based on track index
#   - read          (self,str)    Read MIDI events for track based on passed str value
# 
#

class MidiTrack:

    def __init__(self, index):
        self.index      = index # Index    integer (init to passed index value)
        self.events     = [ ]   # Events   List for track
        self.channels   = [ ]   # Channels List for track
        self.length     = 0     # Length   integer (start @ 0)
        #
        # Append MidiChannel 1-16 to MidiTrack
        for i in range(16):
            self.channels.append(MidiChannel(self, i+1))

    #
    # read method
    #
    def read(self, str):
        time = 0                            # Zero out time
        assert str[:4].decode() == "MTrk"   # Make sure initial data is "MTrk" (start of given midi track data in Midi file)
        length, str = getNumber(str[4:], 4) # Get length and string data of first entry
        self.length = length                # Store length from track data to self
        mystr       = str[:length]          # Setup My string for this track
        remainder   = str[length:]          # Setup remaining data (data after this track's data ends)
        while mystr:                        # Loop through track data until done:
            delta_t   = DeltaTime(self)     
            dt, mystr = delta_t.read(mystr)     # Get delta time of this event, increment string
            time      = time + dt               # Add delta time to absolute time
            self.events.append(delta_t)         # Append delta time to track events
            e         = MidiEvent(self)         # Get MIDI event of this event
            mystr     = e.read(time, mystr)     # Get MIDI event sting of this event
            self.events.append(e)               # Append MIDI event data after Delta time
        return remainder                    # When loop done, return remaining data (data after this track's data)

    def write(self):
        time = self.events[0].time
        #
        # build str using MidiEvents
        #
        str = ""                    # Setup string variable
        for e in self.events:       # Loop through This track's events and write to string
            str = str + e.write()
        #
        # Midi events all written to string for this track
        # Append "MTrk" and String length to begining of string and return
        # completed Midi Track string
        #
        return "MTrk" + putNumber(len(str), 4) + str

    def __repr__(self):
        r = "<MidiTrack %d -- %d events\n" % (self.index, len(self.events))
        for e in self.events:
            r = r + "    " + str(e) + "\n"
        return r + "  >"


class MidiFile:

    def __init__(self):
        self.file                = None # File name
        self.format              = 1    # MIDI file format (default to MIDI file 1 format)
        self.tracks              = [ ]  # List of tracks for this file
        self.ticksPerQuarterNote = None # Ticks per quarter note
        self.ticksPerSecond      = None # Ticks per secon
    #
    # Open file
    #  - Filename (string)
    #  - Attributes (defaults to read (r) and binary (r) if no attributes given
    #
    def open(self, filename, attrib="rb"):
        #
        # Test if no filename specified, if so then use Standard In or Standard Out
        #
        if filename == None:
            if attrib in ["r", "rb"]:
                self.file = sys.stdin
            else:
                self.file = sys.stdout
        #
        # Filename specified: Open file with passed attributes (or "rb" if not passed)
        #        
        else:
            self.file = open(filename, attrib)

    def __repr__(self):
        r = "<MidiFile %d tracks\n" % len(self.tracks)
        for t in self.tracks:
            r = r + "  " + t + "\n"
        return r + ">"
    #
    # Close MIDI file
    #
    def close(self):
        self.file.close()
    #
    # Read Midi data from file to string
    #    
    def read(self):
        print("Now Reading Midi file " + self.file.name)
        self.readstr(self.file.read())
    #
    # Parse Midi data string into fields, store and calculate, etc. until end of string
    #  
    def readstr(self, bytes):
        """ Midi files start with MThd. So check that. """
        assert bytes[:4].decode() == "MThd"
        #
        # Get MIDI header data field length
        # NOTE: Only length of 6 is supported
        #
        length, bytes = getNumber(bytes[4:], 4)
        """ Check header length (4 bytes); """
        print(length)
        assert length == 6
        #
        # Get MIDI file format in next 2 bytes
        # and store format for self.format
        #
        format, bytes = getNumber(bytes, 2)
        self.format   = format
        #
        # Only MIDI file format 0 or 1 supported, so do assert here
        #
        assert format == 0 or format == 1   # dunno how to handle 2        
        #
        # Get number of number of tracks (next two bytes) and then
        # time division (next two bytes after number of tracks)
        # from Midi file header
        #
        numTracks, bytes = getNumber(bytes, 2)
        division,  bytes = getNumber(bytes, 2)
        #
        # Test if most significant bit of time division field is set
        # If so,  then time division field is in Frames per second and ticks per frame
        # If not, then time division field is in Ticks per quarter note
        #
        if division & 0x8000:
            #
            # High bit is set, time division is in Frames per second and ticks per frame            
            #
            framesPerSecond = -((division >> 8) | -128)
            ticksPerFrame = division & 0xFF
            assert ticksPerFrame == 24 or \
                   ticksPerFrame == 25 or \
                   ticksPerFrame == 29 or \
                   ticksPerFrame == 30
            if ticksPerFrame == 29: ticksPerFrame = 30  # drop frame
            #
            # Calculate ticks per second by multiplying ticks per frame
            # times frames per second
            #
            self.ticksPerSecond = ticksPerFrame * framesPerSecond
        else:
            #
            # High bit is not set, time division is in ticks per quarter note
            #
            self.ticksPerQuarterNote = division & 0x7FFF
        #
        # Loop Through all track data in the file
        #
        for i in range(numTracks):
            #
            # Get Track data for Track i
            #
            trk  = MidiTrack(i)
            #
            # Read bytes from Track and append to trk
            #
            bytes = trk.read(bytes)
            self.tracks.append(trk)
            #
            # Print out number of tracks and events
            #
            print("tracks " + str(i+1) + " events " + str(len(trk.events)))
    #
    # Write Midi data to file
    #
    def write(self):
        #
        # Call Write self.writestr to build all locally stored MIDI sata
        # to a string and then write to file
        #
        self.file.write(self.writestr())
    #
    # Write All MIDI data to string, MIDI header followed by all MIDI tracks' data
    #
    def writestr(self):
        #
        # Get time division from ticks per quarter note stored value
        #
        division = self.ticksPerQuarterNote
        #
        # Don't handle ticksPerSecond yet, too confusing
        #
        assert (division & 0x8000) == 0
        #
        # Build MIDI header string
        #
        str = "MThd"                                #  - 4 bytes M  T  h  d     (MIDI type header)
        str = str + putNumber(6,                4)  #  - 4 bytes 00 00 00 06    (6)
        str = str + putNumber(self.format,      2)  #  - 2 bytes 00 0X          (MIDI type 0 or 1)
        str = str + putNumber(len(self.tracks), 2)  #  - 2 bytes XX XX          (Number of tracks)
        str = str + putNumber(division,         2)  #  - 2 bytes XX XX          (Ticks per quarter note)
        #
        # File header built OK, loop through all tracks
        # and add MIDI track data for each track
        # 
        for trk in self.tracks:
            str = str + trk.write()
        #
        # MIDI header and track data all written to string OK
        # Return string
        #
        return str
    
# End of file Midi.py
    