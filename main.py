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
		#c = Item.all().filter('user_name =','Prachi').filter('category_name =','ABC').filter('item_name =','PQS').get().delete()
		if not user:
			html = '<html><body>'
			html = html + '<center><h1>Voting Website</h1></center>'
			html = html + ('<center><a href=\"%s\">Sign in or register</a></center>'% (users.create_login_url("/")))
			html = html + '</body></html>'
		else:
			self.storeUser(user.nickname())
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
		
    def storeUser(self,name):
		users = db.GqlQuery("SELECT * FROM User")
		flag = False
		for u in users:
			if u.user_name == name :
				flag = True
				break
		if flag == False :
			usr = User(user_name=name)
			usr.put()
		return
		
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
			self.listCategory()
		if self.request.get('categoryOption') == "addNewCategory" :
			self.addNewCategory()
		if self.request.get('categoryOption') == "editCategory" :
			self.editCategory()
		if self.request.get('button') == "Add Category" :
			categoryName = self.request.get('categoryName')
			self.addCategoryToDatastore(categoryName)
		if self.request.get('button') == "View Items" :
			stg = self.request.get('info')
			categoryName, userName = stg.split(" : ")
			self.viewItems(userName,categoryName)
		if self.request.get('button') == "Edit Category" :
			categoryName = self.request.get('categoryName')
			userName = self.request.get('userName')
			self.editGivenCategory(userName,categoryName)
		if self.request.get('editbutton') == "Add Item" :
			categoryName = self.request.get('categoryName')
			userName = self.request.get('userName')
			itemName = self.request.get('addItemName')
			item = Item(user_name=userName,category_name=categoryName,item_name=itemName,wins='0',loses='0')
			item.put()
			self.redirect("/category")
		if self.request.get('editbutton') == "Delete Item" :
			categoryName = self.request.get('categoryName')
			userName = self.request.get('userName')
			itemName = self.request.get('deleteItemName')
			self.deleteItemFromDatastore(userName,categoryName,itemName)
		
    def listCategory(self):
		user = users.get_current_user()
		welcomeString = ('Welcome, %s!'% user.nickname())
		signOutString = users.create_logout_url("/")
		usrs = db.GqlQuery("SELECT * FROM User")
		categories = db.GqlQuery("SELECT * FROM Category")
		html = template.render('template/page_begin.html', {})
		html = html + '<div id="content" style="width:60%; height:100%; float:left">'
		html = html + '<center>'+ welcomeString +'</center><br>'
		html = html + '<form action="/category" method="post">'
		for u in usrs:
			for c in categories:
				if u.user_name == c.user_name :
					html = html + '<input type="radio" name="info" value="' + c.category_name + ' : ' + c.user_name + '">' + c.category_name + ' by ' + c.user_name + '<br>'
		html = html + '<input type="submit" name="button" value="View Items">'
		html = html + '</div>'
		html = html + '<div id="sidebar" style="width:20%; height:100%; float:right; background-color:yellow">'
		html = html + '<center><a href="'+ signOutString +'">sign out</a></center>'
		html = html + '</div>'
		html = html + template.render('template/page_end.html', {})
		self.response.out.write(html)
		
    def viewItems(self,user_name,category_name):
 		welcomeString = ('Welcome, %s!'% user_name)
		signOutString = users.create_logout_url("/")
		items = Item.all().filter('user_name =',user_name).filter('category_name =',category_name)
		html = template.render('template/page_begin.html', {})
		html = html + '<div id="content" style="width:60%; height:100%; float:left">'
		html = html + '<center>'+ welcomeString +'</center><br>'
		html = html + '<h4>Category : ' + category_name + ' of ' + user_name + '</h4><br>'
		for i in items:
			html = html + i.item_name + '<br>'
		html = html + '<br><br><form action="/category" method="get">'
		html = html + '<input type="submit" name="button" value="Back">'
		html = html + '</div>'
		html = html + '<div id="sidebar" style="width:20%; height:100%; float:right; background-color:yellow">'
		html = html + '<center><a href="'+ signOutString +'">sign out</a></center>'
		html = html + '</div>'
		html = html + template.render('template/page_end.html', {})
		self.response.out.write(html)
		
    def addNewCategory(self):
		user = users.get_current_user()
		welcomeString = ('Welcome, %s!'% user.nickname())
		signOutString = users.create_logout_url("/")
		html = template.render('template/page_begin.html', {})
		html = html + template.render('template/add_category_page.html', {'welcomeString': welcomeString,'signOutString': signOutString})
		html = html + template.render('template/page_end.html', {})
		self.response.out.write(html)
	
    def addCategoryToDatastore(self, categoryName):
		user = users.get_current_user()
		userName = user.nickname()
		category = Category(user_name=userName,category_name=categoryName)
		category.put()
		self.redirect("/category")
		
    def editCategory(self):
		user = users.get_current_user()
		welcomeString = ('Welcome, %s!'% user.nickname())
		signOutString = users.create_logout_url("/")
		categories = Category.all().filter('user_name =',user.nickname())
		html = template.render('template/page_begin.html', {})
		html = html + '<div id="content" style="width:60%; height:100%; float:left">'
		html = html + '<center>'+ welcomeString +'</center><br>'
		html = html + '<h3>Categories created by you : </h3>'
		html = html + '<form action="/category" method="post">'
		for c in categories:
				html = html + '<input type="radio" name="categoryName" value="' + c.category_name + '">' + c.category_name + '<br>'
		html = html + '<input type="hidden" name="userName" value="' + user.nickname() + '">'
		html = html + '<input type="submit" name="button" value="Edit Category">'
		html = html + '</div>'
		html = html + '<div id="sidebar" style="width:20%; height:100%; float:right; background-color:yellow">'
		html = html + '<center><a href="'+ signOutString +'">sign out</a></center>'
		html = html + '</div>'
		html = html + template.render('template/page_end.html', {})
		self.response.out.write(html)
		
    def editGivenCategory(self,userName,categoryName):
		welcomeString = ('Welcome, %s!'% userName)
		signOutString = users.create_logout_url("/")
		items = Item.all().filter('user_name =',userName).filter('category_name =',categoryName)
		html = template.render('template/page_begin.html', {})
		html = html + '<div id="content" style="width:60%; height:100%; float:left">'
		html = html + '<center>'+ welcomeString +'</center><br>'
		html = html + '<h4>Category : ' + categoryName + ' of ' + userName + '</h4><br>'
		for i in items:
			html = html + i.item_name + '<br>'
		html = html + '<br><br><form action="/category" method="post">'
		html = html + 'Enter item to be added<input type="text" name="addItemName">'
		html = html + '<input type="submit" name="editbutton" value="Add Item"><br><br>'
		html = html + 'Enter item to be deleted<input type="text" name="deleteItemName">'
		html = html + '<input type="submit" name="editbutton" value="Delete Item">'
		html = html + '<input type="hidden" name="userName" value="' + userName + '">'
		html = html + '<input type="hidden" name="categoryName" value="' + categoryName + '"></form>'
		html = html + '</div>'
		html = html + '<div id="sidebar" style="width:20%; height:100%; float:right; background-color:yellow">'
		html = html + '<center><a href="'+ signOutString +'">sign out</a></center>'
		html = html + '</div>'
		html = html + template.render('template/page_end.html', {})
		self.response.out.write(html)
		
    def addItemToDatastore(userName,categoryName,itemName):
		item = Item(user_name=userName,category_name=categoryName,item_name=itemName,wins='0',loses='0')
		item.put()
		self.redirect("/category")
		
    def deleteItemFromDatastore(userName,categoryName,itemName):
		itm = Item.all().filter('user_name =',userName).filter('category_name =',categoryName).filter('item_name =',itemName).get().delete()
		self.redirect('/category')
		
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
		
class User(db.Model):
	user_name = db.StringProperty()
	
class Item(db.Model):
	user_name = db.StringProperty()
	category_name = db.StringProperty()
	item_name = db.StringProperty()
	wins = db.StringProperty()
	loses = db.StringProperty()
		
app = webapp2.WSGIApplication([
    ('/', MainHandler),
	('/category', CategoryPage),
	('/vote', VotePage),
	('/result', ResultPage)
], debug=True)
