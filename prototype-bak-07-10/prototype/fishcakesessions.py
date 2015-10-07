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
     

