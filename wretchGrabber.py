#!/usr/bin/env python
'''
description: a simple album grabber for http://www.wretch.cc/,
             a well-known album service provider in Taiwan,
             whose EOL date was expected to be Dec 26, 2013 :(
     source: https://github.com/guessi/wretchGrabber
     author: Kuo-Le, Mei (guessi@gmail.com)
    license: GNU General Public License, version 2
      usage: put the album's URL into the file <album.txt>,
             then execute wretchGrabber and wait

             $ python wretchGrabber.py

             you can always abort it anytime by <CTRL-C>
'''
import os
import re
import urllib2

class wretchGrabber():
	# initialize the most common use variables
	def __init__(self):
		self.book_id = ''
		self.user_id = ''
		self.folder_name = ''
		self.url_prefix = 'http://www.wretch.cc/album'
		self.page_max = 1

	# restore all configurations
	def resetDefault(self):
		self.user_id = ''
		self.book_id = ''
		self.folder_name = ''
		self.page_max = 1

	# if the folder not exist, create it
	def makeFolder(self):
		self.folder_name = "download/%s/album-%s" % (self.user_id, self.book_id)
		if not os.path.exists(self.folder_name):
			os.makedirs(self.folder_name)

	# try to get the raw content from the given URL
	def getContent(self, url):
		req = urllib2.Request(url)
		req.add_header("User-Agent", "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11")
		res = urllib2.urlopen(req)
		return res.read()

	# check if the given URL meet our expectation
	def verifyURL(self, url):
		match = re.search("http:\/\/www.wretch.cc\/album\/album.php\?id=([a-zA-Z0-9]+)\&book=([\d]+)", url)
		if match:
			self.user_id = match.group(1)
			self.book_id = match.group(2)
			self.makeFolder()
			self.findMaxPage()
		else:
			self.resetDefault()

	# try to find out all pages of the album and grab them all
	def findMaxPage(self):
		url = self.url_prefix + "/album.php?id=" + self.user_id + "&book=" + self.book_id
		raw = self.getContent(url)
		page = re.findall("\"\.\/album.php\?id=[a-zA-Z0-9]+\&book=[\d]+\&page=([\d]+)\"", raw)
		if page:
			self.page_max = max(page)
		print("target album: %s" % url)
		self.getAllPages()
		print("all done")

	# find out all photo links in the album
	def getAllPages(self):
		print("total pages: %s" % self.page_max)
		for page_num in range(1, int(self.page_max) + 1):
			url = self.url_prefix + "/album.php?id=" + self.user_id + "&book=" + self.book_id + "&page=" + str(page_num)
			print("current page: %s" % page_num)
			raw = self.getContent(url)
			list = re.findall("src=.*\/thumbs\/t([\d]+).jpg\?", raw)
			self.getSinglePage(list)

	# extract the picture ID list
	def getSinglePage(self, list):
		for image_id in list:
			self.getById(image_id)

	# extract links from page source
	def getRealPath(self, image_id):
		raw = self.getContent(self.url_prefix + "/show.php?i=" + self.user_id + "&b=" + self.book_id + "&f=" + image_id)
		m1 = re.search("<img.*class=\'displayimg\'.*src=\'(http:\/\/.*\.yimg\.com\/.*[\d\+\.jpg\?[a-zA-Z0-9_\.\-]+)\'.*>", raw)
		m2 = re.search("<img.*id=\'DisplayImage\'.*src=\'(http:\/\/.*\.yimg\.com\/.*[\d\+\.jpg\?[a-zA-Z0-9_\.\-]+)\'.*>", raw)
		if m1:
			return m1.group(1)
		elif m2:
			return m2.group(1)
		else:
			return None

	# pass photo link to saveImage()
	def getById(self, image_id):
		link = self.getRealPath(image_id)
		if link:
			self.saveImage(link, image_id)

	# get photo back to client side
	def saveImage(self, image, image_id):
		filename = "%s/%s.jpg" % (self.folder_name, image_id)
		print("saving: %s.jpg ..." % image_id),
		file = open(filename, 'wb')
		file.write(urllib2.urlopen(image).read())
		file.close()
		print("done")

if __name__ == "__main__":
	try:
		with open('album.txt') as f:
			target = f.readline()
		f.close()
		instance = wretchGrabber()
		instance.verifyURL(target)
	except:
		print("abort")
		pass
