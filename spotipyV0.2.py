#!/usr/bin/env python2.7
# coding=UTF-8

import spotify
import threading
from random import randint
from random import shuffle
import os
import sys
import thread
import time
import colorama
import readline
import spotipy

USER = sys.argv[1]
PASSWORD = sys.argv[2]

class spotifyRPI(object):

    def __init__(self):
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n.....init...............")
        #os.system("sh /home/pi/sleepKill.sh &")

        #os.system("sh /home/pi/showPic.sh /home/pi/heartBW_klein.jpg")
        #os.system("espeak 'i am alive. make some mofucking noise'")
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

        self.vsession.login(USER, PASSWORD)

        while not self.logged_in_event.wait(0.1):
            self.vsession.process_events()

        self.INIT = 0x00
        self.NOSONGS = 0x01
        self.PLAY = 0x02

        self.showPics = False

        self.state = self.INIT

        # instantiate spotipy object:
        self.spotipy = spotipy.Spotify()

        if(int(self.vsession.connection.state) == 1):
            os.system("clear")
            print("...hat geklappt alter!!!")
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
            # fil = open('/home/pi/yay.txt', 'a+b')
            # if(fil):
            lastinput = fil.readlines()[-1].replace("\n", "").encode("utf8")
            if(lastinput != "zonk"):
                self.searchy(lastinput)
                fil.write("zonk\n")
            # fil.close()
            # print to playlist.txt for telegram
            fil = open("/home/pi/playlist.txt", 'w')
            i = len(self.vtitelliste[self.vtitelcounter:])
            for song in reversed(self.vtitelliste[self.vtitelcounter:]):
                fil.write(str(i) + " " + song.name.encode("utf8") + "\n" + song.artists[0].name.encode("utf8") + "\n----------------\n")
                i -= 1
        # fil.write("wird noch ")
            fil.close()
            if len(self.vtitelliste) > 0:
	        with open('/home/pi/currentsong.txt', 'w') as current:
	            current.write(self.vtitelliste[self.vtitelcounter].link.url)
            time.sleep(5)

            import time


    # thread.start_new_thread(self.askTelegram(),())

    def getCover(self,track):
        im = track.album.cover()
        im.load()
        f = open('cover.jpg','wb')
        f.write(im.data)
        f.close()
        time.sleep(0.5)
        #os.system("sh /home/pi/showPic.sh /home/pi/cover.jpg")
        if self.showPics:
            os.system("sudo killall fbi; sleep 1; sudo fbi -t 100 -T 1 -1 -d /dev/fb0 -noverbose -a -random /home/pi/cover.jpg")


    def longSearch(self):
        try:
        	encoding = 'utf-8' if sys.stdin.encoding in (None, 'ascii') else sys.stdin.encoding
            request = raw_input('Welchen Kuenstler soll ich spielen, Sir ?').decode(encoding)
            if request:
                results = self._suche(str(request), type='artist')
                print results
                results = results['artists']
                if results.get('items'):
                    artists = results['items']
                    self._printArray(artists)
                    # count = len(artists)-1
                    #XXX Check error handling with non integer input
                    request = raw_input('welchen von denen, alter? ')
                    if request.isdigit():
                        request = int(request)
                        uri = artists[request]['uri']
                        #TODO handle different album types like singles etc
                        results = self.spotipy.artist_albums(uri, album_type='album', country='DE')
                        albums = results['items']
                        while results['next']:
                            results = self.spotipy.next(results)
                            albums.extend(results['items'])

                        self._printArray(albums)

                        request = raw_input('welchen von denen, alter? ')
                        if request.isdigit():
                            request = int(request)
                            album_id = albums[request]['id']
                            #TODO handle different album types like singles etc
                            results = self.spotipy.album_tracks(album_id)
                            titles = results['items']
                            while results['next']:
                                results = self.spotipy.next(results)
                                titles.extend(results['items'])
                            self._printArray(titles)
                            request = raw_input('track number?')
                            if request.isdigit():
                                request = int(request)
                                self.vtitelcounter = request
                                title_query = [self.vsession.get_track(title['uri']) for title in titles]

                                self.vtitelliste = title_query
                                track = title_query[int(request)]
                                track.load()
                                if track.is_loaded:
                                    self.vsession.player.load(track)

                                    if title_query:
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
            tmptrack = self.vtitelliste[int(self.vtitelcounter)]
            if tmptrack.is_loaded and tmptrack.availability:

                self.vsession.player.load(tmptrack)
                #os.system("espeak 'next track: %s'"%tmptrack.name)
                self.vsession.player.play()
                print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
                print('______________________________')
                print('')
                print(tmptrack.artists[0].name)
                print(tmptrack.album.name + ' ' + str(tmptrack.album.year))
                print(tmptrack.name)
                # print(tmptrack.popularity)
                print('______________________________')
                print('\n\n\n\n\n\n\n\n\n\n\n\n')
                self.getCover(tmptrack)
            else:
                print 'leider doch nicht...irgendwie nicht auffindbar'
        else:
            if(self.state != self.NOSONGS):
                self.state = self.NOSONGS
                if self.showPics:
                    os.system("sh /home/pi/showPic.sh /home/pi/franzl_knarre_klein.jpg")
                print "keine songs mehr alter lauch..."

    def showPic(self, path):
        if self.showPics:
            os.system("fbi -noverbose -t 5 %s" % path)

    def eingabe(self):
        encoding = 'utf-8' if sys.stdin.encoding in (None, 'ascii') else sys.stdin.encoding
        vsucheingabe = raw_input('?').decode(encoding)
        if(vsucheingabe):
            self.searchy(vsucheingabe.encode('utf-8').lower())


    def randomizePlaylist(self):
        tempCurrSong = self.vtitelliste[self.vtitelcounter]
        self.vtitelliste = self.vtitelliste[self.vtitelcounter+1:]
        shuffle(self.vtitelliste)
        self.vtitelliste.insert(0, tempCurrSong)
        self.vtitelcounter = 0


    def suche(self, suchString, trackCount = 10, albumCount = 10, artistCount = 10):
        tmpSuche = self.vsession.search(suchString,track_count = trackCount, album_count = albumCount, artist_count = artistCount)
        tmpSuche.load(3)
        while not tmpSuche.is_loaded:
            time.sleep(0.5)
        return tmpSuche

    def _suche(self, input, type):
        """ type= ‘artist’, ‘album’, ‘track’ or ‘playlist’
        """
        return self.spotipy.search(input, limit=10, offset=0, type=type)

    def replacePlaylistWithSearch(self, suche):
        self.vtitelliste = [t for t in suche.tracks]
        self.vtitelcounter = 0

    def addSearch2Playlist(self, suche):
        ret = 0
        for t in suche.tracks:
            if t.availability:
                ret = 1
                self.vtitelliste.append(t)
        return ret

    def add2Playlist(self, songs2add, position = 0):
        self.vtitelliste.insert(self.vtitelcounter+1+position, songs2add)


    def searchy(self, vsucheingabe):
        endMarker = vsucheingabe[-1]
        suchString = vsucheingabe[:-1]

        if vsucheingabe == 'q':
            sys.exit()
        if vsucheingabe == 's':
            self.longSearch()
        elif 's ' in vsucheingabe[:2]:
            vsuche = self.suche(str(vsucheingabe[2:]))
            if vsuche.artists:
                self.printArray(vsuche.artists, 'artists')
            if vsuche.albums:
                self.printArray(vsuche.albums, 'albums')
            if vsuche.tracks:
                self.printArray(vsuche.tracks, 'tracks')
            if vsuche.did_you_mean:
                self.printArray(vsuche.did_you_mean, 'did u mean')
        elif vsucheingabe == 'n':
            self.playNextSong()
        elif vsucheingabe == 'ls':
            self.printArray(self.vtitelliste[self.vtitelcounter:], "datt steht an")
        elif vsucheingabe == "latin":
            vsuche = self.suche("roots of chicha", trackCount = 100)
            self.replacePlaylistWithSearch(vsuche)
            self.randomizePlaylist()
            self.playSong()
            print("pack die chicha aus, mausebacke")
        elif 'https' in vsucheingabe:
        	print("oha...neuste technik am start alter")
        	spID = vsucheingabe[-22:]
        	#print(spID)
        	track = self.vsession.get_track('spotify:track:%s'%spID).load()
        	#print track.name
        	self.add2Playlist(track)
        	#self.playSong()
        elif endMarker == '?':
            vsuche = self.suche(str(suchString))
            self.addSearch2Playlist(vsuche)
            self.randomizePlaylist()
            # self.playSong()
        elif endMarker == '!':
            vsuche = self.suche(str(suchString),trackCount=1)
            if(vsuche.tracks):
                self.vtitelliste = [t for t in vsuche.tracks]
                self.vtitelcounter = 0
                valbumbrowser = vsuche.tracks[0].album.browse()
                valbumbrowser.load()
                self.addSearch2Playlist(valbumbrowser)
                self.playSong()
        elif endMarker == '+':
            vsuche = self.suche(str(suchString))
            self.add2Playlist(vsuche.tracks[0])
        elif endMarker == '@':
            vsuche = self.suche(str(suchString))
            self.addSearch2Playlist(vsuche)
        elif vsucheingabe == 'random':
            self.randomizePlaylist()
        else:
            vsuche = self.suche(str(vsucheingabe), trackCount = 1)
            if self.addSearch2Playlist(vsuche):
                if(self.vsession.player.state.encode("utf8") in "unloaded" or self.vsession.player.state.encode("utf8") in "paused"):
                    self.playSong()
                else:
                    tmpDiff = len(self.vtitelliste)-self.vtitelcounter-1
                    print('')
                    print("coming up next... in %s songs"%tmpDiff)
                    print("%s (%s)"%(self.vtitelliste[-1].name,self.vtitelliste[-1].artists[0].name))
                    print('')
            else:
                print("\nhabe nix gefunden, aber \nlegastenie kann behandelt werden, dj")

        if vsucheingabe == 'stop':
            self.vsession.player.pause()

        if vsucheingabe == 'checki':
            print spotify.AudioBufferStats.stutter
            print spotify.AudioBufferStats.samples


    def printArray(self, liste, listname):
        count = len(liste)-1
        print('')
        print(listname)
        print('______________________________')
        print('')
        for a in reversed(liste):
            if listname == 'albums':
                print(str(count) + '...' + a.name + ' ' + str(a.year) + ' ' + str(a.type))
            else:
                print(str(count) + '...' + a.name)
            count -= 1
        print('______________________________')
    print('')

    def _printArray(self, results):
        count = len(results)-1
        print('')
        print(type)
        print('______________________________')
        print('')
        # TODO check if ifs are necessary
        for result in reversed(results):
            print(str(count) + '...' + result['name'])
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
