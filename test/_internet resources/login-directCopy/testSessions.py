# !important The Following Code requires three basic HTML Files, 
# login.html, signup.html, and activate.html 
# 
# SUAS: Simple User Authentication then Session 
# User Session Management Library 
# The following code creates a memcache/datastore session manager that simply 
# tracks whether or not a user remains logged in, and mimics the 
# google "users" service to the greatest extent possible 
# 
# Copyright Andrew Tutt 2010. MIT License.
# https://groups.google.com/forum/#!topic/google-appengine/UBqihupyvjM

from google.appengine.api import mail 
from google.appengine.ext import db 
from google.appengine.api import memcache 
from google.appengine.ext import webapp 
from google.appengine.ext.webapp import template 

import os 
import uuid 

class user(db.Model): 
    email = db.EmailProperty() 
    username = db.StringProperty() 
    password = db.StringProperty() 
    session_id = db.StringProperty() 
    activated = db.BooleanProperty(default=False) 
    activation_code = db.StringProperty(default=str(uuid.uuid4())) 

class session: 

    def __init__(self,handler): 
        """Requires a webapp requesthandler passed as a constructor""" 
        self.handler = handler 
        self.session_id = None 

    def create_user(self, email, username, password): 
        """Create a new user in the datastore""" 
        tmp = user(key_name=username.lower()) 
        tmp.username = username 
        tmp.email = email 
        tmp.password = password 

        mail.send_mail( 
            sender=email, 
            to=email, 
            subject="Account Activation", 
            body="""Dear """+username+""": 

A new account has been created with this email address at http://www.example.com 

But in order to log in and play you must first activate your account 
with your unique activation code included in this email. Simply click 
the link included here to activate your account or copy and paste the 
following URL into your browser 

"""+"http://www.example.com/validate?activate="+tmp.activation_code) 

        self._sync_user(tmp) 

    def get_current_user(self): 
        """Returns the currently logged in user or "None" if no 
session""" 
        return self._fetch_user_by_cookie() 

    def grab_login(self, username, password): 
        """Generates a session for the user if user/pass match 
database""" 
        tmp = self._fetch_user_with_pass(username,password) 
        if tmp: 
            self._sync_user(tmp) 
        return tmp 

    def logout(self): 
        """Logout the logged in user""" 
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
                ssid = '='.join(('ssid',sid)) 
                self.handler.response.headers.add_header('Set- Cookie',ssid) 
        else: 
            sid = self.session_id 

        data = memcache.get(sid) 
        if data is None: 
            data = user.all().filter('session_id = ',sid).get() 
            if data is not None: memcache.add(sid, data) 

        return data 

    def _fetch_user_with_pass(self,u,p): 
        tmp = user.get_by_key_name(u.lower()) 
        if not tmp: return None 
        if tmp.password != p: return None 
        if tmp.activated == False: return False 
        return tmp 

class Login(webapp.RequestHandler): 
    def get(self): 
        variables = {'callback_url':self.request.get('continue')} 
        path = os.path.join(os.path.dirname(__file__), 'login.html') 
        self.response.out.write(template.render(path,variables)) 

    def post(self): 
        c = self.request.get('continue') 
        if not c: c = '/' 
        u = self.request.get('user') 
        p = self.request.get('pass') 
        tmp = session(self).grab_login(u,p) 

        if not tmp: 
            if tmp is None: msg = 'Bad username and/or password' 
            if tmp is False: msg = 'That account has not been activated yet.' 
            variables = {'callback_url':c, 
                         'message':msg,} 
            path = os.path.join(os.path.dirname(__file__), 'login.html') 
            self.response.out.write(template.render(path,variables)) 
        else: 
            self.redirect(c) 

class ActivateAccount(webapp.RequestHandler): 
    def get(self): 
        proposed_code = self.request.get('activate') 
        a_user = user.all().filter('activation_code = ',proposed_code).get() 
        if a_user: 
            a_user.activated = True 
            a_user.put() 
            result = "Your account was activated successfully." 
        else: 
            result = "There was a problem activating that account." 

        variables = {'result':result} 

        path = os.path.join(os.path.dirname(__file__), 'activate.html') 
        self.response.out.write(template.render(path,variables)) 


class SignUp(webapp.RequestHandler): 
    def get(self): 
        path = os.path.join(os.path.dirname(__file__), 'signup.html') 
        self.response.out.write(template.render(path,None)) 

    def post(self): 
        u = self.request.get('user') 
        e = self.request.get('email') 
        p = self.request.get('pass') 
        session(self).create_user(e,u,p) 
        self.redirect('/') 

class DoLogout(webapp.RequestHandler): 
    def get(self): 
        c = self.request.get('continue') 
        if not c: c = '/' 
        session(self).logout() 
        self.redirect(c) 

def login_required(handler_method): 
    """ 
    A decorator to require that a user be logged in to access a 
handler method. 

    >>> @login_required 
    ... def get(self): 
    ...     self.response.out.write('Hello, ' + 
self.session.user.nickname) 

    We will redirect to a login page if the user is not logged in. 
    """ 
    def check_login(self, *args): 
        user = session(self).get_current_user() 
        if not user: 
            self.redirect('='.join(('/login? continue',self.request.uri))) 
        else: 
            handler_method(self, *args) 

    return check_login 
