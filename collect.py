import json
from twython import Twython
import sys

from config import (consumer_key, consumer_secret, access_token, access_token_secret)
from send import send_to_google_drive

def filter_tweets(tweet, keyword):
	### Method to filter out tweets that might be spam
	### Edit omit.txt to update a list of keywords you want to exclude

	## filter based on keywords in text
	text = tweet[0]['text'].lower()

	with open('omit.txt', 'r') as f:
		##open file with keywords and test them against the tweet
		for line in f:
			omitted_word = line.lower().rstrip()

			if omitted_word in text:
				#if keywords appear in the tweet, its a bad tweet
				return False

	return True


def find_tweets(twitter, place_id, keyword):
	### Return tweets from a certain place id

	#`count` param defaults to 15, maximum of 100. using 3 for now to test
	if keyword == '':
		results = twitter.search(q = 'place:'+place_id, count = '10')
	else:
		results = twitter.search(q = 'place:'+place_id+' '+keyword, count = '10')

	#turn results in json string
	tweets = json.loads( json.dumps(results) )

	reliable_tweets = []

	for i in range(len(tweets['statuses'])):
		tweet_id = tweets['statuses'][i]['id_str']

		#retrieve tweet based on tweet_id
		t = twitter.lookup_status(id = tweet_id)
		tweet = json.loads( json.dumps(t) )

		#this is where we're going to filter these tweets then return
		reliable = filter_tweets(tweet, keyword)

		if reliable == True:
			#sample parse for tweet output
			print tweet[0]['user']['screen_name']+': '+tweet[0]['text']
			reliable_tweets.append(tweet)

	send_to_google_drive(reliable_tweets)



def find_place(location, keyword=''):
	### Determine place id based on querying location

	#configure twython connection
	twitter = Twython(consumer_key, consumer_secret, access_token, access_token_secret)

	results = twitter.search_geo(query = location, max_results = '5')

	#turn results into json string, then turn json string into parsable dictionary
	locations = json.loads( json.dumps(results) )

	#results return different location possibilities based on the location you enter
	#we need the user to tell us which location is the right one to use
	print "Results based on your provided location:"
	for i in range(len(locations['result']['places'])):
		print str(i+1)+'. ', locations['result']['places'][i]['full_name']
		### TODO: option for "other"

	place_number = input('Please enter the location you want to use: ')
	place_number = place_number - 1 #adjust for array counting

	place_id = locations['result']['places'][place_number]['id']

	find_tweets(twitter, place_id, keyword)
