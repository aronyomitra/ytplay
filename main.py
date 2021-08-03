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
        print (str(i+1) + ") " + p.title)
        print (p.author)
        print (p.duration)
        print ()

    choice = int(input("\nEnter selection: "))

audioStreamURL = pafylist[choice-1].getbestaudio().url

player = vlc.MediaPlayer(audioStreamURL)
player.play()

time.sleep(2)
while player.is_playing():
    time.sleep(1)
