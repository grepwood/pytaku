#!/usr/bin/env python3

import requests
from mirrors.exceptions.dead import DeadMirror

class cloud9_handler(object):
	def __is_mirror_dead(self):
		response = self.__session.get(player_url)
		status_code = response.status_code
		self.__session.post(player_url, headers={'Connection':'close'})
		return status_code == 404

	def __init__(self, browser, player_url):
		self.url = []
		self.__session = requests
		for url in player_url:
			if self.__is_mirror_dead(url) == True:
				raise DeadMirror
			browser.driver.get(player_url)
			browser.wait_for_document_to_finish_loading()
			self.url.append("")
