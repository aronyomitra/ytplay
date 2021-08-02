from urllib import request
import re
import pafy
import vlc
import time

query = input("Enter youtube search query: ")

query = query.replace(' ', '+')

url = 'https://youtube.com/results?search_query=' + query

resp = request.urlopen(url)
respData = resp.read()

videos = re.findall(r'watch\?v=(\S{11})', str(respData))
pafylist = []

for i in range (0, 5):
    temp = "https://youtube.com/watch?v=" + videos[i]
    p = pafy.new(temp, basic = False)
    pafylist.append(p)

print ()
for i in range (0, len(pafylist)):
    p = pafylist[i]
    print (str(i+1) + ") " + p.title)
    print (p.author)
    print (p.duration)
    print ()

choice = int(input("\nEnter selection: "))
audioStreamURL = pafylist[choice-1].getbestaudio().url

# print (audioStreamURL)

player = vlc.MediaPlayer(audioStreamURL)
player.play()

time.sleep(2)
while player.is_playing():
    time.sleep(1)