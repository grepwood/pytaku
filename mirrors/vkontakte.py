#!/usr/bin/env python3

import re

class vkontakte_handler(object):
	def __init__(self, browser, player_url):
		self.url = []
		for url in player_url:
			browser.driver.get(url)
			browser.wait_for_document_to_finish_loading()
			messy_js = browser.driver.find_elements_by_xpath('//html/body/div[7]/script')[0].get_attribute('innerHTML')
			without_newlines = re.sub("\n", "", messy_js)
			before_url = re.sub('^.*cache720":"', "", without_newlines)
			after_url = re.sub('",".*$', "", before_url)
			self.url.append(re.sub('\\\\/', "/", after_url))
