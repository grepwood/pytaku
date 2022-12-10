#!/usr/bin/env python3

import re
from selenium.webdriver.common.by import By

class vkontakte_handler(object):
	def __init__(self, browser, player_url):
		self.url = []
		for url in player_url:
			browser.driver.get(url)
			browser.wait_for_document_to_finish_loading()
			messy_js = browser.driver.find_element(By.XPATH, '//html/body/div[7]/script').get_attribute('innerHTML')
			without_newlines = re.sub("\n", "", messy_js)
			before_url = re.sub('^.*cache720":"', "", without_newlines)
			after_url = re.sub('",".*$', "", before_url)
			self.url.append(re.sub('\\\\/', "/", after_url))
		self.compatible_with_watchtogether = False
		self.download_possible = True
