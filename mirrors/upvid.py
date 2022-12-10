#!/usr/bin/env python3

import re
from selenium.webdriver.common.by import By

class upvid_handler(object):
	def __goto_site(self, browser, url):
		browser.driver.get(url)
		browser.wait_for_document_to_finish_loading()

	def __extract_url(self, browser):
		messy_js = browser.driver.find_element(By.XPATH, '/html/body/script[3]').get_attribute('innerHTML')
		messy_js = re.sub("\n", "", messy_js)
		messy_js = re.sub("\t", "", messy_js)
		messy_js = re.sub("'\);source.setAttribute\('type', 'video/mp4'\);.*$", "", messy_js)
		messy_js = re.sub("^.*'src', '", "", messy_js)
		return messy_js

	def __init__(self, browser, player_url):
		self.url = []
		for url in player_url:
			self.__goto_site(browser, url)
			primary_iframe = browser.driver.find_element(By.XPATH, '/html/body/iframe')
			browser.driver.switch_to.frame(primary_iframe)
			secondary_iframe = browser.driver.find_element(By.XPATH, '/html/body/iframe')
			browser.driver.switch_to.frame(secondary_iframe)
			final_url = self.__extract_url(browser)
			self.url.append(final_url)
		self.compatible_with_watchtogether = False
		self.download_possible = True
