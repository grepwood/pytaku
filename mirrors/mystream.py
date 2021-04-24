#!/usr/bin/env python3

from bs4 import BeautifulSoup

class mystream_handler(object):
	def __goto_site(self, browser, url):
		browser.driver.get(url)
		browser.wait_for_document_to_finish_loading()

	def __extract_url(self, browser):
		soup = BeautifulSoup(browser.driver.page_source, "html.parser")
		return soup.find('video', attrs={'class': 'vjs-tech', 'id': 'videoPlayer_html5_api'}).findChild('source').attrs['src']

	def __init__(self, browser, player_url):
		self.url = []
		for url in player_url:
			self.__goto_site(browser, url)
			final_url = self.__extract_url(browser)
			self.url.append(final_url)
