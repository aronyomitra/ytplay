from urllib import request
import re
import pafy
import vlc
import time

regex1 = re.compile(r'watch\?v=(\S{11})')
regex2 = re.compile(r'^!s(earch)?(( +\S+)+)$', re.IGNORECASE)
regex3 = re.compile(r'^!p(lay)?(( +\S+)+)$', re.IGNORECASE)
# regex4 = re.compile(r'^!p(lay)? ((https://)?(www.)?youtube.com/watch\?v=\S{11})$', re.IGNORECASE)
searchLen = 5

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
    
    if x:
        searchquery = x.group(2).strip().replace(' ', '+')
        url = 'https://youtube.com/results?search_query=' + searchquery
        resp = request.urlopen(url)
        respData = resp.read()
        srespData = str(respData)

        pafylist = []
        start = 0
        for i in range (0, searchLen):
            match = regex1.search(srespData, start)
            temp = 'https://youtube.com/watch?v=' + match[1]
            p = pafy.new(temp, basic = False)
            pafylist.append(p)
            start = match.end()
        
        print()
        for i in range (0, len(pafylist)):
            p = pafylist[i]
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
    
    elif y:
        searchquery = y.group(2).strip().replace(' ', '+')
        url = 'https://youtube.com/results?search_query=' + searchquery
        
        resp = request.urlopen(url)
        respData = resp.read()
        srespData = str(respData)
        
        match = regex1.search(srespData)
        url = 'https://youtube.com/watch?v=' + match[1]
        try:
            p = pafy.new(url)
        except KeyError:
            p._have_basic = True
            p = pafy.new(url)
        
        audioStreamURL = p.getbestaudio().url
        
        print ()
        print (p.title)
        print (p.author)
        print (p.duration)
        print ("(https://youtube.com/watch?v=" + p.videoid + ")")

        player.set_mrl(audioStreamURL)
        player.play()

    command = command.lower()

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
    
    elif 'fw' in command:
        x = re.match(r'^fw( \d+)?$', command)
        if x:
            delta = 10
            if x.group(1) is not None:
                delta = int(x.group(1).strip())
        
            player.set_time(player.get_time() + delta*1000)
        else:
            pass
            # error msg
    
    elif 'rw' in command:
        x = re.match(r'^rw( \d+)?$', command)
        if x:
            delta = 10
            if x.group(1) is not None:
                delta = int(x.group(1).strip())

            player.set_time(player.get_time() - delta*1000)
        else:
            pass
            # error
    
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
            #error
    
            

