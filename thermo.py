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

def tweet_to_image(image, tweet: dict):
    arial = ImageFont.truetype("arial.ttf")
    text = wrap('%s ' % tweet['text'], width = 40)
    height = arial.font.height * len(text)

    image = image.crop((0, -height - 10, image.size[0], image.size[1]))
    draw = ImageDraw.Draw(image)
    draw.rectangle( (0, 0, image.size[0], height + 10), fill="white" )
    #username and text
    draw.text(
        (20, 15),
        '%s:\n%s' % ( tweet['user']['name'], ' \n'.join(text)),
        font = arial
    )
    #time
    draw.text((20, image.size[1] - 25), tweet['created_at'])
    return image

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

def to_print(print_job): 
    job = MSWinPrint.document(papersize= 'letter')
    job.begin_document('tweet')
    if type(print_job) is dict:
        job.text((5, 5), print_job['username'])
        y = 5
        for wrap in print_job['text']:
            y += 15
            job.text((5, y), wrap)
        
        job.text((5, y + 15), print_job['time'])
    else:
        job.image((0, 0), print_job, (100, 100))
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
                qr = tweet_to_image(qr, tweet)
                to_print(qr)
            else:
                to_print(info)
            tweeples[user] = max(map(lambda x:x['created_at'], new_tweets))
            update(user, tweeples[user])