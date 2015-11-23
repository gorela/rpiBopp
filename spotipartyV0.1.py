#!/usr/bin/env python2.7

import spotify
import threading
from random import randint
from random import shuffle
import os, sys, re
import thread
import time
import sendJson


class spotifyRPI(object):

    def __init__(self):
        self.sender = sendJson.sendJson()
        # self.printServer("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n.....init...............")
        #os.system("sh /home/pi/sleepKill.sh &")
        # os.system("sh /home/pi/showPic.sh /home/pi/heartBW_klein.jpg")
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

        self.vsession.login('passs', 'wort')

        while not self.logged_in_event.wait(0.1):
            self.vsession.process_events()

        self.INIT = 0x01
        self.NOSONGS = 0x02
        self.PLAY = 0x04
        self.PARTY = 0x08

        self.partyNextCounter = 0

        self.state = self.INIT

        self.globalSongID = 0


        if(int(self.vsession.connection.state) == 1):
            os.system("clear")
            self.printServer("...hat geklapp alter!!!")
            thread.start_new_thread(self.askTelegram, ())
            # thread.start_new_thread(self.eingabe,())

    def connection_state_listener(self, session):
        if session.connection.state is spotify.ConnectionState.LOGGED_IN:
            self.logged_in_event.set()

    def end_track_listener(self, session):
        if(self.state != self.NOSONGS):
            self.printServer('am arsch')    
            # self.vtitelcounter += 1
        self.playNextSong()
        self.state = self.NOSONGS

    def askTelegram(self):
        while(True):
            fil = open('yay.txt', 'a+b')
            if(fil):
                lastinput = fil.readlines()[-1].replace("\n", "").encode("utf8")
            if(lastinput != "zonk"):
                self.searchy(lastinput)
                fil.write("zonk\n")
            fil.close()
            # printServer to playlist.txt for telegram
            fil = open("playlist.txt", 'w')
            # os.system("python sendJson.py "+ str(self.vtitelliste[0]))
            
            i = len(self.vtitelliste[self.vtitelcounter:])
            for vote,song,idd in reversed(self.vtitelliste[self.vtitelcounter:]):
                fil.write(str(i) + " " + song.name.encode("utf8") + "\n" + song.artists[0].name.encode("utf8") + "\n----------------\n")
                self.sender.sendText(str(song.name.encode("utf8")))
                i -= 1
        # fil.write("wird noch ")
            fil.close()

            time.sleep(5)
    # thread.start_new_thread(self.askTelegram(),())

    def playNextSong(self):
        self.vtitelcounter += 1
        self.playSong()

    def playSong(self):
        if self.vtitelcounter < len(self.vtitelliste):
            self.printServer('laeuft')
            self.state = self.PLAY
            self.vsession.player.load(
                self.vtitelliste[int(self.vtitelcounter)][1])
            self.vsession.player.play()
            # self.printServer('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
            # self.printServer('______________________________')
            self.printServer('da hab ich ne juute scheibe gefunden')
            self.printServer("songID: %s" % self.vtitelliste[int(self.vtitelcounter)][2])
            self.printServer(self.vtitelliste[int(self.vtitelcounter)][1].artists[0].name.encode('utf-8'))
            self.printServer(self.vtitelliste[int(self.vtitelcounter)][1].album.name.encode('utf-8'))
            self.printServer(self.vtitelliste[int(self.vtitelcounter)][1].name.encode('utf-8'))
            # self.printServer('______________________________')
            # self.printServer('\n\n\n\n\n\n\n\n\n\n\n\n')
        else:
            if(self.state != self.NOSONGS):
                self.state = self.NOSONGS
                #os.system("sh /home/pi/showPic.sh /home/pi/franzl_knarre_klein.jpg")
                self.printServer("keine songs mehr alter lauch...")

    def showPic(self, path):
        os.system("fbi -noverbose -t 5 %s" % path)

    def eingabe(self):
        encoding = 'utf-8' if sys.stdin.encoding in (None, 'ascii') else sys.stdin.encoding
        vsucheingabe = raw_input('?').decode(encoding)
        #printServer vsucheingabe.encode('utf-8')
        #vsucheingabe = str(raw_input('?')).encode("utf8")
        # self.printServer('hab noch %d songs in der kiste pirat' %len(self.vtitelliste))
        if(vsucheingabe):
            self.searchy(vsucheingabe.encode('utf-8'))
    # thread.start_new_thread(self.eingabe,())

    def searchy(self, vsucheingabe):
        #
        #   PARTY
        #
        # if self.state == self.PARTY:
        if True:
            voting = re.match(r"^(\d)+(\+|\-)$", vsucheingabe)
            # if vsucheingabe in "party's over":
            #     self.printServer("wir werden alle nicht juenger...")
            #     self.state = self.NOSONGS
            if voting:
                voting = voting.group(0)
                tmpIdd = int(voting[:-1])
                tmpVote = 0
                hit = [item for item in self.vtitelliste if int(item[2]) == tmpIdd]
                if hit:
                    if voting[-1] in '+':
                        self.printServer("song >>%s<< aufgewertet" % hit[0][1].name)
                        tmpVote = 1
                    else:
                        self.printServer("song >>%s<< abgestraft" % hit[0][1].name)
                        tmpVote = -1
                    for i, item in enumerate(self.vtitelliste):
                        if item[2] == tmpIdd:
                            item[0] += tmpVote
                    self.vtitelliste[self.vtitelcounter+1:] = reversed(sorted(self.vtitelliste[self.vtitelcounter+1:]))
                else:
                    self.printServer("diese songID gibts doch gar nicht...gib nicht auf cowboy!")
            elif vsucheingabe in 'ls':
                # self.printArray(self.vtitelliste[self.vtitelcounter:], "datt steht an")
                i = len(self.vtitelliste)
                reversedList = reversed(self.vtitelliste[self.vtitelcounter: self.vtitelcounter+5])
                for vote, song, idd in reversedList:
                    self.printServer(str(idd) + " " + song.name.encode("utf8") + "\n" + song.artists[0].name.encode("utf8") + "\n")
                    i -= 1
            else:
                vsuche = self.vsession.search(str(vsucheingabe).encode('utf-8'))
                vsuche.load()
                if(vsuche.tracks):
                    if len(self.vtitelliste) > 0:
                        randomPosition = randint(self.vtitelcounter+1,len(self.vtitelliste))
                        relativeRandomPosition = randomPosition - self.vtitelcounter
                        self.vtitelliste.insert(randomPosition, [0,vsuche.tracks[0],self.gimmeID()])
                        self.printServer("ich spiele zu ihren ehren:\n------------------ \n%s \nvon \n%s\n------------------\nnach %d Liedern\n" %(vsuche.tracks[0].name.encode('utf-8'), vsuche.tracks[0].artists[0].name.encode('utf-8'),relativeRandomPosition))
                    else:
                        self.vtitelliste.append([0,vsuche.tracks[0],self.gimmeID()])
                else:
                    self.printServer("habe den song %s trotz grosser anstrengungen nicht finden koennen meister. sry..." % vsucheingabe)
            if(self.vsession.player.state.encode('utf-8')in "unloaded" or self.vsession.player.state.encode('utf-8') in "paused" or self.state == self.NOSONGS):
                        self.playSong()
        #
        #
        #
        # else:
        #     if vsucheingabe in 's':
        #         self.longSearch()
        #     elif 's ' in vsucheingabe[:2]:
        #         vsuche = self.vsession.search(str(vsucheingabe[2:]))
        #         vsuche.load()
        #         if vsuche.artists:
        #             self.printArray(vsuche.artists, 'artists')
        #         if vsuche.albums:
        #             self.printArray(vsuche.albums, 'albums')
        #         if vsuche.tracks:
        #             self.printArray(vsuche.tracks, 'tracks')
        #         if vsuche.did_you_mean:
        #             self.printArray(vsuche.did_you_mean, 'did u mean')
        #     elif vsucheingabe in 'n':
        #         self.playNextSong()
        #     elif vsucheingabe in 'ls':
        #         self.printArray(self.vtitelliste[self.vtitelcounter:], "datt steht an")
        #         i = len(self.vtitelliste[self.vtitelcounter:])
        #         for song in reversed(self.vtitelliste[self.vtitelcounter:]):
        #             self.printServer(str(i) + " " + song.name.encode("utf8") + "\n" + song.artists[0].name.encode("utf8") + "\n----------------\n")
        #             i -= 1
        #     elif vsucheingabe in "latin":
        #         vsuche = self.vsession.search("roots of chicha")
        #         vsuche.load()
        #         self.vtitelliste = [t for t in vsuche.tracks]
        #         self.vtitelcounter = int(randint(0, len(self.vtitelliste)-1))
        #         self.playSong()
        #     elif vsucheingabe[-1] in '?':
        #         vsuche = self.vsession.search(str(vsucheingabe[:-1]))
        #         vsuche.load()
        #         if vsuche.tracks:
        #             self.vtitelliste = [t for t in vsuche.tracks]
        #             self.vtitelcounter = int(randint(0, len(self.vtitelliste)-1))
        #             self.playSong()
        #     elif vsucheingabe[-1] in '!':
        #         vsuche = self.vsession.search(str(vsucheingabe[:-1]), track_count=1)
        #         vsuche.load()
        #         if vsuche.tracks:
        #             self.vtitelliste = [t for t in vsuche.tracks]
        #             self.vtitelcounter = 0
        #             valbumbrowser = vsuche.tracks[0].album.browse()
        #             valbumbrowser.load()
        #             vtracks = valbumbrowser.tracks
        #             [self.vtitelliste.append(t) for t in vtracks]
        #             self.playSong()
        #     elif vsucheingabe[-1] in '+':
        #         vsuche = self.vsession.search(str(vsucheingabe[:-1]))
        #         vsuche.load()
        #         if vsuche.tracks:
        #             self.vtitelliste.insert(self.vtitelcounter+1, vsuche.tracks[0])
        #     # self.vtitelcounter += 1
        #     # self.playSong()
        #     elif vsucheingabe[-1] in '@':
        #         vsuche = self.vsession.search(str(vsucheingabe[:-1]))
        #         vsuche.load()
        #         if vsuche.tracks:
        #             [self.vtitelliste.append(t) for t in vsuche.tracks]
        #     elif vsucheingabe in 'random':
        #         tempCurrSong = self.vtitelliste[self.vtitelcounter]
        #         self.vtitelliste = self.vtitelliste[self.vtitelcounter+1:]
        #         shuffle(self.vtitelliste)
        #         self.vtitelliste.insert(0, tempCurrSong)
        #         self.vtitelcounter = 0
        #     elif vsucheingabe in 'stop':
        #         self.vsession.player.pause()
        #     elif vsucheingabe in "party's on":
        #         self.printServer("jetzt geht das richtig rund junge!")
        #         self.state = self.PARTY
        #     # thread.start_new_thread(self.showPic,("/home/pi/franzl_knarre_klein.jpg",))
        #     # os.system("rm /home/pi/yay.txt")
        #     else:
        #         vsuche = self.vsession.search(str(vsucheingabe))
        #         vsuche.load()
        #         if(vsuche.tracks):
        #             self.vtitelliste.append(vsuche.tracks[0])
        #             if(self.vsession.player.state.encode('utf-8')in "unloaded" or self.vsession.player.state.encode('utf-8') in "paused" or self.state == self.NOSONGS):
        #                 self.playSong()

    def printArray(self, liste, listname):
        count = len(liste)-1
        # self.printServer('')
        self.printServer(listname.encode('utf-8'))
        # self.printServer('______________________________')
        # self.printServer('')
        for vote,song,idd in reversed(liste):
            self.printServer(str(idd) + '...' + song.name.encode('utf-8')+'...v: '+str(vote))
            count -= 1
        # self.printServer('______________________________')
        # self.printServer('')

    def startThreads(self):
        thread.start_new_thread(self.askTelegram, ())
        thread.start_new_thread(self.eingabe, ())
        time.sleep(10)

    def printServer(self, text):
        print(text)
        self.sender.sendText(text)
        pass

    def gimmeID(self):
        self.globalSongID+=1
        return self.globalSongID

if __name__ == '__main__':
    superPlayer = spotifyRPI()
    while True:
        # superPlayer.startThreads()
        superPlayer.eingabe()

