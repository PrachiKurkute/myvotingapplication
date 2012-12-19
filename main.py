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
import random
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from xml.etree.ElementTree import Element, SubElement, tostring, XML, fromstring

class MainHandler(webapp2.RequestHandler):
    def get(self):
		user = users.get_current_user()
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
			html = html + '<center>' + signOutString + '</center><br><br>'
			html = html + '<form action="/search" method="post">'
			html = html + '<input type="text" name="searchItem">'
			html = html + '<input type="submit" name="button" value="Search"></form>'
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
		if self.request.get('button') == "Submit" :
			if self.request.get('categoryOption'):
				if self.request.get('categoryOption') == "listCategory" :
					self.listCategory()
				if self.request.get('categoryOption') == "addNewCategory" :
					self.addNewCategory()
				if self.request.get('categoryOption') == "editCategory" :
					self.editCategory()
				if self.request.get('categoryOption') == "addComment" :
					self.commentHandle()
			else:
				msg = 'Select one option'
				html = template.render('template/error_page.html', {'error_msg': msg,'destination': 'category','method': 'get'})
				self.response.out.write(html)
		if self.request.get('button') == "Add Category" :
			if self.request.get('categoryName'):
				categoryName = self.request.get('categoryName')
				flag = self.categoryExists(categoryName)
				if flag == True:
					msg = 'Given Category already Exists'
					html = template.render('template/error_page.html', {'error_msg': msg,'destination': 'category','method': 'get'})
					self.response.out.write(html)
				if flag == False:
					self.addCategoryToDatastore(categoryName)
			else:
				msg = 'Empty Category Name'
				html = template.render('template/error_page.html', {'error_msg': msg,'destination': 'category','method': 'get'})
				self.response.out.write(html)
		if self.request.get('button') == "View Items" :
			if self.request.get('info'):
				stg = self.request.get('info')
				categoryName, userName = stg.split(" : ")
				self.viewItems(userName,categoryName)
			else:
				msg = 'Select One Option'
				html = template.render('template/error_page.html', {'error_msg': msg,'destination': 'category','method': 'get'})
				self.response.out.write(html)
		if self.request.get('button') == "Edit Category" :
			if self.request.get('categoryName'):
				categoryName = self.request.get('categoryName')
				userName = self.request.get('userName')
				self.editGivenCategory(userName,categoryName)
			else:
				msg = 'Select One Option'
				html = template.render('template/error_page.html', {'error_msg': msg,'destination': 'category','method': 'get'})
				self.response.out.write(html)
		if self.request.get('button') == "Select Category" :
			if self.request.get('categoryName'):
				categoryName = self.request.get('categoryName')
				userName = self.request.get('userName')
				self.addCommentHandle(userName,categoryName)
			else:
				msg = 'Select One Option'
				html = template.render('template/error_page.html', {'error_msg': msg,'destination': 'category','method': 'get'})
				self.response.out.write(html)
		if self.request.get('button') == "Select Item" :
			if self.request.get('itemName'):
				itemName = self.request.get('itemName')
				userName = self.request.get('userName')
				categoryName = self.request.get('categoryName')
				self.addCommentPage(userName,categoryName,itemName)
			else:
				msg = 'Select One Option'
				html = template.render('template/error_page.html', {'error_msg': msg,'destination': 'category','method': 'get'})
				self.response.out.write(html)
		if self.request.get('button') == "Add Comment" :
			if self.request.get('commentName'):
				commentName = self.request.get('commentName')
				userName = self.request.get('userName')
				categoryName = self.request.get('categoryName')
				itemName = self.request.get('itemName')
				self.addCommentToItem(userName,categoryName,itemName,commentName)
			else:
				msg = 'Select One Option'
				html = template.render('template/error_page.html', {'error_msg': msg,'destination': 'category','method': 'get'})
				self.response.out.write(html)
		if self.request.get('editbutton') == "Add Item" :
			categoryName = self.request.get('categoryName')
			userName = self.request.get('userName')
			if self.request.get('addItemName'):
				itemName = self.request.get('addItemName')
				commentName = self.request.get('addComment')
				flag = self.itemExists(userName,categoryName,itemName)
				if flag == True:
					msg = 'Given item already exists in  category ' + categoryName
					html = template.render('template/error_page.html', {'error_msg': msg,'destination': 'category','method': 'get'})
					self.response.out.write(html)
				if flag == False:
					self.addItemToDatastore(userName,categoryName,itemName,commentName)
			else:
				msg = 'Empty Item Name'
				html = template.render('template/error_page.html', {'error_msg': msg,'destination': 'category','method': 'get'})
				self.response.out.write(html)
		if self.request.get('editbutton') == "Delete Item" :
			categoryName = self.request.get('categoryName')
			userName = self.request.get('userName')
			if self.request.get('deleteItemName'):
				itemName = self.request.get('deleteItemName')
				flag = self.itemExists(userName,categoryName,itemName)
				if flag == False:
					msg = 'Given item does not exist in  category ' + categoryName
					html = template.render('template/error_page.html', {'error_msg': msg,'destination': 'category','method': 'get'})
					self.response.out.write(html)
				if flag == True:
					self.deleteItemFromDatastore(userName,categoryName,itemName)
			else:
				msg = 'Empty Item Name'
				html = template.render('template/error_page.html', {'error_msg': msg,'destination': 'category','method': 'get'})
				self.response.out.write(html)
		if self.request.get('editbutton') == "Set" :
			categoryName = self.request.get('categoryName')
			userName = self.request.get('userName')
			if self.request.get('expirationDate'):
				date = self.request.get('expirationDate')
				year, month, day = date.split("-")
				expirationDate = year + '-' + month + '-' + day
				self.setExpirationDate(userName,categoryName,expirationDate)
			else:
				msg = 'Empty Item Name'
				html = template.render('template/error_page.html', {'error_msg': msg,'destination': 'category','method': 'get'})
				self.response.out.write(html)
	
    def error(self):
		html = '<html><body>Non Option is selected</body></html>'
		self.response.out.write(html)
		
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
		html = html + '<input type="submit" name="button" value="View Items"></form>'
		html = html + '</div>'
		html = html + '<div id="sidebar" style="width:20%; height:100%; float:right; background-color:yellow">'
		html = html + '<center><a href="'+ signOutString +'">sign out</a></center>'
		html = html + '<form action="/search" method="post">'
		html = html + '<input type="text" name="searchItem">'
		html = html + '<input type="submit" name="button" value="Search"></form>'
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
		html = html + '<input type="submit" name="button" value="Back"></form>'
		html = html + '</div>'
		html = html + '<div id="sidebar" style="width:20%; height:100%; float:right; background-color:yellow">'
		html = html + '<center><a href="'+ signOutString +'">sign out</a></center>'
		html = html + '<form action="/search" method="post">'
		html = html + '<input type="text" name="searchItem">'
		html = html + '<input type="submit" name="button" value="Search"></form>'
		html = html + '</div>'
		html = html + template.render('template/page_end.html', {})
		self.response.out.write(html)
		
    def addNewCategory(self):
		user = users.get_current_user()
		welcomeString = ('Welcome, %s!'% user.nickname())
		signOutString = users.create_logout_url("/")
		html = template.render('template/page_begin.html', {})
		html = html + template.render('template/add_category_page.html', {'welcomeString': welcomeString,'signOutString': signOutString})
		html = html + '<form action="/search" method="post">'
		html = html + '<input type="text" name="searchItem">'
		html = html + '<input type="submit" name="button" value="Search"></form>'
		html = html + template.render('template/page_end.html', {})
		self.response.out.write(html)
	
    def addCategoryToDatastore(self, categoryName):
		user = users.get_current_user()
		userName = user.nickname()
		category = Category(user_name=userName,category_name=categoryName)
		category.put()
		self.redirect("/category")
		
    def categoryExists(self,categoryName):
		user = users.get_current_user()
		userName = user.nickname()
		category = Category.all().filter('user_name =',userName)
		for c in category:
			if c.category_name == categoryName:
				return True
		return False
		
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
		html = html + '<input type="submit" name="button" value="Edit Category"></form>'
		html = html + '</div>'
		html = html + '<div id="sidebar" style="width:20%; height:100%; float:right; background-color:yellow">'
		html = html + '<center><a href="'+ signOutString +'">sign out</a></center>'
		html = html + '<form action="/search" method="post">'
		html = html + '<input type="text" name="searchItem">'
		html = html + '<input type="submit" name="button" value="Search"></form>'
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
		html = html + 'Enter item to be added: <input type="text" name="addItemName">'
		html = html + 'Enter comment for am item: <input type="text" name="addComment">'
		html = html + '<input type="submit" name="editbutton" value="Add Item"><br><br>'
		html = html + 'Enter item to be deleted<input type="text" name="deleteItemName">'
		html = html + '<input type="submit" name="editbutton" value="Delete Item"><br><br>'
		html = html + 'Expiration Date: <input type="date" name="expirationDate">'
		html = html + '<input type="submit" name="editbutton" value="Set"><br><br>'
		html = html + '<input type="hidden" name="userName" value="' + userName + '">'
		html = html + '<input type="hidden" name="categoryName" value="' + categoryName + '"></form>'
		html = html + '</div>'
		html = html + '<div id="sidebar" style="width:20%; height:100%; float:right; background-color:yellow">'
		html = html + '<center><a href="'+ signOutString +'">sign out</a></center>'
		html = html + '<form action="/search" method="post">'
		html = html + '<input type="text" name="searchItem">'
		html = html + '<input type="submit" name="button" value="Search"></form>'
		html = html + '</div>'
		html = html + template.render('template/page_end.html', {})
		self.response.out.write(html)
		
    def addItemToDatastore(self,userName,categoryName,itemName,commentName):
		item = Item(user_name=userName,category_name=categoryName,item_name=itemName,comment=commentName,wins=0,loses=0)
		item.put()
		self.redirect("/category")
		
    def itemExists(self,userName,categoryName,itemName):
		user = users.get_current_user()
		userName = user.nickname()
		items = Item.all().filter('user_name =',userName).filter('category_name =',categoryName)
		for i in items:
			if i.item_name == itemName:
				return True
		return False
		
    def deleteItemFromDatastore(self,userName,categoryName,itemName):
		itm = Item.all().filter('user_name =',userName).filter('category_name =',categoryName).filter('item_name =',itemName).get().delete()
		self.redirect('/category')
		
    def commentHandle(self):
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
		html = html + '<input type="submit" name="button" value="Select Category"></form>'
		html = html + '</div>'
		html = html + '<div id="sidebar" style="width:20%; height:100%; float:right; background-color:yellow">'
		html = html + '<center><a href="'+ signOutString +'">sign out</a></center>'
		html = html + '<form action="/search" method="post">'
		html = html + '<input type="text" name="searchItem">'
		html = html + '<input type="submit" name="button" value="Search"></form>'
		html = html + '</div>'
		html = html + template.render('template/page_end.html', {})
		self.response.out.write(html)
		
    def addCommentHandle(self,userName,categoryName):
		welcomeString = ('Welcome, %s!'% userName)
		signOutString = users.create_logout_url("/")
		items = Item.all().filter('user_name =',userName).filter('category_name =',categoryName)
		html = template.render('template/page_begin.html', {})
		html = html + '<div id="content" style="width:60%; height:100%; float:left">'
		html = html + '<center>'+ welcomeString +'</center><br>'
		html = html + '<h4>Category : ' + categoryName + ' of ' + userName + '</h4><br>'
		html = html + '<br><br><form action="/category" method="post">'
		for i in items:
			if not i.comment:
				html = html + '<input type="radio" name="itemName" value="' + i.item_name + '">' + i.item_name + '<br>'
		html = html + '<input type="submit" name="button" value="Select Item"><br><br>'
		html = html + '<input type="hidden" name="userName" value="' + userName + '">'
		html = html + '<input type="hidden" name="categoryName" value="' + categoryName + '"></form>'
		html = html + '</div>'
		html = html + '<div id="sidebar" style="width:20%; height:100%; float:right; background-color:yellow">'
		html = html + '<center><a href="'+ signOutString +'">sign out</a></center>'
		html = html + '<form action="/search" method="post">'
		html = html + '<input type="text" name="searchItem">'
		html = html + '<input type="submit" name="button" value="Search"></form>'
		html = html + '</div>'
		html = html + template.render('template/page_end.html', {})
		self.response.out.write(html)
		
    def addCommentPage(self,userName,categoryName,itemName):
		welcomeString = ('Welcome, %s!'% userName)
		signOutString = users.create_logout_url("/")
		items = Item.all().filter('user_name =',userName).filter('category_name =',categoryName)
		html = template.render('template/page_begin.html', {})
		html = html + '<div id="content" style="width:60%; height:100%; float:left">'
		html = html + '<center>'+ welcomeString +'</center><br>'
		html = html + '<h4>Add comment for item : ' + itemName + ' of category : ' + categoryName + '</h4><br>'
		html = html + '<br><br><form action="/category" method="post">'
		html = html + '<input type="text" name="commentName"<br>'
		html = html + '<input type="submit" name="button" value="Add Comment"><br><br>'
		html = html + '<input type="hidden" name="itemName" value="' + itemName + '">'
		html = html + '<input type="hidden" name="userName" value="' + userName + '">'
		html = html + '<input type="hidden" name="categoryName" value="' + categoryName + '"></form>'
		html = html + '</div>'
		html = html + '<div id="sidebar" style="width:20%; height:100%; float:right; background-color:yellow">'
		html = html + '<center><a href="'+ signOutString +'">sign out</a></center>'
		html = html + '<form action="/search" method="post">'
		html = html + '<input type="text" name="searchItem">'
		html = html + '<input type="submit" name="button" value="Search"></form>'
		html = html + '</div>'
		html = html + template.render('template/page_end.html', {})
		self.response.out.write(html)
		
    def addCommentToItem(self,userName,categoryName,itemName,commentName):
		item = Item.all().filter('user_name =',userName).filter('category_name =',categoryName).filter('item_name =',itemName).get()
		item.comment = commentName
		item.put()
		self.redirect("/category")
		
    def setExpirationDate(self,userName,categoryName,expirationDate):
		category = Category.all().filter('user_name =',userName).filter('category_name =',categoryName).get()
		category.expiration_date = expirationDate
		category.put()
		self.redirect("/category")
		
class VotePage(webapp2.RequestHandler):
    def get(self):
		user = users.get_current_user()
		welcomeString = ('Welcome, %s!'% user.nickname())
		signOutString = users.create_logout_url("/")
		usrs = db.GqlQuery("SELECT * FROM User")
		categories = db.GqlQuery("SELECT * FROM Category")
		html = template.render('template/page_begin.html', {})
		html = html + '<div id="content" style="width:60%; height:100%; float:left">'
		html = html + '<center>'+ welcomeString +'</center><br>'
		html = html + '<form action="/vote" method="post">'
		for u in usrs:
			for c in categories:
				if u.user_name == c.user_name :
					if c.expiration_date:
						html = html + '<input type="radio" name="info" value="' + c.category_name + ' : ' + c.user_name + '">' + c.category_name + ' by ' + c.user_name + ' with expiration date : ' + c.expiration_date + '<br>'
					else:
						html = html + '<input type="radio" name="info" value="' + c.category_name + ' : ' + c.user_name + '">' + c.category_name + ' by ' + c.user_name + ' with no expiration date<br>'
		html = html + '<input type="submit" name="button" value="Select for Voting"></form>'
		html = html + '</div>'
		html = html + '<div id="sidebar" style="width:20%; height:100%; float:right; background-color:yellow">'
		html = html + '<center><a href="'+ signOutString +'">sign out</a></center>'
		html = html + '<form action="/search" method="post">'
		html = html + '<input type="text" name="searchItem">'
		html = html + '<input type="submit" name="button" value="Search"></form>'
		html = html + '</div>'
		html = html + template.render('template/page_end.html', {})
		self.response.out.write(html)
		
    def post(self):
		if self.request.get('button') == 'Select for Voting':		
			if self.request.get('info'):
				stg = self.request.get('info')
				categoryName, userName = stg.split(" : ")
				flag = self.canVote(userName,categoryName)
				if flag == True:
					self.handleVoting(userName,categoryName)
				if flag == False:
					msg = 'Category is expired'
					html = template.render('template/error_page.html', {'error_msg': msg,'destination': 'vote','method': 'get'})
					self.response.out.write(html)
			else:
				msg = 'Select one option'
				html = template.render('template/error_page.html', {'error_msg': msg,'destination': 'vote','method': 'get'})
				self.response.out.write(html)
		if self.request.get('button') == 'Vote':
			if self.request.get('itemoption'):
				itemName = self.request.get('itemoption')
				userName = self.request.get('userName')
				categoryName = self.request.get('categoryName')
				stg = self.request.get('info')
				firstItem, secondItem = stg.split(" : ")
				if firstItem == itemName:
					winItem = firstItem
					looseItem = secondItem
				else:
					winItem = secondItem
					looseItem = firstItem
				self.registerVote(userName,categoryName,winItem,looseItem)
			else:
				msg = 'Select one option'
				html = template.render('template/error_page.html', {'error_msg': msg,'destination': 'vote','method': 'get'})
				self.response.out.write(html)
		
    def canVote(self,userName,categoryName):
		category = Category.all().filter('user_name =',userName).filter('category_name =',categoryName).get()
		now = datetime.datetime.now()
		current_year = int(now.year)
		current_month = int(now.month)
		current_dayNo = int(now.day)
		if not category.expiration_date:
			return True
		else:			
			expiration_year, expiration_month, expiration_dayNo = str(category.expiration_date).split("-")
			expiration_year = int(expiration_year)
			expiration_month = int(expiration_month)
			expiration_dayNo = int(expiration_dayNo)
			if expiration_year >= current_year and expiration_month >= current_month and expiration_dayNo >= current_dayNo:
				return True
			else:
				return False
			
    def handleVoting(self,userName,categoryName):
		user = users.get_current_user()
		welcomeString = ('Welcome, %s!'% user.nickname())
		signOutString = users.create_logout_url("/")
		usrs = db.GqlQuery("SELECT * FROM User")
		categories = db.GqlQuery("SELECT * FROM Category")
		items = Item.all().filter('user_name =',userName).filter('category_name =',categoryName)
		if( items.count() >= 2):
			randomNumber_1 = random.randint(0,items.count() - 1 )
			randomNumber_2 = randomNumber_1
			while(randomNumber_1 == randomNumber_2):
				randomNumber_2 = random.randint(0,items.count() - 1 )
			itemOne = items[randomNumber_1]
			itemTwo = items[randomNumber_2]
			html = template.render('template/page_begin.html', {})
			html = html + '<div id="content" style="width:60%; height:100%; float:left">'
			html = html + '<center>'+ welcomeString +'</center><br>'
			html = html + '<form action="/vote" method="post">'
			html = html + '<input type="radio" name="itemoption" value=' + itemOne.item_name + '>' + itemOne.item_name + '<br>'
			html = html + '<input type="radio" name="itemoption" value=' + itemTwo.item_name + '>' + itemTwo.item_name + '<br>'
			html = html + '<input type="submit" name="button" value="Vote">'
			html = html + '<input type="hidden" name="info" value="' + itemOne.item_name + ' : ' + itemTwo.item_name + '">'
			html = html + '<input type="hidden" name="userName" value=' + userName + '>'
			html = html + '<input type="hidden" name="categoryName" value=' + categoryName + '></form>'
			html = html + '</div>'
			html = html + '<div id="sidebar" style="width:20%; height:100%; float:right; background-color:yellow">'
			html = html + '<center><a href="'+ signOutString +'">sign out</a></center>'
			html = html + '<form action="/search" method="post">'
			html = html + '<input type="text" name="searchItem">'
			html = html + '<input type="submit" name="button" value="Search"></form>'
			html = html + '</div>'
			html = html + template.render('template/page_end.html', {})
			self.response.out.write(html)
		else:
			msg = 'Not enough items in category ' + categoryName + ' of user ' + userName + '. Choose another category'
			html = template.render('template/error_page.html', {'error_msg': msg,'destination': 'vote','method': 'get'})
			self.response.out.write(html)
			
    def registerVote(self,userName,categoryName,winItem,looseItem):
		item1 = Item.all().filter('user_name =',userName).filter('category_name =',categoryName).filter('item_name =',winItem).get()
		item1.wins = item1.wins + 1
		item1.put()
		item2 = Item.all().filter('user_name =',userName).filter('category_name =',categoryName).filter('item_name =',looseItem).get()
		item2.loses = item2.loses + 1
		item2.put()
		self.redirect("/vote")
			
class ResultPage(webapp2.RequestHandler):
    def get(self):
		user = users.get_current_user()
		welcomeString = ('Welcome, %s!'% user.nickname())
		signOutString = users.create_logout_url("/")
		usrs = db.GqlQuery("SELECT * FROM User")
		categories = db.GqlQuery("SELECT * FROM Category")
		html = template.render('template/page_begin.html', {})
		html = html + '<div id="content" style="width:60%; height:100%; float:left">'
		html = html + '<center>'+ welcomeString +'</center><br>'
		html = html + '<form action="/result" method="post">'
		for u in usrs:
			for c in categories:
				if u.user_name == c.user_name :
					html = html + '<input type="radio" name="info" value="' + c.category_name + ' : ' + c.user_name + '">' + c.category_name + ' by ' + c.user_name + '<br>'
		html = html + '<input type="submit" name="button" value="See Results"></form>'
		html = html + '</div>'
		html = html + '<div id="sidebar" style="width:20%; height:100%; float:right; background-color:yellow">'
		html = html + '<center><a href="'+ signOutString +'">sign out</a></center>'
		html = html + '<form action="/search" method="post">'
		html = html + '<input type="text" name="searchItem">'
		html = html + '<input type="submit" name="button" value="Search"></form>'
		html = html + '</div>'
		html = html + template.render('template/page_end.html', {})
		self.response.out.write(html)
		
    def post(self):
		if self.request.get('button') == 'See Results':		
			if self.request.get('info'):
				stg = self.request.get('info')
				categoryName, userName = stg.split(" : ")
				self.handleResults(userName,categoryName)
			else:
				msg = 'Select one option'
				html = template.render('template/error_page.html', {'error_msg': msg,'destination': 'result','method': 'get'})
				self.response.out.write(html)
		
    def handleResults(self,userName,categoryName):
		user = users.get_current_user()
		welcomeString = ('Welcome, %s!'% user.nickname())
		signOutString = users.create_logout_url("/")
		html = template.render('template/page_begin.html', {})
		html = html + '<div id="content" style="width:60%; height:100%; float:left">'
		html = html + '<center>'+ welcomeString +'</center><br>'
		usrs = db.GqlQuery("SELECT * FROM User")
		categories = db.GqlQuery("SELECT * FROM Category")
		items = Item.all().filter('user_name =',userName).filter('category_name =',categoryName)
		html = html + '<br><br><form action="/result" method="get">'
		html = html + '<input type="submit" name="button" value="Back"></form>'
		html = html + 'Category: ' + categoryName + '<br><br>'
		html = html + '<table><tr><td>Item Name</td><td>Wins</td><td>Losses</td><td>Percentage</td><td>Comment</td></tr>'
		for i in items:
			sum = i.wins + i.loses
			if sum == 0:
				percent = 0.00
			else:
				percent = float(i.wins) / (sum) * 100
			html = html + '<tr><td>' + i.item_name
			html = html + '</td><td>' + str(i.wins)
			html = html + '</td><td>' + str(i.loses)
			html = html + '</td><td>' + str(percent) + '</td>'
			if i.comment:
				html = html + '<td>' + i.comment + '</td><tr>'
			else:
				html = html + '<td>None</td><tr>'
		hrml = html + '</table>'
		html = html + '</div>'
		html = html + template.render('template/page_end.html', {})
		self.response.out.write(html)
		
class SearchPage(webapp2.RequestHandler):
    def get(self):
		html = 'This is get of SearchPage'
		self.response.out.write(html)
		
    def post(self):
		if self.request.get('button') == "Search" :
			if self.request.get('searchItem'):
				searchItem = self.request.get('searchItem')
				self.handleSearch(searchItem)
			else:
				msg = 'Empty search'
				html = template.render('template/error_page.html', {'error_msg': msg,'destination': '','method': 'get'})
				self.response.out.write(html)
				
    def handleSearch(self,searchItem):
		user = users.get_current_user()
		welcomeString = ('Welcome, %s!'% user.nickname())
		signOutString = users.create_logout_url("/")
		html = template.render('template/page_begin.html', {})
		html = html + '<div id="content" style="width:60%; height:100%; float:left">'
		html = html + '<center>'+ welcomeString +'</center><br>'
		html = html + 'Search item : ' + searchItem + ' found in : <br>'
		items = Item.all()
		for i in items:
			itemName = i.item_name
			if itemName.find(searchItem) != -1:
				html = html + ' item : ' + i.item_name + ' in category : ' + i.category_name + '<br>'
		html = html + '</div>'
		html = html + template.render('template/page_end.html', {})
		self.response.out.write(html)
		
class ExportCategory(webapp2.RequestHandler):
    def get(self):
		user = users.get_current_user()
		welcomeString = ('Welcome, %s!'% user.nickname())
		signOutString = users.create_logout_url("/")
		usrs = db.GqlQuery("SELECT * FROM User")
		categories = db.GqlQuery("SELECT * FROM Category")
		html = template.render('template/page_begin.html', {})
		html = html + '<div id="content" style="width:60%; height:100%; float:left">'
		html = html + '<center>'+ welcomeString +'</center><br>'
		html = html + 'Categories<br><br>'
		html = html + '<form action="/exportcategory" method="post">'
		for u in usrs:
			for c in categories:
				if u.user_name == c.user_name :
					html = html + '<input type="radio" name="info" value="' + c.category_name + ' : ' + c.user_name + '">' + c.category_name + ' by ' + c.user_name + '<br>'
		html = html + '<input type="submit" name="button" value="Select to export"></form>'
		html = html + '</div>'
		html = html + '<div id="sidebar" style="width:20%; height:100%; float:right; background-color:yellow">'
		html = html + '<center><a href="'+ signOutString +'">sign out</a></center>'
		html = html + '<form action="/search" method="post">'
		html = html + '<input type="text" name="searchItem">'
		html = html + '<input type="submit" name="button" value="Search"></form>'
		html = html + '</div>'
		html = html + template.render('template/page_end.html', {})
		self.response.out.write(html)
		
    def post(self):
		if self.request.get('button') == "Select to export" :
			stg = self.request.get('info')
			categoryName, userName = stg.split(" : ")
			self.exportToXML(userName,categoryName)

    def exportToXML(self,userName,categoryName):
		self.response.headers['Content-Type'] = 'text/xml'
		file_name = categoryName.replace(' ', '_')
		self.response.headers['Content-Disposition'] = "attachment; filename=" + str(file_name) + ".xml"
		items = Item.all().filter('category_name =',categoryName).filter('user_name =',userName)
		root = Element('CATEGORY')
		categoryName = SubElement(root, 'NAME')
		categoryName.text = categoryName
		for item in items:
			itemTag = SubElement(root, 'ITEM')
			itemNameTag = SubElement(itemTag, 'NAME')
			itemNameTag.text = item.item_name
		self.response.out.write(tostring(root))	
		
class ImportCategory(webapp2.RequestHandler):
    def get(self):
		user = users.get_current_user()
		welcomeString = ('Welcome, %s!'% user.nickname())
		signOutString = users.create_logout_url("/")
		html = template.render('template/page_begin.html', {})
		html = html + '<div id="content" style="width:60%; height:100%; float:left">'
		html = html + '<center>'+ welcomeString +'</center><br>'
		html = html + 'Upload the category file <br><br>'
		html = html + '<form method="post" action="/importcategory" enctype="multipart/form-data">'		
		html = html + '<input type="file" name="imported_file">'
		html = html + '<input type="hidden" name="task_name" value="import_category"> <br> <br>'
		html = html + '<input type="submit" name="button" value="Import"></form>'
		html = html + '</div>'
		html = html + '<div id="sidebar" style="width:20%; height:100%; float:right; background-color:yellow">'
		html = html + '<center><a href="'+ signOutString +'">sign out</a></center>'
		html = html + '<form action="/search" method="post">'
		html = html + '<input type="text" name="searchItem">'
		html = html + '<input type="submit" name="button" value="Search"></form>'
		html = html + '</div>'
		html = html + template.render('template/page_end.html', {})
		self.response.out.write(html)
		
    def post(self):
		if self.request.get('button') == "Import" :
			user = users.get_current_user()
			userName = user.nickname()
			category_file = self.request.get('imported_file')
			self.importCategory(userName,category_file)

    def importCategory(self,userName,category_file):
		if category_file == "":
			msg = 'Error: No file uploaded or blank file'
			html = template.render('template/error_page.html', {'error_msg': msg,'destination': '','method': 'get'})
			self.response.out.write(html)
			return
		else:
			x = self.request.POST.multi['imported_file'].file.read()
			x = x.replace('\n', '')
			
			# parse xml file		
			root = fromstring(x)
			categoryName = root.findall('NAME')
			categoryName = categoryName[0].text.strip()
			
			# check whether the category with the same name is already present
			if self.categoryPresent(categoryName) == False:
				# create a new category with new name
				category_new = Category(user_name=userName,category_name=categoryName)
				category_new.put()

				# add items in the newly created category
				for child in root:
					if child.tag == "ITEM":
						childName = child.findall('NAME')[0].text.strip()
						self.createNewItem(userName,categoryName,childName)
			else:		
				msg = 'Conflict: Category ' + categoryName + ' cannot be imported.'
				html = template.render('template/error_page.html', {'error_msg': msg,'destination': '','method': 'get'})
				self.response.out.write(html)
				return
		html = '<html><body>'
		html = html + '<center><h1>File successfully imported</h1></center>'
		html = html + '<br><br><form action="/" method="get">'
		html = html + '<center><input type="submit" name="button" value="Back"></form></center>'
		html = html + '</body></html>'
		self.response.out.write(html)
	
    def categoryPresent(self,categoryName):
		user = users.get_current_user()
		userName = user.nickname()
		category = Category.all().filter('user_name =',userName)
		for c in category:
			if c.category_name == categoryName:
				return True
		return False
		
    def createNewItem(self,userName,categoryName,itemName):
		item = Item(user_name=userName,category_name=categoryName,item_name=itemName,wins=0,loses=0)
		item.put()
		return
		
class Category(db.Model):
	user_name = db.StringProperty()
	category_name = db.StringProperty()
	expiration_date = db.StringProperty()
		
class User(db.Model):
	user_name = db.StringProperty()
	
class Item(db.Model):
	user_name = db.StringProperty()
	category_name = db.StringProperty()
	item_name = db.StringProperty()
	comment = db.StringProperty()
	wins = db.IntegerProperty()
	loses = db.IntegerProperty()
		
app = webapp2.WSGIApplication([
    ('/', MainHandler),
	('/category', CategoryPage),
	('/vote', VotePage),
	('/result', ResultPage),
	('/search', SearchPage),
	('/exportcategory', ExportCategory),
	('/importcategory', ImportCategory)
], debug=True)
