import fitbit
import gather_keys_oauth2 as Oauth2
import time
import datetime
from collections import namedtuple
import json
import configparser

#############################################################################
#getting the data from the Oauth authorization
parser = configparser.SafeConfigParser()
parser.read('config.ini')
USER_ID = parser.get('Login Parameters', 'USER_ID')
CLIENT_SECRET = parser.get('Login Parameters', 'CLIENT_SECRET')

##############################################################################
#data structures
ActBasic = namedtuple("ActBasic", "steps actMinutes calories distance")
ActPercent = namedtuple("ActPercent", "steps actMinutes calories distance")

################################################################################
#login in
### find user in the file(just demo1) and make the Oauth autentication
##case login in isnt in the file before,  create user 
###create user
def finduser(user):

	f = open('user.txt', 'a+')
	f.seek(0)
	lines = f.read()
	if lines.find(user)!=-1:
		print ("user exist")
		f.close()
		return True
	else:
		print("user dosnt exist, creating user...")
		f.write(user)
		f.write("\n")
		print ("user created")
		f.close()
		return False
################################################################

#####make Oauth autentication ----test 2----
def generateToken(user):
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
	f = open(user +"_refresh", "w+")
	line = user_id + "\n" + REFRESH_TOKEN + "\n" + ACCESS_TOKEN
	f.write(line)
	f.close()

############################################################

############################################################
#refresh token 
def refresh(user):
	
	f = open(user +'_refresh', 'r+')
	userid = f.readline()
	REFRESH_TOKEN = f.readline()
	ACCESS_TOKEN = f.readline()

	f.close()
	REFRESH_TOKEN = REFRESH_TOKEN.rstrip('\n')
	authd_client = fitbit.Fitbit(USER_ID, CLIENT_SECRET, oauth2=True, access_token=ACCESS_TOKEN, refresh_token=REFRESH_TOKEN)


	mystring = str(authd_client.client.refresh_token())
	REFRESH_TOKEN = authd_client.client.token['refresh_token']
	ACCESS_TOKEN = authd_client.client.token['access_token']
	user_id = authd_client.client.token['user_id']
	#print (authd_client.client.token['refresh_token'])
	f = open(user +"_refresh", "w+")
	line = user_id + "\n" + REFRESH_TOKEN + "\n" + ACCESS_TOKEN
	f.write(line)
	f.close()
	return authd_client

def getActivities(user):
	authd_client = refresh(user)
	with open(user+'_Activities.json', 'w') as fp:
		json.dump(authd_client.activities(), fp)

def getActivitiesBasic(user):
	getActivities(user)
	with open(user+'_Activities.json') as data_file:
		data = json.load(data_file)
    
	activeMinutes = data['summary']['lightlyActiveMinutes']
	caloriesOut = data['summary']['caloriesOut']
	distance = data['summary']['distances'][1]['distance']
	steps = data['summary']['steps']


	
	return ActBasic(steps, activeMinutes, caloriesOut, distance)

def percentActivities(user):
	getActivities(user)
	with open(user+'_Activities.json') as data_file:
		data = json.load(data_file)
	Gsteps = data['goals']['steps']
	GactiveMinutes = data['goals']['activeMinutes']
	GcaloriesOut = data['goals']['caloriesOut']
	Gdistance = data['goals']['distance']
    
	activeMinutes = data['summary']['lightlyActiveMinutes']
	caloriesOut = data['summary']['caloriesOut']
	distance = data['summary']['distances'][1]['distance']
	steps = data['summary']['steps']

	activeMinutesP = activeMinutes / GactiveMinutes
	caloriesOutP =	caloriesOut / GcaloriesOut
	distanceP = distance / Gdistance
	stepsP = steps / Gsteps

	
	return ActPercent(stepsP, activeMinutesP, caloriesOutP, distanceP)

############################################################
#time analise
def initTime(HR, MIM, SEC):
	#set initial time with current day
	now = datetime.datetime.now() 
	HRi = HR
	MIMi = MIM
	SECi = SEC
	initTime = now.replace(hour = HRi, minute = MIMi, second = SECi, microsecond = 0)
	return initTime

def endTime(HR,MIM,SEC):
	#set end  time eith current day
	now = datetime.datetime.now()  
	HRe = HR
	MIMe = MIM
	SECe = SEC
	endTime = now.replace(hour = HRe, minute = MIMe, second = SECe, microsecond = 0)
	return endTime

def timePercentage():
	now = datetime.datetime.now() 
	iniTime = initTime(9,0,0)
	enTime = endTime(19,0,0)
	if enTime > now > iniTime:
		elapsedTime = datetime.datetime.now() - iniTime
		MaxElapsedTime = enTime - iniTime
		return elapsedTime / MaxElapsedTime
	else:
		return 0
	#return (elapsedTime(endTime, initTime) / MaxElapsedTime(endTime, initTime))

##############################################################

# get user goals
# get user current stats (steps, distance, etc)
#get corrent time to compere with stats complete percentage
####if (init time - current time)/total time < stats/goal
		####send proper message


if __name__ == '__main__':
	user = input("user:")
	if not finduser(user):
		#create token
		generateToken(user)

	percentageTime = timePercentage()
	print("by now it have already passed " + str(percentageTime) + " of your setted activity time during the day")
	Act = getActivitiesBasic(user)
	print ("and you have  walked " +str(Act.steps)+ " today")
