import fitbit
import gather_keys_oauth2 as Oauth2
import json
from pprint import pprint
import datetime
import csv
import configparser
import os.path



def generateToken():
	"""for OAuth2.0"""
	"""for obtaining Access-token and Refresh-token"""
	server = Oauth2.OAuth2Server(USER_ID, CLIENT_SECRET)
	server.browser_authorize()
	print('FULL RESULTS = %s' % server.oauth.token)
	print('ACCESS_TOKEN = %s' % server.oauth.token['access_token'])
	print('User Id = %s' % server.oauth.token['user_id'])
	 
	ACCESS_TOKEN = server.oauth.token['access_token']
	REFRESH_TOKEN = server.oauth.token['refresh_token']
	user_id = server.oauth.token['user_id']

	authd_client = fitbit.Fitbit(USER_ID, CLIENT_SECRET,
	                             access_token=ACCESS_TOKEN, refresh_token=REFRESH_TOKEN)

	mystring = str(authd_client.client.refresh_token())
	REFRESH_TOKEN = authd_client.client.token['refresh_token']
	ACCESS_TOKEN = authd_client.client.token['access_token']
	user_id = authd_client.client.token['user_id']
	#print (authd_client.client.token['refresh_token'])
	f = open("refresh", "w+")
	line = user_id + "\n" + REFRESH_TOKEN + "\n" + ACCESS_TOKEN
	f.write(line)
	f.close()


################################################################################
#getting the data from the Oauth authorization
parser = configparser.SafeConfigParser()
parser.read('config-mim.ini')
USER_ID = parser.get('Login Parameters', 'USER_ID')
CLIENT_SECRET = parser.get('Login Parameters', 'CLIENT_SECRET')
DATE = '2016-07-11'#the date that you what to retrive the data (yyyy/mm/dd)

#################################################################################
#getting the access token and refreshing it for next use
if os.path.isfile('refresh'):
	f = open('refresh', 'r+')
else:
	generateToken()
	f = open('refresh', 'r+')

userid = f.readline()
REFRESH_TOKEN = f.readline()
ACCESS_TOKEN = f.readline()

f.close()

REFRESH_TOKEN = REFRESH_TOKEN.rstrip('\n')
authd_client = fitbit.Fitbit(USER_ID, CLIENT_SECRET, oauth2=True, access_token=ACCESS_TOKEN, refresh_token=REFRESH_TOKEN)#getting access


mystring = str(authd_client.client.refresh_token())
REFRESH_TOKEN = authd_client.client.token['refresh_token']
ACCESS_TOKEN = authd_client.client.token['access_token']
user_id = authd_client.client.token['user_id']

#saving new access data to access user data next time
f = open("refresh", "w+")
line = user_id + "\n" + REFRESH_TOKEN + "\n" + ACCESS_TOKEN
f.write(line)
f.close()

##################################################################################################################################################

#getting the minute level data
stepsData = authd_client.intraday_time_series('activities/steps', base_date= DATE, detail_level='1min', start_time="00:00", end_time="23:59")

Maxminute = 1440 #number of minutes of data you got
currentMinute = 1#should go until the last mim passed

#getting user nema
name = authd_client.user_profile_get()
name = name['user']['displayName']

#open and prepering the csv file
with open(user_id + '_steps.csv', 'w') as csvfile:
	fieldnames = ['time', 'steps']
	writer = csv.DictWriter(csvfile, lineterminator = '\n', fieldnames=fieldnames)
	spamwriter = csv.writer(csvfile)
	firstrow = {"this is the dateiled steps count (number of steps per minute) of " + name + " on the date of " + DATE}
	spamwriter.writerow(firstrow)
	writer.writeheader()

	#writing the steps on the csv file
	while currentMinute < Maxminute:
		#f.write(x["activities-steps-intraday"]['dataset'][n]['time'])
		csvDataTime =stepsData["activities-steps-intraday"]['dataset'][currentMinute]["time"]
		csvDataValue =stepsData["activities-steps-intraday"]['dataset'][currentMinute]["value"]
		
		writer.writerow({'time': csvDataTime, 'steps': csvDataValue})
		currentMinute = currentMinute+1
		pass


