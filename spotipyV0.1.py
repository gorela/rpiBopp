#!/usr/bin/env python2.7

import spotify
import threading
from random import randint
from random import shuffle
import os
import thread
import time


class spotifyRPI(object):

    # initialises when spotifyRPI class is called,
    # e.g:
    # > rpyb = spotifyRPI()
    # upon calling rpyb:
    # print..., os.system(...), rpyb.logged_in_event, rpyb.titelliste,etc are called or defined
    def __init__(self):
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n.....init...............")
        #os.system("sh /home/pi/sleepKill.sh &")
        os.system("sh /home/pi/showPic.sh /home/pi/heartBW_klein.jpg")
        self.logged_in_event = threading.Event()
        self.titelliste = []
        self.titelcounter = 0
        self.config = spotify.Config()
        self.config.user_agent = "raspberry pi"
        self.config.device_id = "123456789"

        # Important; is used a lot to hand the session to spotify as a prefix
        # and is therefore abbreviated to .session
        self.session = spotify.Session(config=self.config)

        self.session.on(
            spotify.SessionEvent.END_OF_TRACK, self.end_track_listener)

        self.session.on(
            spotify.SessionEvent.CONNECTION_STATE_UPDATED,
            self.connection_state_listener)

        # Audio sink for delivery of the PCM audio frames to your OS
        self.audio = spotify.AlsaSink(self.session)

        # @gorela:
        # "Note that when using EventLoop, your event listener functions
        # are called from the EventLoop thread, and not from your main thread.
        # You may need to add synchronization primitives to protect your
        # application code from threading issues."
        # aus: https://pyspotify.mopidy.com/en/latest/quickstart/
        # ganz unten im quickstart guide steht noch ausführlicher was dazu
        self.loop = spotify.EventLoop(self.session)
        self.loop.start()

        self.session.login('mistergonzo', 'hundekuchen')

        # @gorela wurde das nicht schon durch das loop oben erreicht?:

        # >while not self.logged_in_event.wait(0.1):
        # >    self.session.process_events()

        # State machine for different playback scenarios!
        self.INIT = 0x00
        self.NOSONGS = 0x01
        self.PLAY = 0x02

        self.state = self.INIT
        if(int(self.session.connection.state) == 1):
            os.system("clear")
            print("...hat geklapp alter!!!")
            thread.start_new_thread(self.askTelegram, ())
            # thread.start_new_thread(self.eingabe,())

    def connection_state_listener(self, session):
        if session.connection.state is spotify.ConnectionState.LOGGED_IN:
            self.logged_in_event.set()

    # @gorela: wieso übergibt man hier die session,
    # obwohl 'session' nicht benutzt wird?
    def end_track_listener(self, session):
        if(self.state != self.NOSONGS):
            print('am arsch')
            # self.titelcounter += 1
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
            i = len(self.titelliste[self.titelcounter:])
            for song in reversed(self.titelliste[self.titelcounter:]):
                fil.write(str(i) + " " + song.name.encode("utf8") + "\n" + song.artists[0].name.encode("utf8") + "\n----------------\n")
                i -= 1
        # fil.write("wird noch ")
            fil.close()

            time.sleep(5)
    # thread.start_new_thread(self.askTelegram(),())

    def longSearch(self):
        try:
            sucheingabe = raw_input('Welchen Kuenstler soll ich spielen, Sir ?').encode("utf8")
            if sucheingabe:
                suche = self.session.search(str(sucheingabe))
                suche.load()
                self.printArray(suche.artists, "artists")

                artisteingabe = raw_input('welchen von denen, alter? ')
                if artisteingabe.isdigit():
                    artistt = self.session.get_artist(
                        suche.artists[int(artisteingabe)].link.uri)
                    print artistt.load().name

                    artisttbrowser = artistt.browse()
                    artisttbrowser.load()

                    albums = artisttbrowser.albums

                    self.printArray(albums, "albums")

                    albumeingabe = raw_input('welches album solls sein, maeuschen? ')

                    if albumeingabe.isdigit():
                        album = self.session.get_album(
                            albums[int(albumeingabe)].link.uri)
                        albumbrowser = album.browse()
                        albumbrowser.load()
                        tracks = albumbrowser.tracks

                        self.printArray(tracks, "tracks")

                        titeleingabe = raw_input('track nummer? ')
                        if titeleingabe.isdigit():

                            self.titelcounter = int(titeleingabe)
                            self.titelliste = [t for t in tracks]
                            print type(self.titelliste)
                            self.session.player.load(tracks[int(titeleingabe)])
                            self.session.player.play()
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
        self.titelcounter += 1
        self.playSong()

    def playSong(self):
        if self.titelcounter < len(self.titelliste):
            print('laeuft')
            self.state = self.PLAY
            self.session.player.load(
                self.titelliste[int(self.titelcounter)])
            self.session.player.play()
            print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
            print('______________________________')
            print('')
            print(self.titelliste[int(self.titelcounter)].artists[0].name)
            print(self.titelliste[int(self.titelcounter)].album.name)
            print(self.titelliste[int(self.titelcounter)].name)
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
        sucheingabe = str(raw_input('?')).encode("utf8")
        if(sucheingabe):
            self.searchy(sucheingabe)
    # thread.start_new_thread(self.eingabe,())

    def searchy(self, sucheingabe):
        if sucheingabe in 's':
            self.longSearch()
        elif 's ' in sucheingabe[:2]:
            suche = self.session.search(str(sucheingabe[2:]))
            suche.load()
            if suche.artists:
                self.printArray(suche.artists, 'artists')
            if suche.albums:
                self.printArray(suche.albums, 'albums')
            if suche.tracks:
                self.printArray(suche.tracks, 'tracks')
            if suche.did_you_mean:
                self.printArray(suche.did_you_mean, 'did u mean')
        elif sucheingabe in 'n':
            self.playNextSong()
        elif sucheingabe in 'ls':
            self.printArray(self.titelliste[self.titelcounter:], "datt steht an")
        elif sucheingabe in "latin":
            suche = self.session.search("roots of chicha")
            suche.load()
            self.titelliste = [t for t in suche.tracks]
            self.titelcounter = int(randint(0, len(self.titelliste)-1))
            self.playSong()
        elif sucheingabe[-1] in '?':
            suche = self.session.search(str(sucheingabe[:-1]))
            suche.load()
            self.titelliste = [t for t in suche.tracks]
            self.titelcounter = int(randint(0, len(self.titelliste)-1))
            self.playSong()
        elif sucheingabe[-1] in '!':
            suche = self.session.search(str(sucheingabe[:-1]), track_count=1)
            suche.load()
            if(suche.tracks):
                self.titelliste = [t for t in suche.tracks]
                self.titelcounter = 0
                albumbrowser = suche.tracks[0].album.browse()
                albumbrowser.load()
                tracks = albumbrowser.tracks
                [self.titelliste.append(t) for t in tracks]
                self.playSong()
        elif sucheingabe[-1] in '+':
            suche = self.session.search(str(sucheingabe[:-1]))
            suche.load()
            self.titelliste.insert(self.titelcounter+1, suche.tracks[0])
        # self.titelcounter += 1
        # self.playSong()
        elif sucheingabe[-1] in '@':
            suche = self.session.search(str(sucheingabe[:-1]))
            suche.load()
            [self.titelliste.append(t) for t in suche.tracks]
        elif sucheingabe in 'random':
            tempCurrSong = self.titelliste[self.titelcounter]
            self.titelliste = self.titelliste[self.titelcounter+1:]
            shuffle(self.titelliste)
            self.titelliste.insert(0, tempCurrSong)
            self.titelcounter = 0
        elif sucheingabe in 'stop':
            self.session.player.pause()
        # thread.start_new_thread(self.showPic,("/home/pi/franzl_knarre_klein.jpg",))
        # os.system("rm /home/pi/yay.txt")
        else:
            suche = self.session.search(str(sucheingabe))
            suche.load()
            if(suche.tracks):
                self.titelliste.append(suche.tracks[0])
                if(self.session.player.state.encode("utf8") in "unloaded" or self.session.player.state.encode("utf8") in "paused"):
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
