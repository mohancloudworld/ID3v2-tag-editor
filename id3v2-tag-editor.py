#!/usr/bin/python
import os.path 
import sys
import binhex
import getopt
import Image
import StringIO

# Licence:  GPLv2 (GNU General Public License - version 2).
# Disclaimer: Use at your own risk.
# To know the status of this utility, refer to the README.

def usage():
	print "Usage: %s [options]... <mp3-file> " % (sys.argv[0])
	print "options: to add TAGs"
	print "\t-a <artist>"
	print "\t-A <album>"
	print "\t-t <title>"
	print "\t-c <comments>[,<short content descrip.>]"
	print "\t-g <genre>"
	print "\t-y <year>"
	print "\t-T <track no>"
	print "\t-P <jpeg-file>[,<picture type - integer>[,<description>]]"
	print "\t-l (optional) to list all TAGs"
	print	""
	print "\tNote:\t(1) Always write the data to out.mp3 file, even when just reading the TAGs"
	print "\t\t(2) Image is resize to (640,960), to save space"
	print "\t\t(3) Writes binary data of TAGs (APIC, GEOB, MCDI) into files in local directory"
	
	
def disp(buf, sz): # For troubleshooting
	print "Displaying..."
	tmp=0
	while tmp < sz:
		print tmp, binhex.binascii.hexlify(buf[tmp]), buf[tmp]
		tmp+=1

def decode_header(header):
	id3_identifier = header[0:0+3]
	if id3_identifier != "ID3":
		print "Invalid ID3 Header"
		sys.exit(2)
	id3_ver = header[3]
	if ( binhex.binascii.hexlify(id3_ver) == "FF") :
		print "Invalid Version: ",  binhex.binascii.hexlify(id3_ver)
		sys.exit(2)
	id3_rev = header[4]
	if ( binhex.binascii.hexlify(id3_rev) == "FF") :
		print "Invalid Version: ",  binhex.binascii.hexlify(id3_rev)
		sys.exit(2)
	header_flags = header[5]
	id3_tag_sz = decode_tag_sz(header[6:6+4])
	if( (ord(header_flags) & 0x1F ) !=  False):
		print "Invalid Flags in Header", binhex.binascii.hexlify(header_flags)
		sys.exit(2)
	return [id3_identifier, id3_ver, id3_rev, header[0:0+10], header_flags, id3_tag_sz]

def decode_extended_header(header, id3_rev):
	if ( ord(id3_rev) == 4 ) :
		extended_header_sz = ( (ord(header[0]) & 0x7F) << 24) + ( (ord(header[1]) & 0x7F) << 16) \
				+ ( (ord(header[2]) & 0x7F) << 8) + ( (ord(header[3]) & 0x7F) )
		extended_header = header[0:0+extended_header_sz]
		print "Extended Header, Not parsed"
	else:
		print "Has Extended Header, Not Implemented"
		sys.exit(2)
	return [extended_header, extended_header_sz]

def decode_frame(data, id3_ver):
	tag = data[0:0+4]
	if( tags_dict.has_key(tag) ):
		sz 	= decode_frame_sz(data[4:4+4], id3_ver)
		frame_flags = data[8:8+2]
		header_sz = 10
		data 	= data[header_sz:header_sz+sz]
		print "Frame ID:\t\t", tag,
		print ":", tags_dict[tag]
		print "Size:\t\t\t", sz
		print "Flags:\t\t\t", binhex.binascii.hexlify(frame_flags)
	else:
		sz 	= None
		frame_flags = None
		data 	= None
		header_sz = None
	return [tag, header_sz, sz, frame_flags, data]

def encode_frame(tag,data, id3_ver, header_flags):
	data 	= encode_payload(tag,data)
	sz  	= encode_frame_sz(len(data), id3_ver)
	frame_flags = chr(0)+chr(0)
	# Synchronisation
	if ( (ord(header_flags) & 0x80) != False): 
		data = unsynchronised(data)
	frame = tag+sz+frame_flags+data
	[tag, header_sz, sz, frame_flags, data] = decode_frame(frame, id3_ver)
	decode_payload(tag, header_flags, frame_flags, data, sz, id3_ver)	
	return frame

#---------------------------------------------------------------------
# Encoding Byte
#---------------------------------------------------------------------
# $00 - ISO-8859-1 (ASCII).
# $01 - UCS-2 in ID3v2.2 and ID3v2.3, UTF-16 encoded Unicode with BOM.
# $02 - UTF-16BE encoded Unicode without BOM in ID3v2.4 only.
# $03 - UTF-8 encoded Unicode in ID3v2.4 only.
#----------------------------------------------------------------------

def decode_text(data,sz):
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

def synchronised(data): # converting 0XFF00 => 0xFF
	indx = 0
	out_data = []
	while indx+1 < len(data) :
		if (data[indx] == '\xFF') and (data[indx+1] == '\x00'):
			out_data.append('\xFF') # remove 0x00 and proceed
			indx += 2
		else:
			out_data.append(data[indx]) # copy one byte and proceed
			indx += 1
	if (indx < len(data)):
		out_data.append(data[indx:]) # copy remaining bytes, if any
	return b"".join(out_data)
	
def unsynchronised(data): # converting 0XFF => 0xFF00
	indx = 0
	out_data = []
	while indx < len(data) :
		if (data[indx] == '\xFF'):
			out_data.append('\xFF'+'\x00') # add 0x00 and proceed
			indx += 1
		else:
			out_data.append(data[indx]) # copy one byte and proceed
			indx += 1
	if (indx < len(data)):
		out_data.append(data[indx:]) # copy remaining bytes, if any
	return b"".join(out_data)
	
def decode_payload(tag, header_flags, frame_flags, data, sz, id3_ver):
	# Handling 'Data length indicator'
	if ( (ord(frame_flags[1]) & 0x01) != False): 
		data_length_indicator = decode_frame_sz(data[0:0+4], id3_ver)
		print "Data_length_indicator:\t", data_length_indicator
		data=data[4:]
		sz -=4

	# Unsynchronisation
	if ( ((ord(header_flags) & 0x80) != False) or ( (ord(frame_flags[1]) & 0x02) != False)): 
			data= synchronised(data)
			
	if is_text_info_frame(tag):
		data = decode_text(data, len(data))
		chunks = data.split('\x00')	# '\x00' separated chunks
		chunk_indx = 0
		print "Data:\t\t\t", 	
		while chunk_indx < len(chunks): 
			print chunks[chunk_indx] + " ",
			chunk_indx +=1
		print ""
	elif(tag == "APIC"):
		text_encoding = binhex.binascii.hexlify(data[0])
		chunks = data[1:sz].split('\x00', 2)
		mime_type = decode_text(data[0]+chunks[0],len(data[0]+chunks[0]))
		picture_type = binhex.binascii.hexlify(chunks[1][0])
		picture_type_int = ord(chunks[1][0])
		description = decode_text(data[0]+chunks[1][1:],len(data[0]+chunks[1][1:]))
		img_data = chunks[2]; # image
		
		print "Text encoding\t\t", text_encoding
		print "MIME type:\t\t", mime_type
		print "Picture type:\t\t", "$", picture_type, ": " + picture_type_dict[int(picture_type)]
		print "Description:\t\t", description
		print "Data:\t\t\t<image>"
		
		file_name = suffix+":"+mime_type+":"+picture_type_dict[picture_type_int]+":"+description
		fp = open(file_name.replace("/", " "), "wb")
		fp.write(img_data)
		fp.close()
	elif(tag == "POPM"):
		chunks = data[0:0+sz].split('\x00', 1)
		email_to_user = decode_text(chunks[0],len(chunks[0]))
		rating = binhex.binascii.hexlify(chunks[1][0])
		print "Email to user:\t\t", email_to_user
		print "Rating:\t\t\t", rating
		chunk_indx = 1
		while chunk_indx < len(chunks[1]):
			print "Rating:\t", binhex.binascii.hexlify(chunks[1][chunk_indx])		
			chunk_indx +=1
	elif(tag == "USLT"):
		text_encoding = binhex.binascii.hexlify(data[0])
		language = binhex.binascii.hexlify(data[1])+binhex.binascii.hexlify(data[2])+binhex.binascii.hexlify(data[3])
		language_str = chr(ord(data[1]))+chr(ord(data[2]))+chr(ord(data[3]))
		chunks = data[4:sz].split('\x00', 1)
		content_descriptor = decode_text(data[0]+chunks[0],len(data[0]+chunks[0]))
		lyrics_text = decode_text(data[0]+chunks[1],len(data[0]+chunks[1]))
		print "Text encoding:\t\t", text_encoding
		print "Language:\t\t", language + " : " + language_str
		print "Content descriptor:\t", content_descriptor
		print "Lyrics/text:\t\t", lyrics_text
	elif(tag == "GEOB"):
		text_encoding = binhex.binascii.hexlify(data[0])
		chunks = data[1:sz].split('\x00', 3)
		mime_type = decode_text(chunks[0],len(chunks[0]))
		filename = decode_text(data[0]+chunks[1],len(data[0]+chunks[1]))
		content_description = decode_text(data[0]+chunks[2],len(data[0]+chunks[2]))
		data = chunks[3] # data
		print "Text encoding:\t\t", text_encoding
		print "MIME type:\t\t", mime_type
		print "Filename:\t\t", filename
		print "Content description:\t", content_description
		print "Encapsulated object:\t", "<binary data>"
		file_name = suffix+":"+":"+content_description+":"+filename+"."+mime_type
		fp = open(file_name.replace("/", " "), "wb")
		fp.write(data)
		fp.close()
	elif(tag == "MCDI"):
		cd_toc = data # data
		#print "CD TOC:\t\t\t", cd_toc # Not to Display
		print "CD TOC:\t\t\t", "<binary data>"
		file_name = suffix+"-"+"CD TOC"
		fp = open(file_name.replace("/", " "), "wb")
		fp.write(data)
		fp.close()
	elif(tag == "COMM"):
		text_encoding = binhex.binascii.hexlify(data[0])
		language = binhex.binascii.hexlify(data[1])+binhex.binascii.hexlify(data[2])+binhex.binascii.hexlify(data[3])
		language_str = chr(ord(data[1]))+chr(ord(data[2]))+chr(ord(data[3]))
		chunks = data[4:sz].split('\x00', 1)
		short_content_descrip = decode_text(data[0]+chunks[0],len(data[0]+chunks[0]))
		the_actual_text = decode_text(data[0]+chunks[1],len(data[0]+chunks[1]))
		print "Text encoding:\t\t", text_encoding
		print "Language:\t\t", language + " : " + language_str
		print "Short content descrip.:\t", short_content_descrip
		print "The actual text:\t", the_actual_text
	elif(tag == "USER"):
		text_encoding = binhex.binascii.hexlify(data[0])
		language = binhex.binascii.hexlify(data[1])+binhex.binascii.hexlify(data[2])+binhex.binascii.hexlify(data[3])
		language_str = chr(ord(data[1]))+chr(ord(data[2]))+chr(ord(data[3]))
		data = decode_text(data[0]+data[4:], len(data[0]+data[4:]))
		the_actual_text = data	
		print "Text encoding:\t\t", text_encoding
		print "Language:\t\t", language + " : " + language_str
		print "The actual text:\t", data	
	elif tags_dict.has_key(tag):
		data = decode_text(data, sz) # data
		print "Data:\t\t\t", data	
	else:
		data = "<Not Decoded>" # Unknown TAG
		print "Data:\t\t\t", data	
	
def encode_payload(tag,opt):
	args = opt.split(',')
	if (is_text_info_frame(tag)):
		if(len(args) != 1):
			print "Invalid parameters for adding TAG:", tag
			sys.exit(2)
		data = args[0]
		text_encoding = chr(0)	# $00 - ISO-8859-1 (ASCII).
		encoded_data  = text_encoding+data.encode('ascii')
	elif (tag == "APIC"):
		if(len(args) < 1) or (len(args) > 3):
			print "Invalid parameters for adding TAG:", tag
			sys.exit(2)
		img_file = args[0] 	# Image File
		if(len(args) > 1):
			img_type = int(args[1])
		else:
			img_type = 3 		# Default: Cover (front) 
				
		if(len(args) > 2):
			description = args[2]
		else:
			description = "" # Blank (Null)
		
		if picture_type_dict.has_key(img_type) == False:
			print "Unknown 'Picture type' : ", img_type
			sys.exit(2)
		text_encoding = chr(0)	# $00 - ISO-8859-1 (ASCII).
		mime_type = "image/jpeg".encode('ascii')+chr(0)
		pic_type = chr(img_type)	# Picture type'
		description = description.encode('ascii')+chr(0)	
		pic_data = get_img(img_file)
		encoded_data = text_encoding+mime_type+pic_type+description+pic_data
	elif (tag == "COMM"):
		if(len(args) < 1) or (len(args) > 2):
			print "Invalid parameters for adding TAG:", tag
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
		print "Unknown/ReadOnly TAG:", tag
		sys.exit(2)
	return encoded_data
	
def decode_tag_sz(data):
	if ( ((ord(data[0]) & 0x80) != False) or ((ord(data[1]) & 0x80) != False) or \
	     ((ord(data[2]) & 0x80) != False) or ((ord(data[3]) & 0x80) != False) ):
		print "Invalid TAG sz"
		sys.exit(2);
	sz = ( (ord(data[0]) << 21) + (ord(data[1]) << 14) + (ord(data[2]) << 7) + (ord(data[3])) )
	return sz

def encode_tag_sz(sz):
	byte_3 = sz & 0x7F
	sz = sz >> 7
	byte_2 = sz & 0x7F
	sz = sz >> 7
	byte_1 = sz & 0x7F
	sz = sz >> 7
	byte_0 = sz & 0x7F
	sz = sz >> 7
	if (sz > 0):
		print "TAG sz is too large"
		sys.exit(2);
	str_sz = chr(byte_0)+chr(byte_1)+chr(byte_2)+chr(byte_3)
	return str_sz

def decode_frame_sz(data, id3_ver):
	if ord(id3_ver) == 3:
		sz = (ord(data[0]) << 24) + (ord(data[1]) << 16) + (ord(data[2]) << 8) + (ord(data[3]))
	else:
		if ( ((ord(data[0]) & 0x80) != False) or ((ord(data[1]) & 0x80) != False) or\
			  ((ord(data[2]) & 0x80) != False) or ((ord(data[3]) & 0x80) != False) ):
			print "Invalid TAG sz"
			sys.exit(2);
		sz = ( (ord(data[0]) << 21) + (ord(data[1]) << 14) + (ord(data[2]) << 7) + (ord(data[3])) )
	return sz

def encode_frame_sz(sz, id3_ver):
	if ord(id3_ver) == 3:
		byte_3 = sz & 0xFF
		sz = sz >> 8
		byte_2 = sz & 0xFF
		sz = sz >> 8
		byte_1 = sz & 0xFF
		sz = sz >> 8
		byte_0 = sz & 0xFF
		sz = sz >> 8
	else:
		byte_3 = sz & 0x7F
		sz = sz >> 7
		byte_2 = sz & 0x7F
		sz = sz >> 7
		byte_1 = sz & 0x7F
		sz = sz >> 7
		byte_0 = sz & 0x7F
		sz = sz >> 7
	if (sz > 0):
		print "TAG sz is too large"
		sys.exit(2);
	str_sz =  chr(byte_0)+chr(byte_1)+chr(byte_2)+chr(byte_3)
	return str_sz

def get_img(img_file):
	buffer = StringIO.StringIO()
	img = Image.open(img_file)
	img = img.resize((640,960), Image.NEAREST)
	img.save(buffer,"JPEG")
	data= buffer.getvalue()
	print "img sz:", len(data)
	return data

def is_text_info_frame(tag): # Text information frames
	if( (tags_dict.has_key(tag)) and (tag[0] == "T") and (tag != "TXXX" )):
		return True
	else:
		return False

#---------------------------------------------------------------------
# Tags
#---------------------------------------------------------------------

tags_dict = {\
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
        'TDRL':'Release time',\
        \
        \
        \
        'TCMP':'(Unofficial) iTunes Compilation Flag',\
        'TSO2':'(Unofficial) iTunes uses this for Album Artist sort order',\
        'TSTU':'(Unofficial) Unknown, Added Temporarily',\
        \
        \
        \
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
       
picture_type_dict = {\
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
                  
opt_map = {'a':'TOPE',\
           'A':'TALB',\
           'AX':'TOAL',\
           't':'TIT2',\
           'c':'COMM',\
           'g':'TCON',\
           'yx':'TYER',\
           'y':'TDRC',\
           'T':'TRCK',\
           'P':'APIC'
           }

# *** Start of main() ***

if (len(sys.argv) <= 1):
		usage()
		sys.exit(2)
try:
	fp = open(sys.argv[-1], 'rb')
except IOError, err:
	print str(err) 
	usage()
	sys.exit(2)
ip_buf = fp.read()
fp.close()

try:
	opts, args = getopt.getopt(sys.argv[1:-1], 'a:A:t:c:g:y:T:P:l')
except getopt.GetoptError, err:
	print str(err) 
	usage()
	sys.exit(2)

print "File Name:", sys.argv[-1]
suffix = os.path.basename(sys.argv[-1]) # only basename
print "File Size:", len(ip_buf)
print "opts:", opts
print "args:", args

print "\n**********************************"

# Validating ID3 Header
[id3_identifier, id3_ver, id3_rev, header, header_flags, id3_tag_sz] = decode_header(ip_buf[0:])
print "ID3v2/file identifier:\t", id3_identifier
print "ID3v2 version:\t\t",binhex.binascii.hexlify(id3_ver), binhex.binascii.hexlify(id3_rev)
print "ID3v2 flags:\t\t" ,binhex.binascii.hexlify(header_flags)
print "ID3v2 size:\t\t", id3_tag_sz
print "**********************************\n"

# Decoding Extended Header
extended_header_flag = ord(header_flags) & 0x40
if (extended_header_flag == 0):
	extended_header = ""
	extended_header_sz = 0
else:
	[extended_header, extended_header_sz] = decode_extended_header(ip_buf[10:], id3_rev)
	
indx=10+extended_header_sz
id3_tag = ip_buf[0:id3_tag_sz+10]
song_data = ip_buf[id3_tag_sz+10:]

frames_buf = []
frames_buf.append(extended_header)
while (indx) < (id3_tag_sz+10):
	print "Index:\t\t\t", indx
	[tag, header_sz, sz, frame_flags, data] = decode_frame(id3_tag[indx:], id3_ver)
	#if  tags_dict.has_key(tag) == False:
	if  (tag == '\x00'+'\x00'+'\x00'+'\x00'): # tag == NULL+NULL+NULL+NULL
		break
	match = 0
	for opt in opts:
		if ( (opt_map.has_key(opt[0][1:])) and (tag == opt_map[opt[0][1:]]) ):
			match = 1
			print "Removing in out file"
			break
	if match == 0:
		frames_buf.append(id3_tag[indx:indx+header_sz+sz])
	decode_payload(tag, header_flags,frame_flags, data, sz, id3_ver)
	indx=indx+header_sz+sz
	print "----------------------------------"			
	
for opt in opts:
	if (opt_map.has_key(opt[0][1:])):
		print "\nAdding Frame:", opt_map[opt[0][1:]]
		frames_buf.append(encode_frame(opt_map[opt[0][1:]],opt[1], id3_ver, header_flags))

#frames_buf.append('\x00' * 100) # Padding
out_frames = b"".join(frames_buf)
new_buf = header[0:0+6]+encode_tag_sz(len(out_frames))+ out_frames + song_data
	
o_fp = open('./out.mp3', 'wb')
o_fp.write(new_buf)
o_fp.close()
	
print "\n*** Done ***\n" 
	
