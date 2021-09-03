from urllib import request
import re
import pafy
import vlc
import time

query = input("Enter youtube search query: ")

query = query.replace(' ', '+')
url = 'https://youtube.com/results?search_query=' + query
regex = re.compile(r'watch\?v=(\S{11})')
searchLen = 5

resp = request.urlopen(url)
respData = resp.read()
srespData = str(respData)
quickplay = False

if '!p' in query:
    quickplay = True
    searchLen = 1

pafylist = []
start = 0
for i in range (0, searchLen):
    match = regex.search(srespData, start)
    temp = 'https://youtube.com/watch?v=' + match[1]
    p = pafy.new(temp, basic = False)
    pafylist.append(p)
    start = match.end()

choice = 1
if not quickplay:               
    print ()
    for i in range (0, len(pafylist)):
        p = pafylist[i]
        try:
            print (str(i+1) + ") " + p.title)
        except KeyError:
            p._ydl_info['like_count'] = 0
            p._ydl_info['dislike_count'] = 0
           
            p._have_basic = True
            print (str(i+1) + ") " + p.title)
        print (p.author)
        print (p.duration)
        print ()

    choice = int(input("\nEnter selection: "))

try:
    audioStreamURL = pafylist[choice-1].getbestaudio().url
except KeyError:
    pafylist[choice-1]._have_basic = True
    audioStreamURL = pafylist[choice-1].getbestaudio().url


player = vlc.MediaPlayer(audioStreamURL)
player.play()

time.sleep(2)
print ()
print (pafylist[choice-1].title)
print (pafylist[choice-1].author)
print (pafylist[choice-1].duration)
print ("(https://youtube.com/watch?v=" + pafylist[choice-1].videoid + ")")
while True:
    comm = input ("\n>>")
    if comm == "p":
        if player.get_state() == vlc.State.Playing:
            print ("Paused")
        elif player.get_state() == vlc.State.Ended or player.get_state() == vlc.State.Stopped:
            print ("Track has ended")
        else:
            print ("Resumed")
        player.pause()
    elif comm == 's':
        player.stop()
        print ("Stopped")
    elif comm == 'restart':
        print ("Restarting track")
        player.stop()
        player.play()
    elif comm == 'r':
        player.set_time(player.get_time() + 10000)
    elif comm == 'l':
        player.set_time(player.get_time() - 10000)
    elif comm == 'q':
        break
    elif comm == 'v+':
        player.audio_set_volume(player.audio_get_volume() + 10)
        time.sleep(1)
        print ("Volume: " + str(player.audio_get_volume()))
    elif comm == 'v-':
        player.audio_set_volume(player.audio_get_volume() - 10)
        time.sleep(1)
        print ("Volume: " + str(player.audio_get_volume()))
    elif comm == 'mute':
        player.audio_toggle_mute()
    elif comm == 'status':
        print(player.get_state())
    elif comm == 'np':
        print ("Now Playing: " + pafylist[choice-1].title)
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
    else:
        print ("Invalid command. Try '?' for help")