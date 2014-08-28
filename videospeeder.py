#!/usr/bin/env python
#coding:utf-8
# Author:  Beining --<ACICFG>
# Contact: http://www.cnbeining.com/   |https://github.com/cnbeining/videospeeder
# Purpose: Acceletate video to bypass Letvcloud's transcode.
# Created: 08/28/2014
# LICENSE: GNU v2

import sys
import os
import os, sys, subprocess, shlex, re
from subprocess import call
import uuid
import math
import shutil
import getopt



#----------------------------------------------------------------------
def probe_file(filename):
    cmnd = ['ffprobe', '-show_format', '-pretty', '-loglevel', 'quiet', filename]
    p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #print filename
    out, err =  p.communicate()
    #print out
    if err:
        print err
        return None
    return out


#----------------------------------------------------------------------
def time_to_sec(time_raw):
    """
    str->int
    
    ignore .*."""
    time_list = time_raw.split(':')
    hr = int(time_list[0]) * 3600
    minute = int(time_list[1]) * 60
    sec = int(float(time_list[2]))
    return int(hr + minute + sec)

#----------------------------------------------------------------------
def get_abspath(filename):
    """"""
    return str(os.path.abspath(filename))

#----------------------------------------------------------------------
def process(filename, target_bitrate, speedtime, outputfile):
    """str,int,float,str->?
    filename,outputfile comes with the path."""
    tmpdir = '/tmp/videospeeder-' + str(uuid.uuid4())
    if not os.path.exists(tmpdir):
        os.makedirs(tmpdir)
    audio_format = ''
    audio_duration = ''
    video_duration_sec = 0
    video_size_byte = 0
    audio_bitrate = ''
    audio_duration_sec = 0
    audio_size_byte = 0
    video_format = ''
    video_duration = ''
    video_bitrate = ''
    #demux audio file
    print('INFO: Checking audio...')
    os.system('ffmpeg -i \'' + filename + '\' -vn -c:a copy ' + tmpdir+'/audio.aac' +' > /dev/null 2>&1')
    try:
        for line in probe_file(tmpdir+'/audio.aac').split('\n'):
            if 'format_name' in line:
                audio_format = str(line.split('=')[1])
            if 'duration' in line:
                audio_duration = str(line.split('=')[1])
    except:
        print('ERROR: Cannot read audio file!')
        shutil.rmtree(tmpdir)
        exit()
    #In case someone screw the audio up
    if not 'aac' in audio_format:
        print(audio_format)
        print('ERROR: You have to use AAC as audio format!')
        shutil.rmtree(tmpdir)
        exit()
    #Check original file
    try:
        for line in probe_file(filename).split('\n'):
            if 'duration' in line:
                video_duration = str(line.split('=')[1])
                #Sti. there's a tag called "totalduration"...
                break
    except:
        print('ERROR: Cannot read video file!')
        shutil.rmtree(tmpdir)
        exit()
    #Calc...
    #By bitrate
    if target_bitrate != 0:
        print('INFO: Doing calculation...')
        try:
            video_duration_sec = time_to_sec(video_duration)
            video_size_byte = int(os.path.getsize(filename))
            audio_duration_sec = time_to_sec(audio_duration)
            audio_size_byte = int(os.path.getsize(tmpdir+'/audio.aac'))
        except:
            print('ERROR: Cannot calculate time, did you input a bitrate too high?')
            shutil.rmtree(tmpdir)
            exit()
        try:
            os.remove(tmpdir+'/audio.aac')
            pass
        except:
            print('WARNING: Cannot remove the aac file now...')
        time_audio = float(((audio_size_byte * 8.0) / audio_duration_sec) / 1180000)
        time_video = float(((video_size_byte * 8.0) / video_duration_sec) / target_bitrate)
        if time_audio < 1 and time_video < 1:
            print('ERROR: Cannot calculate target, your target bitrate is higher than the original file!')
            shutil.rmtree(tmpdir)
            exit()
        if time_audio == 1 and time_video == 1:
            speedtime = 1.1
        elif time_audio > time_video:
            speedtime = time_audio
        else:
            speedtime = time_video
    #Make patch
    print('INFO: Adding ' + str(speedtime - 1) + ' times to audio...')
    py_path = sys.path[0]
    os.chdir(py_path)
    os.system('ffmpeg -i \'' + filename + '\'  -c copy ' + tmpdir+'/video.mkv' +'> /dev/null 2>&1')
    os.system('mkvextract timecodes_v2 '+ tmpdir + '/video.mkv 0:' + tmpdir +'/tc-track0.txt '+ '1:' + tmpdir +'/tc-track1.txt > /dev/null 2>&1')
    #Video
    f = open(tmpdir + '/tc-track0.txt', 'r')
    video_timecode = f.readlines()
    f.close()
    video_timecode_speed = '# timecode format v2' + '\n'
    for i in video_timecode[1:]:
        video_timecode_speed = video_timecode_speed + str(float(i.strip()) * speedtime) + '\n'
    f = open(tmpdir + '/video_timecode_speed.txt', 'w')
    f.write(video_timecode_speed)
    f.close()
    #Audio
    f = open(tmpdir + '/tc-track1.txt', 'r')
    audio_timecode = f.readlines()
    f.close()
    audio_timecode_speed = '# timecode format v2' + '\n'
    for i in audio_timecode[1:]:
        audio_timecode_speed = audio_timecode_speed + str(float(i.strip()) * speedtime) + '\n'
    f = open(tmpdir + '/audio_timecode_speed.txt', 'w')
    f.write(audio_timecode_speed)
    f.close()
    py_path = sys.path[0]
    os.chdir(py_path)
    print('INFO: Making patched mkv...')
    os.system('mkvmerge -o  ' + tmpdir + '/video_patched.mkv --timecodes 0:' + tmpdir + '/video_timecode_speed.txt  --timecodes 1:' + tmpdir + '/audio_timecode_speed.txt ' +tmpdir + '/video.mkv > /dev/null 2>&1')
    try:
        os.remove(tmpdir+'/video.mkv')
        pass
    except:
        print('WARNING: Cannot remove the temporary mkv file now...')
    print('INFO: Making final output file...')
    os.system('ffmpeg -i ' + tmpdir + '/video_patched.mkv -c copy  '+outputfile +'> /dev/null 2>&1')
    print('Done!')
    #clean up
    try:
        shutil.rmtree(tmpdir)
    except:
        print('ERROR: Cannot remove temp dir, do it by yourself!')

#----------------------------------------------------------------------
def usage():
    """"""
    print('''Usage:
    
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
        ''')


#----------------------------------------------------------------------
if __name__=='__main__':
    argv_list = []
    argv_list = sys.argv[1:]
    filename = ''
    target_bitrate = 0
    outputfile = ''
    speedtime = 3
    try:
        opts, args = getopt.getopt(argv_list, "hi:b:x:o:", ['help', 'input','bitrate', 'speedtime'
                                                           'outputfile'])
    except getopt.GetoptError:
        usage()
        exit()
    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
            exit()
        elif o in ('-i', '--input'):
            filename = a
            try:
                argv_list.remove('-i')
            except:
                break
        elif o in ('-b', '--bitrate'):
            target_bitrate = int(a)
            try:
                argv_list.remove('-b')
            except:
                break
        elif o in ('-x', '--speedtime'):
            speedtime = int(a)
            try:
                argv_list.remove('-x')
            except:
                break        
        elif o in ('-o', '--outputfile'):
            outputfile = a
            try:
                argv_list.remove('-o')
            except:
                break
    if filename == '':
        print('ERROR: No input file!')
        exit()
    if outputfile == '':
        outputfile = filename.split('.')[0]
        for i in filename.split('.')[1:-1]:
            outputfile = outputfile + '.' + i
        outputfile = outputfile + '.speed.mp4'
    process(filename, target_bitrate, speedtime, outputfile)
    exit()