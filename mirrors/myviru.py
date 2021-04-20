#!/usr/bin/env python3

import requests
import re
from bs4 import BeautifulSoup

class myviru_handler(object):
	def __init__(self, player_url):
		self.url = []
		self.cookie = []
		session = requests
		for url in player_url:
			response = session.get(url)
			soup = BeautifulSoup(response.text, "html.parser")
			mess = str(soup.findAll('script')[-2]).split(", ")[0]
			mess = re.sub("\n", "", mess)
			mess = re.sub("\r", "", mess)
			mess = re.sub("^.*v=", "", mess)
			mess = re.sub("\\\\u0026.*$", "", mess)
			mess = re.sub("%3a", ":", mess)
			mess = re.sub("%2f", "/", mess)
			mess = re.sub("%26", "&", mess)
			mess = re.sub("%3d", "=", mess)
			mess = re.sub("%3f", "?", mess)
			cookie_dict = {'UniversalUserID': response.cookies.get_dict()['UniversalUserID']}
			response = session.get(mess, allow_redirects=False, cookies=cookie_dict)
			self.url.append(response.headers['Location'])
			self.cookie.append(cookie_dict)
