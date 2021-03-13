import json #標準のjsonモジュールとconfig.pyの読み込み
from requests_oauthlib import OAuth1Session #OAuthのライブラリの読み込み
import tweepy
import time
import datetime
import urllib.error
import urllib.request
import re
import sys, calendar
import os
import config

twitter_id = OtogibaraEra
start_page = 3
end_page = 4

def download_file(url, page, tweet_id, file_name):
    print("",end="")
    urllib.request.urlretrieve(url, 'media/' + str(page) + '/' + str(tweet_id) + '/' + file_name)

def mkIdDir(page,tweet_id):
    if not os.path.exists('media/' + str(page) + '/' + tweet_id):
        os.mkdir('media/' + str(page) + '/' + tweet_id)

def mkPageDir(page):
    if not os.path.exists('media/' + str(page)):
        os.mkdir('media/' + str(page))

def add_tweet(tweet_id,screen_name,date,reply_id,full_text,ex_urls,media_type,media_urls,f):
    #print("tweet ID:%s" % tweet_id)
    #print("screen name:%s" % screen_name)
    #print("reply ID:%s" % reply_id)
    #print("tweet:%s" % full_text)
    #print("ex_urls:")
    #print(ex_urls)
    #print("media_type:%s" % media_type)
    #print("media_names:")
    #print(media_urls)
    data = f"\"{tweet_id}\" {{\n\t\"screenName\": \"{screen_name}\",\n\t\"created_at\": \"{date}\",\n\t\"replyId\": \"{reply_id}\",\n\t\"text\": {repr(full_text)},\n\t\"exUrls\": {ex_urls},\n\t\"mediaType\": \"{media_type}\",\n\t\"mediaUrls\": {media_urls}\n}},"
    #f.writelines("\"%s\": {\n\tscreenName: \"%s\",\n\treplyId: \"%s\",\n\ttext: \"%s\",\n\texUrls: " % (tweet_id,screen_name,reply_id,repr(full_text)),end="")
    #f.writelines(ex_urls,end="")
    #f.writelines(",\n\tmediaType: \"%s\",\n\tmediaUrls: " % (media_type),end="")
    #f.writelines(media_urls,end="")
    #f.writelines(",\n},")
    print(data)
    f.write(data)

def get_tweet_status(tweet,page,selfJson,officialJson):
    media_type = "null"
    ex_urls = []
    media_urls = []
    if hasattr(tweet, 'extended_entities'): #resultが'extended_entities'属性を持っているか判定
        ex_media = tweet.extended_entities['media']
        for url in tweet.entities['urls']:
            expanded_url=url['expanded_url']
            try:
                full_url= urllib.request.urlopen(expanded_url).geturl()
            except:
                full_url= expanded_url
            ex_urls.append(full_url)

        if 'video_info' in ex_media[0]:
            ex_media_video_variants = ex_media[0]['video_info']['variants']
            media_name = '%s.mp4' % (tweet.id)
            if 'animated_gif' == ex_media[0]['type']:
                media_type = "gif"
                #GIFファイル
                gif_url = ex_media_video_variants[0]['url']
                #print("gif url:%s" % gif_url)
                mkIdDir(page,"%s" % tweet.id)
                download_file(gif_url,page,tweet.id, media_name)
                media_urls.append(media_name)
            else:
                #動画ファイル
                media_type = "movie"
                bitrate_array = []
                for movie in ex_media_video_variants:
                    bitrate_array.append(movie.get('bitrate',0))
                max_index = bitrate_array.index(max(bitrate_array))
                movie_url = ex_media_video_variants[max_index]['url']
                #print("movie url:%s" % movie_url)
                mkIdDir(page,"%s" % tweet.id)
                download_file(movie_url,page,tweet.id, media_name)
                media_urls.append(media_name)
        else:
            #画像ファイル
            for image in ex_media:
                media_type = "pic"
                image_url = image['media_url']
                image_name = image_url.split("/")[len(image_url.split("/"))-1]
                #print("image url:%s" % image_url)
                mkIdDir(page,"%s" % tweet.id)
                download_file(image_url + ':orig',page,tweet.id, image_name)
                media_urls.append(image_name)

    add_tweet(tweet.id,tweet.user.screen_name,tweet.created_at,tweet.in_reply_to_status_id,tweet.full_text,ex_urls,media_type,media_urls,selfJson)
    officialJson.write(json.dumps(tweet._json, indent=4, ensure_ascii=False))
    officialJson.write(",\n")
    #print(json.dumps(tweet._json, indent=4, ensure_ascii=False))


auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
auth.set_access_token(config.access_token, config.access_token_secret)
api = tweepy.API(auth)

for i in range(start_page,end_page+1):
    selfJson = open("json/selfmake_page"+str(i)+".json",mode='a')
    officialJson = open("json/official_page"+str(i)+".json",mode='a')
    mkPageDir(i)
    public_tweets = api.user_timeline(screen_name=twitter_id, count=200, page=i,tweet_mode='extended', include_entities=True)
    for tweet in public_tweets:
        get_tweet_status(tweet,i,selfJson,officialJson)
    