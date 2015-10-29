#!/usr/bin/env python2.7

import spotify
import threading
from random import randint
from random import shuffle
import os
import thread
import time


class spotifyRPI(object):

    def __init__(self):
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n.....init...............")
        #os.system("sh /home/pi/sleepKill.sh &")
        os.system("sh /home/pi/showPic.sh /home/pi/heartBW_klein.jpg")
        self.logged_in_event = threading.Event()
        self.vtitelliste = []
        self.vtitelcounter = 0
        self.vconfig = spotify.Config()
        self.vconfig.user_agent = "raspberry pi"
        self.vconfig.device_id = "123456789"

        self.vsession = spotify.Session(config=self.vconfig)

        self.vsession.on(
            spotify.SessionEvent.END_OF_TRACK, self.end_track_listener)

        self.vsession.on(
            spotify.SessionEvent.CONNECTION_STATE_UPDATED,
            self.connection_state_listener)

        self.vaudio = spotify.AlsaSink(self.vsession)
        self.vloop = spotify.EventLoop(self.vsession)
        self.vloop.start()

        self.vsession.login('mistergonzo90', 'hundekuchen04')

        while not self.logged_in_event.wait(0.1):
            self.vsession.process_events()

        self.INIT = 0x00
        self.NOSONGS = 0x01
        self.PLAY = 0x02

        self.state = self.INIT
        if(int(self.vsession.connection.state) == 1):
            os.system("clear")
            print("...hat geklapp alter!!!")
            thread.start_new_thread(self.askTelegram, ())
            # thread.start_new_thread(self.eingabe,())

    def connection_state_listener(self, session):
        if session.connection.state is spotify.ConnectionState.LOGGED_IN:
            self.logged_in_event.set()

    def end_track_listener(self, session):
        if(self.state != self.NOSONGS):
            print('am arsch')    
            # self.vtitelcounter += 1
        self.playNextSong()
        self.state = self.NOSONGS

    def askTelegram(self):
        while(True):
            fil = open('/home/pi/yay.txt', 'a+b')
            if(fil):
                lastinput = fil.readlines()[-1].replace("\n", "").encode("utf8")
            if(lastinput != "zonk"):
                self.searchy(lastinput)
                fil.write("zonk\n")
            fil.close()
            # print to playlist.txt for telegram
            fil = open("/home/pi/playlist.txt", 'w')
            i = len(self.vtitelliste[self.vtitelcounter:])
            for song in reversed(self.vtitelliste[self.vtitelcounter:]):
                fil.write(str(i) + " " + song.name.encode("utf8") + "\n" + song.artists[0].name.encode("utf8") + "\n----------------\n")
                i -= 1
        # fil.write("wird noch ")
            fil.close()

            time.sleep(5)
    # thread.start_new_thread(self.askTelegram(),())

    def longSearch(self):
        try:
            vsucheingabe = raw_input('Welchen Kuenstler soll ich spielen, Sir ?').encode("utf8")
            if vsucheingabe:
                vsuche = self.vsession.search(str(vsucheingabe))
                vsuche.load()
                self.printArray(vsuche.artists, "artists")

                vartisteingabe = raw_input('welchen von denen, alter? ')
                if vartisteingabe.isdigit():
                    vartist = self.vsession.get_artist(
                        vsuche.artists[int(vartisteingabe)].link.uri)
                    print vartist.load().name

                    vartistbrowser = vartist.browse()
                    vartistbrowser.load()

                    valbums = vartistbrowser.albums

                    self.printArray(valbums, "albums")

                    valbumeingabe = raw_input('welches album solls sein, maeuschen? ')

                    if valbumeingabe.isdigit():
                        valbum = self.vsession.get_album(
                            valbums[int(valbumeingabe)].link.uri)
                        valbumbrowser = valbum.browse()
                        valbumbrowser.load()
                        vtracks = valbumbrowser.tracks

                        self.printArray(vtracks, "tracks")

                        vtiteleingabe = raw_input('track nummer? ')
                        if vtiteleingabe.isdigit():

                            self.vtitelcounter = int(vtiteleingabe)
                            self.vtitelliste = [t for t in vtracks]
                            print type(self.vtitelliste)
                            self.vsession.player.load(vtracks[int(vtiteleingabe)])
                            self.vsession.player.play()
                            self.playSong()
            else:
                print("kakkvogel")
        except IndexError:
            print("tomaten auf den augen oder watt?")
        else:
            pass
        finally:
            pass

    def playNextSong(self):
        self.vtitelcounter += 1
        self.playSong()

    def playSong(self):
        if self.vtitelcounter < len(self.vtitelliste):
            print('laeuft')
            self.state = self.PLAY
            self.vsession.player.load(
                self.vtitelliste[int(self.vtitelcounter)])
            self.vsession.player.play()
            print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
            print('______________________________')
            print('')
            print(self.vtitelliste[int(self.vtitelcounter)].artists[0].name)
            print(self.vtitelliste[int(self.vtitelcounter)].album.name)
            print(self.vtitelliste[int(self.vtitelcounter)].name)
            print('______________________________')
            print('\n\n\n\n\n\n\n\n\n\n\n\n')
        else:
            if(self.state != self.NOSONGS):
                self.state = self.NOSONGS
                os.system("sh /home/pi/showPic.sh /home/pi/franzl_knarre_klein.jpg")
                print "keine songs mehr alter lauch..."

    def showPic(self, path):
        os.system("fbi -noverbose -t 5 %s" % path)

    def eingabe(self):
        vsucheingabe = str(raw_input('?')).encode("utf8")
        if(vsucheingabe):
            self.searchy(vsucheingabe)
    # thread.start_new_thread(self.eingabe,())

    def searchy(self, vsucheingabe):
        if vsucheingabe in 's':
            self.longSearch()
        elif 's ' in vsucheingabe[:2]:
            vsuche = self.vsession.search(str(vsucheingabe[2:]))
            vsuche.load()
            if vsuche.artists:
                self.printArray(vsuche.artists, 'artists')
            if vsuche.albums:
                self.printArray(vsuche.albums, 'albums')
            if vsuche.tracks:
                self.printArray(vsuche.tracks, 'tracks')
            if vsuche.did_you_mean:
                self.printArray(vsuche.did_you_mean, 'did u mean')
        elif vsucheingabe in 'n':
            self.playNextSong()
        elif vsucheingabe in 'ls':
            self.printArray(self.vtitelliste[self.vtitelcounter:], "datt steht an")
        elif vsucheingabe in "latin":
            vsuche = self.vsession.search("roots of chicha")
            vsuche.load()
            self.vtitelliste = [t for t in vsuche.tracks]
            self.vtitelcounter = int(randint(0, len(self.vtitelliste)-1))
            self.playSong()
        elif vsucheingabe[-1] in '?':
            vsuche = self.vsession.search(str(vsucheingabe[:-1]))
            vsuche.load()
            self.vtitelliste = [t for t in vsuche.tracks]
            self.vtitelcounter = int(randint(0, len(self.vtitelliste)-1))
            self.playSong()
        elif vsucheingabe[-1] in '!':
            vsuche = self.vsession.search(str(vsucheingabe[:-1]), track_count=1)
            vsuche.load()
            if(vsuche.tracks):
                self.vtitelliste = [t for t in vsuche.tracks]
                self.vtitelcounter = 0
                valbumbrowser = vsuche.tracks[0].album.browse()
                valbumbrowser.load()
                vtracks = valbumbrowser.tracks
                [self.vtitelliste.append(t) for t in vtracks]
                self.playSong()
        elif vsucheingabe[-1] in '+':
            vsuche = self.vsession.search(str(vsucheingabe[:-1]))
            vsuche.load()
            self.vtitelliste.insert(self.vtitelcounter+1, vsuche.tracks[0])
        # self.vtitelcounter += 1
        # self.playSong()
        elif vsucheingabe[-1] in '@':
            vsuche = self.vsession.search(str(vsucheingabe[:-1]))
            vsuche.load()
            [self.vtitelliste.append(t) for t in vsuche.tracks]
        elif vsucheingabe in 'random':
            tempCurrSong = self.vtitelliste[self.vtitelcounter]
            self.vtitelliste = self.vtitelliste[self.vtitelcounter+1:]
            shuffle(self.vtitelliste)
            self.vtitelliste.insert(0, tempCurrSong)
            self.vtitelcounter = 0
        elif vsucheingabe in 'stop':
            self.vsession.player.pause()
        # thread.start_new_thread(self.showPic,("/home/pi/franzl_knarre_klein.jpg",))
        # os.system("rm /home/pi/yay.txt")
        else:
            vsuche = self.vsession.search(str(vsucheingabe))
            vsuche.load()
            if(vsuche.tracks):
                self.vtitelliste.append(vsuche.tracks[0])
                if(self.vsession.player.state.encode("utf8") in "unloaded" or self.vsession.player.state.encode("utf8") in "paused"):
                    self.playSong()

    def printArray(self, liste, listname):
        count = len(liste)-1
        print('')
        print(listname)
        print('______________________________')
        print('')
        for a in reversed(liste):
            print(str(count) + '...' + a.name)
            count -= 1
        print('______________________________')
    print('')

    def startThreads(self):
        thread.start_new_thread(self.askTelegram, ())
        thread.start_new_thread(self.eingabe, ())
        time.sleep(10)

if __name__ == '__main__':
    superPlayer = spotifyRPI()
    while True:
        # superPlayer.startThreads()
        superPlayer.eingabe()

