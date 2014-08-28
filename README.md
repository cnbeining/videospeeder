videospeeder
============

Yet another video patch tool to bypass Letvcloud's encode by accelerating the video.

*WOULD LEAD TO QUALITY OTHER THAN YUANHUA UNABLE TO PLAY!!!*

Also check:
https://github.com/cnbeining/audioblacker , Audioblacker, the one that does not add time to video;

https://github.com/cnbeining/FlvPatcher , FlvPatcher's cnBeining's fork, the one uses VFR.

Requirement
-------

- Python 2.7
- ffmpeg
- ffprobe
- mkvextract
- mkvmerge
- Enough spare space: at least 3 times of the original file size.

Usage
------

Usage:
    
    python videospeeder.py (-h) (-i input.mp4) (-o output.mp4) (-b 0) (-x 3)
    
    -h: Default: None
        Help.
    
    -i: Default: Blank
        Input file.
        If the file and audioblacker are not under the same path,
        it is suggested to use absolute path to avoid possible failure.
    
    -o Default: input_filename.black.mp4
       Output file.
       Would be in the same folder with the original file if not specified.
       
    -b: Default: 0
        Target bitrate.
    
    -x: Default: 3
        Target speeding time.
        
    If bitrate is set, it will override the speeding time, if also set.
    Videospeeder will calculate both audio and video timing to make sure
    that both the audio and the video meets the requirments.
    
    Please notice that if your original video/audio bitrate is too small,
    Videospeeder would throw you an ERROR and quit.


Author
-----

Beining, http://www.cnbeining.com/

License
-----

GNUv2 license.

Misc
-----

- You are not supposed to refer/mention/promote this software at any service within Chinese Mainland.

- Thanks to @dantmnf 's help, without which this script would never be finished. Also enlightened by https://github.com/cnbeining/FlvPatcher/blob/master/3xspeed.sh  .

History
----

0.1: The very beginning
