#!/usr/bin/env python3

import re
import requests
from bs4 import BeautifulSoup

class cda_file(object):
	def __goto_cda(self, browser, player_url):
		browser.driver.get(player_url)
		browser.wait_for_document_to_finish_loading(verbose=False)

	def __get_cda_video_id(self, url):
		return re.sub("^.*/", "", url)

	def __get_qualities(self, soup):
		result = []
		for item in soup.find('div', attrs={'class': 'wrapqualitybtn'}).findChildren('a'):
			result.append(item.text)
		return result

	def __get_direct_link(self, url, browser):
		self.__goto_cda(browser, url)
		return browser.driver.find_elements_by_xpath('//html/body/div/div[1]/div/div/div/div/div/div/span[3]/span[1]/span/span[1]/video')[0].get_attribute('src')

	def __init__(self, url, browser):
		cda_video_id = self.__get_cda_video_id(url)
		cda_video_article_url = 'https://www.cda.pl/video/'+cda_video_id
		session = requests
		response = session.get(cda_video_article_url)
		soup = BeautifulSoup(response.text, "html.parser")
		self.quality = self.__get_qualities(soup)
		self.url = []
		for quality in self.quality:
			cda_embed_url = 'https://ebd.cda.pl/800x450/'+cda_video_id+'?wersja='+quality
			direct_link = self.__get_direct_link(cda_embed_url, browser)
			self.url.append(direct_link)
			print('Cda '+quality+': '+direct_link)

class cda_handler(object):
	def __init__(self, browser, player_url):
		self.url = []
		for url in player_url:
			x = cda_file(url, browser)
			self.url.append(x.url[-1])
