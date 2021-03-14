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
import config as config

twitter_id = "OtogibaraEra"
q = f"(from:{twitter_id})"
since_date = "201001010000"
until_date = "201912140816"


def download_file(url, page, tweet_id, file_name):
    print("",end="")
    urllib.request.urlretrieve(url, 'media/' + str(page) + '/' + str(tweet_id) + '/' + file_name)

def mkIdDir(page,tweet_id):
    if not os.path.exists('media/' + str(page) + '/' + tweet_id):
        os.mkdir('media/' + str(page) + '/' + tweet_id)

def mkPageDir(page):
    if not os.path.exists('media/' + str(page)):
        os.mkdir('media/' + str(page))

def add_tweet(tweet_id,screen_name,date,reply_id,full_text,ex_urls,media_type,media_names,f):
    data = f"\"{tweet_id}\" {{\n\t\"screenName\": \"{screen_name}\",\n\t\"created_at\": \"{date}\",\n\t\"replyId\": \"{reply_id}\",\n\t\"text\": {repr(full_text)},\n\t\"exUrls\": {ex_urls},\n\t\"mediaType\": \"{media_type}\",\n\t\"mediaNames\": {media_names}\n}},"
    print(data)
    f.write(data)

def get_tweet_status(tweet,page,excerptJson,fullJson):
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

    add_tweet(tweet.id,tweet.user.screen_name,tweet.created_at,tweet.in_reply_to_status_id,tweet.text,ex_urls,media_type,media_urls,excerptJson)
    fullJson.write(json.dumps(tweet._json, indent=4, ensure_ascii=False))
    fullJson.write(",\n")
    #print(json.dumps(tweet._json, indent=4, ensure_ascii=False))


auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
auth.set_access_token(config.access_token, config.access_token_secret)
api = tweepy.API(auth,wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

i = 0

for page in tweepy.Cursor(api.search_full_archive, query=q, maxResults=500,fromDate = since_date,toDate = until_date,environment_name="test4").pages(27):
    i = i+1
    excerptJson = open("json/excerpt_page"+str(i)+".json",mode='a')
    fullJson = open("json/full_page"+str(i)+".json",mode='a')
    mkPageDir(i)
    for tweet in page:
        get_tweet_status(tweet,i,excerptJson,fullJson)

    