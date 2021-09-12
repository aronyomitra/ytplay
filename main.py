from urllib import request
import re
import pafy
import vlc
import time

'''This is a small CLI program to search for audio on Youtube and play it using libVLC. We will use pafy (https://pypi.org/project/pafy/)
to obtain information about a specific video - title, author, duration, and most importantly, get a streaming URL for the audio, which
we will feed into the libVLC instance to play music. Continuous input is taken from the user and commands are parsed using the re module.
It is possible to change songs, pause, seek etc all using the same interface. Note that using input() here is non-blocking as the libVLC
player is multithreaded'''

# Compile Regexes to check commands later on
regex1 = re.compile(r'watch\?v=(\S{11})')
regex2 = re.compile(r'^!s(earch)?(( +\S+)+)$', re.IGNORECASE)
regex3 = re.compile(r'^!p(lay)?(( +\S+)+)$', re.IGNORECASE)
# regex4 = re.compile(r'^!p(lay)? ((https://)?(www.)?youtube.com/watch\?v=\S{11})$', re.IGNORECASE)

# Default number of search results
searchLen = 5

# Create a VLC MediaPlayer object which will play media when fed a streaming URL(MRL)
vlcInstance = vlc.Instance("--verbose=-1", "--no-video")
player = vlcInstance.media_player_new()

# Main loop
while True:
    command = input("\n>>")
    command = command.strip()

    if command.lower() == 'quit' or command.lower() == 'q' or command.lower() == 'exit':
        break
    
    x = regex2.match(command)
    y = regex3.match(command)
    
    # Search command
    if x:
        # Replace spaces with + to get search page url (a bit crude, will implement better soln later)
        searchquery = x.group(2).strip().replace(' ', '+')
        url = 'https://youtube.com/results?search_query=' + searchquery
        resp = request.urlopen(url)
        respData = resp.read()
        # Convert byte data into string
        srespData = str(respData)

        pafylist = []
        start = 0
        # Fill list with pafy objects
        for i in range (0, searchLen):
            match = regex1.search(srespData, start)
            temp = 'https://youtube.com/watch?v=' + match[1]
            # The basic=False flag stops pafy from retrieving video information right after initialization
            # Design choice to reduce perceived latency
            p = pafy.new(temp, basic = False)
            pafylist.append(p)
            start = match.end()
        
        print()
        for i in range (0, len(pafylist)):
            p = pafylist[i]
            # A certain bug in pafy code can cause videos with zero likes to cause a crash. This eliminates that possibility
            try:
                print (str(i+1) + ") " + p.title)
            except KeyError:
                p._have_basic = True
                print (str(i+1) + ") " + p.title)
            print (p.author)
            print (p.duration)
            print ()

        choice = input("\nEnter selection (x to cancel): ")
        if choice == 'x':
            continue
        
        try:
            nchoice = int(choice)
        except ValueError:
            print ("Please enter an integer in the range")
            continue
        
        if nchoice < 1 or nchoice > searchLen:
            print ("Please enter an integer in the range")
            continue

        p = pafylist[nchoice-1]
        audioStreamURL = p.getbestaudio().url

        print ()
        print (p.title)
        print (p.author)
        print (p.duration)
        print ("(https://youtube.com/watch?v=" + p.videoid + ")")

        player.set_mrl(audioStreamURL)
        player.play()
    
    # Play command - Play the first option in seach results
    elif y:
        searchquery = y.group(2).strip().replace(' ', '+')
        url = 'https://youtube.com/results?search_query=' + searchquery
        
        resp = request.urlopen(url)
        respData = resp.read()
        srespData = str(respData)
        
        match = regex1.search(srespData)
        url = 'https://youtube.com/watch?v=' + match[1]

        p = pafy.new(url, basic=False)
        try:
            test = p.title
        except KeyError:
            p._have_basic = True
        
        audioStreamURL = p.getbestaudio().url
        
        print ()
        print (p.title)
        print (p.author)
        print (p.duration)
        print ("(https://youtube.com/watch?v=" + p.videoid + ")")

        player.set_mrl(audioStreamURL)
        player.play()

    command = command.lower()

    # Media control commands
    if command == 'pause' or command == 'p':
        state = player.get_state()
        if state == vlc.State.Playing:
            print ("Paused")
        elif state == vlc.State.Ended or state == vlc.State.Stopped:
            print ("Track has ended")
        else:
            print ("Resumed")
        player.pause()
    
    elif command == 'stop' or command == 's':
        player.stop()
        print ("Stopped")

    elif command == 'play':
        player.play()
        print ("Playing")

    elif command == 'replay' or command == 'restart':
        print ("Restarting track")
        player.stop()
        player.play()
    
    elif command == 'v+':
        player.audio_set_volume(player.audio_get_volume() + 10)
        time.sleep(1)
        print ("Volume: " + str(player.audio_get_volume()))
    elif command == 'v-':
        player.audio_set_volume(player.audio_get_volume() - 10)
        time.sleep(1)
        print ("Volume: " + str(player.audio_get_volume()))
    elif command == 'mute':
        player.audio_toggle_mute()

    elif command == 'status':
        print(player.get_state())

    # Nowplaying command displays a neat progress bar
    elif command == 'np' or command == "nowplaying":
        print ("Now Playing: " + p.title)
        pos = player.get_position()
        pos = int(pos*30 + 1)
        print ("[", end='')
        for i in range(1, pos):
            print("=", end='')
        print ("o", end='')
        for i in range (pos, 30):
            print ("-", end='')
        print ("]")
        if player.get_state() == vlc.State.Paused:
            print ("Paused")
    
    # Forward, default 10 seconds
    elif 'fw' in command:
        x = re.match(r'^fw( \d+)?$', command)
        if x:
            delta = 10
            if x.group(1) is not None:
                delta = int(x.group(1).strip())
        
            player.set_time(player.get_time() + delta*1000)
        else:
            pass
            print ("Invalid command. Try entering '?' for help")
    
    # Rewind, default 10 seconds
    elif 'rw' in command:
        x = re.match(r'^rw( \d+)?$', command)
        if x:
            delta = 10
            if x.group(1) is not None:
                delta = int(x.group(1).strip())

            player.set_time(player.get_time() - delta*1000)
        else:
            pass
            print ("Invalid command. Try entering '?' for help")
    
    # Seek to a specific time or percent completed
    elif 'seek' in command:
        x = re.match(r'^seek (\d+)%?$', command)
        if x:
            l = len(command)
            if command[l-1] == '%':
                perc = int(x.group(1))/100
                player.set_position(perc)
            else:
                t = int(x.group(1))
                player.set_time(t*1000)
        else:
            pass
            print ("Invalid command. Try entering '?' for help")
    
    # HELP
    elif command == 'help' or command == '?':
        print ("\nWelcome to ytplay - a lightweight command line Youtube Music Player")
        print ("-------------------------------------------------------------------")
        print ("ytplay can search for music on youtube, play it and let you control the media like any other music player.")
        print ("Only, you interact with it through commands. Here's a list:")
        print ("\n* Search for music - !search <search term> \t[shortcut - !s]")
        print ("\teg: !search despacito cover\n\t    !s claire de lune debussy")
        print ()
        print ("* Quickplay (searches with the query and plays the first result that comes up) - !play <search term> \t[shortcut - !p]")
        print ("\teg: !play never gonna give you up\n\t    !p coldplay amsterdam")
        print ("  Playing a song while another is playing will immediately start playing the new song")
        print()
        print ("  The remaining commands do not need a !")
        print ("* Pause - pause \t[shortcut - p]")
        print ("* Obtain information on currently playing track - nowplaying \t[shortcut - np]")
        print ("* Restart track - restart")
        print ("* Stop track - stop \t[shorcut - s]")
        print ("* Increase volume - v+")
        print ("* Decrease volume - v-")
        print ("* Toggle mute - mute")
        print ("* Forward by N seconds (default 10 if no number given) - fw N")
        print ("* Rewind by N seconds (default 10 if no number given) - rw N")
        print ("* Go to N% position of track - seek N%")
        print ("    eg: seek 50%")
        print ("\n* Go to N seconds from beginning of track - seek N")
        print ("    eg: seek 120 \tgoes to the 2 minute mark")
        print ("\n* Quit - quit \t[shortcut - q]")            

    else:
        if not x and not y:
            print ("Invalid command. Try entering '?' for help")
