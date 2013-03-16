id3v2-tag-editor.py
===================

A command line editor for id3v2 tags. Written in python.

Status:
(1) Supported versions: id3v2.3, id3v2.4
(2) Supported frames (reading): Text info frames, URL link frames, APIC, PCNT, POPM, USLT, GEOB, MCDI, COMM, USER
(3) Supported frames (writing): artist, album, title, comments, genre, year, track no, jpeg-file
(4) Supported flags: 'Unsynchronisation', 'Data length indicator'
(5) While writing APIC frame, image is resize to (640,960), to save space
(6) Writes binary data of frames (APIC, GEOB, MCDI) into files in local directory
(7) Issues:(a) While modifying a frame, skips writing all similar frames into output file
               (It should skip frames with same 'Content type' only)
	   (b) Repetition of frames while reading/writing is not checked 
	   (b) Output file name hardcoded to "out.mp3"
	   (c) Other frames & flags need to be implemented

Note: usage is compatible with id3v2 linux utility, see usage() in the code
