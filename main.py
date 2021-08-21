from datetime import datetime
import re
import praw
import os
import csv 
from replit import db
from keep_alive import keep_alive
import time

reddit = praw.Reddit(
    client_id=os.getenv('client_id'),
    client_secret=os.getenv('client_secret'),
    username=os.getenv('username'),
    password=os.getenv('password'),
    user_agent="<ReplyBot1.0>",
)

def clean_string(raw_string):
    cleaned_string = raw_string.lower()
    cleaned_string = re.sub(r'[^A-Za-z0-9 ]+', '', cleaned_string)
    return cleaned_string

class RedditBot:
    def __init__(self, filename):
        self.response_list = []
        
        if len(db) == 0:
          with open(filename) as csv_file:
              csv_reader = csv.reader(csv_file, delimiter=",")
              for row in csv_reader:
                  self.response_list.append(
                                          {
                                            'phrase': clean_string(row[0]),
                                            'reply': row[1]
                                          }
                                          )
          db['response_list'] = self.response_list
        else:
          print("Pulling from DB")
          self.response_list = db['response_list']
    
    def find_match(self, comment):
        for i, dictionary in enumerate(self.response_list):
             if dictionary['phrase'] in clean_string(comment.body):
                 if self.cooled_down(i):
                    self.make_reply(i, comment)
    
    def cooled_down(self, i):
        dictionary = self.response_list[i]
        if 'last_posted' not in dictionary.keys():
            return True
        else:
            now = datetime.now()
            duration = now - datetime.fromtimestamp(dictionary['last_posted'])
            duration_seconds = duration.total_seconds()
            hours = divmod(duration_seconds, 3600)[0]
            if hours >= 0:
                return True
            else:
                print(f"Couldnt post *{dictionary['phrase']}*. Cool Down time: {24 - hours}")
        return False
    
    def make_reply(self, i, comment): 
        dictionary = self.response_list[i] 
        try:
            comment.reply(dictionary['reply'])
            print(comment.body)
            print(dictionary['phrase'])
            print(dictionary['reply'])
            time.sleep(60 * 60 * 3)
        except Exception as e:
            print(e)
        now = datetime.now()
        self.response_list[i]['last_posted'] = now.timestamp()
        db['response_list'] = self.response_list

#db.clear
keep_alive()  
bot = RedditBot("pairs.csv")
subreddit = reddit.subreddit("all")

for comment in subreddit.stream.comments(skip_existing=True):
    bot.find_match(comment)