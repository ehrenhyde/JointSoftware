import os
import urllib
import jinja2
import webapp2
import json

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        variables = {
        }
        template = JINJA_ENVIRONMENT.get_template('home.html')
        self.response.write(template.render(variables))
class MonsterHandler(webapp2.RequestHandler):
    def post(self):
        data = json.loads(self.request.body)
        name = data['name']
        jsonRetVal = json.dumps(
            {
                'colour':'green',
                'teeth':{
                    'num':24,
                    'size':'huge'
                    },
                'favouriteFood':name           
            }
        )
        #https://docs.python.org/2/library/json.html
        self.response.out.write(jsonRetVal)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/monster',MonsterHandler)
], debug=True)
