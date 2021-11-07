#!/usr/bin/env python3

import re
import requests
from bs4 import BeautifulSoup

class gdrive_handler(object):
	def __fish_out_confirmation_code(self, soup):
		for item in soup.find('a', attrs={'id': 'uc-download-link'}).attrs['href'].split('&'):
			if re.match("^confirm=.*$", item):
				return re.sub("=.*$", "", re.sub("^confirm=", "", item))
		return None

	def __fish_out_cookie(self, response):
		for item in response.headers['Set-Cookie'].split('; '):
			if re.match("^download_warning_", item):
				return item
		return None

	def __word_looks_like_garbage(self, word):
		not_garbage = ['https:', '', 'drive.google.com', 'file', 'd', 'preview']
		return not (word in not_garbage)

	def __retrieve_video_id(self, address):
		for word in address.split('/')[::-1]:
			if self.__word_looks_like_garbage(word):
				return word
		return None

	def __init__(self, player_url):
		self.url = []
		self.cookie = []
		session = requests
		for url in player_url:
			google_id = self.__retrieve_video_id(url)
			magic_url = 'https://drive.google.com/uc?export=download&id=' + google_id
			response = session.get(magic_url)
			soup = BeautifulSoup(response.text, "html.parser")
			confirmation_code = self.__fish_out_confirmation_code(soup)
			magic_cookie = self.__fish_out_cookie(response)
			cookies = {magic_cookie: confirmation_code}
			self.url.append(magic_url + '&confirm=' + confirmation_code)
			self.cookie.append(cookies)
		self.compatible_with_watchtogether = False
		self.download_possible = True
		self.requires_cookie = True
