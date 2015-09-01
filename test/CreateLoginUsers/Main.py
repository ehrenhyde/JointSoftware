#Test Github
import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
# [END imports]

class Account(ndb.Model):
	name = ndb.StringProperty()
	Email = ndb.StringProperty()
	Emergency_Contact = ndb.StringProperty()
	Emergency_Phone= ndb.StringProperty()
	Password = ndb.StringProperty()
	Picture = ndb.BlobProperty(default=None)
	Credits = ndb.IntegerProperty(default=0)
	Admin= ndb.BooleanProperty()
	Treasurer = ndb.BooleanProperty()
	EventManager = ndb.BooleanProperty()

class Event(ndb.Model):
	name = ndb.StringProperty()
	Description  = ndb.StringProperty()
	Date= ndb.DateProperty(auto_now_add=True)
	Time = ndb.TimeProperty(auto_now_add=True)
	Duration = ndb.IntegerProperty()
	Location = ndb.StringProperty()

	#Sesion Creation then redirect to events page		
class Login(webapp2.RequestHandler):
    def post(self):
		self.redirect('/events')
		
#Sesion deletion then redirect to login page		
class Logout(webapp2.RequestHandler):
    def get(self):
		self.redirect('/')
	
class MainPage(webapp2.RequestHandler):
    def get(self):
		template_values = {}
		template = JINJA_ENVIRONMENT.get_template('login.html')
		self.response.write(template.render(template_values))

class Users(webapp2.RequestHandler):
    def get(self):
		accounts = Account.query().order(Account.name)
		template_values = {
		'Accounts' : accounts,
		}
		template = JINJA_ENVIRONMENT.get_template('users.html')
		self.response.write(template.render(template_values))
class changeUserDetails(webapp2.RequestHandler):
    def post(self):
		ID = long(self.request.get('userId'))
		a = Account.get_by_id(ID)
		a.name =self.request.get('name')
		a.Email =self.request.get('email')
		a.Emergency_Contact =self.request.get('emergencyName')
		a.Emergency_Phone =self.request.get('emergencyMobile')
		a.Password =self.request.get('password')
		#a.Admin = self.request.get('isAdmin')
		#a.Treasurer = self.request.get('isTreasurer')
		#a.EventManager = self.request.get('isEventManager')
		a.put()
		self.redirect('/users')

class CreateUser(webapp2.RequestHandler):
    def get(self):
		template_values = {}
		template = JINJA_ENVIRONMENT.get_template('createUser.html')
		self.response.write(template.render(template_values))

    def post(self):
		a = Account()
		a.name =self.request.get('name')
		a.Email =self.request.get('email')
		a.Emergency_Contact =self.request.get('emergencyName')
		a.Emergency_Phone =self.request.get('emergencyMobile')
		a.Password =self.request.get('password')
		a.Admin = False
		a.Treasurer = False
		a.EventManager = False
		a.put()
		self.redirect('/users')

class profile(webapp2.RequestHandler):
      def get(self): 
		ID = long(self.request.get('userId'))
		user = Account.get_by_id(ID)
		template_values = {
		'user' : user,
		}
		template = JINJA_ENVIRONMENT.get_template('profile.html')
		self.response.write(template.render(template_values))	
		
class EventsMain(webapp2.RequestHandler):
    def get(self):
		template_values = {}
		template = JINJA_ENVIRONMENT.get_template('events.html')
		self.response.write(template.render(template_values))	
		
class CreateEvent(webapp2.RequestHandler):
    def get(self):
		template_values = {}
		template = JINJA_ENVIRONMENT.get_template('createEvent.html')
		self.response.write(template.render(template_values))			
		
    def post(self):
		a = Event()
		a.name =self.request.get('name')
		a.Description =self.request.get('desc')
		a.Location = self.request.get('location')
		a.put()
		self.redirect('/events')		
		
class EventDetails(webapp2.RequestHandler):
    def get(self):
		template_values = {}
		template = JINJA_ENVIRONMENT.get_template('eventDetails.html')
		self.response.write(template.render(template_values))
		
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
	('/logout',Logout)
	
], debug=True)