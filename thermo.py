from data import * 
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from sys import argv
from textwrap import wrap
from twitter import *
from qrcode.MyQR import myqr
import re
import MSWinPrint

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
    arial = ImageFont.truetype("arial.ttf", size= 6)
    text = wrap('%s ' % tweet['text'], width = 40)
    height = arial.font.height * len(text)
    
    #username and text
    to_print('%s:\n%s' % ( tweet['user']['name'], ' \n'.join(text)))
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

def to_print(data): 
    job = MSWinPrint.document(papersize= 'letter')
    job.begin_document('tweet')
    if type(data) is dict:
        job.text((5, 5), data['username'])
        y = 5
        for wrap in data['text']:
            y += 15
            job.text((5, y), wrap)
        
        job.text((5, y + 15), data['time'])
    elif type(data) is str:
        job.text((5, 5), data)
    else:
        job.image((0, 0), data, (100, 100))
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
            info = dict(
                username = '%s:' % tweet['user']['name'],
                tid = tweet['id'],
                text = wrap(tweet['text'], width= 40),
                time = tweet['created_at']
            )
            if link(tweet['text']):
                qr = qr_generate(
                    ''.join(link(tweet['text'])[0]), 
                    '{username}{tid}.png'.format(**info)
                )
                tweet['text'] = re.sub(
                    open('link.rex').read(), '', tweet['text']
                )
                tweet_to_image(qr, tweet)
            else:
                to_print(info)
            tweeples[user] = max(map(lambda x:x['created_at'], new_tweets))
            update(user, tweeples[user])