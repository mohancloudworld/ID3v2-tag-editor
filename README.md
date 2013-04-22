id3v2-tag-editor.py
===================

A command line editor for id3v2 tags. Written in python.

Status:
(1) Supported versions: id3v2.3, id3v2.4
(2) Supported frames (reading): Text info frames, URL link frames, APIC, PCNT, POPM, USLT, GEOB, MCDI, COMM, USER
(3) Supported frames (writing): artist, album, title, comments, genre, year, track no, album-art(attached-picture) 
(4) Interactive-mode added
(5) Deleting of frames: 
    Can delete all frames at once. 
    In 'interactive-mode', can delete individual frames (only that are supported for 'writing')
(6) Supported flags: 'Unsynchronisation', 'Data length indicator'
(7) While writing APIC frame, image is resize to (640,960), to save space
(8) Writes binary data of frames (APIC, GEOB, MCDI) into files in local directory
(9) Multiple (two) levels of verbosity is supported
(10) Issues:(a) While modifying a frame, skips writing all other similar frames into output file
               (It should skip frames with same 'Content type' only)
	   (b) Repetition of frames while reading/writing is not checked 
	   (c) 'Data length indicator' flag is not used while writing frames 
	   (d) writing and deleting of frames is limited to only few types of frames 
	   (e) Other frames & flags need to be implemented

Note: usage is compatible with id3v2 linux utility
