import speech_recognition as sr
import os
import re
import pyaudio
import sys
import webbrowser
import requests
import youtube_dl
import wikipedia
import random
import pyaudio
import pyttsx3
import time
import vlc
import datetime
import wolframalpha
from os.path import isdir, isfile, exists, basename
from re import search, IGNORECASE
from subprocess import Popen, run, PIPE
from sys import argv
import argparse
import logging
from magic import from_file
from twilio.rest import Client
from gtts import gTTS
import logging
import subprocess
import sys


def checkfor(args, rv=0):
    if isinstance(args, str):
        if ' ' in args:
            raise ValueError('no spaces in single command allowed')
        args = [args]
    try:
        rc = subprocess.call(args, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
        if rc != rv:
            raise OSError
        logging.info(f'found required program "{args[0]}"')
    except OSError as oops:
        logging.error(
            f'required program "{args[0]}" not found: {oops.strerror}.')
        sys.exit(1)


def wolfram(search):
    app_id = "53LKA6-QRALH3RGXQ"
    client = wolframalpha.Client(app_id)
    res = client.query(search)
    ans = next(res.results).text
    return ans


def response(audioString):
    print(audioString)
    tts = gTTS(text=audioString, lang='en')
    tts.save("audio.mp3")
    p = vlc.MediaPlayer("audio.mp3")
    p.play()


def myCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something!")
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source)
    try:
        command = r.recognize_google(audio).lower()
        print("You said: " + command)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print(
            "Could not request results from Google Speech Recognition service; {0}".format(e))
    return command


filetypes = {
    r'\.(pdf|epub)$': ['mupdf'],
    r'\.(txt|tex|md|rst|py|sh)$': ['gvim', '--nofork'],
    r'\.html$': ['firefox'],
    r'\.xcf$': ['gimp'],
    r'\.e?ps$': ['gv'],
    r'\.(jpe?g|png|gif|tiff?|p[abgp]m|bmp|svg)$': ['gpicview'],
    r'\.(pax|cpio|zip|jar|ar|xar|rpm|7z)$': ['tar', 'tf'],
    r'\.(tar\.|t)(z|gz|bz2?|xz)$': ['tar', 'tf'],
    r'\.(mp4|mkv|avi|flv|mpg|movi?|m4v|webm|vob)$': ['mpv'],
    r'\.(s3m|xm|mod|mid)$':
    ['urxvt', '-title', 'Timidity++', '-e', 'timidity', '-in', '-A30a']
}
othertypes = {'dir': ['rox'], 'txt': ['gvim', '--nofork']}


def assistant(command):
    print("I am here")
    if "open" in command:
        m = re.search('open(.+)', data)
        mi = m.group(1)
        mi = mi[1:]
        url = 'https://www.' + mi+'.com'
        print("Redirecting to", url)
        webbrowser.open(url)
        print("done")
        response(mi+" has been opened for you sir")
    elif 'time' in command:
        now = datetime.datetime.now()
        response('Current time is %d hours %d minutes' %
                 (now.hour, now.minute))
    elif 'song' in command:
        print("Playing a song")
        response('Which song sir enter name and duration of play')
        k = input()
        x = int(input())
        for i in os.listdir(os.getcwd()+'/songs'):
            if k in i:
                song = vlc.MediaPlayer('songs/'+i)
                song.play()
                timeout = time.time()+x
                print(timeout, time.time())
                while True:
                    if time.time() > timeout:
                        song.stop()
                        break
        print("song played")
    elif 'hello' in command:
        response('Hello nice to meet you again sir')
    elif 'encrypt' in command:
        response('Enter text')
        text = input()

    elif 'file' in command:
        response('Which file sir')
        files = myCommand()
        files = locate(files)
        for nm in files:
            logging.info(f"trying '{nm}'")
            if isdir(nm):
                cmds = othertypes['dir'] + [nm]
            elif isfile(nm):
                cmds = matchfile(filetypes, othertypes, nm)
            else:
                cmds = None
            if not cmds:
                logging.warning(f"do not know how to open '{nm}'")
                continue
            try:
                Popen(cmds)
            except OSError as e:
                print("failed")
    elif 'app' in command:
        response('Which app sir')
        appname = myCommand()
        if checkfor(appname):
            Popen("appname")
    elif 'hello' in command:
        response('Hello nice to meet you again sir')
    elif 'encrypt' in command:
        response('Enter text')
        text = input()

    elif 'hello' in command:
        response(random.choice(list(open('greetings.txt', 'r'))))
    elif 'joke' in command:
        print(random.choice(list(open('jokes.txt', 'r'))),
              "\U0001F923", "\U0001F923")
    elif 'photo' in command:
        os.system('streamer -f jpeg -o photos/pic.jpeg')
        response('Photo taken')
    elif 'list' in command:
        shopping_list = []
        response('What do you want to buy')
        response('Say done to stop adding')
        while True:
            item = myCommand()
            if item == 'done':
                break
            shopping_list.append(item)
        response('Here is yout list')
        for item in shopping_list:
            response(item)

    else:
        try:
            ans = wolfram(command)
            print(ans)
            response(ans)
        except:
            url = f"https://www.google.com/search?q={command}&source=lnms&sa=X&ved=0"
            webbrowser.open(url)


def matchfile(fdict, odict, fname):
    for k, v in fdict.items():
        if search(k, fname, IGNORECASE) is not None:
            return v + [fname]
    if b'text' in from_file(fname):
        return odict['txt'] + [fname]
    return None


def locate(args):
    files = []
    try:
        for nm in args:
            if exists(nm):
                files.append(nm)
            else:
                cp = run(['locate', nm], stdout=PIPE)
                paths = cp.stdout.decode('utf-8').splitlines()
                if len(paths) == 1:
                    files.append(paths[0])
                elif len(paths) == 0:
                    logging.warning(f"path '{nm}' not found")
                else:
                    # more than one path found.
                    basenames = []
                    for p in paths:
                        if basename(p) == nm:
                            basenames.append(p)
                            logging.info(f'found possible match "{p}"')
                    if len(basenames) == 1:
                        files.append(basenames[0])
                    else:
                        logging.warning(f"ambiguous path '{nm}' skipped")
                        for p in basenames:
                            logging.warning(f"found '{p}'")
    except FileNotFoundError:
        files = args
    return files


time.sleep(2)
response("Hi, what can I do for you?")
while 1:
    data = myCommand()
    assistant(data)
