from __future__ import print_function
import tweepy
import json
import time
import sqlite3
from dateutil import parser
import cred
from nltk.tokenize import word_tokenize
from spellchecker import SpellChecker
import nltk
nltk.download('stopwords')
nltk.download('punkt')
import string
import re
from textblob import TextBlob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


WORDS = ['#Chadwick Boseman']

CONSUMER_KEY = cred.APIK
CONSUMER_SECRET = cred.APISK
ACCESS_TOKEN = cred.Token
ACCESS_TOKEN_SECRET = cred.TokenS

stopword = nltk.corpus.stopwords.words('english')
# This function takes the 'text' and stores it
# into a MySQL database
conn = sqlite3.connect('tweets.db')
c = conn.cursor()
def store_data(tweet_id, screen_name, text, misspelt, profanity):
    c.execute("INSERT INTO corona VALUES("'"{0}"'","'"{1}"'","'"{2}"'","'"{3}"'","'"{4}"'")".format(tweet_id, screen_name, text, misspelt, profanity))
    conn.commit()

def off(num):
    if num >= 0:
        return 'not offensive'
    else:
        return 'offensive'

def remove_stopwords(text_token):
    text = [word for word in text_token if word not in stopword]
    return text

def remove_punct(text):
    text  = "".join([char for char in text if char not in string.punctuation])
    text = re.sub('[0-9]+', '', text)
    return text

def tweetchecker(text):
    misspelt = []
    text = remove_punct(text)
    spell = SpellChecker()
    text = word_tokenize(text)
    text = remove_stopwords(text)
    misspelled = spell.unknown(text)
    for word in misspelled:
        misspelt.append(spell.correction(word))
    senti = TextBlob(str(text)).sentiment[0]
    print
    return text, len(misspelt), senti

class StreamListener(tweepy.StreamListener):
    #This is a class provided by tweepy to access the Twitter Streaming API.
    def __init__(self, time_limit=700):
        self.start_time = time.time()
        self.limit = time_limit
        super(StreamListener, self).__init__()


    def on_connect(self):
        # Called initially to connect to the Streaming API
        print("You are now connected to the streaming API.")

    def on_error(self, status_code):
        # On error - if an error occurs, display the error / status code
        print('An Error has occured: ' + repr(status_code))
        return False

    def on_data(self, data):
        #This is the meat of the script...it connects to your MySQL and stores the tweet
        if (time.time() - self.start_time) < self.limit:
           # Decode the JSON from Twitter
            datajson = json.loads(data)
            #grab the wanted data from the Tweet
            text = datajson['text']
            screen_name = datajson['user']['screen_name']
            tweet_id = datajson['id']
            created_at = parser.parse(datajson['created_at'])
            #print out a message to the screen that we have collected a tweet
            print("Tweet collected at ",created_at)

            #print('Type ',(remove_punct(text)))
            #Clean data
            tup = tweetchecker(text)
            text = tup[0]
            misspelt_count = tup[1]
            profanity = off(tup[2])
            #insert the data into the MySQL database
            store_data(tweet_id, screen_name, text, misspelt_count, profanity)
            return True
        else:
            c.close()
            conn.close()
            return False
            
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
#Set up the listener. The 'wait_on_rate_limit=True' is needed to help with Twitter API rate limiting.
#listener = StreamListener(api=tweepy.API(wait_on_rate_limit=True))
streamer = tweepy.Stream(auth=auth, listener=StreamListener(time_limit=500), tweet_mode='extended')
print("Tracking: " + str(WORDS))
streamer.filter(track=WORDS)

#------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------

def extract_data():
    conn = sqlite3.connect("tweets.db")
    c = conn.cursor()
    insert_query = "SELECT misspelt FROM corona"
    c.execute(insert_query)
    misspelt = c.fetchall()
    for i in range(len(misspelt)):
        misspelt[i] = int(misspelt[i][0])

    return misspelt

def extract_off():
    conn = sqlite3.connect("tweets.db")
    c = conn.cursor()
    insert_query = "SELECT profanity FROM corona"
    c.execute(insert_query)
    data = c.fetchall()
    off = []
    for i in range(len(data)):
        off.append(data[i][0])
    return off

def str_to_int(array):
    for i in range(len(array)):
        array[i] = int(array[i])

    return array

def count_off(array):
    off = []
    non_off = []
    for i in range(len(array)):
        if array[i] == 'offensive':
             off.append(array[i])
        else:
            non_off.append(array[i])
    return off, non_off

def offandmis():
    sum_non = 0
    sum_off = 0
    for i in range(len(off)):
        if off[i] == 'offensive':
            sum_off = sum_off + misspelt[i]
        else:
            sum_non = sum_non + misspelt[i]
    return sum_non, sum_off

#Offensive words
a = extract_off()
count = count_off(a)
non_off = count[1]
off = count[0]
off = np.array(off)
non_off = np.array(non_off)
names = ['offensive', 'non_offensive']
values = [len(off), len(non_off)]
fig = plt.figure(figsize=(9,3))
ax = fig.add_axes([0,0,1,1])
ax.axis('equal')
ax.pie(values, labels = names, autopct='%1.2f%%')
plt.title('Non and offensive tweets')
plt.show()

#Misspelt words
a = extract_data()
#print(type(a))
sum = 0
misspelt = np.array(a)
std_dvt = np.std(misspelt)
avg = np.average(misspelt)
for i in misspelt:
    sum = sum + i
print('*-------------------------------Misspelt and Corrected words-------------------------------------*')
print('My data set had a total number of ',sum,' misspelt words which were corrected.' )
print('The standard deviation of the number of misspelt words ',std_dvt)
print('The average of misspelt words per tweet were',avg)
print('*------------------------------------------------------------------------------------------------*')

print('*---------------------misspelt words in offensive and non-offensive tweets-----------------------*')
a = offandmis()
values = [a[1], a[0]]
plt.figure(figsize=(9,3))
plt.ylabel('Misspelt words')
plt.bar(names,values)
plt.title('misspelt words in offensive and non-offensive tweets')
plt.show()
print('*------------------------------------------------------------------------------------------------*')
