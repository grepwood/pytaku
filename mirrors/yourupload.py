#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup

class yourupload_handler(object):
	def __init__(self, player_url):
		self.url = []
		self.referer = []
		self.__session = requests
		for url in player_url:
			self.referer.append(url)
			self.__response = self.__session.get(url)
			self.__soup = BeautifulSoup(self.__response.text, "html.parser")
			self.url.append(self.__soup.find('meta', {'property': 'og:video'}).attrs['content'])
