from os import startfile
from twitter import *
from time import ctime
from datetime import datetime
import json

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
                parse.append('%s+0000 %s' % (ctime()[:-4], ctime()[-4:]))
                
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

template ='''{username}:
    {text}
        {time}

'''

to_print = ''

#get updates
for user in user_list:
    tweets = t.statuses.user_timeline(screen_name=user['name'])
    *new_tweets, = filter(
        lambda x: convert(x['created_at']) > convert(user['lastmsg']), tweets
    )
    if new_tweets:
        for tweet in new_tweets:
            info = dict(
                username = tweet['user']['name'],
                text = tweet['text'],
                time = tweet['created_at']
            )
            to_print += template.format(**info)
        user['lastmsg'] = max(map(lambda x:x['created_at'], new_tweets))

#writing changes
with open('tweeples.txt', 'w') as tweeples:
    for user in user_list:
        tweeples.write('{name}={lastmsg}\n'.format(**user))
        
#sending to printer
if to_print:
    with open('tweets.txt', 'w', encoding= 'utf-8') as tempfile:
        tempfile.write(to_print)
    startfile('tweets.txt', 'print')