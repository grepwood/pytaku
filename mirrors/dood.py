#!/usr/bin/env python3

from bs4 import BeautifulSoup

class dood_handler(object):
	def __goto_streamtape(self, browser, dood_url):
		browser.driver.get(dood_url)
		browser.wait_for_document_to_finish_loading()
	
	def __get_url(self, browser):
		soup = BeautifulSoup(browser.driver.page_source,"html.parser")
		return soup.findAll('video')[0].attrs['src']
	
	def __init__(self, browser, dood_url):
		self.url = []
		for url in player_url:
			self.__goto_streamtape(browser, dood_url)
			self.url.append(self.__get_url(browser))
