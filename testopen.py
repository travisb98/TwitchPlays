

with open('babygotback.txt','r') as f:


    lyrics = f.read().split("\n").trim()
    print(lyrics)