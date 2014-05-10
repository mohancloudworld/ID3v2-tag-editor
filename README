# Welcome to the ID3v2-tag-editor

* ID3v2-tag-editor is a command line editor for Id3v2 metadata for audio (MP3) files 
* Supported versions: Id3v2.3 and Id3v2.4
* It has two modes of operation (a) Command-line mode (b) Interactive mode
* Supported frames for reading: Text info frames, URL link frames, APIC, PCNT, POPM, USLT, GEOB, MCDI, COMM, USER
* Supported frames for writing: artist, album, title, comments, genre, year, track no, album-art (attached-picture) 
* Deletion of frames: 
    (a) Can delete all frames at once. 
    (b) In 'Interactive-mode', can delete individual frames (only that are supported for 'writing')
* Supported flags: 'Unsynchronisation', 'Data length indicator'
* While writing album-art info (APIC frame), image is re-sized to (640,960), to save space
* Multiple (two) levels of verbosity is supported
* In verbose (-vv) mode, to display frames with binary data (APIC, GEOB, MCDI), the data is written into files in local directory. In all other modes, binary data is skipped.
* Most of the user input is parsed as unicode-data, so user can feed information in multiple languages
* The usage is compatible with "id3v2" linux utility

## **Known Issues:**

* While modifying a frame, skips writing all other similar frames into output file
(It should skip frames with same 'Content type' only)
* Repetition of frames while reading/writing is not checked 
* 'Data length indicator' flag is not used while writing frames 
* writing and deleting of frames is limited to only few types of frames 
* Other frames & flags need to be implemented

## **Usage:**

usage: id3v2-tag-editor.py [-h] [-v] [-D] [-l] [-t TITLE] [-A ALBUM]
                           [-a ARTIST] [-c COMMENTS_INFO] [-g GENRE] [-y YEAR]
                           [-T TRACK] [-P ALBUM_ART_INFO] [-i]
                           inp_file [inp_file ...]

for more detail usage info type:
<pre><code>./id3v2-tag-editor.py --help</code></pre>

### **Command-line mode:**
To display all the ID3v2 frames in a file, use option -l or --list.
<pre><code>./id3v2-tag-editor.py -l inp_file</code></pre>

To increase the verbosity of the display, use "-vv" option.
<pre><code>./id3v2-tag-editor.py -l -vv inp_file</code></pre>

To display all the ID3v2 frames in multiple files, add all files to the command-line.
<pre><code>./id3v2-tag-editor.py -l inp_file1 inp_file2 ...</code></pre>

To add/modify title frame of a file, use option -t or --title.
<pre><code>./id3v2-tag-editor.py -t TITLE inp_file</code></pre>

To add/modify album-art-info frame of a file, use option -P or --picture. 
<pre><code>./id3v2-tag-editor.py --picture IMAGE inp_file</code></pre>
<pre><code>./id3v2-tag-editor.py -P IMAGE,IMAGE-TYPE,IMAGE-DESCRIPTION inp_file</code></pre>

To add/modify multiple frames of a file, concatenate the options. Refer to "usage" info for all such editable frames.
<pre><code>./id3v2-tag-editor.py -t TITLE -A ALBUM inp_file</code></pre>

To delete all the ID3v2 frames in a file, use option -D or --delete-all.
<pre><code>./id3v2-tag-editor.py -D inp_file</code></pre>

### **Interactive mode:**
In this mode, user can interactively list, add/modify and delete (all or individual) frames. Can save changes and/or exit at any desired state.   
To enter into interactive mode, use option -i or --interactive.
<pre><code>./id3v2-tag-editor.py -i inp_file</code></pre>

