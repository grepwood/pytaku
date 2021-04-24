#!/usr/bin/env python3

import requests
from mirrors.exceptions.dead import DeadMirror

class clipwatching_handler(object):
	def __is_mirror_dead(self, url):
		return requests.get(url).text == 'File was deleted'

	def __init__(self, player_url):
		self.url = []
		for url in player_url:
			if self.__is_mirror_dead(url) == True:
				raise DeadMirror
