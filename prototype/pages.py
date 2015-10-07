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

import model
import fishcakesessions

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.redirect('/login')

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

            
class changeUserDetails(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        #Todo add security that checks logged in user is admin
	ID = long(self.request.get('targetUserId'))
	a = Account.get_by_id(ID)
	a.Name =self.request.get('name')
	a.Email =self.request.get('email')
	a.Emergency_Contact =self.request.get('emergencyName')
	a.Emergency_Phone =self.request.get('emergencyMobile')
	a.Password =self.request.get('password')
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
            
	a.put()

	self.redirect('/users')

#https://cloud.google.com/appengine/docs/python/blobstore/
class myProfilePhotoUpload(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        try:
            upload = self.get_uploads()[0]
            user = Session(self).get_current_user()
            user.ProfilePicBlobKey = upload.key()
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

class CreateUser(webapp2.RequestHandler):
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

    def post(self):
        #Todo check login as extra security measure
	a = Account()
	a.Name =self.request.get('name')
	a.Email =self.request.get('email')
	a.Emergency_Contact =self.request.get('emergencyName')
	a.Emergency_Phone =self.request.get('emergencyMobile')
	a.Password =self.request.get('password')
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
	a.put()
	self.redirect('/users')

class Logout(webapp2.RequestHandler):
    def get(self):
        Session(self).logout()
        self.redirect('/login')

class profile(webapp2.RequestHandler):
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
		
class EventsMain(webapp2.RequestHandler):
    def get(self):
        user = Session(self).get_current_user()
        if not user:
            nextPath = '='.join(('/login?continue',self.request.url))
            self.redirect(nextPath)
        else:
            query_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            UpcomingEvents = Event.query(Event.Date>=query_date).order(Event.Date)

            PastEvents = Event.query()
            
            for X in UpcomingEvents:
                PastEvents = PastEvents.filter(Event.Name != X.Name)
            
	    template_values = {
                'UpcomingEvents' : UpcomingEvents,
                'PastEvents' : PastEvents,
                'user': user
                }
	    template = JINJA_ENVIRONMENT.get_template('events.html')
            self.response.write(template.render(template_values))	
		
class CreateEvent(webapp2.RequestHandler):
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
            #todo add security for create event( user is event manager)
        
        if 'isRepeat' in self.request.POST:
            intervaltype = int(self.request.get('intervaltype'))
            if intervaltype == 1:
                delay = timedelta(days=7)
            elif intervaltype == 2:
                delay = timedelta(days=14)
            elif intervaltype == 3:
                delay = timedelta(month=1)    
        strDate = self.request.get('date')
        yearMonthDay = strDate.split('-')
        datevalue = date(int(yearMonthDay[0]),int(yearMonthDay[1]), int(yearMonthDay[2]))
       
        if 'isRepeat' in self.request.POST:
             repeats = int(self.request.get('intervalnum'))
        else:
            repeats = 1
        
        for eventnum in range(repeats):
            user = Session(self).get_current_user()
            a = Event()
            a.Name =self.request.get('name')
            a.Description =self.request.get('desc')
            a.Location = self.request.get('location')
            a.Date =  datevalue
            if 'isRepeat' in self.request.POST:
                datevalue = datevalue + delay
            strTime = self.request.get('time')
            hoursMins = strTime.split(':')
            a.Time = time(int(hoursMins[0]),int(hoursMins[1]))
            #a.Attendees = Attendees(UserID = user.key.integer_id(),AttendingStatus = 'Attending')
            a.put()
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
                if targetEvent.Attendees[attendeeNum].UserID == user.key.integer_id():
                    UserAttending = True
                AttendeeName.insert(attendeeNum, attendee.Name)
                AttendeeStatus.insert(attendeeNum, targetEvent.Attendees[attendeeNum].AttendingStatus)
	    template_values = {
                'user':user,
                'Event':targetEvent,
                'Accounts' : Accounts,
                'UserAttending': UserAttending,
                'AttendeeNames': AttendeeName,
                'AttendeeStatus': AttendeeStatus
            }
	    template = JINJA_ENVIRONMENT.get_template('eventDetails.html')
	    self.response.write(template.render(template_values))
       
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
        if event.Date> date.today():

            validDate = True 
            
        elif event.Date == date.today():
             #TODO if it is today make sure its not with in hour
           # if event.Date != date.today():
            validDate = True 
            #else:
                #hour_delay = timedelta(hours=1)#time 1 hour before event
                #valid_time = event.Time - hour_delay
                #if valid_time < time.localtime(time.time()):
                    #validDate = true
                #else:
                    #success = False
                    #comment = 'attendence can not be changed 1 hour before event'    
        
        else:
            success = False
            comment = 'attendence can not be changed to past events'

        if validDate:       
            user = Account.get_by_id(userId)
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
                newButtonMsg = 'Change to Maybe'
            success = True
                
       
        if success:
            jsonRetVal = json.dumps(
                {
                    'success':success,
                    'oldStatus':currentAttendStatus,
                    'newStatus':newStatus,
                    'newButtonMsg':newButtonMsg,
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

class CancelEvent(webapp2.RequestHandler):
    def get(self):
        user = Session(self).get_current_user()
        if not user:
            nextPath = '='.join(('/login?continue',self.request.url))
            self.redirect(nextPath)
        else:
            UserAttending = False
            targetEventId = long(self.request.get('eventId'))
            targetEvent = Event.get_by_id(targetEventId)
            Accounts = Account.query()
            for attendeeNum in range(targetEvent.Attendees_count):#loops all attendees
                attendee =  Account.get_by_id(targetEvent.Attendees[attendeeNum].UserID)#gets account of attendee
                targetEvent.Attendees = [i for i in targetEvent.Attendees if i.UserID != attendee.key.integer_id()]#removes attendie for event
                targetEvent.put()#saves event
                attendee.Credits = user.Credits + 1 #refunds credit
                attendee.put()#saves user
            targetEvent.key.delete()#removes the event
            self.redirect('/events')   

class SaveComment(webapp2.RequestHandler):
    def post(self):
        data = json.loads(self.request.body)
        eventId = data['eventId']
        comment = data['Comment']
        #Update server with values
        a = Event.get_by_id(eventId)
        a.Comment = comment
        a.put()
        success = True    
        jsonRetVal = json.dumps(
            {
                'success':success          
            }
        )
        self.response.write(jsonRetVal)

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
                'success':success
            }
        )
        self.response.write(jsonRetVal)
