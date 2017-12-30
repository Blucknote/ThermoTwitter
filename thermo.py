from data import * 
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from sys import argv
from textwrap import wrap
from twitter import *
from qrcode.MyQR import myqr
import re
import MSWinPrint

PRINT_WIDTH = 20

def qr_generate(text, fname): 
    qr_name = myqr.run(
        text,
        version=1,
        level='H',
        picture=None,
        colorized=False,
        contrast=1.0,
        brightness=1.0,
        RAM= True
    )
    return qr_name

def tweet_to_image(qr: Image, tweet: dict):    
    #username and text
    to_print(tweet, True)
    to_print(qr)
    #time
    to_print(tweet['created_at'])

#check args
if len(argv) > 1:
    if argv[1] == 'add':
        add()
    if argv[1] == 'remove':
        remove()
    if argv[1] == 'settings':
        edit_settings()
    if argv[1] == 'tui':
        try:
            import asciimatics
        except:
            import pip
            pip.main(['install', 'asciimatics'])
        else:
            import tui    

#authorising
t = Twitter(auth= OAuth(**settings))

def convert(twitter_time):
    return datetime.strptime(twitter_time, '%a %b %d %H:%M:%S %z %Y')

def to_print(data, qr = False): 
    job = MSWinPrint.document(papersize= 'letter')
    job.setfont("arial", 8)
    job.begin_document('tweet')
    if type(data) is dict:
        job.text((5, 5), data['user']['name'])
        y = 5
        for line in wrap(data['text'], width= PRINT_WIDTH):
            y += 15
            job.text((5, y), line)
        if not qr:
            job.text((5, y + 15), data['created_at'])
    elif type(data) is str:
        job.text((5, 0), data)
    else:
        job.image((0, -15), data, (120, 120))
    job.end_document()

def link(text):
    pattern = open('link.rex').read()
    return re.findall(pattern, text)

#get updates
for user in tweeples:
    tweets = t.statuses.user_timeline(screen_name=user)
    *new_tweets, = filter(
        lambda x: convert(x['created_at']) > convert(tweeples[user]),
        tweets
    )
    if new_tweets:
        for tweet in new_tweets:
            if link(tweet['text']):
                qr = qr_generate(''.join(link(tweet['text'])[0]), '111.png')
                tweet['text'] = re.sub(
                    open('link.rex').read(), '', tweet['text']
                )

                tweet_to_image(qr, tweet)
            else:
                to_print(tweet)
        tweeples[user] = max(map(lambda x:x['created_at'], new_tweets))
        update(user, tweeples[user])