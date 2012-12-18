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
		user = users.get_current_user()
		if not user:
			html = '<html><body>'
			html = html + '<center><h1>Voting Website</h1></center>'
			html = html + ('<center><a href=\"%s\">Sign in or register</a></center>'% (users.create_login_url("/")))
			html = html + '</body></html>'
		else:
			welcomeString = ('<p>Welcome, %s! </p>'% user.nickname())
			signOutString = ('<a href="%s">sign out</a>'% users.create_logout_url("/"))
			html = template.render('template/page_begin.html', {})
			html = html + '<div id="content" style="width:60%; height:100%; float:left">'
			html = html + '<center>' + welcomeString + '</center><br>'
			html = html + '</div>'
			html = html + '<div id="sidebar" style="width:20%; height:100%; float:right; background-color:yellow">'
			html = html + '<center>' + signOutString + '</center>'
			html = html + '</div>'
			html = html + template.render('template/page_end.html', {})
		self.response.out.write(html)
		
class CategoryPage(webapp2.RequestHandler):
    def get(self):
		user = users.get_current_user()
		welcomeString = ('Welcome, %s!'% user.nickname())
		signOutString = users.create_logout_url("/")
		html = template.render('template/page_begin.html', {})
		html = html + template.render('template/category_page.html', {'welcomeString': welcomeString,'signOutString': signOutString})
		html = html + template.render('template/page_end.html', {})
		self.response.out.write(html)
		
    def post(self):
		if self.request.get('categoryOption') == "listCategory" :
			self.listCategory("Listing Categories")
		if self.request.get('categoryOption') == "addNewCategory" :
			self.addNewCategory()
		if self.request.get('categoryOption') == "editCategory" :
			self.editCategory("Listing Categories")
		if self.request.get('button') == "Add Category" :
			categoryName = self.request.get('categoryName')
			self.addCategoryToDatastore(categoryName)
		
    def listCategory(self,name):
		html = 'This is listCategory function of ' + name
		self.response.out.write(html)
		
    def addNewCategory(self):
		user = users.get_current_user()
		welcomeString = ('Welcome, %s!'% user.nickname())
		signOutString = users.create_logout_url("/")
		html = template.render('template/page_begin.html', {})
		html = html + template.render('template/add_category_page.html', {'welcomeString': welcomeString,'signOutString': signOutString})
		html = html + template.render('template/page_end.html', {})
		self.response.out.write(html)
		
    def editCategory(self,name):
		html = 'This is listCategory function of ' + name
		self.response.out.write(html)
		return
	
    def addCategoryToDatastore(self, categoryName):
		user = users.get_current_user()
		userName = user.nickname()
		k = userName + '_' + categoryName
		category = Category(key_name=k,user_name=userName,category_name=categoryName)
		category.put()
		self.redirect("/category")
		
class VotePage(webapp2.RequestHandler):
    def get(self):
		html = 'This is get of Vote'
		self.response.out.write(html)

class ResultPage(webapp2.RequestHandler):
    def get(self):
		html = 'This is get of Result'
		self.response.out.write(html)
		
class Category(db.Model):
	user_name = db.StringProperty()
	category_name = db.StringProperty()
		
class Item(db.Model):
	user_name = db.StringProperty()
	category_name = db.StringProperty()
	item_name = db.StringProperty()
	wins = db.IntegerProperty()
	loses = db.IntegerProperty()
		
app = webapp2.WSGIApplication([
    ('/', MainHandler),
	('/category', CategoryPage),
	('/vote', VotePage),
	('/result', ResultPage)
], debug=True)
