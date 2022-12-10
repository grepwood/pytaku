#!/usr/bin/env python3

import requests
from selenium.webdriver.common.by import By
from mirrors.exceptions.dead import DeadMirror

class mp4upload_handler(object):
	def __is_mirror_dead(self, player_url):
		response = self.__session.get(player_url)
		status_code = response.status_code
		self.__session.post(player_url, headers={'Connection':'close'})
		return status_code == 404

	def __goto_mp4upload(self, browser, player_url):
		browser.driver.get(player_url)
		browser.wait_for_document_to_finish_loading()

	def __init__(self, browser, player_url):
		self.url = []
		self.__session = requests
		for url in player_url:
			if self.__is_mirror_dead(url) == True:
				raise DeadMirror
			self.__goto_mp4upload(browser, url)
			self.url.append(browser.driver.find_element(By.XPATH, '//*[@id="player_html5_api"]').get_attribute('src'))
		self.compatible_with_watchtogether = False
		self.download_possible = True
		self.requires_referer = True
		self.requires_tls_compromise = True
