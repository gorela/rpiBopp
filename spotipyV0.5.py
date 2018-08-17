#!/usr/bin/env python

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
import pickle
import spotipy
import spotipy.util as util
import spotipy.oauth2 as oauth2
import argparse


class spotifyRPI(object):

    def __init__(self):
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n.....init...............")
        #os.system("sh /home/pi/sleepKill.sh &")
        
        #os.system("sh /home/pi/showPic.sh /home/pi/heartBW_klein.jpg")
        #os.system("espeak 'i am alive. make some mofucking noise'")


        ##########################
        # spotipy init
        ##########################

        scope = 'user-library-read'

        if len(sys.argv) > 1:
            self.username = sys.argv[1]
        else:
            print "Usage: %s username" % (sys.argv[0],)
            sys.exit()

        self.token = util.prompt_for_user_token(self.username, scope)

        if self.token:
            self.sp = spotipy.Spotify(auth=self.token)
            print ".....spotipy rennt.........."

        ################################
        # parser KRAM
        ################################

        self.parser=argparse.ArgumentParser()

        self.parser.add_argument('eingabe', nargs = '*', help = "da musste was tippen")
        self.parser.add_argument('-c' , nargs = 1, type = int, default = 3, help = "wieviele sollen gesucht werden")
        self.parser.add_argument('-o' , nargs = 1, type = int, default = 0, help = "ab wo soll gesucht werden")
        self.parser.add_argument('-s', action = 'store_true', help = "sofocht spielen oder wie oder watt?")
        self.parser.add_argument('-a', action = 'store_true', help = "direkt das ganze album")
        self.parser.add_argument('-k', action = 'store_true', help = "ma schauen was die zarte kuenstlerseele treibt")
        self.parser.add_argument('-f', action = 'store_true', help = "voller output")
        self.parser.add_argument('-aa', action = 'store_true', help = "direkt das ganze album")

        print ".....parser operational................"


        self.logged_in_event = threading.Event()
        self.tmpLst = []
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

        self.vsession.login('piotr22', 'mamaMukk3')

        while not self.logged_in_event.wait(0.1):
            self.vsession.process_events()

        self.INIT = 0x00
        self.NOSONGS = 0x01
        self.PLAY = 0x02

        self.showPics = False
        with open("hitlist.pkl","rb") as f:
            self.hitlist = pickle.load(f) 

        self.state = self.INIT
        if(int(self.vsession.connection.state) == 1):
            os.system("clear")
            print("...hat geklappt alter!!!")
            thread.start_new_thread(self.askTelegram, ())
            # thread.start_new_thread(self.eingabe,())

    def connection_state_listener(self, session):
        if session.connection.state is spotify.ConnectionState.LOGGED_IN:
            self.logged_in_event.set()

    def end_track_listener(self, session):
        #if(self.state != self.NOSONGS):
        print('am arsch')    
            # self.vtitelcounter += 1
        self.playNextSong()
        #self.state = self.NOSONGS

    def askTelegram(self):
        while(True):
            try:
                fil = open('yay.txt', 'a+b')
                if(fil):
                    lastinput = fil.readlines()[-1].replace("\n", "").encode("utf8")
                if(lastinput != "zonk"):
                    fil.write("zonk\n")
                    self.searchy(lastinput)
                fil.close()
                # print to playlist.txt for telegram
                # print len(self.vtitelliste),self.vtitelcounter
                fil = open("playlist.txt", 'w')
                if len(self.vtitelliste)>self.vtitelcounter:
                    i = len(self.vtitelliste[self.vtitelcounter:])
		    for song in reversed(self.vtitelliste[self.vtitelcounter:]):
                        fil.write(str(i) + " " + song.name.encode("utf8") + "\n" + song.artists[0].name.encode("utf8") + "\n----------------\n")
                        i -= 1
            # fil.write("wird noch ")
                    if len(self.vtitelliste) > 0:
	                with open('currentsong.txt', 'w') as current:
	                    current.write(self.vtitelliste[self.vtitelcounter].link.url)
                fil.close()
                time.sleep(5)
            except:
                print("catched telegram-error")
		print(sys.exc_info()[0])
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



    def playNextSong(self):
        if len(self.vtitelliste)>self.vtitelcounter:
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
                print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
                print('______________________________')
                print('')
                print(tmptrack.artists[0].name)
                print(tmptrack.album.name + ' ' + str(tmptrack.album.year))
                print(tmptrack.name)
                # print(tmptrack.popularity)
                print('______________________________')
                print('\n\n\n\n')
                self.getCover(tmptrack)
                self.saveHitList(tmptrack)
            else:
                print 'leider doch nicht...irgendwie nicht auffindbar'
        else:
            if(self.state != self.NOSONGS):
                self.state = self.NOSONGS
                if self.showPics:
                    os.system("sh /home/pi/showPic.sh /home/pi/franzl_knarre_klein.jpg")
                print "keine songs mehr alter lauch..."

                tmptrack = self.vtitelliste[-1]              
                self.vsession.player.load(tmptrack)
                tr =  tmptrack.link.uri[14:]
                print tr
                t = []
                t.append(tr)
                rec = self.sp.recommendations(seed_tracks=t, country = "US", min_energy=0.4 , min_popularity=50, limit=1)
                print rec['tracks'][0]['name']
                print rec['tracks'][0]['uri']
                track = self.vsession.get_track(rec['tracks'][0]['uri']).load()
                self.add2Playlist(track)
                self.playSong()

    def saveHitList(self,track):
        i = randint(0,300)
        if i < 100:        
            try:
                with open("hitlist.pkl",'rb') as f:
                    self.hitlist = pickle.load(f)
                if track.link.uri not in self.hitlist:
                    if len(self.hitlist) > 98:
                        self.hitlist[i] = track.link.uri
                        with open("hitlist.pkl",'wb') as f:
                            pickle.dump(self.hitlist[:99],f)
                    else:
                        self.hitlist.append(track.link.uri)
                        with open("hitlist.pkl",'wb') as f:
                            pickle.dump(self.hitlist,f)
                    print("geht steil, alter chartstuermer "+str(i))
            except:
                print("catched pickle-error"+str(sys.exc_info()[0]))

    def playHitList(self):
        for links in self.hitlist:
        	track = self.vsession.get_track(links).load()
        	#print track.name
        	self.add2Playlist(track)
        self.randomizePlaylist()
        self.playNextSong()

    def printHitList(self):
        liste = []
        for links in self.hitlist:
        	liste.append(self.vsession.get_track(links).load())
        self.printArray(liste,"das geht in der neustadt, eulchen")


    def showPic(self, path):
        if self.showPics:
            os.system("fbi -noverbose -t 5 %s" % path)

    def eingabe(self):
        #sp_oauth = oauth2.SpotifyOAuth(client_id, client_secret, redirect_uri)
        #print str(oauth2.is_token_expired(self.token))
        print str(self.state)
        encoding = 'utf-8' if sys.stdin.encoding in (None, 'ascii') else sys.stdin.encoding
        # vsucheingabe = raw_input('?').decode(encoding)
        vsucheingabe = raw_input('?')
        if vsucheingabe.isdigit() and self.tmpLst:
            # print "kleine kontrolle"
            try:
                nr = int(vsucheingabe)
                linki =  self.tmpLst[nr]
                if 'track' in linki:
                    track = self.vsession.get_track(linki).load()
                    self.add2Playlist(track)
                elif 'album' in linki:
                    print "heute mal nen ganzes album, alter goenner"
                    altr =  self.sp.album_tracks(linki)['items']
                    for tr in altr:
                        track = self.vsession.get_track(tr['uri']).load()
                        self.add2Playlist(track)


            except Exception, e:
                print "nummerino mein lieber"            
        elif(vsucheingabe):
            self.searchy(vsucheingabe.encode('utf-8').lower())

    

    def suche(self, suchString, count = 10, offset = 0, artDerSuche = 'track'):
        '''
        suuuche
        '''
        result = self.sp.search(suchString, limit = count, offset = offset ,type = artDerSuche)
        return result

    def printAndCountAndAppend(self, tr,spaces,tmp):
        print " "*spaces+ str(tmp) + '. ' + tr['name'] 
        # print tr.keys()
        self.tmpLst.append(tr['uri'])
        tmp += 1
        return tmp

    def printResult(self, result):
        tmp = 0
        self.tmpLst = []
        # print result.keys()
        if 'tracks' in result.keys():
            print
            print "Suchergebnisse insgesamt:"
            print result['tracks']['total']
            print
            for tr in result['tracks']['items']:
                print tr['artists'][0]['name']
                # print "  " + tr['name']
                tmp = self.printAndCountAndAppend(tr,2,tmp) 
        if 'albums' in result.keys():
            print
            print "Suchergebnisse:"
            print result['albums']['total']
            print
            for al in result['albums']['items']:
                print al['artists'][0]['name']
                # print al['artists'][0].keys()
                ident = al['id']
                album_tracks = self.sp.album_tracks(ident) 
                tmp = self.printAndCountAndAppend(al,2,tmp)
                print "     (" + str(album_tracks['total']) + " songs)"
                if self.args.f:    
                    for altr in album_tracks['items']:
                        # print "    " + altr['name']
                        tmp = self.printAndCountAndAppend(altr,4,tmp)
                    print

        if 'artists' in result.keys():
            print
            print "Suchergebnisse:"
            print result['artists']['total']
            print
            for ar in result['artists']['items']:
                print ar['name'] 
                artist_albums = self.sp.artist_albums(ar["id"])
                print  "  " + str(artist_albums["total"]) + " alben"
                if self.args.f:    
                    for al in artist_albums['items']:
                        print al['name']
                        ident = al['id']
                        album_tracks = sp.album_tracks(ident) 
                        print "  " + al['name'] + " ..... " + str(album_tracks['total']) + " songs"
                        for altr in album_tracks['items']:
                            tmp = self.printAndCountAndAppend(altr,4,tmp)
                            print "       (" + altr['artists'][0]['name'] + ")"



    def randomizePlaylist(self):
        tempCurrSong = self.vtitelliste[self.vtitelcounter]
        self.vtitelliste = self.vtitelliste[self.vtitelcounter+1:]
        shuffle(self.vtitelliste)
        self.vtitelliste.insert(0, tempCurrSong)
        self.vtitelcounter = 0



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
        if songs2add:
            self.vtitelliste.insert(self.vtitelcounter+1+position, songs2add)
            return 1
        else:
            return 0


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
        elif vsucheingabe == 'b':
            self.vtitelcounter -= 1
            self.playSong()
        elif vsucheingabe == 'ls':
            self.printArray(self.vtitelliste[self.vtitelcounter:], "datt steht an")
        elif vsucheingabe == "latin":
            vsuche = self.suche("roots of chicha", trackCount = 100)
            self.replacePlaylistWithSearch(vsuche)
            self.randomizePlaylist()
            self.playSong()
            print("pack die chicha aus, mausebacke")
        elif vsucheingabe == 'hitlist':
            self.playHitList()
        elif vsucheingabe == 'show hitlist':
            self.printHitList()
        elif 'playlist' in vsucheingabe:
            print("lass ma sehen das listchen")
            playlistURL = vsucheingabe[13:].replace(".com","").replace("/",":")
            playlist = self.vsession.get_playlist(playlistURL).load()
            print(playlist.name)
            #print(playlist.tracks) 
            self.replacePlaylistWithSearch(playlist) 
            self.playSong()          
        elif 'https' in vsucheingabe:
        	print("oha...neuste technik am start alter")
        	spID = vsucheingabe[-22:]
        	#print(spID)
        	track = self.vsession.get_track('spotify:track:%s'%spID).load()
        	#print track.name
        	self.add2Playlist(track)
        	#self.playSong()
        elif 'spotify:track:' in vsucheingabe:
            print "--------------------------------------------"
            track = self.vsession.get_track(vsucheingabe).load()
            self.add2Playlist(track)
        elif endMarker == '?':
            vsuche = self.suche(str(suchString))
            self.addSearch2Playlist(vsuche)
            self.randomizePlaylist()            
            # self.playSong()
        elif endMarker == '!':
            self.args = self.parser.parse_args(vsucheingabe.split())
            res = self.suche(" ".join(self.args.eingabe), count=self.args.c, artDerSuche="track", offset = self.args.o)
            tr = res['tracks']['items'][0]['uri']
            track = self.vsession.get_track(tr).load()
            self.vtitelliste = []            
            self.vtitelliste.append(track)
            self.vtitelcounter = 0
            self.playSong()
            print self.sp.recommendations(seed_tracks=tr)
        elif endMarker == '+':
            vsuche = self.suche(str(suchString))
            self.add2Playlist(vsuche.tracks[0])
        elif endMarker == '@':
            vsuche = self.suche(str(suchString))
            self.addSearch2Playlist(vsuche)
        elif vsucheingabe == 'random':
            self.randomizePlaylist()
        else:
            self.args = self.parser.parse_args(vsucheingabe.split())
            res = self.suche(" ".join(self.args.eingabe), count=self.args.c, artDerSuche="album" if self.args.a else "artist" if self.args.k else "track", offset = self.args.o)
            self.printResult(res)

            # result = self.sp.search(str(vsucheingabe), type = 'track')
            # song = result['tracks']['items'][0]['uri']
            # print song
            # track = self.vsession.get_track(song).load()
            # if self.add2Playlist(track):
            print self.vsession.player.state
            if(self.vsession.player.state.encode("utf8") in "unloaded" or self.vsession.player.state.encode("utf8") in "paused"):
                # self.playSong()
                self.playNextSong()

            else:
                tmpDiff = len(self.vtitelliste)-self.vtitelcounter-1
                print('')
                print("coming up next... in %s songs"%tmpDiff)
                print("%s (%s)"%(self.vtitelliste[-1].name,self.vtitelliste[-1].artists[0].name))
                print('')
            # else:
            #     print("\nhabe nix gefunden, aber \nlegastenie kann behandelt werden, dj")

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

    def startThreads(self):
        thread.start_new_thread(self.askTelegram, ())
        thread.start_new_thread(self.eingabe, ())
        time.sleep(2)

if __name__ == '__main__':
    try:
        superPlayer = spotifyRPI()
    except:
        print("very bad error")

    while True:
            # superPlayer.startThreads()
        #superPlayer.eingabe()
        try:

            superPlayer.eingabe()

        except:
            print("bad error")
            superPlayer.token = util.prompt_for_user_token(superPlayer.username, 'user-library-read')

            if superPlayer.token:
                superPlayer.sp = spotipy.Spotify(auth=superPlayer.token)
                print ".....spotipy rennt.........."
            #sys.exit()  

