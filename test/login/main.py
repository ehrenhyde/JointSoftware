import os
import urllib
import uuid

#from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import memcache

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

DEFAULT_ORG_NAME = "freedivers_brisbane"

class User(ndb.Model):
    username = ndb.StringProperty()
    password = ndb.StringProperty()
    session_id = ndb.StringProperty()

class Session:
    def __init__(self,handler):
        #Requires a webapp requesthandler to be passed as a contructor
        self.handler = handler
        self.session_id = None

    def create_user(self,email,username,password):
        #creates a user in the datastore
        tmp = User(key_name=username.lower())
        tmp.username = username
        tmp.password = password

        self._sync_user(tmp)

    def get_current_user(self):
        #Returns the currently logged in user or "None" if no session
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
        sid = str(self._gen_session_id())
        ssid = '='.join(('ssid',sid))
        self.handler.response.headers.add_header('Set-Cookie',ssid)
        _user.session_id = sid
        self.session_id = sid
        _user.put()
        memcache.add(sid,_user)

    def _fetch_user_by_cookie(self):
        if not self.session_id:
            try:
                sid = self.handler.request.cookies['ssid']
            except:
                sid = ""
                ssid = "=".join(('ssid',sid))
                self.handler.response.headers.add_header('Set-Cookie',ssid)
        else:
            sid = self.session_id

        data = memcache.get(sid)
        if data is None:
            #data = User.all().filter('session_id = ',sid).get()
            data = User.query(User.session_id == sid).get()
            if data is not None: memcache.add(sid,data)

        return data

    def _fetch_user_with_pass(self,u,p):
        diverUserQuery = User.gql("WHERE username = :1", u)
        tmp = diverUserQuery.get()
        if not tmp:
            return None
        if tmp.password != p: return None
        return tmp

def login_required(handler_method):
    def check_login(self,*args):
        user = Session(self).get_current_user()
        if not user:
            self.redirect('='.join(('/login?continue',self.request.uri)))
        else:
            handler_method(self,*args)
        
    return check_login
    
class CreateUser(webapp2.RequestHandler):
    def post(self):
        u = self.request.get('username')
        p = self.request.get('password')
        newUser = User()
        newUser.username = u
        newUser.password = p
        newUser.put()

        msg = 'User : '+newUser.username + ' was added'
        variables = {
            'message':msg
        }
        template = JINJA_ENVIRONMENT.get_template('login.html')
        self.response.write(template.render(variables))

@login_required
class LoggedIn(webapp2.RequestHandler):
    def get(self):
        user = Session(self).get_current_user()
        username = user.username
        variables = {
            'username':username
        }
        template = JINJA_ENVIRONMENT.get_template('loggedIn.html')
        self.response.write(template.render(variables))
        

class Login(webapp2.RequestHandler):
    def get(self): 
        variables = {'callback_url':self.request.get('continue')} 
        template = JINJA_ENVIRONMENT.get_template('login.html')
        self.response.write(template.render(variables)) 

    def post(self): 
        c = self.request.get('continue') 
        if not c: c = '/loggedIn' 
        u = self.request.get('username') 
        p = self.request.get('password') 
        tmp = Session(self).grab_login(u,p) 
        if not tmp: 
            if tmp is None: msg = 'Bad username and/or password' 
            variables = {
                'message':msg
            } 
            template = JINJA_ENVIRONMENT.get_template('login.html')
            self.response.write(template.render(variables)) 
        else:
            #self.response.write('found user name = ' + tmp.username + ' pass  = ' + tmp.password)
            self.redirect(c)

class MainPage(webapp2.RequestHandler):
    def get(self):
        template_values={
        }
        template = JINJA_ENVIRONMENT.get_template('login.html')
        self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
        ('/',MainPage),
        ('/login',Login),
        ('/createUser',CreateUser),
        ('/loggedIn',LoggedIn)
], debug = True)
