from datetime import datetime
from os import getcwd
from PIL import Image, ImageDraw, ImageFont
from textwrap import wrap
from time import ctime
from twitter import *
from MyQR import myqr
import re
import MSWinPrint
import json

def qr_generate(text, fname): 
    version, level, qr_name = myqr.run(
        text,
        version=1,
        level='H',
        picture=None,
        colorized=False,
        contrast=1.0,
        brightness=1.0,
        save_name=fname,
        save_dir=getcwd()
    )

def tweet_to_image(image: str, tweet: dict):
    arial = ImageFont.truetype("arial.ttf")
    height = arial.font.height * len(wrap('%s ' % tweet['text'], width = 40))
    img=Image.open(image)
    img=img.crop((0, -height - 10, img.size[0], img.size[1]))
    draw = ImageDraw.Draw(img)
    draw.rectangle( (0, 0, img.size[0], height + 10), fill="white" )
    #username and text
    draw.text(
        (20, 15),
        '%s:\n%s' % ( tweet['user']['name'],
                      ' \n'.join(wrap('%s ' % tweet['text'], width = 40))
                      ),
        font = arial
    )
    #time
    draw.text((20, img.size[1] - 25), tweet['created_at'])
    img.save('res.png')
    

#read settings for twitter. tokens etc
settings = json.loads(open('settings.json', 'r').read())

#authorising
t = Twitter(auth= OAuth(**settings))

#read tweeples
user_list = []
with open('tweeples.txt', 'r') as tweeples:
    for line in tweeples:
        if line[0] == '#':
            continue
        else:
            parse = line.split('=')
            if len(parse) == 1:
                curtime = ctime()
                parse.append('%s+0000 %s' % (curtime[:-4], curtime[-4:]))
                
            if parse[0][-1] == '\n':
                parse[0] = parse[0][:-1]  #avoiding newline symbols
            if parse[1][-1] == '\n':
                parse[1] = parse[1][:-1]
                
            user_list.append(dict(
                name = parse[0], lastmsg = parse[1]
            ))

def convert(twitter_time):
    if twitter_time[-1] == '\n':
        twitter_time = twitter_time[:-1] #avoiding newline symbols
    return datetime.strptime(twitter_time, '%a %b %d %H:%M:%S %z %Y')

def to_print(print_job): 
    job = MSWinPrint.document(papersize= 'letter')
    job.begin_document('tweet')
    try:
        image = Image.open(print_job)
    except:
        job.text((5, 5), print_job['username'])
        y = 5
        for wrap in print_job['text']:
            y += 15
            job.text((5, y), wrap)
        
        job.text((5, y + 15), print_job['time'])
    else:
        job.image((0, 0), image, (100, 100))
    job.end_document()

def link(text):
    pattern = open('link.rex').read()
    return re.findall(pattern, text)

#get updates
for user in user_list:
    tweets = t.statuses.user_timeline(screen_name=user['name'])
    *new_tweets, = filter(
        lambda x: convert(x['created_at']) > convert(user['lastmsg']), tweets
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
                qr_generate(
                    ''.join(link(tweet['text'])[0]),
                    '{username}{tid}.png'.format(**info)
                )
                tweet['text'] = re.sub(
                    open('link.rex').read(), '', tweet['text']
                )
                tweet_to_image('{username}{tid}.png'.format(**info), tweet)
                to_print('res.png')
            else:
                to_print(info)
        user['lastmsg'] = max(map(lambda x:x['created_at'], new_tweets))

#writing changes
with open('tweeples.txt', 'w') as tweeples:
    for user in user_list:
        tweeples.write('{name}={lastmsg}\n'.format(**user))