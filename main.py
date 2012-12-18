#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import datetime
import os
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext.webapp import template

class MainHandler(webapp2.RequestHandler):
    def get(self):
		html = template.render('template/page_begin.html', {})
		html = html + '<div id="content" style="width:60%; height:100%;' 
		html = html + 'float:left; background-color:green">'
		html = html + '<center>Your Content</center><br>'
		html = html + '<center>My Content</center><br>'
		html = html + '</div>'
		html = html + '<div id="sidebar" style="width:20%; height:100%; float:right; background-color:yellow">'
		html = html + 'Your sidebar'
		html = html + '</div>'
		html = html + template.render('template/page_end.html', {})
		self.response.out.write(html)
		
class Category(webapp2.RequestHandler):
    def get(self):
		html = 'This is get of Category'
		self.response.out.write(html)
		
class Vote(webapp2.RequestHandler):
    def get(self):
		html = 'This is get of Vote'
		self.response.out.write(html)

class Result(webapp2.RequestHandler):
    def get(self):
		html = 'This is get of Result'
		self.response.out.write(html)
app = webapp2.WSGIApplication([
    ('/', MainHandler),
	('/category', Category),
	('/vote', Vote),
	('/result', Result)
], debug=True)
