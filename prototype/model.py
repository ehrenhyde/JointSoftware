from google.appengine.ext import ndb
from google.appengine.ext import blobstore


class Attendees(ndb.Model):
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
	ProfilePicBlobKey = ndb.BlobKeyProperty()
	session_id = ndb.StringProperty()
	TestField = ndb.StringProperty()

class Event(ndb.Model):
        #EventNum =ndb.IntegerProperty()
	Name = ndb.StringProperty()
	Description  = ndb.StringProperty()
	Date= ndb.DateProperty()
	Time = ndb.TimeProperty()
	Location = ndb.StringProperty()
	Attendees = ndb.StructuredProperty(Attendees, repeated=True)
	Attendees_count = ndb.ComputedProperty(lambda e: len(e.Attendees))
	Comment = ndb.TextProperty()
