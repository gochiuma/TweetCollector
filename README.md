# TweetCollector
## Preparetion
1. `write config.py`  
```
consumer_key = ''  
consumer_secret = ''  
access_token = ''  
access_token_secret = ''  
```
2. `mkdir media`  
3. `mkdir json`  

## Use
### tweetCollector-free.py
tweetCollector-free.py uses free APIs.  
It can collect the latest 3200 tweets.

### Collector-full_archive.py
tweetCollector-free.py uses Twitter Premium Search APIs.  
It can collect tweets for all periods up to the API call limit.  
To use this, you need to subscribe to the Twitter Premium Search API.