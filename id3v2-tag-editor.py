#!/usr/bin/python

# License:  GPLv3 (GNU General Public License - version 3).
# Disclaimer: Use at your own risk.
# To know the status of this utility, refer to the README.

import os.path
import sys
import shlex
import binhex
from PIL import Image
import StringIO
import argparse
import logging

# Some 'Music apps' in mobile phone are not working with 'Unsynchronisation' flag, so set it to False
# Decoding with 'Unsynchronisation' flag is still enabled.
unsynchronisation_in_encoding_enabled = False

#class new_myModule3(object):
class TagEditorID3v2Major3(object):
    "A ID3v2.3 tag editor"

    def __init__(self, logger):
        self.major_ver = 3
        self.tag_header_sz = 10
        self.frame_header_sz = 10
        self.tag_unsynchronisation_enabled = True
        self.default_encoding_type = 'utf-16' # choose from self.encoding_types_dict, used for creating/modifying Frames
        self.id3_identifier = None
        self.tag_sz = None
        self.song_data = None
        self.tag_header = None
        self.suffix = None
        self.tag_body = None
        self.revision_no = None
        self.tag_body_sz = None
        self.tag_header_flags = None
        self.logger = logger

        # Supported "Encoding Byte":"Encoding Types"
        self.encoding_types_dict = {
            '\x00'  : 'ascii', # $00 - ISO-8859-1 (ASCII).
            '\x01'  : 'utf-16' # $01 - UCS-2 in ID3v2.2 and ID3v2.3, UTF-16 encoded Unicode with BOM.
        }
        # Supported "Encoding Types":"String Terminator"
        self.string_terminators_dict = {
            'ascii'     : '\x00',       # $00 - ISO-8859-1 (ASCII)
            'utf-16'    : '\x00'+'\x00' # $00 00 - UTF-16
        }
        # Declared/Supported Frames
        self.declared_frames_dict = {
            'AENC'  : 'Audio encryption',
            'APIC'  : 'Attached picture',
            'COMM'  : 'Comments',
            'COMR'  : 'Commercial frame',
            'ENCR'  : 'Encryption method registration',
            'EQUA'  : 'Equalization',
            'ETCO'  : 'Event timing codes',
            'GEOB'  : 'General encapsulated object',
            'GRID'  : 'Group identification registration',
            'IPLS'  : 'Involved people list',
            'LINK'  : 'Linked information',
            'MCDI'  : 'Music CD identifier',
            'MLLT'  : 'MPEG location lookup table',
            'OWNE'  : 'Ownership frame',
            'PRIV'  : 'Private frame',
            'PCNT'  : 'Play counter',
            'POPM'  : 'Popularimeter',
            'POSS'  : 'Position synchronisation frame',
            'RBUF'  : 'Recommended buffer size',
            'RVAD'  : 'Relative volume adjustment',
            'RVRB'  : 'Reverb',
            'SYLT'  : 'Synchronized lyric/text',
            'SYTC'  : 'Synchronized tempo codes',
            'TALB'  : 'Album/Movie/Show title',
            'TBPM'  : 'BPM (beats per minute)',
            'TCOM'  : 'Composer',
            'TCON'  : 'Content type',
            'TCOP'  : 'Copyright message',
            'TDAT'  : 'Date',
            'TDLY'  : 'Playlist delay',
            'TENC'  : 'Encoded by',
            'TEXT'  : 'Lyricist/Text writer',
            'TFLT'  : 'File type',
            'TIME'  : 'Time',
            'TIT1'  : 'Content group description',
            'TIT2'  : 'Title/songname/content description',
            'TIT3'  : 'Subtitle/Description refinement',
            'TKEY'  : 'Initial key',
            'TLAN'  : 'Language(s)',
            'TLEN'  : 'Length',
            'TMED'  : 'Media type',
            'TOAL'  : 'Original album/movie/show title',
            'TOFN'  : 'Original filename',
            'TOLY'  : 'Original lyricist(s)/text writer(s)',
            'TOPE'  : 'Original artist(s)/performer(s)',
            'TORY'  : 'Original release year',
            'TOWN'  : 'File owner/licensee',
            'TPE1'  : 'Lead performer(s)/Soloist(s)',
            'TPE2'  : 'Band/orchestra/accompaniment',
            'TPE3'  : 'Conductor/performer refinement',
            'TPE4'  : 'Interpreted, remixed, or otherwise modified by',
            'TPOS'  : 'Part of a set',
            'TPUB'  : 'Publisher',
            'TRCK'  : 'Track number/Position in set',
            'TRDA'  : 'Recording dates',
            'TRSN'  : 'Internet radio station name',
            'TRSO'  : 'Internet radio station owner',
            'TSIZ'  : 'Size',
            'TSRC'  : 'ISRC (international standard recording code)',
            'TSSE'  : 'Software/Hardware and settings used for encoding',
            'TYER'  : 'Year',
            'TXXX'  : 'User defined text information frame',
            'UFID'  : 'Unique file identifier',
            'USER'  : 'Terms of use',
            'USLT'  : 'Unsychronized lyric/text transcription',
            'WCOM'  : 'Commercial information',
            'WCOP'  : 'Copyright/Legal information',
            'WOAF'  : 'Official audio file webpage',
            'WOAR'  : 'Official artist/performer webpage',
            'WOAS'  : 'Official audio source webpage',
            'WORS'  : 'Official internet radio station homepage',
            'WPAY'  : 'Payment',
            'WPUB'  : 'Publishers official webpage',
            'WXXX'  : 'User defined URL link frame'
        }

        # Supported picture types in 'APIC' frames
        self.picture_types_dict = {
            0x00    : 'Other',
            0x01    : '32x32 pixels \'file icon\' (PNG only)',
            0x02    : 'Other file icon',
            0x03    : 'Cover (front)',
            0x04    : 'Cover (back)',
            0x05    : 'Leaflet page',
            0x06    : 'Media (e.g. label side of CD)',
            0x07    : 'Lead artist/lead performer/soloist',
            0x08    : 'Artist/performer',
            0x09    : 'Conductor',
            0x0A    : 'Band/Orchestra',
            0x0B    : 'Composer',
            0x0C    : 'Lyricist/text writer',
            0x0D    : 'Recording Location',
            0x0E    : 'During recording',
            0x0F    : 'During performance',
            0x10    : 'Movie/video screen capture',
            0x11    : 'A bright coloured fish',
            0x12    : 'Illustration',
            0x13    : 'Band/artist logotype',
            0x14    : 'Publisher/Studio logotype'
        }

        # Mapping 'option' to 'Frames', for adding/modifying Frames
        self.write_opts_dict = {
            'artist'    : 'TPE1',
            'album'     : 'TALB',
            'title'     : 'TIT2',
            'comments'  : 'COMM',
            'genre'     : 'TCON',
            'year'      : 'TYER',
            'track'     : 'TRCK',
            'picture'   : 'APIC'
        }

    def createHeader(self, song_data):
        id3_identifier = "ID3"
        major_ver = chr(self.major_ver)
        revision_no = chr(0x00)
        tag_header_flags = chr(0x00)
        tag_sz = self.encodeTagSz(0x00) # empty tag_body
        new_buf = "".join([id3_identifier, major_ver, revision_no, tag_header_flags, tag_sz, song_data])
        return self.decodeHeader(new_buf)

    def decodeHeader(self, buf):
        self.tag_header = buf[0:0+self.tag_header_sz]
        self.id3_identifier = self.tag_header[0:0+3]
        if self.id3_identifier != "ID3":
            self.logger.warning("Invalid ID3 Header")
            self.logger.warning("Adding ID3 Header")
            return self.createHeader(buf) # adding a header

        self.checkMajorVersion() # checking
        self.setRevisionNumber()
        self.setHeaderFlags()
        self.decodeTagSz()
        self.extractTagBodyAndSong(buf)
        syncd_tag_body = self.getSynchronisedTagBody()
        return syncd_tag_body

    def decodeExtendedHeader(self, tag_body):
        extended_header_sz = self.decodeFrameSize(tag_body)
        extended_header = tag_body[0:0+extended_header_sz]
        self.logger.error("Extended Header, Not parsed")
        return [extended_header, extended_header_sz]

    def checkMajorVersion(self):
        if self.major_ver != ord(self.tag_header[3]):
            self.logger.critical("Unmatched Major version: %d" % ord(self.tag_header[3]))
            error_msg = "Unmatched Major version: %d" % ord(self.tag_header[3])
            raise Exception(1, error_msg)
        self = TagEditorID3v2Major3(self.logger)

    def setRevisionNumber(self):
        self.revision_no = ord(self.tag_header[4])
        if self.revision_no == 0xFF:
            self.revision_no = None
            self.logger.critical("Unsupported Revision Number: %d" % self.revision_no)
            error_msg = "Unsupported Revision Number: %d" % self.revision_no
            raise Exception(1, error_msg)

    def setHeaderFlags(self):
        self.tag_header_flags = ord(self.tag_header[5])
        if  (self.tag_header_flags & 0x1F) != False:
            self.logger.critical("Invalid Header Flags: 0x%.2x" % self.tag_header_flags)
            error_msg = "Invalid Header Flags: 0x%.2x" % self.tag_header_flags
            raise Exception(1, error_msg)

    def synchronise(self, data): # converting 0xFF00 => 0xFF
        data = data.replace('\xFF'+'\x00', '\xFF')
        return data

    def unsynchronise(self, data): # converting 0xFF00 => 0xFF0000
        data = data.replace('\xFF', '\xFF'+'\x00')
        #data = data.replace('\xFF'+'\x00', '\xFF'+'\x00')
        return data

    def getSynchronisedTagBody(self):
        # checking if Synchronisation is needed
        if (self.tag_unsynchronisation_enabled) and ((self.tag_header_flags & 0x80) != False):
            syncd_tag_body = self.synchronise(self.tag_body)
        else:
            syncd_tag_body = self.tag_body
        return syncd_tag_body

    def decodeFrame(self, data):
        frame_id = data[0:0+4]
        sz = self.decodeFrameSize(data[4:4+4])
        frame_header_flags = (ord(data[8]) << 8) + ord(data[9])
        frame_header_sz = self.frame_header_sz
        data = data[frame_header_sz:frame_header_sz+sz]
        if self.declared_frames_dict.has_key(frame_id):
            if self.logger.isEnabledFor(logging.INFO):
                self.logger.info("\nFrame ID:\t\t%s (%s)" % (frame_id, self.declared_frames_dict[frame_id]))
            else:
                self.logger.warning("\n%s:" % (self.declared_frames_dict[frame_id]))
        else: # Unknown Frame ID
            if self.logger.isEnabledFor(logging.INFO):
                self.logger.info("\nFrame ID:\t\t%s (%s)" % (frame_id, "Unknown Frame ID"))
            else:
                self.logger.warning("\n%s (%s):" % (frame_id, "Unknown Frame ID"))
        self.logger.info("Size:\t\t\t%d" % sz)
        self.logger.info("Flags:\t\t\t0x%0.4x" % frame_header_flags)
        return [frame_id, sz, frame_header_flags, data]

    def hasDataLengthIndicator(self, frame_header_flags):
        if (frame_header_flags & 0x01) != False:
            return True

    def isFrameUnsynchronisationFlagSet(self, frame_header_flags):
        if (frame_header_flags & 0x02) != False:
            return True

    def extractTagBodyAndSong(self, buf):
        self.tag_body = buf[self.tag_header_sz:self.tag_header_sz+self.tag_sz]
        self.tag_body_sz = len(self.tag_body)
        self.song_data = buf[self.tag_header_sz+self.tag_sz:]

    def extractFrames(self, buf):
        frames_dict = {}
        indx = 0
        buf_sz = len(buf)
        while (indx+self.frame_header_sz) <= buf_sz:
            frame_id = buf[indx:indx+4]
            if frame_id == '\x00'+'\x00'+'\x00'+'\x00': # frame_id == NULL+NULL+NULL+NULL
                break
            sz = self.frame_header_sz+self.decodeFrameSize(buf[indx+4:indx+4+4])
            frame = buf[indx:indx+sz]
            if frames_dict.has_key(frame_id): # for each similar Frame (same TAG), append
                frames_dict[frame_id].append(frame)
            else:
                frames_dict.update({frame_id:[frame]})
            indx += sz
        return frames_dict

    # append the Frame
    def appendFrame(self, frames_dict, frame_id, frame):
        self.logger.warning("\nAppending frame: %s" % frame_id)
        if frames_dict.has_key(frame_id):
            frames_dict[frame_id].append(frame)
        else:
            frames_dict.update({frame_id:[frame]})

    # remove Frames that match with frame_details
    def removeFrame(self, frames_dict, frame_id):
        if self.write_opts_dict.has_key(frame_id): # frame as descriptive names, like 'tilte'
            frame_id = self.write_opts_dict[frame_id]
        else: # frame as standard Frame ID, like 'TIT2'
            frame_id = frame_id # redundant
        if frames_dict.has_key(frame_id):
            for frame in reversed(frames_dict[frame_id]): # for each similar Frame (same TAG)
                frames_dict[frame_id].remove(frame)
                self.logger.warning("Removed frame: %s" % frame_id)
            if len(frames_dict[frame_id]) == 0: # delete entries with no frames
                del frames_dict[frame_id]

    # remove all Frames
    def removeAllFrames(self, frames_dict):
        self.logger.warning("\nRemoving all Frames:")
        for frame_id in frames_dict.keys(): # for each TAG
            self.removeFrame(frames_dict, frame_id)

    # display Frames that match with frame_details
    def dispFrame(self, frames_dict, frame_id):
        if self.write_opts_dict.has_key(frame_id): # frame as discriptive names, like 'tilte'
            frame_id = self.write_opts_dict[frame_id]
        else: # frame as standard Frame ID, like 'TIT2'
            frame_id = frame_id # redundant
        if frames_dict.has_key(frame_id):
            for frame in frames_dict[frame_id]: # for each Frame of the TAG
                [frame_id, sz, frame_header_flags, data] = self.decodeFrame(frame)
                self.decodePayload(frame_id, self.tag_header_flags, frame_header_flags, data, sz)
                self.logger.info("----------------------------------")
        else:
            self.logger.warning("\nFrame not found")

    # display all Frames
    def dispAllFrames(self, frames_dict):
        self.logger.warning("\nDisplaying all Frames:")
        for frame_id in frames_dict: # for each TAG
            self.dispFrame(frames_dict, frame_id)

    def assignTagBody(self, syncd_frames):
        # checking if Unsynchronisation is needed
        if (unsynchronisation_in_encoding_enabled) and (self.tag_unsynchronisation_enabled):
            unsyncd_frames = self.unsynchronise(syncd_frames)
            if len(syncd_frames) != len(unsyncd_frames):
                # set 'Unsynchronisation', for entire TAG
                self.tag_header_flags = self.tag_header_flags | 0x80
                self.tag_body = unsyncd_frames
        else: # if Unsynchronisation is not needed
            self.tag_body = syncd_frames
        self.tag_body_sz = len(self.tag_body)

    def constructFile(self):
        if self.tag_body_sz: # non-empty body
            out_data = self.tag_header[0:0+5] + chr(self.tag_header_flags) +  self.encodeTagSz(self.tag_body_sz) + \
                       self.tag_body + self.song_data
        else: # if no Frames, remove ID3v2 TAG
            out_data = self.song_data
        return out_data

    def decodePayload(self, frame_id, tag_header_flags, frame_header_flags, data, sz):
        # Handling 'Data length indicator'
        if self.hasDataLengthIndicator(frame_header_flags) == True:
            data_length_indicator = self.decodeFrameSize(data[0:0+4])
            self.logger.info("Data_length_indicator:\t%d" % data_length_indicator)
            data = data[4:]
            sz -= 4
        # Unsynchronisation, only if not handled globally
        if (self.tag_unsynchronisation_enabled == False) and \
           (self.isFrameUnsynchronisationFlagSet(frame_header_flags) == True):
            data = self.synchronise(data)

        if self.isTextInfoFrame(frame_id):
            text_encoding = binhex.binascii.hexlify(data[0])
            encoding_type = self.encoding_types_dict[data[0]]
            chunks = self.splitNullTerminatedEncStrings(data[1:sz], encoding_type, -1) # -1 => as many splits as possible
            # All text information frames supports multiple strings, stored as a 'termination code' separated list
            info = []
            for enc_data in chunks:
                info.append(self.decodeText(data[0]+enc_data, len(data[0]+enc_data)))
            # If the textstring is followed by a termination \
            # all the following information should be ignored and not be displayed.
            if  chunks[-1] != "": # if terminated, last chunk will be empty
                self.logger.info("Text encoding:\t\t%s" % text_encoding)
                self.logger.warning("Information:\t\t%s" % (", ".join(info)))
        elif frame_id == "TXXX":
            text_encoding = binhex.binascii.hexlify(data[0])
            encoding_type = self.encoding_types_dict[data[0]]
            chunks = self.splitNullTerminatedEncStrings(data[1:sz], encoding_type, 1)
            description = self.decodeText(data[0]+chunks[0], len(data[0]+chunks[0]))
            value = self.decodeText(data[0]+chunks[1], len(data[0]+chunks[1]))
            self.logger.info("Text encoding:\t\t%s" % text_encoding)
            self.logger.warning("Description:\t\t%s" % description)
            self.logger.warning("Value:\t\t\t%s" % value)

        elif self.isUrlLinkFrame(frame_id):
            # Yet to implement the following provision:
            #   If the text string is followed by a string termination, all the following
            #   information should be ignored and not be displayed.
            url = self.decodeText(data, len(data))
            self.logger.warning("URL:\t\t\t%s" % url)
        elif frame_id == "WXXX":
            text_encoding = binhex.binascii.hexlify(data[0])
            encoding_type = self.encoding_types_dict[data[0]]
            chunks = self.splitNullTerminatedEncStrings(data[1:sz], encoding_type, 1)
            description = self.decodeText(data[0]+chunks[0], len(data[0]+chunks[0]))
            url = self.decodeText(chunks[1], len(chunks[1]))
            self.logger.info("Text encoding:\t\t%s" % text_encoding)
            self.logger.warning("Description:\t\t%s" % description)
            self.logger.warning("URL:\t\t\t%s" % url)
        elif frame_id == "APIC":
            text_encoding = binhex.binascii.hexlify(data[0])
            # since 'picture_type' can be '\x00', parsing/splitting is done step-by-step
            chunks = self.splitNullTerminatedEncStrings(data[1:sz], 'ascii', 1)
            mime_type = self.decodeText(chunks[0], len(chunks[0]))
            if mime_type == "": # MIME Type is omitted
                mime_type = "image/"
            picture_type = binhex.binascii.hexlify(chunks[1][0])
            picture_type_int = ord(chunks[1][0])
            encoding_type = self.encoding_types_dict[data[0]]
            chunks = self.splitNullTerminatedEncStrings(chunks[1][1:], encoding_type, 1)
            description = self.decodeText(data[0]+chunks[0], len(data[0]+chunks[0]))
            image = chunks[1] # image
            self.logger.info("Text encoding\t\t%s" % text_encoding)
            self.logger.info("MIME type:\t\t%s" % mime_type)
            self.logger.warning("Picture type:\t\t$%s : %s" % (picture_type, self.picture_types_dict[picture_type_int]))
            self.logger.info("Description:\t\t%s" % description)

            if mime_type == "-->": # image link
                self.logger.warning("Data:\t\t\t%s" % image)
            else:
                self.logger.warning("Data:\t\t\t<Not displayed>")
                img_type = mime_type.split("/")[1]
                file_name = self.suffix+"_"+ self.picture_types_dict[picture_type_int]+"_"+description+"."+img_type
                file_name = file_name.replace("/", "|")
                if self.logger.isEnabledFor(logging.INFO):
                    self.writeFile(file_name, image)
                    self.logger.info("\t\t\tWritten into file:%s" % file_name)
        elif frame_id == "PCNT":
            counter = data
            chunk_indx = 0
            self.logger.warning("Counter:\t\t\t", )
            while chunk_indx < len(counter):
                self.logger.warning("%s" % binhex.binascii.hexlify(counter[chunk_indx]),)
                chunk_indx += 1
            self.logger.info("")
        elif frame_id == "POPM":
            chunks = self.splitNullTerminatedEncStrings(data[0:sz], 'ascii', 1)
            email_to_user = self.decodeText(chunks[0], len(chunks[0]))
            rating = binhex.binascii.hexlify(chunks[1][0])
            self.logger.info("Email to user:\t\t%s" % email_to_user)
            self.logger.warning("Rating:\t\t\t%s" % rating)
            chunk_indx = 1
            self.logger.warning("Counter:\t\t\t", )
            while chunk_indx < len(chunks[1]):
                self.logger.warning("%s" % binhex.binascii.hexlify(chunks[1][chunk_indx]),)
                chunk_indx += 1
            self.logger.warning("")
        elif frame_id == "USLT":
            text_encoding = binhex.binascii.hexlify(data[0])
            language = binhex.binascii.hexlify(data[1])+binhex.binascii.hexlify(data[2])+binhex.binascii.hexlify(data[3])
            language_str = chr(ord(data[1]))+chr(ord(data[2]))+chr(ord(data[3]))
            encoding_type = self.encoding_types_dict[data[0]]
            chunks = self.splitNullTerminatedEncStrings(data[4:sz], encoding_type, 1)
            content_descriptor = self.decodeText(data[0]+chunks[0], len(data[0]+chunks[0]))
            lyrics_text = self.decodeText(data[0]+chunks[1], len(data[0]+chunks[1]))
            self.logger.info("Text encoding:\t\t%s" % text_encoding)
            self.logger.info("Language:\t\t0x%s : %s" % (language, language_str))
            self.logger.warning("Content descriptor:\t%s" % content_descriptor)
            self.logger.warning("Lyrics/text:\t\t%s" % lyrics_text)
        elif frame_id == "GEOB":
            text_encoding = binhex.binascii.hexlify(data[0])
            encoding_type = self.encoding_types_dict[data[0]]
            chunks = self.splitNullTerminatedEncStrings(data[1:sz], encoding_type, 3)
            mime_type = self.decodeText(chunks[0], len(chunks[0]))
            filename = self.decodeText(data[0]+chunks[1], len(data[0]+chunks[1]))
            content_description = self.decodeText(data[0]+chunks[2], len(data[0]+chunks[2]))
            data = chunks[3] # data
            self.logger.info("Text encoding:\t\t%s" % text_encoding)
            self.logger.info("MIME type:\t\t%s" % mime_type)
            self.logger.warning("Filename:\t\t%s" % filename)
            self.logger.warning("Content description:\t%s" % content_description)
            self.logger.warning("Encapsulated object:\t<Not displayed>")
            file_name = self.suffix+"_"+content_description+"_"+filename+"."+mime_type
            file_name = file_name.replace("/", "|")
            if self.logger.isEnabledFor(logging.INFO):
                self.writeFile(file_name, data)
                self.logger.info("\t\t\tWritten into file:%s" % file_name)
        elif frame_id == "MCDI":
            cd_toc = data # data
            self.logger.warning("CD TOC:\t\t\t<Not displayed>")
            file_name = self.suffix+"_"+"CD TOC"
            file_name = file_name.replace("/", "|")
            if self.logger.isEnabledFor(logging.INFO):
                self.writeFile(file_name, cd_toc)
            self.logger.info("\t\t\tWritten into file:%s" % file_name)
        elif frame_id == "COMM":
            text_encoding = binhex.binascii.hexlify(data[0])
            language = binhex.binascii.hexlify(data[1])+binhex.binascii.hexlify(data[2])+binhex.binascii.hexlify(data[3])
            language_str = chr(ord(data[1]))+chr(ord(data[2]))+chr(ord(data[3]))
            encoding_type = self.encoding_types_dict[data[0]]
            chunks = self.splitNullTerminatedEncStrings(data[4:sz], encoding_type, 1)
            short_content_descrip = self.decodeText(data[0]+chunks[0], len(data[0]+chunks[0]))
            the_actual_text = self.decodeText(data[0]+chunks[1], len(data[0]+chunks[1]))
            self.logger.info("Text encoding:\t\t%s" % text_encoding)
            self.logger.info("Language:\t\t0x%s : %s" % (language, language_str))
            self.logger.warning("Short content descrip.:\t%s" % short_content_descrip)
            self.logger.warning("The actual text:\t%s" % the_actual_text)
        elif frame_id == "USER":
            text_encoding = binhex.binascii.hexlify(data[0])
            language = binhex.binascii.hexlify(data[1])+binhex.binascii.hexlify(data[2])+binhex.binascii.hexlify(data[3])
            language_str = chr(ord(data[1]))+chr(ord(data[2]))+chr(ord(data[3]))
            data = self.decodeText(data[0]+data[4:], len(data[0]+data[4:]))
            the_actual_text = data
            self.logger.info("Text encoding:\t\t%s" % text_encoding)
            self.logger.info("Language:\t\t0x%s : %s" % (language, language_str))
            self.logger.warning("The actual text:\t%s" % data)
        elif self.declared_frames_dict.has_key(frame_id): # TAG not supported yet
            data = "<Not Decoded> TAG not supported yet"
            self.logger.warning("Data:\t\t\t%s" % data)
        else: # Unknown TAG
            data = "<Not Decoded> Unknown TAG"
            self.logger.warning("Data:\t\t\t%s", data)

    def isTextInfoFrame(self, frame_id): # Text information frames
        if  (self.declared_frames_dict.has_key(frame_id)) and (frame_id[0] == "T") and (frame_id != "TXXX"):
            return True
        else:
            return False

    def isUrlLinkFrame(self, frame_id): # URL link frames
        if  (self.declared_frames_dict.has_key(frame_id)) and (frame_id[0] == "W") and (frame_id != "WXXX"):
            return True
        else:
            return False

    def decodeText(self, data, sz):
        if sz == 0:
            return ""
        encoding_byte = data[0]
        if self.encoding_types_dict.has_key(encoding_byte):
            encoding_type = self.encoding_types_dict[encoding_byte]
        else:
            encoding_type = None # unspecified 'encoding_byte'

        # decode
        if encoding_type: # known encoding_type
            text = data[1:sz].decode(encoding_type)
        else:
            text = data[0:sz].decode('ascii') # ASCII (for unspecified 'encoding_byte')
        return text

    def encodeFrame(self, frame_id, data, tag_header_flags):
        data = self.encodePayload(frame_id, data)
        frame_header_flags = chr(0)+chr(0) # all flags: unset
        #  checking if Unsynchronisation is needed
        if (unsynchronisation_in_encoding_enabled) and (self.tag_unsynchronisation_enabled == False):
            unsyncd_data = self.unsynchronise(data)
            if len(data) != len(unsyncd_data):
                data = unsyncd_data
                # set 'Unsynchronisation', for the frame
                frame_header_flags = frame_header_flags[0] + chr(ord(frame_header_flags[1]) | 0x02)
        sz = self.encodeFrameSize(len(data))
        frame = frame_id+sz+frame_header_flags+data
        [frame_id, sz, frame_header_flags, data] = self.decodeFrame(frame)
        self.decodePayload(frame_id, tag_header_flags, frame_header_flags, data, sz)
        return frame

    def encodePayload(self, frame_id, opt):
        args = opt.split(',')
        if self.isTextInfoFrame(frame_id):
            if len(args) != 1:
                self.logger.critical("Invalid parameters for adding TAG:%s" % frame_id)
                error_msg = "Invalid parameters for adding TAG:%s" % frame_id
                raise Exception(1, error_msg)
            text_encoding = self.getEncByteForEncType(self.default_encoding_type)
            data = args[0].decode('utf-8').encode(self.default_encoding_type)
            encoded_data = text_encoding+data
        elif frame_id == "APIC":
            if (len(args) < 1) or (len(args) > 3):
                self.logger.critical("Invalid parameters for adding TAG:%s" % frame_id)
                error_msg = "Invalid parameters for adding TAG:%s" % frame_id
                raise Exception(1, error_msg)
            image = args[0]    # Image File
            if len(args) > 1:
                img_type = int(args[1])
            else:
                img_type = 3       # Default: Cover (front)

            if len(args) > 2:
                description = args[2].decode('utf-8')
            else:
                description = "" # Blank (Null)

            if self.picture_types_dict.has_key(img_type) == False:
                self.logger.warning("Unknown 'Picture type' : %d" % img_type)
                self.logger.warning("Defaulting to 3: Cover (front)")
                img_type = 3       # Default: Cover (front)

            text_encoding = self.getEncByteForEncType(self.default_encoding_type)
            str_terminator = self.getStrTerminatorForEncType(self.default_encoding_type)
            mime_type = "image/jpeg".encode('ascii')+self.getStrTerminatorForEncType('ascii') # MIME type is always 'ascii'
            pic_type = chr(img_type)   # Picture type'
            description = description.encode(self.default_encoding_type)+str_terminator
            pic_data = self.getImageData(image)
            encoded_data = text_encoding+mime_type+pic_type+description+pic_data
        elif frame_id == "COMM":
            if (len(args) < 1) or (len(args) > 2):
                self.logger.critical("Invalid parameters for adding TAG:%s" %frame_id)
                error_msg = "Invalid parameters for adding TAG:%s" %frame_id
                raise Exception(1, error_msg)
            data = args[0].decode('utf-8')
            if len(args) > 1:
                description = args[1].decode('utf-8')
            else:
                description = "" # Blank (Null)
            text_encoding = self.getEncByteForEncType(self.default_encoding_type)
            str_terminator = self.getStrTerminatorForEncType(self.default_encoding_type)
            language = "---".encode('ascii') # User dependent, cannot be determined
            short_content_description = description.encode(self.default_encoding_type)+str_terminator
            the_actual_text = data.encode(self.default_encoding_type)
            encoded_data = text_encoding+language+short_content_description+the_actual_text
        else:
            self.logger.critical("Unknown/ReadOnly TAG:%s" % frame_id)
            error_msg = "Unknown/ReadOnly TAG:%s" % frame_id
            raise Exception(1, error_msg)
        return encoded_data

    def decodeTagSz(self):
        # MSB of all bytes should be 0
        if ((ord(self.tag_header[6]) | ord(self.tag_header[7]) | ord(self.tag_header[8]) | ord(self.tag_header[9])) & 0x80) != False:
            self.logger.critical("Invalid TAG sz"); error_msg = "Invalid TAG sz"; raise Exception(1, error_msg)
        self.tag_sz = ((ord(self.tag_header[6]) << 21) + (ord(self.tag_header[7]) << 14) +\
                        (ord(self.tag_header[8]) << 7) + (ord(self.tag_header[9])))

    def encodeTagSz(self, sz):
        byte_3 = sz & 0x7F;   sz = sz >> 7
        byte_2 = sz & 0x7F;   sz = sz >> 7
        byte_1 = sz & 0x7F;   sz = sz >> 7
        byte_0 = sz & 0x7F;   sz = sz >> 7
        if sz > 0: self.logger.critical("TAG sz is too large"); error_msg = "TAG sz is too large"; raise Exception(1, error_msg)
        str_sz = chr(byte_0)+chr(byte_1)+chr(byte_2)+chr(byte_3)
        return str_sz

    def decodeFrameSize(self, data):
        sz = (ord(data[0]) << 24) + (ord(data[1]) << 16) + (ord(data[2]) << 8) + (ord(data[3]))
        return sz

    def encodeFrameSize(self, sz):
        byte_3 = sz & 0xFF;   sz = sz >> 8
        byte_2 = sz & 0xFF;   sz = sz >> 8
        byte_1 = sz & 0xFF;   sz = sz >> 8
        byte_0 = sz & 0xFF;   sz = sz >> 8
        if sz > 0: self.logger.critical("TAG sz is too large"); error_msg = "TAG sz is too large"; raise Exception(1, error_msg)
        str_sz = chr(byte_0)+chr(byte_1)+chr(byte_2)+chr(byte_3)
        return str_sz

    # data = (EncStr1+delimiter) + (EncStr2+delimiter) + ... + StrN
    # 'data' contains concatenated encoded-strings (EncStr1, EncStr2, ...) terminated according to Encoding-Type
    # and a last string (StrN) which may be encoded or a binary string.
    # This function splits 'data' and returns [EncStr1, EncStr2, ... , StrN]
    def splitNullTerminatedEncStrings(self, data, encoding_type, no_of_splits):
        data_dec = data.decode(encoding_type, 'ignore')
        chunks = data_dec.split('\x00', no_of_splits) # String-Terminator for decoded data is always '\x00'
        enc_str_lst = []
        for data_dec_seg in chunks[:-1]: # except last chunk
            enc_str_lst.append(data_dec_seg.encode(encoding_type)) # encoding and keeping in the list
        # to extracting the last segment:
        # reconstructing the string 'data_chunks' from chunks (except last chunk)
        data_dec_chunks = '\x00'.join(chunks[:-1])   # joining all chunks with '\x00' in-between
        if len(chunks[:-1]): data_dec_chunks += '\x00' # if chunks has atlest 2 elements, append '\x00'
        data_chunks = data_dec_chunks.encode(encoding_type) # this is the original string, except last segment
        data_chunks_len = len(data_chunks)
        enc_str_lst.append(data[data_chunks_len:]) # last segment
        return enc_str_lst

    # returns encoding_byte for a give encoding_type
    def getEncByteForEncType(self, encoding_type):
        # finding the 'encoding' byte
        encoding_byte = None # initialize
        for supported_encoder in self.encoding_types_dict:
            if self.encoding_types_dict[supported_encoder] == encoding_type: # matched
                encoding_byte = supported_encoder
                break
        return encoding_byte

    # returns string_terminator for a give encoding_type
    def getStrTerminatorForEncType(self, encoding_type):
        # finding 'String Terminator'
        if self.string_terminators_dict.has_key(encoding_type):
            string_terminator = self.string_terminators_dict[encoding_type]
        else:
            error_msg = "Unsupported String Terminator"
            raise Exception(1, error_msg)
        return string_terminator

    # returns string_terminator for a give encoding_byte
    def getStrTerminatorForEncByte(self, encoding_byte):
        # finding 'Encoding Type'
        if self.encoding_types_dict.has_key(encoding_byte):
            encoding_type = self.encoding_types_dict[encoding_byte]
        else:
            error_msg = "Illegal Encoding Byte"
            raise Exception(1, error_msg)
        # finding 'String Terminator'
        if self.string_terminators_dict.has_key(encoding_type):
            string_terminator = self.string_terminators_dict[encoding_type]
        else:
            error_msg = "Unsupported String Terminator"
            raise Exception(1, error_msg)
        return string_terminator

    # extract image data (resized), from image-file
    def getImageData(self, img_file):
        img_buf = StringIO.StringIO()
        img = Image.open(img_file)
        img = img.resize((640, 960), Image.NEAREST)
        self.logger.info("Image re-sized to 640x960")
        img.save(img_buf, "JPEG")
        data = img_buf.getvalue()
        return data

    def writeFile(self, file_name, data):
        fp = open(file_name, "wb")
        fp.write(data)
        fp.close()

    def disp(self, buf, sz): # For troubleshooting
        self.logger.debug("Displaying...")
        sz = min(sz, len(buf)) # limit "sz" to buf length
        indx = 0
        while indx < sz:
            self.logger.debug("%s %s %s" % (indx, binhex.binascii.hexlify(buf[indx]), buf[indx]))
            indx += 1

    def displayInteractiveHelp(self):
        self.logger.warning("\nInteractive-mode usage:")
        self.logger.warning("\tdel <frame-id>\t: to delete a frame")
        self.logger.warning("\tdel *\t: to delete all frames")
        self.logger.warning("\tlist <frame-id>\t: to list a frame")
        self.logger.warning("\tlist *\t: to list all frames")
        self.logger.warning("\tadd <frame-id> <data> ...\t: to add frames")
        self.logger.warning("\tsave\t: to save changes into the file")
        self.logger.warning("\thelp\t: to display this message")
        self.logger.warning("\tquit\t: to quit")

    # main control function
    def process(self, file_name, inp_buf, opts_dict, suffix):
        self.suffix = suffix
        # Validating ID3 Header
        syncd_tag_body = self.decodeHeader(inp_buf)

        self.logger.info("ID3v2/file identifier:\t%s" % self.id3_identifier)
        self.logger.info("ID3v2 version:\t\t0x%0.2x %0.2x" % (self.major_ver, self.revision_no))
        self.logger.info("ID3v2 flags:\t\t0x%0.2x" % self.tag_header_flags)
        self.logger.info("ID3v2 size:\t\t%d" % self.tag_sz)
        self.logger.info("**********************************\n")

        # Decoding Extended Header
        extended_header_flag = self.tag_header_flags & 0x40
        if extended_header_flag == 0:
            extended_header = ""
            extended_header_sz = 0
        else:
            [extended_header, extended_header_sz] = self.decodeExtendedHeader(syncd_tag_body)

        syncd_tag_body = syncd_tag_body[extended_header_sz:]

        frames_dict = self.extractFrames(syncd_tag_body)

        data_modified = False
        if opts_dict['delete_all']:
            self.removeAllFrames(frames_dict)
            data_modified = True

        if opts_dict['list']:
            self.dispAllFrames(frames_dict)

        for frame_id in opts_dict:
            if (opts_dict[frame_id] != None) and (self.write_opts_dict.has_key(frame_id)):
                self.removeFrame(frames_dict, frame_id)
                self.logger.warning("\nConstructing Frame: %s" % self.write_opts_dict[frame_id])
                self.logger.info("**********************************")
                self.appendFrame(frames_dict, self.write_opts_dict[frame_id],
                               self.encodeFrame(self.write_opts_dict[frame_id], opts_dict[frame_id], self.tag_header_flags))
                data_modified = True

        # interactive mode
        if opts_dict['interactive']: self.displayInteractiveHelp()
        while opts_dict['interactive']:
            try:
                line = raw_input("Enter your options: ")
                interactive_opts = shlex.split(line)
                if len(line) == 0: continue
                if interactive_opts[0] == "quit":
                    if (data_modified != True) or \
                       (raw_input("Changes not yet written, are you sure you want to exit (type: yes) : ") == "yes"):
                        data_modified = False # discarding changes
                        break
                elif interactive_opts[0] == "del":
                    if len(interactive_opts) == 1:
                        self.logger.warning("To delete a frame, type: del <frame-id>")
                        self.logger.warning("To delete all frames, type: del *")
                    elif interactive_opts[1] == "*":
                        self.removeAllFrames(frames_dict)
                        data_modified = True
                    else:
                        for frame in interactive_opts[1:]:
                            self.removeFrame(frames_dict, frame)
                            data_modified = True
                elif interactive_opts[0] == "list":
                    if len(interactive_opts) == 1:
                        self.logger.warning("To display a frame, type: list <frame-id>")
                        self.logger.warning("To display all frames, type: list *")
                    elif interactive_opts[1] == "*":
                        self.dispAllFrames(frames_dict)
                    else:
                        for frame_id in interactive_opts[1:]:
                            self.dispFrame(frames_dict, frame_id)
                elif interactive_opts[0] == "add":
                    if len(interactive_opts) < 3:
                        self.logger.warning("To add frames, type: add <frame-id-1> <data-1> <frame-id-2> <data-2> ...")
                    else:
                        #for frame_id, frame in pairwise(interactive_opts[1:]):
                        for frame_id, frame in  zip(interactive_opts[1::2], interactive_opts[2::2]):
                            if self.write_opts_dict.has_key(frame_id):
                                self.removeFrame(frames_dict, frame_id)
                                self.logger.warning("\nConstructing Frame: %s" % self.write_opts_dict[frame_id])
                                self.logger.info("**********************************")
                                self.appendFrame(frames_dict, self.write_opts_dict[frame_id], \
                                               self.encodeFrame(self.write_opts_dict[frame_id], \
                                                              frame, self.tag_header_flags))
                                data_modified = True
                            else:
                                self.logger.warning("\nFrame %s is not added" % frame_id)
                elif interactive_opts[0] == "dirty":
                    self.logger.warning("%s" %data_modified)
                elif interactive_opts[0] == "save":
                    if data_modified == True:
                        new_frames_buf = []
                        new_frames_buf.append(extended_header)
                        # construct modified tab_body
                        for frame_id in frames_dict: # for each TAG
                            for frame in frames_dict[frame_id]: # for each similar Frame (same TAG)
                                new_frames_buf.append(frame)
                        self.logger.warning("\nWriting changes into the file")
                        new_frames_buf.append('\x00' * 100) # Padding
                        new_frames = b"".join(new_frames_buf)
                        self.assignTagBody(new_frames)
                        new_buf = self.constructFile()
                        self.writeFile(file_name, new_buf)
                        data_modified = 0
                elif interactive_opts[0] == "help":
                    self.displayInteractiveHelp()
                else:
                    self.logger.warning("\nUnknown command")
            except IOError, err:
                self.logger.critical(str(err))
            except Exception as inst:
                self.logger.error("User Exception:")
                self.logger.error(inst.args)
            except:
                self.logger.critical(str(err))

        if data_modified == True:
            new_frames_buf = []
            new_frames_buf.append(extended_header)
            # construct modified tab_body
            for frame_id in frames_dict: # for each TAG
                for frame in frames_dict[frame_id]: # for each similar Frame (same TAG)
                    new_frames_buf.append(frame)
            self.logger.warning("\nWriting changes into the file")
            new_frames_buf.append('\x00' * 100) # Padding
            new_frames = b"".join(new_frames_buf)
            self.assignTagBody(new_frames)
            new_buf = self.constructFile()
            self.writeFile(file_name, new_buf)

        self.logger.warning("\n*** Done ***\n")

class TagEditorID3v2Major4(TagEditorID3v2Major3):
    "A ID3v2.4 tag editor"

    def __init__(self, logger):
        super(TagEditorID3v2Major4, self).__init__(logger)
        self.major_ver = 4
        self.tag_unsynchronisation_enabled = False
        self.default_encoding_type = 'utf-8' # choose from self.encoding_types_dict, used for creating/modifying Frames

        # added/updated: Supported "Encoding Byte":"Encoding Types"
        self.encoding_types_updates_dict = {
            '\x02'  : 'utf-16-be', # $02 - UTF-16BE encoded Unicode without BOM in ID3v2.4 only.
            '\x03'  : 'utf-8'      # $03 - UTF-8 encoded Unicode in ID3v2.4 only.
        }
        # Supported "Encoding Types":"String Terminator"
        self.string_terminators_updates_dict = {
            'utf-16-be' : '\x00'+'\x00', # $00 00 - UTF-16-BE
            'utf-8'     : '\x00'         # $00 - UTF-8
        }

        # added/updated: Declared/Supported Frames
        self.declared_frames_updates_dict = {
            'ASPI'  : 'Audio seek point index',
            'EQU2'  : 'Equalisation (2)',
            'RVA2'  : 'Relative volume adjustment (2)',
            'SEEK'  : 'Seek frame',
            'SIGN'  : 'Signature frame',
            'TDEN'  : 'Encoding time',
            'TDOR'  : 'Original release time',
            'TDRC'  : 'Recording time',
            'TDRL'  : 'Release time',
            'TDTG'  : 'Tagging time',
            'TIPL'  : 'Involved people list',
            'TMCL'  : 'Musician credits list',
            'TMOO'  : 'Mood',
            'TPRO'  : 'Produced notice',
            'TSOA'  : 'Album sort order',
            'TSOP'  : 'Performer sort order',
            'TSOT'  : 'Title sort order',
            'TSST'  : 'Set subtitle'
        }

        # added/updated: mapping 'option' to 'Frames', for adding/modifying Frames
        self.write_opts_updates_dict = {
            'year'  : 'TDRC'
        }

        # updating: Supported Encoding Types
        self.encoding_types_dict.update(self.encoding_types_updates_dict)
        # updating: String Terminators
        self.string_terminators_dict.update(self.string_terminators_updates_dict)
        # updating: Declared Frames List
        self.declared_frames_dict.update(self.declared_frames_updates_dict)
        # updating: mapping of options to frames
        self.write_opts_dict.update(self.write_opts_updates_dict)

    def decodeFrameSize(self, data):
        # MSB of all bytes should be 0
        if ((ord(data[0]) | ord(data[1]) | ord(data[2]) | ord(data[3])) & 0x80) != False:
            self.logger.critical("Invalid TAG sz"); error_msg = "Invalid TAG sz"; raise Exception(1, error_msg) #sys.exit(2);
        sz = ((ord(data[0]) << 21) + (ord(data[1]) << 14) + (ord(data[2]) << 7) + (ord(data[3])))
        return sz

    def encodeFrameSize(self, sz):
        byte_3 = sz & 0x7F;   sz = sz >> 7
        byte_2 = sz & 0x7F;   sz = sz >> 7
        byte_1 = sz & 0x7F;   sz = sz >> 7
        byte_0 = sz & 0x7F;   sz = sz >> 7
        if sz > 0: self.logger.critical("TAG sz is too large"); error_msg = "TAG sz is too large"; raise Exception(1, error_msg)
        str_sz = chr(byte_0) + chr(byte_1) + chr(byte_2) + chr(byte_3)
        return str_sz

class TagEditorID3v2(object):
    "A generic wrapper for ID3v2 tag editor"

    def __init__(self):
        self.logger = None

    def parse_args(self, inp_args):
        parser = argparse.ArgumentParser()

        parser.add_argument('-v', '--verbose', action='count')
        parser.add_argument('inp_file', action="store", nargs='+')

        group1 = parser.add_argument_group('to delete Frames')
        group1.add_argument('-D', '--delete-all', action='store_true', help='remove ID3v2 TAG')

        group2 = parser.add_argument_group('to list Frames')
        group2.add_argument('-l', '--list', action='store_true')

        group3 = parser.add_argument_group('to add/modify Frames')
        group3.add_argument('-t', '--title')
        group3.add_argument('-A', '--album')
        group3.add_argument('-a', '--artist')
        group3.add_argument('-c', '--comments', metavar='COMMENTS_INFO',
                        help='COMMENTS_INFO = <comments>[,<short content descrip.>]')
        group3.add_argument('-g', '--genre')
        group3.add_argument('-y', '--year')
        group3.add_argument('-T', '--track')
        group3.add_argument('-P', '--picture', metavar='ALBUM_ART_INFO',
                        help='ALBUM_ART_INFO = <image-file>[,<picture-type-integer>[,<description>]]')

        group4 = parser.add_argument_group('to interactively edit Frames')
        group4.add_argument('-i', '--interactive', action="store_true", default=False)

        opts_name_space = parser.parse_args(inp_args)
        opts_dict = vars(opts_name_space)
        return opts_dict

    def getVersionSpecificInstance(self, buf):
        tag_header = buf[0:0+10]
        id3_identifier = tag_header[0:0+3]
        if id3_identifier != "ID3":
            return TagEditorID3v2Major4(self.logger) # Will create the header of the latest ID3v2

        major_ver = ord(tag_header[3])
        if major_ver == 3:
            instance = TagEditorID3v2Major3(self.logger)
        elif major_ver == 4:
            instance = TagEditorID3v2Major4(self.logger)
        else: # others
            instance = None
            self.logger.critical("Unsupported ID3v2 Major Ver: %d" % major_ver)
        return instance

    def wrapper(self, args):
        # Setting a Logger
        self.logger = logging.getLogger('TagEditorID3v2 Logger') # create logger
        ch = logging.StreamHandler() # create console handler
        formatter = logging.Formatter('%(message)s') # create formatter
        ch.setFormatter(formatter) # add formatter to ch
        self.logger.addHandler(ch) # add ch to logger

        # parsing arguments
        opts_dict = self.parse_args(args)

        # verbosity
        if opts_dict['verbose'] >= 2:
            self.logger.setLevel(logging.INFO) #  set level to INFO
        elif (opts_dict['verbose'] == 1) or (opts_dict['list'] == True) or (opts_dict['interactive'] == True):
            self.logger.setLevel(logging.WARNING) #  set level to WARNING
        else:
            self.logger.setLevel(logging.ERROR) #  set default level

        try:
            # process for each file
            for inp_file_name in opts_dict['inp_file']:
                inp_fp = open(inp_file_name, 'rb')
                inp_buf = inp_fp.read()
                inp_fp.close()
                self.logger.warning("File Name: %s" % inp_file_name)
                suffix = os.path.basename(inp_file_name) # only basename
                self.logger.info("File Size: %d" %len(inp_buf))
                #self.logger.info("opts: %s" % opts_dict)
                self.logger.info("\n**********************************")
                versionSpecificInstance = self.getVersionSpecificInstance(inp_buf[0:10])
                if versionSpecificInstance:
                    versionSpecificInstance.process(inp_file_name, inp_buf, opts_dict, suffix)
        except IOError, err:
            self.logger.critical(str(err))
        except Exception as inst:
            self.logger.error("User Exception:")
            self.logger.error(inst.args)
        except:
            self.logger.critical(str(err))

def main(args):
    genericInstance = TagEditorID3v2()
    genericInstance.wrapper(args)

if __name__ == "__main__":
    main(sys.argv[1:])
