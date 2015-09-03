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


DEFAULT_ORG_NAME = "freedivers_brisbane"

"""def org_key(org_name=DEFAULT_ORG_NAME):
    #Constructs a Datastore key for a freediving organisation entity.
    #We use org_name as the key.

    return ndb.Key('Organisation',org_name)"""

"""def diverUser_key(userId):
    return ndb.Key('DiverUser',userId)"""


#class DiverUser(ndb.Model):
    #stores info about users
    #userId = ndb.StringProperty(indexed=True)
    #fruit = ndb.StringProperty(indexed=False)
    #isTreasurer = ndb.BooleanProperty(indexed=False)

    # general info
    #firstName = db.StringProperty(Required=True)
    #lastName = db.StringProperty(Required=True)
    #password = db.StringProperty(Required=True)
    #role = db.StringProperty(Required=True,choices=set(["treasurer","eventManager","user"]))
                                                                                                                                                                                                                            choices=set(["treasurer","eventManager","user"]))
    #email = db.StringProperty(Required=True)
    #photo = db.blob(default=None)
    #credit = db.IntegerProperty(default=0)
    #registrationDate = DateProperty()
                                            
    # emergancy contact
    #emergencyName = db.StringProperty(Required=True)
    #emergencyMobile = db.StringProperty(Required=True)

#events
"""class events(ndb.Model):
#	# general info
#	eventName = db.StringProperty(Required=True)
#	date = DateProperty()
#	location = PostalAddress()
#	description = db.Text()"""
	
class MainPage(webapp2.RequestHandler):
    def get(self):
        #org_name = self.request.get('org_name',DEFAULT_ORG_NAME)
        #greetings_query = Greeting.query(
        #    ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
        #greetings = greetings_query.fetch(10)

	#googleUser = users.get_current_user()
        #userId = googleUser.user_id()
        #diverUserQuery = DiverUser.gql("WHERE userId = :1", userId)
        #diverUser = diverUserQuery.get()

        #isTreasurer = False
        #if diverUser:
        #    isTreasurer = diverUser.isTreasurer# or diverUser.userId == '113550965061104695630' ehren's gmail
	
        #if googleUser:
        #    url = users.create_logout_url(self.request.uri)
        #    url_linktext = 'Logout'
        #else:
        #    url = users.create_login_url(self.request.uri)
        #    url_linktext = 'Login'

        #template_values = {
        #    'isTreasurer':True#isTreasurer
        #}

        #template = JINJA_ENVIRONMENT.get_template('index.html')
        #self.response.write(template.render(template_values))
        self.response.write("<h1>WTF</h1>")
	
"""class Events(webapp2.RequestHandler):
    def get(self):
        self.response.write("EVENTS")"""
		
		
	
"""class DiverUserAdd(webapp2.RequestHandler):
    def get(self):
        templateValues={}
        template = JINJA_ENVIRONMENT.get_template('userAdd.html')
        self.response.write(template.render(templateValues))
        
    def post(self):
        #capture the form data and save to db
        user = users.get_current_user()
        userId = user.user_id()
        #if user:
        #        userId = user.user_id()
        #else:
        #        self.redirect(users.create_login_url(self.request.uri))
        
        org_name = DEFAULT_ORG_NAME
        newUser = DiverUser(parent=org_key(org_name))
        
        newUser.fruit = self.request.get('fruit')
        newUser.userId = userId
        newUser.isTreasurer = False

        #newUser.firstName = self.request.get('firstName')
        #newUser.lastName = self.request.get('lastName')
        #newUser.password = self.request.get('password')
        #newUser.role = self.request.get('role')
        #newUser.email = self.request.get('email')
        #not photo yet
        #let credit default
        #not registration date yet
        #newUser.emergencyName = self.request.get('emergencyName')
        #newUser.emergencyMobile = self.request.get('emergencyMobile')
        
        newUser.put()

        query_params = {'org_name': org_name}
        self.redirect('/?' + urllib.urlencode(query_params))"""

"""class DiverUserUpdate(webapp2.RequestHandler):
    def post(self):
        
        googleUser = users.get_current_user()
        userId = googleUser.user_id()
        
        diverUserQuery = DiverUser.gql("WHERE userId = :1", userId)
        diverUser = diverUserQuery.get()
        msg = "not set"
        if diverUser:
            diverUser.fruit = self.request.get('fruit')
            diverUser.put()
            msg = "put"
        else:
            msg = "not put"
        query_params = {'msg': msg}
        self.redirect('/?' + urllib.urlencode(query_params))"""
    
"""class Users(webapp2.RequestHandler):

	def get(self):
            name = self.request.get('name')
            reps = int(self.request.get('reps'))
            
            user = users.get_current_user()

            currentUserId = user.user_id()
            
            if user:
                    name = user.nickname()
            else:
                    self.redirect(users.create_login_url(self.request.uri))
            
            template_values = {}
            template = JINJA_ENVIRONMENT.get_template('users.html')
            self.response.write(template.render(template_values))"""

app = webapp2.WSGIApplication([
        ('/',MainPage)
        #('/events',Events),
        #('/users',Users),
        #('/userAdd',DiverUserAdd),
        #('/userUpdate',DiverUserUpdate)
], debug = True)
