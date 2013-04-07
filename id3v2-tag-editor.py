#!/usr/bin/python

# Licence:  GPLv2 (GNU General Public License - version 2).
# Disclaimer: Use at your own risk.
# To know the status of this utility, refer to the README.

import os.path 
import sys
import binhex
import getopt
import Image
import StringIO
import logging

# Music apps in mobile phone are not working with 'Unsynchronisation' flag, so set it to False
# Decoding with 'Unsynchronisation' flag is still enabled.
unsynchronisation_in_encoding_enabled = False
		
#class new_myModule3(object):
class TagEditorID3v2Major3(object):
	"A ID3v2.3 tag editor"
	
	def __init__(self):
		self.major_ver = 3
		self.is_global_unsynchronisation_flag_set = False # default
		# supported frames
		self.frames_dict = {\
			'AENC':'Audio encryption',\
			'APIC':'Attached picture',\
			'COMM':'Comments',\
			'COMR':'Commercial frame',\
			'ENCR':'Encryption method registration',\
			'EQUA':'Equalization',\
			'ETCO':'Event timing codes',\
			'GEOB':'General encapsulated object',\
			'GRID':'Group identification registration',\
			'IPLS':'Involved people list',\
			'LINK':'Linked information',\
			'MCDI':'Music CD identifier',\
			'MLLT':'MPEG location lookup table',\
			'OWNE':'Ownership frame',\
			'PRIV':'Private frame',\
			'PCNT':'Play counter',\
			'POPM':'Popularimeter',\
			'POSS':'Position synchronisation frame',\
			'RBUF':'Recommended buffer size',\
			'RVAD':'Relative volume adjustment',\
			'RVRB':'Reverb',\
			'SYLT':'Synchronized lyric/text',\
			'SYTC':'Synchronized tempo codes',\
			'TALB':'Album/Movie/Show title',\
			'TBPM':'BPM (beats per minute)',\
			'TCOM':'Composer',\
			'TCON':'Content type',\
			'TCOP':'Copyright message',\
			'TDAT':'Date',\
			'TDLY':'Playlist delay',\
			'TENC':'Encoded by',\
			'TEXT':'Lyricist/Text writer',
			'TFLT':'File type',\
			'TIME':'Time',\
			'TIT1':'Content group description',\
			'TIT2':'Title/songname/content description',\
			'TIT3':'Subtitle/Description refinement',\
			'TKEY':'Initial key',\
			'TLAN':'Language(s)',\
			'TLEN':'Length',\
			'TMED':'Media type',\
			'TOAL':'Original album/movie/show title',\
			'TOFN':'Original filename',\
			'TOLY':'Original lyricist(s)/text writer(s)',\
			'TOPE':'Original artist(s)/performer(s)',\
			'TORY':'Original release year',\
			'TOWN':'File owner/licensee',\
			'TPE1':'Lead performer(s)/Soloist(s)',\
			'TPE2':'Band/orchestra/accompaniment',\
			'TPE3':'Conductor/performer refinement',\
			'TPE4':'Interpreted, remixed, or otherwise modified by',\
			'TPOS':'Part of a set',\
			'TPUB':'Publisher',\
			'TRCK':'Track number/Position in set',\
			'TRDA':'Recording dates',\
			'TRSN':'Internet radio station name',\
			'TRSO':'Internet radio station owner',\
			'TSIZ':'Size',\
			'TSRC':'ISRC (international standard recording code)',\
			'TSSE':'Software/Hardware and settings used for encoding',\
			'TYER':'Year',\
			'TXXX':'User defined text information frame',\
			'UFID':'Unique file identifier',\
			'USER':'Terms of use',\
			'USLT':'Unsychronized lyric/text transcription',\
			'WCOM':'Commercial information',\
			'WCOP':'Copyright/Legal information',\
			'WOAF':'Official audio file webpage',\
			'WOAR':'Official artist/performer webpage',\
			'WOAS':'Official audio source webpage',\
			'WORS':'Official internet radio station homepage',\
			'WPAY':'Payment',\
			'WPUB':'Publishers official webpage',\
			'WXXX':'User defined URL link frame',\
			\
			\
			\
			'TCMP':'(Unofficial) iTunes Compilation Flag',\
			'TSO2':'(Unofficial) iTunes uses this for Album Artist sort order',\
			'TSTU':'(Unofficial) Unknown',\
		}
		
		# supported picture types in 'APIC' frames
		self.picture_type_dict = {\
			0x00 :'Other',\
			0x01 :'32x32 pixels \'file icon\' (PNG only)',\
			0x02 :'Other file icon',\
			0x03 :'Cover (front)',\
			0x04 :'Cover (back)',\
			0x05 :'Leaflet page',\
			0x06 :'Media (e.g. label side of CD)',\
			0x07 :'Lead artist/lead performer/soloist',\
			0x08 :'Artist/performer',\
			0x09 :'Conductor',\
			0x0A :'Band/Orchestra',\
			0x0B :'Composer',\
			0x0C :'Lyricist/text writer',\
			0x0D :'Recording Location',\
			0x0E :'During recording',\
			0x0F :'During performance',\
			0x10 :'Movie/video screen capture',\
			0x11 :'A bright coloured fish',\
			0x12 :'Illustration',\
			0x13 :'Band/artist logotype',\
			0x14 :'Publisher/Studio logotype'
		}          

		# mapping of option to frames, for writing in o/p
		self.write_opts_dict = {\
			'a':'TPE1',\
			'A':'TALB',\
			't':'TIT2',\
			'c':'COMM',\
			'g':'TCON',\
			'y':'TYER',\
			'T':'TRCK',\
			'P':'APIC'
		}

	def checkMajorVersion(self):
		if(self.major_ver != ord(self.tag_header[3])):
			logging.critical( "Unmatched Major version: %d" % ord(self.tag_header[3]))
			sys.exit(2)
		self = TagEditorID3v2Major3()
		

	def setRevisionNumber(self):
		self.revision_no = ord(self.tag_header[4])
		if(self.revision_no == 0xFF):
			versionSpecific.revision_no = None
			logging.critical( "Unsupported Revision Number: %d" % self.revision_no)
			sys.exit(2)
	
	def setHeaderFlags(self):
		self.tag_header_flags = ord(self.tag_header[5])
		if( (self.tag_header_flags & 0x1F ) !=  False):
			logging.critical( "Invalid Header Flags: 0x%.2x" % self.tag_header_flags)
			sys.exit(2)
		if ( (self.tag_header_flags & 0x80) != False):
			is_global_unsynchronisation_flag_set = True
		
		
	def decodeHeader(self, buf):
		self.tag_header = buf[0:0+10]
		self.id3_identifier = self.tag_header[0:0+3]
		if self.id3_identifier != "ID3":
			logging.critical( "Invalid ID3 Header")
			sys.exit(2)

		self.checkMajorVersion() # checking
		self.setRevisionNumber()
		self.setHeaderFlags()
		self.decodeTagSz()
		return [self.id3_identifier, self.major_ver, self.revision_no, self.tag_header, self.tag_header_flags, self.tag_sz]

	def decodeExtendedHeader(self, tag_body):
		extended_header_sz = self.decodeFrameSize(tag_body)
		extended_header = tag_body[0:0+extended_header_sz]
		logging.error( "Extended Header, Not parsed")
		return [extended_header, extended_header_sz]

	def decodeFrame(self, data):
		frame_id = data[0:0+4]
		if( self.frames_dict.has_key(frame_id) ):
			sz 	= self.decodeFrameSize(data[4:4+4])
			frame_header_flags = (ord(data[8]) << 8) + ord(data[9])
			frame_header_sz = 10
			data 	= data[frame_header_sz:frame_header_sz+sz]
			logging.info( "Frame ID:\t\t%s : %s" % (frame_id, self.frames_dict[frame_id]))
			logging.info( "Size:\t\t\t%d" % sz)
			logging.info( "Flags:\t\t\t0x%0.4x" % frame_header_flags)
		else:
			sz 	= None
			frame_header_flags = None
			data 	= None
			frame_header_sz = None
		return [frame_id, frame_header_sz, sz, frame_header_flags, data]

	def encodeFrame(self, frame_id, data, tag_header_flags):
		data 	= self.encode_payload(frame_id,data)
		frame_header_flags = chr(0)+chr(0) # all flags: unset
		#  checking if Unsynchronisation is needed
		if ( (self.major_ver != 3) and (unsynchronisation_in_encoding_enabled) ):
			unsync_data = self.unsynchronised(data)
			if ( len(data) != len(unsync_data)):
				data = unsync_data
				# set 'Unsynchronisation', for the frame
				frame_header_flags = frame_header_flags[0] + chr(ord(frame_header_flags[1]) | 0x02) 
		sz  	= self.encodeFrameSize(len(data))
		frame = frame_id+sz+frame_header_flags+data
		[frame_id, frame_header_sz, sz, frame_header_flags, data] = self.decodeFrame(frame)
		self.decodePayload(frame_id, tag_header_flags, frame_header_flags, data, sz)	
		return frame

	#---------------------------------------------------------------------
	# Encoding Byte
	#---------------------------------------------------------------------
	# $00 - ISO-8859-1 (ASCII).
	# $01 - UCS-2 in ID3v2.2 and ID3v2.3, UTF-16 encoded Unicode with BOM.
	#----------------------------------------------------------------------

	def decodeText(self, data,sz):
		if (sz == 0):
			return ""
		enc = data[0]
		if enc == chr(0): # ASCII
			text = data[1:sz].decode('ascii')
		elif enc == chr(1): # UTF-16
			bom = data[1:1+2]
			text = data[1:sz].decode('utf-16') # decoding along with BOM
		else:
			text = data[0:sz].decode('ascii') # ASCII (default)
		return text

	def synchronised(self, data): # converting 0xFF00 => 0xFF
		data = data.replace('\xFF'+'\x00', '\xFF')
		return data
	
	def unsynchronised(self, data): # converting 0xFF00 => 0xFF0000
		data = data.replace('\xFF', '\xFF'+'\x00')
		return data 
	
	def hasDataLengthIndicator(self, frame_header_flags):
		if ( (frame_header_flags & 0x01) != False):
			return True		
	
	def isFrameUnsynchronisationFlagSet(self, frame_header_flags):
		if ( (frame_header_flags & 0x02) != False):
			return True		
		
	def decodePayload(self, frame_id, tag_header_flags, frame_header_flags, data, sz):
		if self.major_ver != 3:
			# Handling 'Data length indicator'
			if ( self.hasDataLengthIndicator(frame_header_flags) == True): 
				data_length_indicator = self.decodeFrameSize(data[0:0+4])
				logging.info( "Data_length_indicator:\t%d" % data_length_indicator)
				data=data[4:]
				sz -=4
			# Unsynchronisation, only if not done globally (tag_header_flags)
			if ( (self.is_global_unsynchronisation_flag_set == False) or ( self.isFrameUnsynchronisationFlagSet(frame_header_flags) == True) ): 
				data= self.synchronised(data)
		
		if self.is_text_info_frame(frame_id):
			data = self.decodeText(data, len(data))
			data = data.replace('\x00', ' ') # to print, convert NULL seperated text to space seperated text
			logging.info( "Data:\t\t\t%s" % data)
		elif(frame_id == "TXXX"):
			text_encoding = binhex.binascii.hexlify(data[0])
			chunks = data[1:sz].split('\x00', 1)
			description = self.decodeText(data[0]+chunks[0],len(data[0]+chunks[0]))
			value = self.decodeText(data[0]+chunks[1],len(data[0]+chunks[1]))
			logging.info( "Text encoding:\t\t%s" % text_encoding)
			logging.info( "Description:\t\t%s" % description)
			logging.info( "Value:\t\t\t%s" % value)
			
		elif self.is_url_link_frame	(frame_id):
			# Yet to implement the following provision:
			#	If the text string is followed by a string termination, all the following
			#	information should be ignored and not be displayed.
			url = self.decodeText(data, len(data))
			logging.info( "URL:\t\t\t%s" % url)
		elif(frame_id == "WXXX"):
			text_encoding = binhex.binascii.hexlify(data[0])
			chunks = data[1:sz].split('\x00', 1)
			description = self.decodeText(data[0]+chunks[0],len(data[0]+chunks[0]))
			url = self.decodeText(chunks[1],len(chunks[1]))
			logging.info( "Text encoding:\t\t%s" % text_encoding)
			logging.info( "Description:\t\t%s" % description)
			logging.info( "URL:\t\t\t%s" % url)
		elif(frame_id == "APIC"):
			text_encoding = binhex.binascii.hexlify(data[0])
			chunks = data[1:sz].split('\x00', 2)
			mime_type = self.decodeText(data[0]+chunks[0],len(data[0]+chunks[0]))
			if (mime_type == ""): # MIME Type is ommited
				mime_type = "image/"
			picture_type = binhex.binascii.hexlify(chunks[1][0])
			picture_type_int = ord(chunks[1][0])
			description = self.decodeText(data[0]+chunks[1][1:],len(data[0]+chunks[1][1:]))
			image = chunks[2]; # image
		
			logging.info( "Text encoding\t\t%s" % text_encoding)
			logging.info( "MIME type:\t\t%s" % mime_type)
			logging.info( "Picture type:\t\t$%s : %s" % (picture_type, self.picture_type_dict[picture_type_int]))
			logging.info( "Description:\t\t%s" % description)
		
			if (mime_type == "-->"): # image link
				logging.info( "Data:\t\t\t%s" % image)
			else:
				if (len(mime_type.split("/")) == 2): img_type = mime_type.split("/")[1]
				else: img_type = ""
				file_name = self.suffix+":"+ self.picture_type_dict[picture_type_int]+":"+description+"."+img_type
				fp = open(file_name.replace("/", "|"), "wb")
				fp.write(image)
				fp.close()
				logging.info( "Data:\t\t\tWritten into file:%s" % file_name)
		elif(frame_id == "PCNT"):
			counter = data
			chunk_indx = 1
			logging.info( "Counter:\t\t\t", )
			while chunk_indx < len(counter):
				logging.info( "%s" % binhex.binascii.hexlify(counter[chunk_indx]),)
				chunk_indx +=1
			logging.info( "")
		elif(frame_id == "POPM"):
			chunks = data[0:0+sz].split('\x00', 1)
			email_to_user = self.decodeText(chunks[0],len(chunks[0]))
			rating = binhex.binascii.hexlify(chunks[1][0])
			logging.info( "Email to user:\t\t%s" % email_to_user)
			logging.info( "Rating:\t\t\t%s" % rating)
			chunk_indx = 1
			logging.info( "Counter:\t\t\t", )
			while chunk_indx < len(chunks[1]):
				logging.info( "%s" % binhex.binascii.hexlify(chunks[1][chunk_indx]),)
				chunk_indx +=1
			logging.info( "")
		elif(frame_id == "USLT"):
			text_encoding = binhex.binascii.hexlify(data[0])
			language = binhex.binascii.hexlify(data[1])+binhex.binascii.hexlify(data[2])+binhex.binascii.hexlify(data[3])
			language_str = chr(ord(data[1]))+chr(ord(data[2]))+chr(ord(data[3]))
			chunks = data[4:sz].split('\x00', 1)
			content_descriptor = self.decodeText(data[0]+chunks[0],len(data[0]+chunks[0]))
			lyrics_text = self.decodeText(data[0]+chunks[1],len(data[0]+chunks[1]))
			logging.info( "Text encoding:\t\t%s" % text_encoding)
			logging.info( "Language:\t\t%s : %s" % (language, language_str))
			logging.info( "Content descriptor:\t%s" % content_descriptor)
			logging.info( "Lyrics/text:\t\t%s" % lyrics_text)
		elif(frame_id == "GEOB"):
			text_encoding = binhex.binascii.hexlify(data[0])
			chunks = data[1:sz].split('\x00', 3)
			mime_type = self.decodeText(chunks[0],len(chunks[0]))
			filename = self.decodeText(data[0]+chunks[1],len(data[0]+chunks[1]))
			content_description = self.decodeText(data[0]+chunks[2],len(data[0]+chunks[2]))
			data = chunks[3] # data
			logging.info( "Text encoding:\t\t%s" % text_encoding)
			logging.info( "MIME type:\t\t%s" % mime_type)
			logging.info( "Filename:\t\t%s" % filename)
			logging.info( "Content description:\t%s" % content_description)
			file_name = self.suffix+":"+content_description+":"+filename+"."+mime_type
			fp = open(file_name.replace("/", "|"), "wb")
			fp.write(data)
			fp.close()
			logging.info( "Encapsulated object:\tWritten into file:%s" % file_name)
		elif(frame_id == "MCDI"):
			cd_toc = data # data
			#logging.info( "CD TOC:\t\t\t", cd_toc # Not to Display)
			file_name = self.suffix+":"+"CD TOC"
			fp = open(file_name.replace("/", "|"), "wb")
			fp.write(data)
			fp.close()
			logging.info( "CD TOC:\t\t\tWritten into file:%s" % file_name)
		elif(frame_id == "COMM"):
			text_encoding = binhex.binascii.hexlify(data[0])
			language = binhex.binascii.hexlify(data[1])+binhex.binascii.hexlify(data[2])+binhex.binascii.hexlify(data[3])
			language_str = chr(ord(data[1]))+chr(ord(data[2]))+chr(ord(data[3]))
			chunks = data[4:sz].split('\x00', 1)
			short_content_descrip = self.decodeText(data[0]+chunks[0],len(data[0]+chunks[0]))
			the_actual_text = self.decodeText(data[0]+chunks[1],len(data[0]+chunks[1]))
			logging.info( "Text encoding:\t\t%s" % text_encoding)
			logging.info( "Language:\t\t%s : %s" % (language, language_str))
			logging.info( "Short content descrip.:\t%s" % short_content_descrip)
			logging.info( "The actual text:\t%s" % the_actual_text)
		elif(frame_id == "USER"):
			text_encoding = binhex.binascii.hexlify(data[0])
			language = binhex.binascii.hexlify(data[1])+binhex.binascii.hexlify(data[2])+binhex.binascii.hexlify(data[3])
			language_str = chr(ord(data[1]))+chr(ord(data[2]))+chr(ord(data[3]))
			data = self.decodeText(data[0]+data[4:], len(data[0]+data[4:]))
			the_actual_text = data	
			logging.info( "Text encoding:\t\t%s" % text_encoding)
			logging.info( "Language:\t\t%s : %s" % (language, language_str))
			logging.info( "The actual text:\t%s" % data	)
		elif self.has_key(frame_id): # TAG not supported yet
			#data =self. decodeText(data, sz) # data
			data = "<Not Decoded> TAG not supported yet"
			logging.info( "Data:\t\t\t%s" % data	)
		else: # Unknown TAG
			data = "<Not Decoded> Unknown TAG" 
			logging.info( "Data:\t\t\t", data	)
	
	def encode_payload(self, frame_id,opt):
		args = opt.split(',')
		if (self.is_text_info_frame(frame_id)):
			if(len(args) != 1):
				logging.critical( "Invalid parameters for adding TAG:%s" % frame_id)
				sys.exit(2)
			#data =  args[0] #.decode('utf-8') #args[0]
			data =  args[0].decode('utf-8').encode('utf-8')
			text_encoding = chr(3) #0)	# $00 - ISO-8859-1 (ASCII).
			encoded_data  = text_encoding+data #.encode('ascii')
		elif (frame_id == "APIC"):
			if(len(args) < 1) or (len(args) > 3):
				logging.critical( "Invalid parameters for adding TAG:%s" % frame_id)
				sys.exit(2)
			image = args[0] 	# Image File
			if(len(args) > 1):
				img_type = int(args[1])
			else:
				img_type = 3 		# Default: Cover (front) 
				
			if(len(args) > 2):
				description = args[2]
			else:
				description = "" # Blank (Null)
		
			if self.picture_type_dict.has_key(img_type) == False:
				logging.critical( "Unknown 'Picture type' : %d" % img_type)
				sys.exit(2)
			text_encoding = chr(0)	# $00 - ISO-8859-1 (ASCII).
			mime_type = "image/jpeg".encode('ascii')+chr(0)
			pic_type = chr(img_type)	# Picture type'
			description = description.encode('ascii')+chr(0)	
			pic_data = self.get_img(image)
			encoded_data = text_encoding+mime_type+pic_type+description+pic_data
		elif (frame_id == "COMM"):
			if(len(args) < 1) or (len(args) > 2):
				logging.critical( "Invalid parameters for adding TAG:%s" %frame_id)
				sys.exit(2)
			data = args[0]
			if(len(args) > 1):
				description = args[1]
			else:
				description = "" # Blank (Null)
			text_encoding = chr(0)	# $00 - ISO-8859-1 (ASCII).
			language = "ENG".encode('ascii')
			short_content_description = description.encode('ascii')+chr(0)	# Blank (Null)
			the_actual_text  = data.encode('ascii')
			encoded_data = text_encoding+language+short_content_description+the_actual_text
		else:
			logging.critical( "Unknown/ReadOnly TAG:%s" % frame_id)
			sys.exit(2)
		return encoded_data
	
	def decodeTagSz(self):
		# MSB of all bytes should be 0
		if ( ( (ord(self.tag_header[6]) | ord(self.tag_header[7]) | ord(self.tag_header[8]) | ord(self.tag_header[9]) ) & 0x80) != False):
			logging.critical( "Invalid TAG sz");	sys.exit(2);
		self.tag_sz = ( (ord(self.tag_header[6]) << 21) + (ord(self.tag_header[7]) << 14) +\
		 					 (ord(self.tag_header[8]) << 7 ) + (ord(self.tag_header[9])) )
		
	def encodeTagSz(self, sz):
		byte_3 = sz & 0x7F;	sz = sz >> 7
		byte_2 = sz & 0x7F;	sz = sz >> 7
		byte_1 = sz & 0x7F;	sz = sz >> 7
		byte_0 = sz & 0x7F;	sz = sz >> 7
		if (sz > 0):	logging.critical( "TAG sz is too large");	sys.exit(2);
		str_sz = chr(byte_0)+chr(byte_1)+chr(byte_2)+chr(byte_3)
		return str_sz

	def decodeFrameSize(self, data):
		sz = (ord(data[0]) << 24) + (ord(data[1]) << 16) + (ord(data[2]) << 8) + (ord(data[3]))
		return sz

	def encodeFrameSize(self, sz):
		byte_3 = sz & 0xFF;	sz = sz >> 8
		byte_2 = sz & 0xFF;	sz = sz >> 8
		byte_1 = sz & 0xFF;	sz = sz >> 8
		byte_0 = sz & 0xFF;	sz = sz >> 8
		if (sz > 0):	logging.critical( "TAG sz is too large");	sys.exit(2);
		str_sz =  chr(byte_0)+chr(byte_1)+chr(byte_2)+chr(byte_3)
		return str_sz

	def get_img(self, img_file):
		buffer = StringIO.StringIO()
		img = Image.open(img_file)
		img = img.resize((640,960), Image.NEAREST)
		img.save(buffer,"JPEG")
		data= buffer.getvalue()
		logging.info( "img sz:%d" % len(data))
		return data

	def is_text_info_frame(self, frame_id): # Text information frames
		if( (self.frames_dict.has_key(frame_id)) and (frame_id[0] == "T") and (frame_id != "TXXX" )):
			return True
		else:
			return False

	def is_url_link_frame(self, frame_id): # URL link frames
		if( (self.frames_dict.has_key(frame_id)) and (frame_id[0] == "W") and (frame_id != "WXXX" )):
			return True
		else:
			return False

	def disp(self, buf, sz): # For troubleshooting
		logging.info( "Displaying...")
		tmp=0
		while tmp < sz:
			logging.debug( "%s %s %s" % (tmp, binhex.binascii.hexlify(buf[tmp]), buf[tmp]))
			tmp+=1

	# *** Start of main() ***
	def process(self, inp_buf	, opts, args, suffix):
		self.suffix = suffix
		org_frames_buf = []
		# Validating ID3 Header
		try:
			[id3_identifier, id3_ver, id3_rev, tag_header, tag_header_flags, tag_sz] = self.decodeHeader(inp_buf[0:])
		except Exception as inst:
			logging.error( "User Exception" )
			logging.error( inst.args )
			self.usage()
			sys.exit(2)		
		logging.info( "ID3v2/file identifier:\t%s" %id3_identifier)
		logging.info( "ID3v2 version:\t\t0x%0.2x %0.2x" % (id3_ver, id3_rev))
		logging.info( "ID3v2 flags:\t\t0x%0.2x" % tag_header_flags)
		logging.info( "ID3v2 size:\t\t%d" % tag_sz)
		logging.info( "**********************************\n")

		tag_body = inp_buf[len(tag_header):len(tag_header)+tag_sz]
		song_data = inp_buf[10+tag_sz:]

		# Unsynchronisation entire TAG (tag_header_flags)
		if ( (id3_ver == 3) and ( (tag_header_flags & 0x80) != False) ): 
			tag_body = self.synchronised(tag_body)
			tag_sz = len(tag_body)

		# Decoding Extended Header
		extended_header_flag = tag_header_flags & 0x40
		if (extended_header_flag == 0):
			extended_header = ""
			extended_header_sz = 0
		else:
			[extended_header, extended_header_sz] = self.decodeExtendedHeader(tag_body)

		indx=extended_header_sz

		org_frames_buf.append(extended_header)
		while (indx < tag_sz):
			logging.info( "Index:\t\t\t%d" % indx)
			[frame_id, frame_header_sz, sz, frame_header_flags, data] = self.decodeFrame(tag_body[indx:])
			if  (frame_id == '\x00'+'\x00'+'\x00'+'\x00'): # frame_id == NULL+NULL+NULL+NULL
				break
			match = 0
			for opt in opts:
				if ( (self.write_opts_dict.has_key(opt[0][1:])) and (frame_id == self.write_opts_dict[opt[0][1:]]) ):
					match = 1
					break
			self.decodePayload(frame_id, tag_header_flags,frame_header_flags, data, sz)
			if match == 0: org_frames_buf.append(tag_body[indx:indx+frame_header_sz+sz])
			else: logging.info( "Not writing this frame into output file")
			indx=indx+frame_header_sz+sz
			logging.info( "----------------------------------")			

		write_output = False
		new_frames_buf = []
		for opt in opts:
			if (self.write_opts_dict.has_key(opt[0][1:])):
				write_output = True 
				logging.info( "\nAdding Frame: %s" % self.write_opts_dict[opt[0][1:]])
				logging.info( "**********************************\n")
				new_frames_buf.append(self.encodeFrame(self.write_opts_dict[opt[0][1:]], opt[1], tag_header_flags))

		if (write_output == True):
			logging.warning( "\nWriting output into out.mp3")
			#new_frames_buf.append('\x00' * 100) # Padding
			org_frames = b"".join(org_frames_buf)
			new_frames = b"".join(new_frames_buf)
			#  checking if Unsynchronisation is needed
			if ( (id3_ver == 3) and ( ((tag_header_flags & 0x80 ) !=  False) or (unsynchronisation_in_encoding_enabled) ) ):
				unsync_new_frames = self.unsynchronised(new_frames)
				if ( len(new_frames) != len(unsync_new_frames)):
					new_frames = unsync_new_frames
					# set 'Unsynchronisation', for entire TAG (tag_header_flags)
					tag_header_flags = tag_header_flags | 0x80

			new_buf = tag_header[0:0+5] + chr(tag_header_flags) + self.encodeTagSz(len(org_frames)+len(new_frames)) + \
							org_frames + new_frames + song_data
			

			o_fp = open('./out.mp3', 'wb')
			o_fp.write(new_buf)
			o_fp.close()

		logging.info( "\n*** Done ***\n" )

class TagEditorID3v2Major4(TagEditorID3v2Major3):
	"A ID3v2.4 tag editor"
	
	def __init__(self):
		super(TagEditorID3v2Major4, self).__init__()
		self.major_ver = 4
		# added/updated frames 
		self.frames_updates_dict = {\
			'ASPI':'Audio seek point index',\
			'EQU2':'Equalisation (2)',\
			'RVA2':'Relative volume adjustment (2)',\
			'SEEK':'Seek frame',\
			'SIGN':'Signature frame',\
			'TDEN':'Encoding time',\
			'TDOR':'Original release time',\
			'TDRC':'Recording time',\
			'TDRL':'Release time',\
			'TDTG':'Tagging time',\
			'TIPL':'Involved people list',\
			'TMCL':'Musician credits list',\
			'TMOO':'Mood',\
			'TPRO':'Produced notice',\
			'TSOA':'Album sort order',\
			'TSOP':'Performer sort order',\
			'TSOT':'Title sort order',\
			'TSST':'Set subtitle'
		}

		# added/updated mapping of options to frames, for writing in o/p
		self.write_opts_updates_dict = {\
			'y':'TDRC'
		}

		# updating the frames List
		self.frames_dict.update(self.frames_updates_dict)
		# updating mapping of options to frames
		self.write_opts_dict.update(self.write_opts_updates_dict)
					
	def decodeFrameSize(self, data):
		# MSB of all bytes should be 0
		if ( ( (ord(data[0]) | ord(data[1]) | ord(data[2]) | ord(data[3]) ) & 0x80) != False):
			logging.critical( "Invalid TAG sz");	sys.exit(2);
		sz = ( (ord(data[0]) << 21) + (ord(data[1]) << 14) + (ord(data[2]) << 7) + (ord(data[3])) )
		return sz

	def encodeFrameSize(self, sz):
		byte_3 = sz & 0x7F;	sz = sz >> 7
		byte_2 = sz & 0x7F;	sz = sz >> 7
		byte_1 = sz & 0x7F;	sz = sz >> 7
		byte_0 = sz & 0x7F;	sz = sz >> 7
		if (sz > 0): logging.critical( "TAG sz is too large");	sys.exit(2);
		str_sz =  chr(byte_0)+chr(byte_1)+chr(byte_2)+chr(byte_3)
		return str_sz

	#---------------------------------------------------------------------
	# Encoding Byte
	#---------------------------------------------------------------------
	# $00 - ISO-8859-1 (ASCII).
	# $01 - UCS-2 in ID3v2.2 and ID3v2.3, UTF-16 encoded Unicode with BOM.
	# $02 - UTF-16BE encoded Unicode without BOM in ID3v2.4 only.
	# $03 - UTF-8 encoded Unicode in ID3v2.4 only.
	#----------------------------------------------------------------------

	def decodeText(self, data, sz):
		if (sz == 0):
			return ""
		enc = data[0]
		if enc == chr(0): # ASCII
			text = data[1:sz].decode('ascii')
		elif enc == chr(1): # UTF-16
			bom = data[1:1+2]
			text = data[1:sz].decode('utf-16') # decoding along with BOM
		elif enc == chr(2): # UTF-16BE
			text = data[1:sz].decode('utf-16-be') 
		elif enc == chr(3): # UTF-8
			text = data[1:sz].decode('utf-8') 
		else:
			text = data[0:sz].decode('ascii') # ASCII (default)
		return text
	
class TagEditorID3v2(object):
	"A generic wrapper for ID3v2 tag editor"
	
	def usage(self):
		logging.critical( "Usage: %s [options]... <mp3-file> " % (sys.argv[0]))
		logging.critical( "options: to add TAGs")
		logging.critical( "\t-a <artist>")
		logging.critical( "\t-A <album>")
		logging.critical( "\t-t <title>")
		logging.critical( "\t-c <comments>[,<short content descrip.>]")
		logging.critical( "\t-g <genre>")
		logging.critical( "\t-y <year>")
		logging.critical( "\t-T <track no>")
		logging.critical( "\t-P <jpeg-file>[,<picture type - integer>[,<description>]]")
		logging.critical( "\t-l (optional) to list all TAGs")
		logging.critical(	"")
		logging.critical( "\tNote:\t(1) Output file name hardcoded to \"out.mp3\"")
		logging.critical( "\t\t(2) Image is resize to (640,960), to save space")
		logging.critical( "\t\t(3) Writes binary data of frames (APIC, GEOB, MCDI) into files in local directory")
	
	def getVersionSpecificInstance(self, buf):
		tag_header = buf[0:0+10]
		id3_identifier = tag_header[0:0+3]
		if id3_identifier != "ID3":
			logging.critical( "Invalid ID3 Header")
			self.usage()
			sys.exit(2)

		major_ver = ord(tag_header[3])
		if (major_ver == 3):
			instance = TagEditorID3v2Major3()
		elif (major_ver == 4):
			instance = TagEditorID3v2Major4()
		else: # others
			instance = None
			logging.critical( "Unsupported ID3v2 Major Ver: %d" % major_ver)
			self.usage()
			sys.exit(2)
		return instance
	
	def wrapper(self, argv):
		logging.basicConfig( stream=sys.stdout, format='%(message)s', level=logging.WARNING)
		if (len(argv) < 2):
				self.usage()
				sys.exit(2)
		inp_file_name = argv[-1] # last argument
		try:
			inp_fp = open(inp_file_name, 'rb')
		except IOError, err:
			logging.info( str(err) )
			self.usage()
			sys.exit(2)
		inp_buf = inp_fp.read()
		inp_fp.close()

		try:
			opts, args = getopt.getopt(argv[1:-1], 'a:A:t:c:g:y:T:P:l')
		except getopt.GetoptError, err:
			logging.info( str(err) )
			self.usage()
			sys.exit(2)
		
		# change verbosity , if '-l' is mentioned
		if (("-l","") in opts): 
			logging.getLogger().setLevel( level=logging.INFO)
		
		logging.info( "File Name: %s" % inp_file_name)
		suffix = os.path.basename(inp_file_name) # only basename
		logging.info( "File Size: %d" %len(inp_buf))
		logging.info( "opts: %s" % opts)
		logging.info( "args: %s" % args)
		logging.info( "\n**********************************")
		versionSpecificInstance = self.getVersionSpecificInstance(inp_buf[0:10])
		versionSpecificInstance.process(inp_buf, opts, args, suffix)
		
def main():
	genericInstance = TagEditorID3v2()
	genericInstance.wrapper(sys.argv)

if __name__ == "__main__":
    main()
