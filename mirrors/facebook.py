#!/usr/bin/env python3

import re
import requests
from bs4 import BeautifulSoup

class facebook_handler(object):
	def __find_script_with_mp4(self):
		count = 0
		for item in self.__soup.findAll('script'):
			if re.match(".*hd_src.*", str(item)):
				return count
			count += 1
		raise ValueError("Facebook handler could not find src_no_ratelimit")

	def __init__(self, player_url):
		self.url = []
		self.__session = requests
		close_header = {'Connection':'close'}
		for url in player_url:
			self.__session = requests.get(url)
			self.__soup = BeautifulSoup(self.__session.text, "html.parser")
			self.__session.post(url, headers=close_header)
			script_index = self.__find_script_with_mp4()
			messy_js = str(self.__soup.findAll('script')[script_index])
# hd_src can also be replaced with src_no_ratelimit for smaller videos
			without_beginning_of_declaration = re.sub('^.*hd_src":"', "", messy_js)
			with_nasty_backslashes = re.sub('".*$', "", without_beginning_of_declaration)
			final_link = re.sub('\\\\', "", with_nasty_backslashes)
			self.url.append(final_link)
		self.compatible_with_watchtogether = False
		self.download_possible = True
