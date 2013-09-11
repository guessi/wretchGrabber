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
		self.page_max = 1
	
	# if the folder not exist, create it
	def make_folder(self):
		if not os.path.exists(self.folder_name):
			os.makedirs(self.folder_name)

	# try to get the raw content from the given URL
	def get_content(self, url):
		req = urllib2.Request(url)
		req.add_header("User-Agent", "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11")
		res = urllib2.urlopen(req)
		return res.read()

	# check if the given URL meet our expectation
	def verify(self, url):
		m1 = re.search("http:\/\/www.wretch.cc\/album\/album.php\?id=([a-zA-Z0-9]+)\&book=([\d]+)", url)
		m2 = re.search("\&page=([\d]+)", url)
		if m1:
			self.user_id = m1.group(1)
			self.book_id = m1.group(2)
			self.folder_name = "%s/album-%s" % (self.user_id, self.book_id)
			self.make_folder()
			self.find_max()

	# try to find out all pages of the album and grab them all
	def find_max(self):
		url = "http://www.wretch.cc/album/album.php?id=" + self.user_id + "&book=" + self.book_id
		raw = self.get_content(url)
		page = re.findall("\"\.\/album.php\?id=[a-zA-Z0-9]+\&book=[\d]+\&page=([\d]+)\"", raw)
		if page:
			self.page_max = max(page)
		print("target album: %s" % url)
		self.find_pages()
		print("all done")

	# find out all photo links in the album
	def find_pages(self):
		print("total pages: %s" % self.page_max)
		for i in range(1, int(self.page_max) + 1):
			url = "http://www.wretch.cc/album/album.php?id=" + self.user_id + "&book=" + self.book_id + "&page=" + str(i)
			print("current page: %s" % i)
			raw = self.get_content(url)
			list = re.findall("src=.*\/thumbs\/t([\d]+).jpg\?", raw)
			self.get_album(list)

	# extract the picture ID list
	def get_album(self, list):
		for image_id in list:
			self.get_by_id(image_id)

	# extract links from page source
	def get_path(self, image_id):
		raw = self.get_content("http://www.wretch.cc/album/show.php?i=" + self.user_id + "&b=" + self.book_id + "&f=" + image_id)
		p1 = "<img.*class=\'displayimg\'.*src=\'(http:\/\/.*\.yimg\.com\/.*[\d\+\.jpg\?[a-zA-Z0-9]+)\'.*>"
		p2 = "<img.*id=\'DisplayImage\'.*src=\'(http:\/\/.*\.yimg\.com\/.*[\d\+\.jpg\?[a-zA-Z0-9\-]+)\'.*>"
		m1 = re.search(p1, raw)
		m2 = re.search(p2, raw)
		if m1:
			return m1.group(1)
		if m2:
			return m2.group(1)

	# pass photo link to get_image()
	def get_by_id(self, image_id):
		link = self.get_path(image_id)
		if link:
			self.get_image(link, image_id)

	# get photo back to client side
	def get_image(self, img, id):
		filename = "%s/%s.jpg" % (self.folder_name, id)
		print("saving: %s.jpg ..." % id),
		file = open(filename, 'wb')
		file.write(urllib2.urlopen(img).read())
		file.close()
		print("done")

if __name__ == "__main__":
	try:
		with open('album.txt') as f:
			target = f.readline()
		f.close()
		instance = wretchGrabber()
		instance.verify(target)
	except:
		print("abort")
		pass
