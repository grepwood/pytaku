#!/usr/bin/env python3

from bs4 import BeautifulSoup
import pdb

class dood_handler(object):
	def goto_streamtape(self, browser, url):
		browser.driver.get(url)
		browser.wait_for_document_to_finish_loading()

	def detect_cf_captcha(self, browser):
		pass

	def get_url(self, browser):
		soup = BeautifulSoup(browser.driver.page_source,"html.parser")
		return soup.findAll('video')[0].attrs['src']
	
	def __init__(self, browser, player_url):
		self.url = []
		pdb.set_trace()
		for url in player_url:
			self.goto_streamtape(browser, url)
			self.url.append(self.get_url(browser))
		self.compatible_with_watchtogether = False
		self.download_possible = True
		self.requires_referer = True
		self.referrer = player_url
