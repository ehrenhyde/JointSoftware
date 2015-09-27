#Test Github
import os
import urllib
import uuid

#depreciated from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import memcache

import jinja2
import webapp2
import json
import datetime

LOCAL_TESTING = False

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
# [END imports]

DEFAULT_ORG_NAME = "freedivers_brisbane"

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
    
class Attendiees(ndb.Model):
        UserID = ndb.IntegerProperty()
        AttendingStatus = ndb.StringProperty()

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
	session_id = ndb.StringProperty()

class Event(ndb.Model):
        EventNum =ndb.IntegerProperty()
	Name = ndb.StringProperty()
	Description  = ndb.StringProperty()
	Date= ndb.DateProperty(auto_now_add=True)
	Time = ndb.TimeProperty(auto_now_add=True)
	Location = ndb.StringProperty()
	Attendiees = ndb.StructuredProperty(Attendiees, repeated=True)
	Attendiees_count = ndb.ComputedProperty(lambda e: len(e.Attendiees))
	Comment = ndb.TextProperty()
	
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

            
class changeUserDetails(webapp2.RequestHandler):
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
	a.put()
	self.redirect('/users')

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
            template_values = {
                'user' : user,
                'targetUser': targetUser
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
            AttendingEvents = Event.query(Event.Attendiees.UserID == user.key.integer_id())
            PastEvents = Event.query(Event.Date < datetime.datetime.today())
            UpcomingEvent = Event.query()
            AttendingUpcomingEvent = Event.query()
            for X in AttendingEvents: #removes events that user is attending from all events
               UpcomingEvent = UpcomingEvent.filter(Event.EventNum != X.key.integer_id())

            for X in UpcomingEvent: #removes events that user isnt attending: creating a query pased on Event num.
               AttendingUpcomingEvent = AttendingUpcomingEvent.filter(Event.EventNum != X.key.integer_id())
            
            for X in PastEvents:#removes any event that have passed
               AttendingUpcomingEvent = AttendingUpcomingEvent.filter(Event.EventNum != X.key.integer_id())
            
            for X in PastEvents:#removes any event that have passed
               UpcomingEvent = UpcomingEvent.filter(Event.EventNum != X.key.integer_id())


            UpcomingEvent =UpcomingEvent.order(Event.EventNum,-Event.Date)
	    template_values = {
                'Events' : AttendingUpcomingEvent,
                'Events2' : UpcomingEvent,
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
        user = Session(self).get_current_user()
	a = Event()
	a.Name =self.request.get('name')
	a.Description =self.request.get('desc')
	a.Location = self.request.get('location')
	#a.Date = self.request.get('date')
	a.Date = datetime.datetime.strptime(self.request.get('date'),"%d-%m-%Y")
	#a.Time = self.request.get('time')
	#a.Attendiees = Attendiees(UserID = user.key.integer_id(),AttendingStatus = 'Attending')
	a.put()
	a.EventNum = a.key.integer_id()
	Attedie = Attendiees(UserID = user.key.integer_id(),AttendingStatus = 'Attending')
        a.Attendiees.append(Attedie)
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
            AdttendieName=[]
            AdttendieStatus=[]
            Accounts = Account.query()
            for AdttendieNum in range(targetEvent.Attendiees_count):
                Attendie =  Account.get_by_id(targetEvent.Attendiees[AdttendieNum].UserID)
                if targetEvent.Attendiees[AdttendieNum].UserID == user.key.integer_id():
                    UserAttending = True
                AdttendieName.insert(AdttendieNum, Attendie.Name)
                AdttendieStatus.insert(AdttendieNum, targetEvent.Attendiees[AdttendieNum].AttendingStatus)
	    template_values = {
                'user':user,
                'Event':targetEvent,
                'Accounts' : Accounts,
                'UserAttending': UserAttending,
                'AttendieNames': AdttendieName,
                'AttendieStatus': AdttendieStatus
            }
	    template = JINJA_ENVIRONMENT.get_template('eventDetails.html')
	    self.response.write(template.render(template_values))
       
class ToggleAttendance(webapp2.RequestHandler):
    def post(self):
        data = json.loads(self.request.body)
        status = data['status']
        eventId = data['eventId']
        userId = data['userId']
        #Update server with values
        ThisEvent = Event.get_by_id(eventId)
        attendie = Attendiees(UserID = userId,AttendingStatus = status)
        ThisEvent.Attendiees.append(attendie)

        if status == 'Attending':
            user = Account.get_by_id(userId)
            user.Credits = user.Credits - 1
            user.put()
        
        ThisEvent.put()
        success = True    
        jsonRetVal = json.dumps(
            {
                'success':success          
            }
        )
        self.response.write(jsonRetVal)

class RemoveAttendance(webapp2.RequestHandler):
    def post(self):
        data = json.loads(self.request.body)
        eventId = data['eventId']
        userId = data['userId']
        #Update server with values
        a = Event.get_by_id(eventId)
        a.Attendiees = [i for i in a.Attendiees if i.UserID != userId]
        a.put()

        user = Account.get_by_id(userId)
        user.Credits = user.Credits + 1
        user.put()
        
        success = True    
        jsonRetVal = json.dumps(
            {
                'success':success          
            }
        )
        self.response.write(jsonRetVal)

class CancleEvent(webapp2.RequestHandler):
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
            for AdttendieNum in range(targetEvent.Attendiees_count):#loops all attendies
                Attendie =  Account.get_by_id(targetEvent.Attendiees[AdttendieNum].UserID)#gets account of attendie
                targetEvent.Attendiees = [i for i in targetEvent.Attendiees if i.UserID != Attendie.key.integer_id()]#removes attendie for event
                targetEvent.put()#saves event
                Attendie.Credits = user.Credits + 1 #refunds credit
                Attendie.put()#saves user
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

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/users',Users),
    ('/createUser', CreateUser),
    ('/changeUserDetails', changeUserDetails),
    ('/profile', profile),
    ('/events',EventsMain),
    ('/createevent',CreateEvent),
    ('/eventdetails',EventDetails),
    ('/login',Login),
    ('/toggleAttendance',ToggleAttendance),
    ('/removeAttendance',RemoveAttendance),
    ('/SaveComment',SaveComment),
    ('/logout',Logout),
    ('/changeCredits',ChangeCredits),
    ('/CancleEvent',CancleEvent)
], debug=True)
