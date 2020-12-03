'''
Merge Test Python code.

Merged work by Alan K. Bartky and Andy Fillebrown

Uses Blender rig by Andy Fillebrown followed by some manual editing 
of the Blender file for some changes (textures, colors, frame rate, etc.)
to be able to output as PNG and import into Adobe Premiere
(frame rate for pictures in Premiere of 29.97)

Alan K. Bartky, 2015-12-21

Source code from Andy Fillebrown from Github:
https://github.com/andy-fillebrown/audiocarver-blender-addon/

'''



'''
MIDI processing Python code
.Created on 19.03.2011

@author: kaiwegner
'''

#----------------------------------------- 
# Import Declarations for MIDI processing
#-----------------------------------------

import sys
import string

import io

import sys, string, types

#
# Global variables for MIDI processing
#
midiTempos                  = [ ]
midiTicksToTime             = [ ]
midiNotes                   = [ ]
midiObjects                 = [ ]
midiObjectsColors           = [ ]
partsPerQuarterNote         = 960  # Value my MIDI sequencer uses, overwritten by value from file...
numberOfTempoEntries        = 0

nextTicksToTimeTickValue        = 0
nextTicksToTimeTicksPerSecond   = 0.0
currentTicksToTimeTickValue     = 0
currentTicksToTicksPerSecond    = 0.0

#
# Class definitions used in MIDI processing
#
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
                                    ("CONTROL_CHANGE",          0xB0),  # Bank if 0 or 32 specified
                                    ("PROGRAM_CHANGE",          0xC0),  # Patch
                                    ("CHANNEL_KEY_PRESSURE",    0xD0),
                                    ("PITCH_WHEEL_CHANGE",      0xE0)]) # Pitch Wheel
#
# Channel mode messages for data for program change or controller change channel voice message
# NOTE: Channel mode messages are the same event as "Program change" that
# have specific "controller numbers of 120-127)
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
        self.track    = track   # track
        self.time     = None    # time (absolute time in MIDI ticks)
        self.type     = None    # Type (e.g. note on, note off, etc.)
        self.channel  = None    # Channel
        self.pitch    = None    # Pitch (MIDI note, 0-127)
        self.velocity = None    # Velocity (MIDI note "volume", 0-127)
        self.data     = None    # data string (bytes)
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

    #
    # Read operation:
    #  - self
    #  - time in absolute MIDI ticks
    #  - String of MIDI data where MIDI time for this event
    #    has already been processed and data should start
    #    with MIDI event byte
    #
    def read(self, time, dbytes):
        global runningStatus
        self.time = time      # Store MIDI event absolute time ticks to self 
        # do we need to use running status?
        #print("byte 0 : ",dbytes[0])
        #
        # Test if most significant bit set in firt byte (index 0 of dbytes)    
        #
        if not (int(dbytes[0]) & 0x80):
            #
            # Most significant bit (7) is not set
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
        # Test current byte to see if bits 7-4 (upper bits) matches
        # a known MIDI channel voice message
        #
        if channelVoiceMessages.has_value(y):
            #
            # Channel message has value y 
            # (most signifcant bits in byte)
            # This means this is a channel voice messge MIDI event
            # First Get channel data
            # This is lower 4 bytes (0x0-0xF) plus
            # one to get channel number 1-16
            #
            self.channel = (x & 0x0F) + 1
            #
            # Get type from upper 4 bits of byte 
            #
            self.type = channelVoiceMessages.whatis(y)
            #
            # Most common events are note on and note off
            # so check for them first to save some time...
            #
            if (self.type == "NOTE_ON" or
                self.type == "NOTE_OFF"
               ):
                #
                # NOTE On or Off event
                #
                self.pitch    = z
                self.velocity = int(dbytes[2])
                #
                # Get channel object associated with
                # this MIDI eventy
                #
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
                #
                # Event processed, advance string by 3 bytes
                # and return
                #    
                return dbytes[3:]
            #
            # Not NOTE ON or NOTE Off event
            # Check for other channel voice 
            # and channel mode events
            #
            # If type is program change or channel 
            # return value associated with program
            # change or channel pressure
            #
            elif (self.type == "PROGRAM_CHANGE"       or
                  self.type == "CHANNEL_KEY_PRESSURE"   
                 ):
                #
                # Channel voice messge is program change or
                # channel key pressure.
                # These events are two bytes long instead
                # of 3
                #    
                self.data = z
                return dbytes[2:]
            
            elif (self.type == "CONTROL_CHANGE"):
                #
                # Control change.
                # Get channel from first byte, bits 3-0
                #
                self.channel = (x & 0x0F) + 1
                #
                # Test if it is a channel mode message 
                # A channel mode message is a control message, 
                # followed by second byte from 120 to 127
                #
                if (z <= 127) and (z >= 120):
                    if channelModeMessages.has_value(z):
                        #
                        # Mode message found in channel mode message table
                        #
                        # Get type string from channelModeMesssage table 
                        # And override "CONTROL_CHANGE" as type in self.type
                        #
                        self.type = channelModeMessages.whatis(z)
                        if self.type == "LOCAL_CONTROL":
                            self.data = (int(dbytes[2]) == 0x7F)
                        elif self.type == "MONO_MODE_ON":
                            self.data = int(dbytes[2])
                        else:
                            self.data = dbytes[1:3]
                else:
                    #
                    # Not a channel mode message, this is a 
                    # control message
                    # For general MIDI
                    # If data is 0 or 32, then this is
                    # bank setting information                    
                    #
                    self.data = dbytes[1:3]
                #
                # Control change or channel Mode message completed processing
                # Advance MIDI data string by 3 bytes
                #
                return dbytes[3:]
            
            elif (self.type == "POLYPHONIC_KEY_PRESSURE"):
                #
                # Polyphonic key pressure, store 2 bytes of data
                #
                self.data = dbytes[1:3]
                return dbytes[3:]
            
            elif (self.type == "PITCH_WHEEL_CHANGE"):
                #
                # Pitch Wheel (Pitch bend) change
                # Pitch bend is in 7 bits, bits 6-0
                # of the next two bytes where the
                # least significant bits are first
                #
                self.data = int(dbytes[1]) + (int(dbytes[2])<<7)
                return dbytes[3:]            
                
            else:
                print("PROGRAM ERROR")
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
                #
                # 2nd byte of meta event unknown
                #
                print("Unknown meta event: FF %02X" % z)
                sys.stdout.flush()
                print("Unknown midi event type")            
            self.type      = metaEvents.whatis(z)
            length, dbytes = getVariableLengthNumber(dbytes[2:])
            self.data      = dbytes[:length]
            if self.type == "SET_TEMPO":
                #
                # MIDI set tempo event
                # Get new tempo where if not in frame mode,
                # this this is expressed in
                # microseconds per quarter note (beat).
                # 
                midiTempo, dummyBytes = getNumber(self.data,length)
                channel = self.track.channels[0]
                channel.tempoChange(self.time, midiTempo)
            #
            # Meta Event processing complete
            # Advance string by read/calculated length
            #
            return dbytes[length:]
        #
        # If none of the above, then we don't know and probably don't
        # care what this MIDI event is.
        # advance string by two bytes and return
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
            x = chr((self.channel - 1) + getattr(channelVoiceMessages, self.type))
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

"""
def register_note(track_index, 
                  channel_index, 
                  pitch, 
                  velocity,
                  keyDownTime, 
                  keyUpTime
                 ):
    pass
"""

def register_note(track_index, 
                  channel_index, 
                  pitch, 
                  velocity,
                  keyDownTime, 
                  keyUpTime
                 ):
    midiNotes.append([keyDownTime, 
                      keyUpTime,
                      track_index,
                      channel_index,
                      pitch,
                      velocity
                     ]
                    ) 



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
#   - setTempo    (self, time, tempo)
#
class MidiChannel:

    """A channel (together with a track) provides the continuity connecting
    a NOTE_ON event with its corresponding NOTE_OFF event. Together, those
    define the beginning and ending times for a Note."""

    def __init__(self, track, index):
        self.index   = index    # index integer
        self.track   = track    # track integer
        # Note On events Dicitonary 
        #  - pitches (key) MIDI note 0-127, 
        #  - MIDI abosulte ticks time
        #  - MIDI Note ON velocity (volume) 1-127 (Note ON with velocity 0 == Note Off event)
        #
        self.pitches = { }      

    def __repr__(self):
        return "<MIDI channel %d>" % self.index

    def noteOn(self, pitch, time, velocity):
        #
        # Note ON, store Note ON pitch (MIDI note), MIDI absolute ticks time and velocity
        # for this pitch (pitch is later used as a key to match Note Off event to
        # corresponding Note ON event to process the data for the entire note
        #
        self.pitches[pitch] = (time, velocity)

    def noteOff(self, pitch, time):
        #
        # Note OFF event (actual Note OFF MIDI event, or NOTE ON event with velocity == 0):
        # Look for corresponding Note ON data in self.pitches dictionary
        #
        if pitch in self.pitches:
            #
            # Match found for NOTE Off event's pitch (MIDI note 0-12)
            # with a corresponding previous Note ON event with same pitch.
            # 
            # Get NOTE On MIDI absolute ticks time and velocity 
            # of the note
            #
            keyDownTime, velocity = self.pitches[pitch]
            register_note(self.track.index, 
                          self.index, 
                          pitch, 
                          velocity,
                          keyDownTime, 
                          time
                         )
            del self.pitches[pitch]
        # The case where the pitch isn't in the dictionary is illegal,
        # I think, but we probably better just ignore it.

    def tempoChange(self, time, tempo):
        #
        # Tempo change, record for later use in 
        # doing math, calculations, etc. from
        # Midi Tempo to actual abosulute time in seconds
        #
        midiTempos.append([time,tempo])

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
        self.events     = [ ]   # MIDI Events   List for track
        self.channels   = [ ]   # Channels      List for track
        self.length     = 0     # Track data byte Length   integer (start @ 0)
        #
        # Append MidiChannel 1-16 to MidiTrack
        for i in range(16):
            self.channels.append(MidiChannel(self, i+1))

    #
    # read method
    #
    def read(self, str):
        time        = 0                     # Zero out time for this track
        assert str[:4].decode() == "MTrk"   # Make sure initial data is "MTrk" (start of given midi track data in Midi file)
        length, str = getNumber(str[4:], 4) # Get length and avdvance MIDI data str past length field
        self.length = length                # Store track data byte length from track data to self
        mystr       = str[:length]          # Setup string data for parsing loop for this track
        remainder   = str[length:]          # Setup remaining data (data after this track's data ends)
        while mystr:                        # Loop through track data until all data parsed for this track:
            delta_t   = DeltaTime(self)     
            dt, mystr = delta_t.read(mystr)     # Get delta time in MIDI ticks of this event, increment string
            time      = time + dt               # Add current delta time to get current absolute time in MIDI ticks
            self.events.append(delta_t)         # Append delta time in MIDI ticks to track events
            e         = MidiEvent(self)
            mystr     = e.read(time, mystr)     # Get MIDI event sting of this event, pass absolute time to read operation
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
        self.tempos              = [ ]  # List of MIDI tempos from SET TEMPO events
        self.ticksPerQuarterNote = None # Ticks per quarter note
        self.ticksPerSecond      = None # Ticks per second
    #
    # Open file
    #  - Filename (string)
    #  - Attributes (defaults to read (r) and binary (r) if no attributes given
    #
    def open(self, filename, attrib="rb"):
        #
        # Test if no filename specified, if so then use Standard In or Standard Out
        #
        print(filename,attrib)
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
        r = ""
        r += ("<MidiFile %d tracks\n" % len(self.tracks))
        #print(r)
        for t in self.tracks:
            #print(t)
            r += "  "
            r += str(t) 
            r += "\n"
        r += ">"
        return r
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
        #print(length)
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
        # If so,  then time division field is in Frames per second
        #         and ticks per frame
        # If not, then time division field is in Ticks per quarter note
        #
        if division & 0x8000:
            #
            # High bit is set, time division is in Frames per second
            # and ticks per frame            
            #
            framesPerSecond = -((division >> 8) | -128)
            ticksPerFrame = division & 0xFF
            #
            # Supported ticks per frame values
            # are: 24, 25, 29 or 30 only
            #
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
            partsPerQuarterNote      = self.ticksPerQuarterNote
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
            # data for this index
            #
            bytes = trk.read(bytes)
            self.tracks.append(trk)
            #
            # Print out number of tracks and events
            #
            print("track: " + str(i+1) + " events: " + str(len(trk.events)))
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

# Start of test/debug code
def createTicksToTimeTable():
    ppq                     = partPerQuarterNote # from global
    currentTempo            = 500000 # default microseconds per beat (120 BPM)
    currentTick             = 0
    cummulativeSeconds      = 0.0
    baseTicksPerSecond      = ppq * 1000000 / currentTempo
    currentTicksPerSecond   = baseTicksPerSecond   
    lastTempo               = currentTempo
    lastTick                = currentTick
    lastTicksPerSecond      = currentTicksPerSecond
    numberOfTempoEntries    = 0
    for tm in midiTempos:
        #
        # Get first current entry data
        #
        currentTick     = tm[0]
        currentTempo    = tm[1]
        currentTicksPerSecond   = ppq * 1000000 / currentTempo
        deltaTicks      = currentTick - lastTick
        #print("Current Tick, Tempo and Delta ticks:",currentTick, currentTempo, deltaTicks)
        if (numberOfTempoEntries == 0):
            if (deltaTicks > 0):
                #
                # First entry greater than 0
                # set default entry at 0
                #
                midiTicksToTime.append([0,0.0,baseTicksPerSecond])
                #print("midiTicksToTime: Create 0 entry", midiTicksToTime[0])
                numberOfTempoEntries += 1        
        numberOfTempoEntries += 1
        if (numberOfTempoEntries == 2):
            nextTicksToTimeTickValue = currentTick
        #
        # Calculate time in seconds of current tempo entry ticks
        #               
        #
        # From previous Tempo calculate ticks per second 
        #  
        lastTicksPerSecond   = ppq * 1000000 / lastTempo
        #
        # current ticks is less than or equal to 
        # requested ticks, calculate and add time to total
        #
        cummulativeSeconds += deltaTicks / lastTicksPerSecond
        #
        # Create new MIDI ticks to time entry
        #
        #print("Last Ticks per second and cummulative seconds", \
        #      lastTicksPerSecond, \
        #      cummulativeSeconds \
        #     )
        midiTicksToTime.append([currentTick,cummulativeSeconds,currentTicksPerSecond])
        #print("midiTicksToTime:", (numberOfTempoEntries-1), midiTicksToTime[(numberOfTempoEntries-1)])
        #
        # Setup for next loop
        #
        lastTick  = currentTick
        lastTempo = currentTempo
    #
    # Calculation complete, table is built, return 
    #
    firstTicksToTimeTickValue = 0
    currentTicksToTimeValue   = 0
    lastTicksToTimeTickValue  = currentTick
    lastTicksToTimeEntryNumber = numberOfTempoEntries
    return
        

def getSecondsFromMidiAbsoluteTicks(midiTicks):
    #
    # Calculating Time from Ticks to Seconds
    # using pre-built Ticks to Time data
    #
    currentTicks            = 0
    currentSeconds          = 0
    currentTicksPerSecond   = 0.0
    cummulativeSeconds      = 0.0
    previousTicks           = -1
    previousTicksPerSecond  = 0.0
    previousSeconds         = 0.0
    valueFound              = 0

    for tickMap in midiTicksToTime:
        #
        # Get current entry data
        #
        currentTicks            = tickMap[0]
        currentSeconds          = tickMap[1]
        currentTicksPerSecond   = tickMap[2]
        if (previousTicks != -1):
            #
            # Have current and last, check if MidiTicks is between them
            #
            if ((midiTicks >= previousTicks) & (midiTicks < currentTicks)):
                #
                # Tick is between current and last, calculate time
                #
                cummulativeSeconds = previousSeconds \
                                   + ((midiTicks - previousTicks) / previousTicksPerSecond)
                valueFound = 1
                break;
        #
        # Not yet found, setup for next loop
        #
        previousTicks          = currentTicks
        previousTicksPerSecond = currentTicksPerSecond
        previousSeconds        = currentSeconds
    #
    # Check if value found, if not, use last value
    #
    if (valueFound != 1):
        cummulativeSeconds = previousSeconds \
                           + ((midiTicks - previousTicks) / previousTicksPerSecond)
    #
    # Calculation complete, return absolute seconds 
    # (absolute seconds where 0.0 seconds is start of Midi file data)
    #
    return cummulativeSeconds
       
def oldGetSecondsFromMidiAbsoluteTicks(midiTicks):
    #
    # Calculating Time from Ticks to Seconds:
    #
    ppq                     = partPerQuarterNote # from global
    currentTempo            = 500000 # default microseconds per beat (120 BPM)
    currentTick             = 0
    currentTicksPerSecond   = ppq * 1000000 / currentTempo
    currentSecondsPerTick   = 1/currentTicksPerSecond
    ticksRemaining          = midiTicks
    cummulativeSeconds      = 0.0
    lastTempo               = currentTempo
    lastTick                = currentTick
    lastTicksPerSecond      = currentTicksPerSecond

    for tm in midiTempos:
        #
        # Get first current entry data
        #
        currentTick     = tm[0]
        currentTempo    = tm[1]
        deltaTicks      = currentTick - lastTick
        #
        # From previous Tempo calculate ticks per second 
        #  
        lastTicksPerSecond   = ppq * 1000000 / lastTempo
        #
        # Test if current tick time of tempo change
        # is greater than requested tick time
        # if so, then exit loop for final calculation
        #
        if (currentTick > midiTicks):
            break
        #
        # current ticks is less than or equal to 
        # requested ticks, calculate and add time to total
        #
        cummulativeSeconds += deltaTicks / lastTicksPerSecond
        #
        # Decrement ticks processed so far
        #
        ticksRemaining -= deltaTicks 
        #
        # Exit loop if no more ticks to process
        # 
        if (ticksRemaining <= 0):
            break
        #
        # Setup for next loop
        #
        lastTick  = currentTick
        lastTempo = currentTempo
    #
    # Loop complete, add to cummulative seconds
    # if Remaining ticks > 0
    #
    if (ticksRemaining > 0):
        #
        # Still ticks left at no more entries
        # or more entries, but final
        # value between tempo changes
        # add final time calculation
        #
        cummulativeSeconds += ticksRemaining / lastTicksPerSecond
    #
    # Calculation complete, return absolute seconds 
    # (absolute seconds where 0.0 seconds is start of Midi file data)
    #
    return cummulativeSeconds
 
m                   = MidiFile()

MidiFileName        = "C:\\Users\Alan\\Downloads\\MAMPlayer2006aug19_035\\Bach-Vivaldi-Concerto-A-Minor-4-pianos.mid"
DebugFileName       = "C:\\Users\Alan\\Downloads\\MAMPlayer2006aug19_035\\Bach-Vivaldi-Concerto-A-Minor-4-pianos.txt"

"""
MidiFileName        = "C:\\Users\Alan\\Downloads\\MAMPlayer2006aug19_035\\Albert Lavignac Galop - Marche.mid"
DebugFileName       = "C:\\Users\Alan\\Downloads\\MAMPlayer2006aug19_035\\Albert Lavignac Galop - Marche.txt"
"""

"""
MidiFileName        = "C:\\Users\Alan\\Downloads\\MAMPlayer2006aug19_035\\RV542.mid"
DebugFileName       = "C:\\Users\Alan\\Downloads\\MAMPlayer2006aug19_035\\RV542Debug.txt"
"""

"""
MidiFileName        = "C:\\Users\Alan\\Downloads\\MAMPlayer2006aug19_035\\RV356.mid"
DebugFileName       = "C:\\Users\Alan\\Downloads\\MAMPlayer2006aug19_035\\RV356Debug.txt"
"""

"""
MidiFileName        = "C:\\Users\Alan\\Downloads\\MAMPlayer2006aug19_035\\FlowersMidi1.mid"
DebugFileName       = "C:\\Users\Alan\\Downloads\\MAMPlayer2006aug19_035\\FlowersMidi1Debug.txt"
"""

"""
MidiFileName        = "C:\\Users\Alan\\Downloads\\MAMPlayer2006aug19_035\\BillieJeanMidi1.mid"
DebugFileName       = "C:\\Users\Alan\\Downloads\\MAMPlayer2006aug19_035\\BillieJeanMidi1Debug.txt"
"""

fileopen                = m.open(MidiFileName,"rb")
filedata                = m.read()
track0                  = m.tracks[0]
track1                  = m.tracks[1]
Debug                   = open(DebugFileName,"w")
TempoTimeMap            = []
CurrentTempo            = 500000  # Microseconds per quarter note (single "beat")
TicksPerQuarterNote     = m.ticksPerQuarterNote
partPerQuarterNote      = TicksPerQuarterNote
CurrentTicksPerSecond   = 0.0
LastAbsoluteTime        = 0.0     # Last Absolute time in seconds
CurrentAbsoluteTime     = 0.0
LastAbsoluteTicks       = 0

#
# Sort data created during test
#
midiTempos.sort()
midiNotes.sort()
#
# From MIDI data, create a time table to map between MIDI tempo data and absolute time
#
createTicksToTimeTable()

 
print("PPQ: ",m.ticksPerQuarterNote); 
print("Writing MIDI event parsed data to debug file, please wait")
Debug.write(str(m))

#
# Import for Blender for creating meshes, file operations, time operations and misc.
#
import bmesh
import bpy
from bpy    import context
from math   import pi, sin, cos, radians
from random import random
import sys
import time

#--------------------------------------------------------
# Global variables imported from Andy Fillebrown's code
#--------------------------------------------------------

note_suffix_number       = 2
note_layer               = 18
note_scale               = 0.01
note_template_object     = None
timeline_count           = 0
timeline_layer           = 17
timeline_text_layer      = 16

track_min                = 9999999
track_max                = 0
track_count              = 1.0
track_scale              = 1.0

pitch_min                = 128
pitch_max                = 0

velocity_min             = 1.0
velocity_max             = 0.0
velocity_scale           = 1.0

#verts_per_second        = 1 # use "0" to get start and end points only
verts_per_second         = 0 # use "0" to get start and end points only

#
# Per note group (track, NOTE (A-G#), or channel
#

verts_per_ring           = 32
max_note_thickness       = 0.02
#max_note_thickness      = 0.25
min_note_duration        = 0.1



angle_start              =  30 / 180 * pi
angle_end                =  89 / 180 * pi
angle_increment          = 0.0

note_range_distance      = 5.0
#note_range_distance     = 4.0

timeline_imported        = False

note_group_angle_start = [
                           89 / 180 * pi,  # piano 1 Right Hand
                           89 / 180 * pi,  # piano 1 Left  Hand
                          149 / 180 * pi,  # piano 2 Right Hand
                          149 / 180 * pi,  # piano 2 Left  Hand
                          210 / 180 * pi,  # piano 3 Right Hand
                          210 / 180 * pi,  # piano 3 Left  Hand
                          270 / 180 * pi,  # piano 4 Right Hand
                          270 / 180 * pi,  # piano 4 Left  Hand
                          150 / 180 * pi,  # violins 1
                          150 / 180 * pi,  # violins 2
                          150 / 180 * pi,  # violas
                          150 / 180 * pi,  # cellos
                          150 / 180 * pi, 
                         ]  

note_group_angle_end =   [
                           30 / 180 * pi,  # piano 1 Right Hand
                           30 / 180 * pi,  # piano 1 Left  Hand
                           90 / 180 * pi,  # piano 2 Right Hand
                           90 / 180 * pi,  # piano 2 Left  Hand
                          269 / 180 * pi,  # piano 3 Right Hand
                          269 / 180 * pi,  # piano 3 Left  Hand
                          329 / 180 * pi,  # piano 4 Right Hand
                          329 / 180 * pi,  # piano 4 Left  Hand
                          209 / 180 * pi,  # violins 1
                          209 / 180 * pi,  # violins 2
                          209 / 180 * pi,  # violas
                          209 / 180 * pi,  # cellos
                          209 / 180 * pi,
                         ]  

note_group_offset =      [
                           0.0,  # piano 1 Right Hand
                           0.0,  # piano 1 Left  Hand
                           0.0,  # piano 2 Right Hand
                           0.0,  # piano 2 Left  Hand
                           0.0,  # piano 3 Right Hand
                           0.0,  # piano 3 Left  Hand
                           0.0,  # piano 4 Right Hand
                           0.0,  # piano 4 Left  Hand
                           0.0,  # violins 1
                           0.1,  # violins 2
                           0.05, # violas
                           0.0,  # cellos
                           0.0
                         ]  

note_group_verts_per_ring = [
                              3,  # piano 1 Right Hand
                              3,  # piano 1 Left  Hand
                              4,  # piano 2 Right Hand
                              4,  # piano 2 Left  Hand
                              5,  # piano 3 Right Hand
                              5,  # piano 3 Left  Hand
                              6,  # piano 4 Right Hand
                              6,  # piano 4 Left  Hand
                             32,  # violins 1
                             32,  # violins 2
                             32,  # violas
                             32,  # cellos
                             32,
                            ]  


# set_cycles_material_color = True

#
# Setup for multiple track based or note (C, C#, D, etc.) based objects
#
#
# Meshes per each track
#
track_meshes             = [];

#
# Create 12 meshes for each track
#
i = 0
while i < 12:
    track_meshes.append(bmesh.new())
    i = i + 1

#-------------------------------------------------------------------
# class definitions variables imported from Andy Fillebrown's code
#-------------------------------------------------------------------

#
# Note Class: fields are
#   - Start time (relative to start time of track)
#   - Duration (time between start and end time for each note)
#   - Velocity
#   - Pitch (MIDI pitch 0 to 127)
#
class Note:
    _startTime = -1
    _duration  = -1
    _velocity  = -1
    _pitch     = -1
    _track     = -1
    _channel   = -1

#-------------------------------------------------------------------
# method definitions variables imported from Andy Fillebrown's code
#-------------------------------------------------------------------

#
# Method to print a message
#
def print_message(message):
    print(message);
    sys.stdout.flush();


#
# Method to deselect all Blender objects
#
def clear_ss():
    bpy.ops.object.select_all(action = 'DESELECT')


#
# Method to get current selected objects
#
def current_ss():
    return bpy.context.selected_objects


#
# Method to create a zero prefixed
# string from a number so that the
# number string is always 3 characters long
# (e.g. number of 0 to 999 becomes "000" to "999")
#
def to_zero_prefixed_string(number):
    zero_prefixed_string = ""
    if number < 100:
        zero_prefixed_string += "0"
    if number < 10:
        zero_prefixed_string += "0"
    zero_prefixed_string += str(int(number))
    return zero_prefixed_string

#
# Method to get the Object name used for a given
# track or note type (e.g. C, C#, D, D#, E, etc.)
#
# Each object consists of a group of meshes where the
# a mesh is created with the group object for each
# note.
#
# So if in Track mode, all notes for a MIDI track
# are put into a single object with multiple meshes
#
def get_note_object_name(note_group_specifier):
    return "Note.Main.1." + str(note_group_specifier)

#
# Method to get the material used for a group of notes,
# where the group is all notes for a Track, or
# all of the same note, but different octaves
#
def get_note_material(note_group_specifier):
    return bpy.data.materials["Note.Material.1." + str(note_group_specifier)]


def get_note_object(note_group_specifier):
    #
    # Get the name used for this note object for a given
    # note group
    #
    note_material    = get_note_material(note_group_specifier)
    note_object_name = get_note_object_name(note_group_specifier)
    #
    # Test if the group note object already exists, if so
    # then use that object.
    # If not, then create a new note group object
    #
    if (note_object_name in bpy.data.objects.keys()):
        #
        # Note group object exists, use that one
        #
        note_object = bpy.data.objects[note_object_name]
    else:
        #
        # Note group object does not exist
        # Select and duplicate the note template object
        # using the main note object from the blender
        # file
        #
        clear_ss()
        note_template_object.select = True
        bpy.ops.object.duplicate()

        # Rename the new note object.
        note_object      = bpy.data.objects["Note.Main.001"]
        note_object.name = note_object_name

    # Set the note mesh materials for this object
    note_object.material_slots[0].material = note_material

    return note_object

#
# Method to get the note group mesh entry based
# on the note group specifier
#
def get_note_mesh(note_group_specifier):
    return track_meshes[int(note_group_specifier - 1)]


def create_note_material(color = "#ffffff"):
    return bpy.data.materials["Note.Material.1.1"]
#     template_material  = bpy.data.materials["Note.Material.0"]
#     note_material      = template_material.copy()
#     note_material.name = "Note.Material." + str(track_count)
#
#     note_material.diffuse_color[0] = float((16 * int(color[1:2], 16)) + int(color[2:3], 16)) / 255.0
#     note_material.diffuse_color[1] = float((16 * int(color[3:4], 16)) + int(color[4:5], 16)) / 255.0
#     note_material.diffuse_color[2] = float((16 * int(color[5:6], 16)) + int(color[6:7], 16)) / 255.0
#
#     r_is_zero = 0.0 == note_material.diffuse_color[0]
#     g_is_zero = 0.0 == note_material.diffuse_color[1]
#     b_is_zero = 0.0 == note_material.diffuse_color[2]
#
#     if r_is_zero:
#         if g_is_zero or b_is_zero:
#             note_material.diffuse_color[0] = 0.0005
#         else:
#             note_material.diffuse_color[0] = 0.001
#     if g_is_zero:
#         if r_is_zero or b_is_zero:
#             note_material.diffuse_color[1] = 0.0005
#         else:
#             note_material.diffuse_color[1] = 0.001
#     if b_is_zero:
#         if r_is_zero or g_is_zero:
#             note_material.diffuse_color[2] = 0.0005
#         else:
#             note_material.diffuse_color[2] = 0.001
#     if set_cycles_material_color:
#         note_material.node_tree.nodes['Glass BSDF'].inputs['Color'].default_value = (note_material.diffuse_color[0],
#                                                                                      note_material.diffuse_color[1],
#                                                                                      note_material.diffuse_color[2],
#                                                                                      1.0)
#     return note_material


#
# Method to create a tapered (starting at max thickness reducing step by 
# step to a point at the end of the note) cylindrical tube
# object based on a note's start time, velocity, duration and previously
# calculated Y and Z positions for the note in space to render
#
def add_round_note_shape_to_mesh(note, position, mesh):
    global max_note_thickness
    #
    # Get start time and previously calculated note y and z positions
    #
    x = note._startTime
    y = position[0]
    z = position[1]
    #
    # Setup for mesh creation loop
    #
    mesh_verts  = mesh.verts
    mesh_faces  = mesh.faces
    x_increment = 10000000000000
    if (0.0 < verts_per_second):
        x_increment = 1.0 / verts_per_second;
    #
    # Pick verts per ring based on note group
    #
    verts_per_ring = note_group_verts_per_ring[int(note._track)]
    mesh_angle_increment = 2 * pi / verts_per_ring
    x1                   = 0.0
    current_thickness    = max_note_thickness
    #
    # mesh creation loop, loop until note's duration (length)
    # is processed. 
    # 
    while (x1 < note._duration):
        x2 = x1 + x_increment
        if (note._duration < x2):
            x2 = note._duration
        angle = 0
        next_thickness = (1.0 - (x2 / (2 * note._duration))) * max_note_thickness
        #
        # Create the circular tapered cylinder section
        # for the note.  The velocity will be used to adjust
        # the radius of the cylinder (higher velocity, the larger the associated
        # radius)
        #
        while (angle < (2 * pi)):
            y1    = note._velocity * sin(angle)
            z1    = note._velocity * cos(angle)
            angle = angle + mesh_angle_increment
            y2    = note._velocity * sin(angle)
            z2    = note._velocity * cos(angle)
            v1    = mesh_verts.new((x + x1, y + y1 * current_thickness, z + z1 * current_thickness))
            v2    = mesh_verts.new((x + x2, y + y1 * next_thickness,    z + z1 * next_thickness   ))
            v3    = mesh_verts.new((x + x2, y + y2 * next_thickness,    z + z2 * next_thickness   ))
            v4    = mesh_verts.new((x + x1, y + y2 * current_thickness, z + z2 * current_thickness))
            mesh_faces.new((v1, v2, v3, v4))
        x1 = x2
        current_thickness = next_thickness


def add_square_note_shape_to_mesh(note, position, mesh):
    x               = note._startTime
    y               = -position[0]
    z               = position[1]
    note_width      = note_range_distance / (pitch_max - pitch_min)
    half_note_width = note_width / 2.0
 
    mesh_verts      = mesh.verts
    mesh_faces      = mesh.faces
 
    x_increment     = 10000000000000


    if (0.0 < verts_per_second):
        x_increment = 1.0 / verts_per_second;
 
    x1 = 0.0
    current_thickness = max_note_thickness
 
    # front
    y1 = y - half_note_width
    y2 = y + half_note_width
    z2 = z - (note._velocity * current_thickness)
    v1 = mesh_verts.new((x, y1, z))
    v2 = mesh_verts.new((x, y1, z2))
    v3 = mesh_verts.new((x, y2, z2))
    v4 = mesh_verts.new((x, y2, z))
    mesh_faces.new((v1, v2, v3, v4))
 
    while (x1 < note._duration):
        x2 = x1 + x_increment
        if (note._duration < x2):
            x2 = note._duration
        next_thickness = (1.0 - (x2 / (2 * note._duration))) * max_note_thickness
 
        # top
        y1 = y - half_note_width
        y2 = y + half_note_width
        z1 = z - (note._velocity * current_thickness)
        z2 = z - (note._velocity * next_thickness   )
        v1 = mesh_verts.new((x + x1, y1, z1))
        v2 = mesh_verts.new((x + x2, y1, z2))
        v3 = mesh_verts.new((x + x2, y2, z2))
        v4 = mesh_verts.new((x + x1, y2, z1))
        mesh_faces.new((v1, v2, v3, v4))
 
        # right
        y1 = y + half_note_width
        z1 = z - (note._velocity * current_thickness)
        z2 = z - (note._velocity * next_thickness   )
        v1 = mesh_verts.new((x + x1, y1, z1))
        v2 = mesh_verts.new((x + x2, y1, z2))
        v3 = mesh_verts.new((x + x2, y1, z))
        v4 = mesh_verts.new((x + x1, y1, z))
        mesh_faces.new((v1, v2, v3, v4))
 
        # bottom
        y1 = y - half_note_width
        y2 = y + half_note_width
        v1 = mesh_verts.new((x + x1, y2, z))
        v2 = mesh_verts.new((x + x2, y2, z))
        v3 = mesh_verts.new((x + x2, y1, z))
        v4 = mesh_verts.new((x + x1, y1, z))
        mesh_faces.new((v1, v2, v3, v4))
 
        # left
        y1 = y - half_note_width
        z1 = z - (note._velocity * current_thickness)        #z2 = z - (note._velocity * current_thickness)
        z2 = z - (note._velocity * next_thickness   )        #z4 = z - (note._velocity * next_thickness)
        v1 = mesh_verts.new((x + x1, y1, z))
        v2 = mesh_verts.new((x + x2, y1, z))
        v3 = mesh_verts.new((x + x2, y1, z2))
        v4 = mesh_verts.new((x + x1, y1, z1))
        mesh_faces.new((v1, v2, v3, v4))
 
        x1 = x2
        current_thickness = next_thickness
 
    # back
    y1 = y - half_note_width
    y2 = y + half_note_width    #z1 = z - (note._velocity * current_thickness)
    z1 = z - (note._velocity * current_thickness)
    v1 = mesh_verts.new((x + x1, y2, z))
    v2 = mesh_verts.new((x + x1, y2, z1))
    v3 = mesh_verts.new((x + x1, y1, z1))
    v4 = mesh_verts.new((x + x1, y1, z))
    mesh_faces.new((v1, v2, v3, v4))


# def add_arc_note_shape_to_mesh(note, start_radius, start_angle, end_radius, end_angle, mesh):
#     global max_note_thickness
# 
#     x = note._startTime
# 
#     mesh_verts = mesh.verts
#     mesh_faces = mesh.faces
#     x_increment = 10000000000000
#     if (0.0 < verts_per_second):
#         x_increment = 1.0 / verts_per_second;
#     x1 = 0.0
#     radius_increment = (end_radius - start_radius) / verts_per_ring
#     angle_increment = (end_angle - start_angle) / verts_per_ring
#     while (x1 < note._duration):
#         x2 = x1 + x_increment
#         if (note._duration < x2):
#             x2 = note._duration
#         radius = start_radius
#         angle = start_angle
#         i = 0
#         while (i < verts_per_ring):
#             y1 = radius * sin(angle)
#             z1 = radius * cos(angle)
#             radius = radius + radius_increment
#             angle = angle + angle_increment
#             y2 = radius * sin(angle)
#             z2 = radius * cos(angle)
#             v1 = mesh_verts.new((x + x1, y1, z1))
#             v2 = mesh_verts.new((x + x2, y1, z1))
#             v3 = mesh_verts.new((x + x2, y2, z2))
#             v4 = mesh_verts.new((x + x1, y2, z2))
#             mesh_faces.new((v1, v2, v3, v4))
#             i = i + 1
#         x1 = x2


def add_circular_ring_note_to_mesh(note, mesh):
    global pitch_min
    global pitch_max
    #
    # Setup Angle start based on note group
    #
    angle_start = note_group_angle_start[int(note._track)]
    angle_end   = note_group_angle_end  [int(note._track)]
    #
    # Calculate the note's Y and Z location on the ring.
    #
    pitch_delta  = note._pitch - pitch_min
    if (angle_end >= angle_start):
        pitch_angle  = angle_start + (pitch_delta * angle_increment)
    else:
        pitch_angle  = angle_start - (pitch_delta * angle_increment)
    #track_offset = 1.0 + (track_count / 10.0)
    #track_offset = 0.4 + (note._track / 12.0)
    track_offset = 1.0 + (note_group_offset[int(note._track)])
    y            = track_offset * sin(pitch_angle)
    z            = track_offset * cos(pitch_angle)
    #
    # Create the mesh for this note based on the
    # Note and the calculated Y and Z position
    # 
    add_round_note_shape_to_mesh(note, (y, z), mesh)


def add_flat_note_to_mesh(note, mesh):
    global pitch_min
    global pitch_max
    y = 0
    z = -0.1 * track_count
    pitch_offset = note._pitch - pitch_min
    if (0.0 < pitch_offset):
        y = -(note_range_distance / 2.0) + (pitch_offset * (note_range_distance / (pitch_max - pitch_min)))
    add_square_note_shape_to_mesh(note, (y, z), mesh)


# def add_spiral_ring_note_to_mesh(note, mesh):
#     pitch_key = (note._pitch % 12.0) - 9.0 # 9 == A
#     pitch_8va = int(note._pitch / 12.0)
# 
#     # Calculate the note's location.
#     start_radius = 1.5 - (4.0 * max_note_thickness * (pitch_8va + ((pitch_key - 1.0) / 12.0)))
#     end_radius   = 1.5 - (4.0 * max_note_thickness * (pitch_8va + ((pitch_key) / 12.0)))
#     pitch_angle  = pitch_key * pi / 6.0 # key * 2pi / 12
#     start_angle  = (pitch_key * 2 * pi / 12.0) - (0.5 * 2 * pi / 12.0)
#     end_angle    = (pitch_key * 2 * pi / 12.0) + (0.5 * 2 * pi / 12.0)
# 
#     #add_round_note_shape_to_mesh(note, (y, z), mesh)
#     add_arc_note_shape_to_mesh(note, start_radius, start_angle + 0.01, end_radius, end_angle - 0.01, mesh)


#
# This method is used to import a note from passed data to create a single Note's object
#

def import_note(note_track, note_pitch, note_on_time, note_off_time, note_volume):
    #
    # Calculate X and Y value for the new note mesh object based on values passed
    #
    first_pt_x = track_scale * note_on_time
    first_pt_y = float(note_pitch)
    duration   = (track_scale * note_off_time) - first_pt_x
    if (duration < min_note_duration):
        #print("note duration changed from " + str(duration) + " to " + str(min_note_duration))
        duration = min_note_duration
    #
    # Get the note's velocity/volume.  This will be used
    # later for circular notes to setup the radius of the mesh
    # object (higher the volume, larger radius for the cylinder)
    #
    velocity = note_volume
    #
    # Create a new Note object and set its values for
    #   - Start time
    #   - Duration
    #   - Velocity
    #   - Pitch
    #
    note            = Note()
    note._startTime = first_pt_x
    note._duration  = duration
    note._velocity  = 0.01 + (velocity_scale * (velocity - velocity_min))
    note._pitch     = first_pt_y
    note._track     = note_track - track_min # Use track index
    #
    # Get mesh object for the note group (based on track)
    # or create a new one for the note group if not already created
    #
    note_mesh       = get_note_mesh(int(note_track))
    #
    # Create and place in 3D space a new Note mesh object
    #
    add_circular_ring_note_to_mesh(note, note_mesh)
    #add_flat_note_to_mesh(note, note_mesh)
    #add_spiral_ring_note_to_mesh(note, note_mesh)

#
# Method to import a selected track
#

#
def import_track(track_number):
    global note_suffix_number
    global track_count
    #
    # Read the track's attributes.
    #
    color = "#ffffff"
    track_name = ""
    i = 0
    #
    # Create the track's note material.
    #
    note_material = create_note_material(color)
    #
    # Select and duplicate the note template object.
    #
    clear_ss()
    note_template_object.select = True
    bpy.ops.object.duplicate()
    #
    # Rename the new note object.
    #
    note_object      = bpy.data.objects["Note.Main.001"]
    note_object.name = note_object.name[0 : -3] + to_zero_prefixed_string(note_suffix_number)
    #
    # Set the note mesh material.
    #
    note_object.material_slots[0].material = note_material

    note_bmesh = bmesh.new();
    #
    # Read the track's note list
    # Use Import note for each note in the track
    # To create Note objects for this track
    #
    for child_node in track_node.childNodes:
        if "NoteList" == child_node.nodeName:
            for note_node in child_node.childNodes:
                if "Note" == note_node.nodeName:
                    import_note(note_node, note_bmesh)

    note_bmesh.to_mesh(note_object.data)

    note_suffix_number += 1
    track_count        += 1

#---------------------------------------
# Begin code created by Alan K. Bartky
#---------------------------------------



#
# Misc. TBD to add or not
#
#bpy.context.scene.frame_end = 40
#
# Set global variabales
#
NumCubes                = 1000000
CurrentCube             = 1
CurrentXLocation        = 0.0
CurrentZLocation        = 0.0
CurrentYLocation        = 0.0
BeginFrame              = 1
EndFrame                = 11650 # 2400 #23400 #14200 # (70 seconds, test) 14400 # 8 minutes

MidiNotesRangeSize      = 8.0
MidiNoteScale           = MidiNotesRangeSize / 128
MidiNoteGroupStepSize   = MidiNoteScale * 4

TimeScale               = 1.0
XScale                  = TimeScale

#YScale                  = 0.5
#ZScale                  = 0.25
#CurrentCubeXScale       = 0.25
NoteSizeAdjustScale = 2.0  

MidiNoteOffset          = -64

channelOriginY =    [    0.0,   # Channel  0 (Piano Primo)
                         0.0,   # Channel  1 (Piano Secundo)
                         0.0,   # Channel  2 
                         0.0,   # Channel  3
                         0.0,   # Channel  4
                         0.0,   # Channel  5
                         0.0,   # Channel  6
                         0.0,   # Channel  7
                         0.0,   # Channel  8
                         0.0,   # Channel  9
                         0.0,   # Channel 10
                         0.0,   # Channel 11
                         0.0,   # Channel 12
                         0.0,   # Channel 13
                         0.0,   # Channel 14
                         0.0,   # Channel 15
                    ]                        
                        
                        
channelOriginZ =    [    0.0 - MidiNotesRangeSize/8,   # Channel  0 (piano primo)
                         0.0 + MidiNotesRangeSize/8,   # Channel  2 (piano secundo)
                         0.0 + (12 * MidiNoteScale),   # Channel  2
                         0.0 + (12 * MidiNoteScale),   # Channel  3
                         0.0 + (12 * MidiNoteScale),   # Channel  4
                         0.0 + (12 * MidiNoteScale),   # Channel  5
                         0.0 + MidiNotesRangeSize/4,   # Channel  6
                         0.0 + MidiNotesRangeSize/4 + (3*(NoteSizeAdjustScale*MidiNoteScale)),   # Channel  7
                         0.0 + MidiNotesRangeSize/4 + (6*(NoteSizeAdjustScale*MidiNoteScale)),   # Channel  8
                         0.0 + MidiNotesRangeSize/4 + (3*(NoteSizeAdjustScale*MidiNoteScale)),   # Channel  9
                         0.0 + MidiNotesRangeSize/4 + (0*(NoteSizeAdjustScale*MidiNoteScale)),   # Channel 10
                         0.0 - MidiNotesRangeSize/4,   # Channel 11
                         0.0 - MidiNotesRangeSize/4 - (3*(NoteSizeAdjustScale*MidiNoteScale)),   # Channel 12
                         0.0 - MidiNotesRangeSize/4 - (0*(NoteSizeAdjustScale*MidiNoteScale)),   # Channel 13
                         0.0 - MidiNotesRangeSize/4,   # Channel 14
                         0.0 - MidiNotesRangeSize/4,   # Channel 15
                    ]     

channelNoteScaleY = [
                        MidiNoteScale*2,  # Channel  0
                        MidiNoteScale*2,  # Channel  1
                        0.0,            # Channel  2 
                        0.0,            # Channel  3
                        0.0,            # Channel  4
                        0.0,            # Channel  5
                        MidiNoteScale*2,            # Channel  6
                        MidiNoteScale*2,            # Channel  7
                        MidiNoteScale*2,            # Channel  8
                        MidiNoteScale*2,            # Channel  9
                        MidiNoteScale*2,            # Channel 10
                        MidiNoteScale*2,  # Channel 11
                        MidiNoteScale*2,            # Channel 12
                        MidiNoteScale*2,            # Channel 13
                        MidiNoteScale*2,            # Channel 14
                        MidiNoteScale*2,            # Channel 15
                    ]  

channelNoteScaleZ = [
                        0.0,  # Channel  0
                        0.0,  # Channel  1
                        MidiNoteScale,  # Channel  2 
                        MidiNoteScale,  # Channel  3
                        MidiNoteScale,  # Channel  4
                        MidiNoteScale,  # Channel  5
                        0.0,  # Channel  6
                        0.0,  # Channel  7
                        0.0,  # Channel  8
                        0.0,  # Channel  9
                        0.0,  # Channel 10
                        0.0,  # Channel 11
                        0.0,  # Channel 12
                        0.0,  # Channel 13
                        0.0,  # Channel 14
                        0.0,  # Channel 15
                    ]  
                                      
                                          
NoteOnState             = 1;
CurrentNoteStartTime    = 0.0
CurrentNoteEndTime      = 0.0
StartMidiNoteNumber     = 0
CurrentMidiNoteNumber   = -1
CurrentMidiChannel      = 0
CurrentMidiVelocity     = 64
MidiNoteOnEvent         = 128+16
MidiNoteOffEvent        = 128
CurrentMidiNoteDuration = 0
FramesPerSecond         = 29.97 # 24 # 30
midiNoteColors          = [#  R     G     B
                            [1.00, 0.00, 0.00], # 0/C/I:           Pure Red
                            [0.00, 0.25, 0.75], # 1/C#/Db/I#:      Light Blue
                            [0.50, 0.50, 0.00], # 2/D/II:          Cyan (Yellow)
                            [0.25, 0.00, 0.75], # 3/D#/Eb/IIIb:    Purple
                            [0.00, 1.00, 0.00], # 4/E/III:         Pure Green
                            [0.75, 0.00, 0.25], # 5/F/IV:          Dark Pink
                            [0.00, 0.50, 0.50], # 6/F#/Gb/IV#:     Aqua
                            [0.75, 0.25, 0.00], # 7/G/V:           Orange
                            [0.00, 0.00, 1.00], # 8/G#/Ab/V+:      Pure Blue
                            [0.25, 0.75, 0.00], # 9/A/VI:          Yellow Green
                            [0.50, 0.00, 0.50], # 10/A#/Bb/VIIb:   Magenta
                            [0.00, 0.75, 0.25], # 11/B/VII:        Bluish Green
"""
                            [0.0, 0.0, 0.8], # 0/C/I:           Pure Blue
                            [0.4, 0.8, 0.0], # 1/C#/Db/I#:
                            [0.0, 0.8, 0.8], # 2/D/II:          Magenta
                            [0.0, 0.8, 0.4], # 3/D#/Eb/IIIb:
                            [0.0, 0.0, 0.8], # 4/E/III:         Pure Red
                            [0.0, 0.4, 0.8], # 5/F/IV: 
                            [0.8, 0.8, 0.0], # 6/F#/Gb/IV#:     Cyan (yellow)
                            [0.4, 0.0, 0.8], # 7/G/V: 
                            [0.0, 0.8, 0.0], # 8/G#/Ab/V+:      Pure Green 
                            [0.8, 0.0, 0.4], # 9/A/VI: 
                            [0.0, 0.8, 0.8], # 10/A#/Bb/VIIb:   Aqua
                            [0.8, 0.4, 0.0], # 11/B/VII:
"""
                          ]
#
# Current Note List
# Channel #  (0-15)
# Note #     (0-127)
# Start Time (seconds from start, start = 0)
# End Time   (seconds from start, start = 0)
# Velocity   (0-127)
CurrentNote = [0,0,0.0,0.0,0];
#
# Current event
# Relative Time (ticks)
# Event type (Note on or Note Off)
# Note number
# Note Velocity (only valid on Note On)
CurrentEvent = [0,0,0,0];
#
# Time tracking variables
#
CurrentTime      = 0.0
CurrentStartTime = 0.0
CurrentEndTime   = 0.0
#
#
# Main python code for adding notes to the mesh.
# This code is a mixture of code from Alan Bartky and Andy Fillebrown's source code
# 
#
midiNoteIndex     = 0

start_time        = time.time()
pitch_min         = 128
pitch_max         = 0
timeline_imported = False

#
# Scan MIDI data for Minimum and Maximum Pitch and velocity/volume
# NOTE: Velocity 
#
for currentNote in midiNotes:
    #
    # Check pitch (MIDI note), change velocity (0 to 127) to volume (0.0 to 1.0)
    #
    currentTrack        = currentNote[2]
    currentPitch        = currentNote[4]
    currentVelocity     = currentNote[5]
    currentVolume       = float(currentVelocity) / 127.0
    if (currentPitch > pitch_max):
        pitch_max = currentPitch
    if (currentPitch < pitch_min):
        pitch_min = currentPitch
    if (currentVolume > velocity_max):
        velocity_max = currentVolume
    if (currentVolume < velocity_min):
        velocity_min = currentVolume
    if (currentTrack > track_max):
        track_max = currentTrack
    if (currentTrack < track_min):
        track_min = currentTrack

print("Track  (  0 to n  ) min and max:",track_min,   track_max   )
print("Volume (0.0 to 1.0) min and max:",velocity_min,velocity_max)
print("Pitch  (  0 to 128) min and max:",pitch_min,   pitch_max   )

#
# Calculate the global velocity scale
#
velocity_scale = (velocity_max - velocity_min) / (1.0 - velocity_min)
#
# Calculate the global angle increment.
#
angle_increment = (angle_end - angle_start) / (pitch_max - pitch_min)
#
# Store the current selection set so it can be restored later.
#
cur_active_obj = bpy.context.scene.objects.active
cur_ss = current_ss()
#
# Turn on the note layers.
#
bpy.context.scene.layers[note_layer] = True
#
# Get the note template object from the Blender template file "Note.Main" object
#
note_template_object = bpy.data.objects["Note.Main"]
#
# Get the track scale from the Track.Scale.X
#
track_scale = bpy.data.objects[".Track.Scale.X"].scale[0]

#
# Setup Track (TEMP FOR NOW, JUST DO ONE TRACK FOR INITIAL DEBUG)
#
color = "#ffffff"
track_name = ""
i = 0
#
# Create the track's note material.
#
note_material = create_note_material(color)
#
# Select and duplicate the note template object.
#
clear_ss()
note_template_object.select = True
bpy.ops.object.duplicate()
#
# Rename the new note object.
#
note_object      = bpy.data.objects["Note.Main.001"]
note_object.name = note_object.name[0 : -3] + to_zero_prefixed_string(note_suffix_number)
#
# Set the note mesh material.
#
note_object.material_slots[0].material = note_material

#note_bmesh = bmesh.new();

#
# Import notes using this single material
#

#while (CurrentCube <= NumCubes):
while(1):
    #
    # Loop through all notes in the previously created MIDI data list
    #
    for currentNote in midiNotes:
        #
        # Get data from list for this note
        #
        currentNoteOnTicks  = currentNote[0]
        currentNoteOffTicks = currentNote[1]
        currentTrack        = currentNote[2]
        currentChannel      = currentNote[3] - 1 # We want channel index, not channel number
        currentPitch        = currentNote[4]
        currentVelocity     = currentNote[5]
        """
        print("Note data:",
              currentNoteOnTicks,
              currentNoteOffTicks,
              currentTrack,
              currentChannel,
              currentPitch,
              currentVelocity)
        """
        #
        # Convert absolute Midi tick time to seconds
        # (traverses tempo map based on tick value)
        # Adjust time to render properly at 29.97 FPS instead of 30 FPS
        # to import properly into Adobe Premiere
        #
        currentNoteOnTime    = getSecondsFromMidiAbsoluteTicks(currentNoteOnTicks) * FramesPerSecond/30.0
        currentNoteOffTime   = getSecondsFromMidiAbsoluteTicks(currentNoteOffTicks) * FramesPerSecond/30.0
        currentNoteTotalTime = currentNoteOffTime - currentNoteOnTime
        currentNoteMidTime   = currentNoteOnTime + (currentNoteTotalTime / 2.0)
        currentVolume        = currentVelocity/127
        #
        # For the Andy Fillebrown based blender rig and mesh creation code,
        # we have everything we need to create the mesh within the note group object.
        # A new mesh for the given note will always be created.
        # A new note group object (multiple meshes within the group object) will be created if not already present
        #
        #import_note(currentPitch, currentNoteOnTime, currentNoteOffTime, currentVolume, note_bmesh)
        import_note(currentTrack, currentPitch, currentNoteOnTime, currentNoteOffTime, currentVolume)                   
        #
        # Per Note rendering, motion and color all setup for a single note event, setup for next note event
        #
        CurrentCube       += 1            # Note number
        if (CurrentCube > NumCubes):
            break
        # 
        # End of loop, bump Note index and continue until all notes processed (or break above occurs)
        #
        midiNoteIndex += 1

    break
#
# DEBUG, END OF TRACK CLEANUP
#

#note_bmesh.to_mesh(note_object.data)

#
# Notes and timing have been imported.
# Add each mesh to it's note, from 1 to 12
#
i = 1
while (i <= 12):
    note = get_note_object(i)
    mesh = get_note_mesh(i)
    mesh.to_mesh(note.data)
    i = i + 1


#note_suffix_number += 1
#track_count        += 1

#
# Note group objects with their individual note meshes have been created so we
# now no longer want or need the note template object,
# so delete the note template objects.
#
clear_ss()
note_template_object.select = True
bpy.ops.object.delete()
#
# Restore the original Blender selection set.
#
clear_ss()
for obj in cur_ss:
    obj.select = True
bpy.context.scene.objects.active = cur_active_obj
print_message("\n... done in %.3f seconds\n" % (time.time() - start_time))

#
# Script done, close all open files
#
m.close()
Debug.close()
