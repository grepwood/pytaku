#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import re

class sibnet_handler(object):
	def __retrieve_secondary_url(self, url):
		response = self.__session.get(url)
		soup = BeautifulSoup(response.text,"html.parser")
		silly_javascript = str(soup.findAll('script', {'type': 'text/javascript'})[4])
		without_junk_after_mp4 = re.sub(".mp4.*$", ".mp4", silly_javascript)
		mp4_location = re.sub('^.*src: "', "", without_junk_after_mp4)
		return "https://video.sibnet.ru"+mp4_location

	def __request_dance(self, sibnet_primary_url, sibnet_secondary_url):
		rq_headers = { 'User-Agent': self.__user_agent, 'referer': sibnet_primary_url }
		sibnet_next_url = sibnet_secondary_url
		rq_response = ""
		result = ""
		while True:
			rq_response = self.__session.get(sibnet_next_url, allow_redirects=False, headers=rq_headers)
			if not re.match('^//',rq_response.headers['Location']) and rq_response.status_code == 302:
				result = rq_response.headers['Location']
				break
			else:
				sibnet_next_url = re.sub('^//','https://',rq_response.headers['Location'])
		return result
	
	def __init__(self, user_agent, sibnet_url):
		self.url = []
		self.__user_agent = user_agent
		self.__session = requests
		for url in sibnet_url:
			secondary_url = self.__retrieve_secondary_url(url)
			final_url = self.__request_dance(url, secondary_url)
			self.url.append(final_url)
