from sys import argv
from sqlite3 import *
from time import ctime, time

data = connect('data.db')
data.row_factory = Row
cursor = data.cursor()

selector = 'select %s from settings'

def check_settings(): 
    try:
        settings = dict(cursor.execute(selector % '*').fetchall()[0])
    except (OperationalError, IndexError):
        cursor.execute('create table settings(consumer_key text,'
                       'consumer_secret text,'
                       'token text,'
                       'token_secret text)')
        settings = dict(cursor.execute(selector % '*').fetchall())
    return settings

def edit_settings(): 
    settings = check_settings()
    settings['consumer_key'] = input('Enter consumer key: ')
    settings['consumer_secret'] = input('Enter consumer_secret key: ')
    settings['token'] = input('Enter token: ')
    settings['token_secret'] = input('Enter token_secret: ')
    
    cursor.execute("insert into settings values("
                   "'{consumer_key}','{consumer_secret}',"
                   "'{token}','{token_secret}')".format(**settings))
    data.commit()
    settings = dict(cursor.execute(selector % '*').fetchall()[0])

def check_tweeples(): 
    try:
        tweeples = dict(cursor.execute('select * from tweeples').fetchall())
    except OperationalError:
        cursor.execute('create table tweeples(name text unique,lastpost text)')
        tweeples = dict(cursor.execute('select * from tweeples').fetchall())
    return tweeples

def add():
    check_tweeples()
    while True:
        print("Send '###' to exit")
        username = input('Enter username: ')
        if username == '###':
            break
        curtime = ctime()
        cursor.execute(
            'insert into tweeples values(?,?)',
            (username,'%s+0000 %s' % (curtime[:-4], curtime[-4:]))            
        )
        data.commit()
        
def add_list(items):
    curtime = ctime()
    for item in items:
        try:
            cursor.execute(
                'insert into tweeples values(?,?)',
                (item, '%s+0000 %s' % (curtime[:-4], curtime[-4:]))                
            )
        except IntegrityError:
            pass  #user exist
        data.commit()        

def remove():
    check_tweeples()
    subs = dict(
        enumerate(
            [sub[0] for sub in cursor.execute('select name from tweeples').fetchall()]
        )
    )
    for value in subs:
        print('%s. %s' % (value, subs[value]))
    unsubs = [
        int(num) for num in input('Send numbers separeted by commas\n').split(',')
    ]
    for unsub in unsubs:
        cursor.execute("delete from tweeples where name=?", (subs[unsub], ))
    data.commit()

def remove_list(items):
    for item in items:
        cursor.execute("delete from tweeples where name=?", (item, ))
    data.commit()        

def update(name, time):
    cursor.execute(
        'update tweeples set lastpost=? where name=?', (time, name)
    )
    data.commit()

settings = check_settings()
if len(argv) > 1 and argv[1] != 'tui' and not settings:
    edit_settings()
    
tweeples = check_tweeples()
if len(argv) > 1 and argv[1] != 'tui' and not tweeples:
    add()