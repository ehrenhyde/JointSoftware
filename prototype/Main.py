####
#[application libraries]
####
import os
import urllib
import uuid

from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.api import memcache
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp.util import run_wsgi_app

import jinja2
import webapp2
import json

from datetime import *
import calendar

LOCAL_TESTING = False
#Setup for Jinja Template Enviroment
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
# [END application libraries]

DEFAULT_ORG_NAME = "freedivers_brisbane"


#NOTE:To be assigned
class Attendance:
    def getToggleButtonMsg(self,event,user):
        userId = user.key.integer_id()
        currentAttendStatus = 'Decline'
        buttonMsg = ""

        #get the users attending status
        for attendee in event.Attendees:
            if attendee.UserID == userId:
                currentAttendStatus = attendee.AttendingStatus

        #use status to detmine button text
        if currentAttendStatus == 'Attending':
            buttonMsg = 'Maybe'
        elif currentAttendStatus == 'Maybe':
            buttonMsg = 'Unregister'
        else:
            buttonMsg = 'Register'

        return buttonMsg
    
    def getAttendanceStatusName(self,event,user):

        userId = user.key.integer_id()
        currentAttendStatus = 'Decline'
        buttonMsg = ""

        #get the users attending status
        for attendee in event.Attendees:
            if attendee.UserID == userId:
                currentAttendStatus = attendee.AttendingStatus

        return currentAttendStatus

####
#Defining the Entity’s for the Data Store
####

#Attendies are stored as a structured datatype with in the Event Modle
class Attendees(ndb.Model):
        UserID = ndb.IntegerProperty()
        AttendingStatus = ndb.StringProperty()

#An Account entity stores all the information about individual users
class Account(ndb.Model):
	Name = ndb.StringProperty()
	Email = ndb.StringProperty()
	Emergency_Contact = ndb.StringProperty()
	Emergency_Phone= ndb.StringProperty()
	Password = ndb.StringProperty()
	Picture = ndb.BlobProperty(default=None)
	Credits = ndb.IntegerProperty(default=0)
	Admin= ndb.BooleanProperty()
	Treasurer = ndb.BooleanProperty()
	EventManager = ndb.BooleanProperty()
	ProfilePicBlobKey = ndb.BlobKeyProperty()
	session_id = ndb.StringProperty()
	TestField = ndb.StringProperty()

#An Event entitiy stores information requarding the event
class Event(ndb.Model):
	Name = ndb.StringProperty()
	Description  = ndb.TextProperty()
	DateTime = ndb.DateTimeProperty()
	Location = ndb.StringProperty()
	#each event contains a list of attendiees represnted by the Atendees entity
	Attendees = ndb.StructuredProperty(Attendees, repeated=True)
	#calculates the total number of attendee Entities linked to each event (data updates when attendee is added/removed)
	Attendees_count = ndb.ComputedProperty(lambda e: len(e.Attendees))
	Comment = ndb.TextProperty()

####
#[Session Handlers], Responsible for the information management of a logged in User
####
class Session:
    def __init__(self,handler):
        #Requires a webapp requesthandler to be passed as a contructor
        self.handler = handler
        self.session_id = None

    def create_user(self,email,username,password):
        #creates a user in the datastore
        tmp = Account(key_name=Email.lower())
        tmp.Email = username
        tmp.Password = password

        self._sync_user(tmp)

    def _generate_test_user(self):
        ##Used during development when the system could be run in "Local Mode"
        newUser = Account.query(Account.Name == 'Test').get()
        if not newUser:
            newUser = Account()
            newUser.Name = "Test"
            newUser.Email = "test@email.com"
            newUser.Emergency_Contact = "Superman"
            newUser.Emergency_Phone= "04 5932 2343"
            newUser.Password = "test"
            newUser.Picture = None
            newUser.Credits = 4
            newUser.Admin= True
            newUser.Treasurer = True
            newUser.EventManager = True
            newUser.put()
	
	return newUser

    def get_current_user(self):
        #Returns the currently logged in user or "None" if no session

        #test environment
        if LOCAL_TESTING:
            #return dummy user
            return self._generate_test_user()
        
        return self._fetch_user_by_cookie()

    def grab_login(self,username,password):
        #Generates a session for the user if user/pass match database
        tmp = self._fetch_user_with_pass(username,password)
        if tmp:
            self._sync_user(tmp)
        return tmp

    def logout(self):
        #Log out the logged in user
        user = self._fetch_user_by_cookie()
        if user:
            memcache.delete(user.session_id)
            user.session_id = None
            user.put()

    def _gen_session_id(self):
        return uuid.uuid4()

    def _sync_user(self, _user):
        #stores a session_id on the users computer
        #and assigns the same session_id to their profile
        #on the database
        sid = str(self._gen_session_id())
        ssid = '='.join(('ssid',sid))
        self.handler.response.headers.add_header('Set-Cookie',ssid)
        _user.session_id = sid
        self.session_id = sid
        _user.put()
        memcache.add(sid,_user)

    def _fetch_user_by_cookie(self):
        #retrive a user based on the session_id on their computer
        if not self.session_id:
            try:
                sid = self.handler.request.cookies['ssid']
            except:
                sid = ""
                ssid = "=".join(('ssid',sid))
                self.handler.response.headers.add_header('Set-Cookie',ssid)
        else:
            sid = self.session_id

        #data = memcache.get(sid)
        data = None #Remove the caching feature (causes bad behaviour in profile 16/09/2015)
        if data is None:
        
            data = Account.query(Account.session_id == sid).get()
            #if data is not None: memcache.add(sid,data)
            #Remove the caching feature (causes bad behaviour in profile 16/09/2015)

        return data

    def _fetch_user_with_pass(self,u,p):
        #retrives a individual user based on their creds
        diverUserQuery = Account.gql("WHERE Email = :1", u)
        tmp = diverUserQuery.get()
        if not tmp:
            return None
        if tmp.Password != p: return None
        return tmp



#Sesion Creation then redirect to events page		
class Login(webapp2.RequestHandler):
    #provides a login form
    def get(self):
        variables = {
                        'callback_url':self.request.get('continue'),
                        'local_testing': LOCAL_TESTING
                    } 
        template = JINJA_ENVIRONMENT.get_template('login.html')
        self.response.write(template.render(variables))
        
    def post(self):
	c = self.request.get('continue')
        if not c: c = '/events' 
        u = self.request.get('Email') 
        p = self.request.get('Password') 
        tmp = Session(self).grab_login(u,p)
        #if not logged in, redirect to login page but keep requested page as a continue variable
        if not tmp: 
            if tmp is None: msg = 'Bad username and/or password' 
            variables = {
                'message':msg,
                'continue':c
            } 
            template = JINJA_ENVIRONMENT.get_template('login.html')
            self.response.write(template.render(variables)) 
        else:
            strC = str(c)
            self.redirect(strC)

#Logs out user
class Logout(webapp2.RequestHandler):
    def get(self):
        Session(self).logout()
        self.redirect('/login')
####
#[END Session Handlers]
####


####
#[User/Account Page Handlers]
####

#Loads User page, supplies List of users to the Template
class Users(webapp2.RequestHandler):
    def get(self):
        user = Session(self).get_current_user()
        if not user: #todo check for admin
            nextPath = '='.join(('/login?continue',self.request.url))
            self.redirect(nextPath)
        else:
            accounts = Account.query().order(Account.Name)
            template_values = {
                'Accounts' : accounts,
                'user':user
            }
            template = JINJA_ENVIRONMENT.get_template('users.html')
            self.response.write(template.render(template_values))

#Calles Entity from data store and updates details of particular user/account           
class ChangeUserDetails(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        #retrieves information from form and updates target user 
	ID = long(self.request.get('targetUserId'))
	a = Account.get_by_id(ID)
	a.Name =self.request.get('name')
	a.Email =self.request.get('email')
	a.Emergency_Contact =self.request.get('emergencyName')
	a.Emergency_Phone =self.request.get('emergencyMobile')
	a.Password =self.request.get('password')
        #Priviledge Update 
        #If Checked box is submitted, privileged is granted, otherwise removed
	if 'isAdmin' in self.request.POST:
            a.Admin = True
        else:
            a.Admin = False      
        if 'isTreasurer' in self.request.POST:
            a.Treasurer = True
        else:
            a.Treasurer = False
        if 'isEventManager' in self.request.POST:
            a.EventManager = True
        else:
            a.EventManager = False

        if self.get_uploads():
            upload = self.get_uploads()[0]
            a.ProfilePicBlobKey = upload.key()
            
	a.put()# pushes the updates to data store

	self.redirect('/users')#NOTE: Change Redirect 

#NOTE: Need Comment
#https://cloud.google.com/appengine/docs/python/blobstore/

#Uploads profile profile to Account in data store 
class MyProfilePhotoUpload(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        try:
            #fetch image from array of uploads
            upload = self.get_uploads()[0]
            user = Session(self).get_current_user()
            user.ProfilePicBlobKey = upload.key()
            #image storage is handled automatically
            user.put()
            self.redirect('/users')
        except:
            self.error(500)
            
class ViewProfilePhoto(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, photo_key):
        if not blobstore.get(photo_key):
            self.error(404)
        else:
            self.send_blob(photo_key)

#Page Handler for user creation
class CreateUser(webapp2.RequestHandler):
    #loads creates user page(only loads if user is logged in)
    def get(self):
        user = Session(self).get_current_user()
        if not user:
            nextPath = '='.join(('/login?continue',self.request.url))
            self.redirect(nextPath)
        else:
            #Todo check if user is admin else don't show
	    template_values = {
                'user':user
            }
	    template = JINJA_ENVIRONMENT.get_template('createUser.html')
	    self.response.write(template.render(template_values))
    #Creates the account based on form elements passed in from /CreateUserPage
    def post(self):
        #creates empty Account entity for new user account
	a = Account()
	a.Name =self.request.get('name')
	newEmail = self.request.get('email')
	a.Email = newEmail
	a.Emergency_Contact =self.request.get('emergencyName')
	a.Emergency_Phone =self.request.get('emergencyMobile')
	a.Password =self.request.get('password')
	#Priviledge Update 
        #If Checked box is submitted, privileged is granted, otherwise removed
	if 'isAdmin' in self.request.POST:
            a.Admin = True
        else:
            a.Admin = False      
        if 'isTreasurer' in self.request.POST:
            a.Treasurer = True
        else:
            a.Treasurer = False
        if 'isEventManager' in self.request.POST:
            a.EventManager = True
        else:
            a.EventManager = False

        duplicateUsers = Account.query(Account.Email==newEmail)
        atLeastOneDuplicate = False
        for duplicateUser in duplicateUsers:
            atLeastOneDuplicate = True

        if not atLeastOneDuplicate:
            a.put()#adds the new user to data store
	self.redirect('/users')
#loads profile page, passes a single user's details into the template
class Profile(webapp2.RequestHandler):
    def get(self):
        user = Session(self).get_current_user()
        if not user:
            nextPath = '='.join(('/login?continue',self.request.url))
            self.redirect(nextPath)
        else:
            targetUser = None
            
            #if the page was passed a userId look at that profile instead
            #Todo
            #If user.Id == ID (user looks at self) or user.isAdmin
            if self.request.get('userId'):
                targetUserId = long(self.request.get('userId'))
                targetUser = Account.get_by_id(targetUserId)
            #else the logged in user
            else:
                targetUser = user

            userUploadURL = blobstore.create_upload_url('/myProfilePhotoUpload')
            targetUserUploadURL = blobstore.create_upload_url('/changeUserDetails')
            template_values = {
                'user' : user,
                'targetUser': targetUser,
                'userUploadURL':userUploadURL,
                'targetUserUploadURL':targetUserUploadURL
	    }
            template = JINJA_ENVIRONMENT.get_template('profile.html')
            self.response.write(template.render(template_values))

#Removes Account entity from data store
class DeleteAccount(webapp2.RequestHandler):
    def post(self):
        user = Session(self).get_current_user()
        if not user:
            nextPath = '='.join(('/login?continue',self.request.url))
            self.redirect(nextPath)
        else:
            data = json.loads(self.request.body)
            userId = data['userId']
            targetAccount = Account.get_by_id(userId)
            targetAccount.key.delete()#removes the event
            success = True
            jsonRetVal = json.dumps(
                {
                    'success':success
                }
            )
            self.response.write(jsonRetVal)

#Updates an accounts credits, amount is passed in through Javasctipt
class ChangeCredits(webapp2.RequestHandler):
    def post(self):
        data = json.loads(self.request.body)
        userId = data['userId']
        creditsChange = data['creditsChange']
        account = Account.get_by_id(userId)
        account.Credits = account.Credits + int(creditsChange)
        account.put()
        success = True
        jsonRetVal = json.dumps(
            {
                'success':success,
                'newCredits' :account.Credits
            }
        )
        self.response.write(jsonRetVal)

####
#[END User/Account Page Handlers]
####


####
#[Event page Managment]
####		
class EventsMain(webapp2.RequestHandler):
    def get(self):
        user = Session(self).get_current_user()
        if not user:
            nextPath = '='.join(('/login?continue',self.request.url))
            self.redirect(nextPath)
        else:
            #delay to alow for Time zones (server time is UTC, localtime is +10 hours)
            query_date = datetime.now()+timedelta(hours=10)
            
            UpcomingEvents = Event.query(Event.DateTime>=query_date).order(Event.DateTime)

            #PastEvents = Event.query(Event.DateTime<query_date).order(-Event.DateTime)
            cutoff_date = datetime.now()+timedelta(weeks=-52)
            PastEvents = ndb.gql("select * from Event where DateTime<:1 and DateTime>:2 order by DateTime DESC",query_date,cutoff_date)
            
            
            

           
            #Get correct text for attendance button and other UI factors
            for event in UpcomingEvents:
                event.ButtonMsg =  Attendance().getToggleButtonMsg(event,user)
                event.userAttendanceStatus = Attendance().getAttendanceStatusName(event,user)

            
	    template_values = {
                'UpcomingEvents' : UpcomingEvents,
                'PastEvents' : PastEvents,
                'user': user
                }
	    template = JINJA_ENVIRONMENT.get_template('events.html')
            self.response.write(template.render(template_values))	
		
class CreateEvent(webapp2.RequestHandler):

    def addDays(self,sourceDatetime,numDays):
        delay = timedelta(days=numDays)
        return sourceDatetime + delay
        
    def addMonths(self,sourceDatetime,numMonths):
        month = sourceDatetime.month - 1 + numMonths
        year = int(sourceDatetime.year + month / 12 )
        month = month % 12 + 1
        day = min(sourceDatetime.day,calendar.monthrange(year,month)[1])
        hour = sourceDatetime.hour
        minute = sourceDatetime.minute
        second = sourceDatetime.second
        return datetime(year,month,day,hour,minute,second)
        
    def get(self):
        user = Session(self).get_current_user()
        if not user:
            nextPath = '='.join(('/login?continue',self.request.url))
            self.redirect(nextPath)
        else:
	    template_values = {
                'user':user
            }
            template = JINJA_ENVIRONMENT.get_template('createEvent.html')
	    self.response.write(template.render(template_values))			
		
    def post(self):
            
        
        
        intervalType = int(self.request.get('intervaltype'))
                
        strDate = self.request.get('date')
        yearMonthDay = strDate.split('-')
        originalDatetimeValue = datetime(int(yearMonthDay[0]),int(yearMonthDay[1]), int(yearMonthDay[2]))
        datetimeValue = datetime(int(yearMonthDay[0]),int(yearMonthDay[1]), int(yearMonthDay[2]))
        if 'isRepeat' in self.request.POST:
             repeats = int(self.request.get('intervalnum'))
        else:
            repeats = 1
        
        for eventNum in range(repeats):
            user = Session(self).get_current_user()
            a = Event()
            a.Name =self.request.get('name')
            a.Description =self.request.get('desc')
            a.Location = self.request.get('location')
            strTime = self.request.get('time')
            hoursMins = strTime.split(':')
            a.DateTime = datetime.combine( datetimeValue,time(int(hoursMins[0]),int(hoursMins[1])))
            a.put()
            if 'isRepeat' in self.request.POST:
                if intervalType == 1:
                    datetimeValue = self.addDays(originalDatetimeValue,7*(eventNum+1))
                elif intervalType == 2:
                    datetimeValue = self.addDays(originalDatetimeValue,14*(eventNum+1))
                elif intervalType==3:
                    datetimeValue = self.addMonths(originalDatetimeValue,1*(eventNum+1))
            Attendee = Attendees(UserID = user.key.integer_id(),AttendingStatus = 'Attending')
            a.Attendees.append(Attendee)
            a.put()    
        self.redirect('/events')		
		
class EventDetails(webapp2.RequestHandler):
    def get(self):
        user = Session(self).get_current_user()
        if not user:
            nextPath = '='.join(('/login?continue',self.request.url))
            self.redirect(nextPath)
        else:
            UserAttending = False
            targetEventId = long(self.request.get('eventId'))
            targetEvent = Event.get_by_id(targetEventId)
            AttendeeName=[]
            AttendeeStatus=[]
            Accounts = Account.query()
            for attendeeNum in range(targetEvent.Attendees_count):
                attendee =  Account.get_by_id(targetEvent.Attendees[attendeeNum].UserID)
                AttendeeName.insert(attendeeNum, attendee.Name)
                AttendeeStatus.insert(attendeeNum, targetEvent.Attendees[attendeeNum].AttendingStatus)

            buttonMsg = Attendance().getToggleButtonMsg(targetEvent,user)
	    template_values = {
                'user':user,
                'Event':targetEvent,
                'Accounts' : Accounts,
                'buttonMsg': buttonMsg,
                'AttendeeNames': AttendeeName,
                'AttendeeStatus': AttendeeStatus
            }
	    template = JINJA_ENVIRONMENT.get_template('eventDetails.html')
	    self.response.write(template.render(template_values))

    def post(self):
        ID = long(self.request.get('eventId'))
        a = Event.get_by_id(ID)
        a.Name =self.request.get('eventName')
        a.Description =self.request.get('eventDesc')
        a.Location = self.request.get('eventLocation')
        strTime = self.request.get('eventTime')
        hoursMins = strTime.split(':')
        strDate = self.request.get('eventDate')
        yearMonthDay = strDate.split('-')
        datevalue = date(int(yearMonthDay[0]),int(yearMonthDay[1]), int(yearMonthDay[2]))
        a.DateTime = datetime.combine( datevalue,time(int(hoursMins[0]),int(hoursMins[1])))
        a.Comment = self.request.get('eventComment')
        a.put()

        self.redirect('/events')

class DeleteEvent(webapp2.RequestHandler):
    def post(self):
        user = Session(self).get_current_user()
        if not user:
            nextPath = '='.join(('/login?continue',self.request.url))
            self.redirect(nextPath)
        else:
            UserAttending = False
            data = json.loads(self.request.body)
            targetEventId = data['eventId']
            targetEvent = Event.get_by_id(targetEventId)
            Accounts = Account.query()
            for attendeeNum in range(targetEvent.Attendees_count):#loops all attendees
                if targetEvent.Attendees[attendeeNum].AttendingStatus == "Attending":
                    attendee =  Account.get_by_id(targetEvent.Attendees[attendeeNum].UserID)#gets account of attendee
                    #targetEvent.Attendees = [i for i in targetEvent.Attendees if i.UserID != attendee.key.integer_id()]#removes attendie for event
                    #targetEvent.put()#saves event
                    attendee.Credits = user.Credits + 1 #refunds credit
                    attendee.put()#saves user
            targetEvent.key.delete()#removes the event
            success = True
            jsonRetVal = json.dumps(
                {
                    'success':success
                }
            )
            self.response.write(jsonRetVal)

####
#[END Event page Managment]
####

####
#[Attendance Management]
####
class ToggleAttendance(webapp2.RequestHandler):
    def removeAttendee(self,event,user):
        #Update server with values
       
        event.Attendees = [i for i in event.Attendees if i.UserID != user.key.integer_id()]
        event.put()

        #Already refunded when switched to Maybe
        #user.Credits = user.Credits + 1 
        #user.put()

    def addAttendee(self,event,user):
        Attendee = Attendees(UserID = user.key.integer_id(),AttendingStatus = 'Attending')
        event.Attendees.append(Attendee)
        event.put()

        user.Credits = user.Credits - 1
        user.put()

    def makeAttendeeMaybe(self,event,user):

        for attendeeNum in range(event.Attendees_count):#loops all attendees
            if event.Attendees[attendeeNum].UserID == user.key.integer_id():
                event.Attendees[attendeeNum].AttendingStatus = "Maybe"
        event.put()
            

        user.Credits = user.Credits + 1
        user.put()
        
    def post(self):
        data = json.loads(self.request.body)
        eventId = data['eventId']
        userId = data['userId']
        event = Event.get_by_id(eventId)
        validDate = False
        #Timedelay to allow for TimeZones 
        #plus 10 for brisbane time + 1 for hour checking event
        query_date = datetime.now()+timedelta(hours=11)
            
        ValidEvents = Event.query(Event.DateTime>=query_date)
        
        for ValidEvent in ValidEvents:
            if ValidEvent.key.integer_id() == event.key.integer_id() :
                validDate = True 
            else:
                #add in catch for Event Manager to still toggle
                #if user is Active Event Manager
                #ValidDate = True
                success = False
                comment = 'attendence can not be changed to past events or with in 1 hour of Event'
        user = Account.get_by_id(userId)
        if validDate:       
            currentAttendStatus = 'Decline'
            newStatus = 'none'
            newButtonMsg = "none set"
            
            for attendee in event.Attendees:
                if attendee.UserID == userId:
                    currentAttendStatus = attendee.AttendingStatus

            if currentAttendStatus == 'Attending':
                #Make Maybe
                self.makeAttendeeMaybe(event,user)
                newStatus = "Maybe"
                newButtonMsg = 'Unregister'
            elif currentAttendStatus == 'Maybe':
                #Make Decline
                self.removeAttendee(event,user)
                newStatus = "Decline"
                newButtonMsg = 'Register'
            else:
                #Make Attending
                self.addAttendee(event,user)
                newStatus = "Attending"
                newButtonMsg = 'Maybe'
            success = True
        newCredits = user.Credits
       
        if success:
            jsonRetVal = json.dumps(
                {
                    'success':success,
                    'oldStatus':currentAttendStatus,
                    'newStatus':newStatus,
                    'newButtonMsg':newButtonMsg,
                    'newCredits':newCredits,
                    'version':'10'
                }
            )
        else:
            jsonRetVal = json.dumps(
                {
                    'success':success,
                    'comment':comment
                } 
            )
        self.response.write(jsonRetVal)

class GetAttendees(webapp2.RequestHandler):
    def post(self):
        data = json.loads(self.request.body)
        eventId = data['eventId']
        status = data['status']
        event = Event.get_by_id(eventId)
        attendeeNames = []
        for attendeeNum in range(event.Attendees_count):
            attendingStatus = event.Attendees[attendeeNum].AttendingStatus
            if attendingStatus == status:
                attendee =  Account.get_by_id(event.Attendees[attendeeNum].UserID)
                attendeeNames.append(attendee.Name)         
        jsonRetVal = json.dumps(
            {
                'success':True,
                'attendeeNames':attendeeNames
            } 
        )
        self.response.write(jsonRetVal)

class GetAttendeesCount(webapp2.RequestHandler):
    def post(self):
        data = json.loads(self.request.body)
        eventId = data['eventId']
        event = Event.get_by_id(eventId)
        attendeesCount = event.Attendees_count                
        jsonRetVal = json.dumps(
            {
                'success':True,
                'attendeesCount':attendeesCount
            } 
        )
        self.response.write(jsonRetVal)

class PrintAttendees(webapp2.RequestHandler):
    def get(self):
        targetEventId = long(self.request.get('eventId'))
        targetEvent = Event.get_by_id(targetEventId)
        attendeeName=[]
        attendeeStatus=[]
        for attendeeNum in range(targetEvent.Attendees_count):
            attendee =  Account.get_by_id(targetEvent.Attendees[attendeeNum].UserID)
            attendeeName.insert(attendeeNum, attendee.Name)
            attendeeStatus.insert(attendeeNum, targetEvent.Attendees[attendeeNum].AttendingStatus)
            
        template_values = {
            'event':targetEvent,
            'attendeeNames': attendeeName,
            'attendeeStatus': attendeeStatus
        }
        template = JINJA_ENVIRONMENT.get_template('printAttendees.html')
        self.response.write(template.render(template_values))
####
#[END Attendance Management]
####


####
#[DEBUG FUNCTION]
####
#Create Demo User DEBUG use only
##class DemoUsers(webapp2.RequestHandler):
##    def get(self):
##        #Create First User
##	a = Account()
##	a.Name ='DemoUser'
##	a.Email ='test@example.com'
##	a.Password ='1234'
##	a.Admin = True
##        a.Treasurer = True
##        a.EventManager = True
##	a.put()
##	self.redirect('/')
####
#[END DEBUG FUNCTION]
####

####
#[Routing Mangment]
####
app = webapp2.WSGIApplication([
    ('/', Login),
    ('/users',Users),
    ('/createUser', CreateUser),
    ('/changeUserDetails', ChangeUserDetails),
    ('/profile', Profile),
    ('/events',EventsMain),
    ('/createevent',CreateEvent),
    ('/eventDetails',EventDetails),
    ('/login',Login),
    ('/toggleAttendance',ToggleAttendance),
    ('/logout',Logout),
    ('/changeCredits',ChangeCredits),
    ('/DeleteEvent',DeleteEvent),
    ('/DeleteAccount',DeleteAccount),
    ('/myProfilePhotoUpload',MyProfilePhotoUpload),
    ('/ViewProfilePhoto/([^/]+)?', ViewProfilePhoto),
    ('/printAttendees',PrintAttendees),
    #[Debug use]('/DemoUsers',DemoUsers),
    ('/GetAttendees',GetAttendees),
    ('/GetAttendeesCount',GetAttendeesCount)
], debug=True)
####
#[END Routing Mangment]
####
