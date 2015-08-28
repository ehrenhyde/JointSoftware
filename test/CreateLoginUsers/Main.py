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
	
class MainPage(webapp2.RequestHandler):
    def get(self):
		accounts = Account.query().order(Account.name)
		template_values = {
		'Accounts' : accounts,
		}
		template = JINJA_ENVIRONMENT.get_template('users.html')
		self.response.write(template.render(template_values))


class AddAccount(webapp2.RequestHandler):
    def get(self):
		template_values = {}
		template = JINJA_ENVIRONMENT.get_template('createUser.html')
		self.response.write(template.render(template_values))

class CreateAccount(webapp2.RequestHandler):
    def post(self):
		a = Account()
		a.name =self.request.get('name')
		a.Email =self.request.get('email')
		a.Emergency_Contact =self.request.get('emergencyName')
		a.Emergency_Phone =self.request.get('emergencyMobile')
		a.Password =self.request.get('password')
		a.put()
		self.redirect('/')

app = webapp2.WSGIApplication([
    ('/', MainPage),
	('/AddAccount',AddAccount),
    ('/createUser', CreateAccount),
], debug=True)