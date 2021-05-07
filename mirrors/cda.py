#!/usr/bin/env python3

import re
import traceback
import time
import requests
from bs4 import BeautifulSoup

class CaptchaFound(Exception):
	"""Raised when we land on Cloudflare captcha instead of the player"""
	pass

class UnknownCdaError(Exception):
	"""Raised when we encounter unknown error with Cda"""
	pass

class IncompleteCdaLoad(Exception):
	"""Raised when loading Cda is incomplete"""
	pass

class CdaRefusesCooperation(Exception):
	"""Raised when Cda absolutely refuses to co-operate"""
	pass

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

	def __detect_captcha(self, browser):
		return browser.driver.title == self.srapcza

	def __get_direct_link(self, url, browser):
		self.__goto_cda(browser, url)
		soup = BeautifulSoup(browser.driver.page_source, "html.parser")
		video_tag = soup.find('video', attrs={'class': 'pb-video-player'})
		if video_tag is None:
			if self.__detect_captcha(browser) == True:
				raise CaptchaFound
			else:
				raise IncompleteCdaLoad
		return video_tag.attrs['src']

	def __get_time(self):
		return int(time.time())

	def __throw_coop_refusal_if_exceeded_timeout(self, time_start, timeout):
		if self.__get_time() - time_start > timeout: raise CdaRefusesCooperation

	def __get_direct_link_from_soup(self, soup):
		return soup.find('video', attrs={'class': 'pb-video-player'}).attrs['src']

	def __verify_direct_link(self, direct_link):
		return re.match("^https://[a-z0-9]*.cda.pl/", direct_link)

	def __deal_with_captcha(self):
		soup = browser.handle_captcha(self.srapcza)
		return self.__get_direct_link_from_soup(soup)

	def __init__(self, url, browser):
		self.srapcza = 'Attention Required! | Cloudflare'
		cda_video_id = self.__get_cda_video_id(url)
		cda_video_article_url = 'https://www.cda.pl/video/'+cda_video_id
		session = requests
		response = session.get(cda_video_article_url)
		soup = BeautifulSoup(response.text, "html.parser")
		self.quality = self.__get_qualities(soup)
		self.url = []
		timeout = 60
		for quality in self.quality:
			cda_embed_url = 'https://ebd.cda.pl/800x450/'+cda_video_id+'?wersja='+quality
			print(cda_embed_url)
			time_start = self.__get_time()
			direct_link = ""
			while True:
				try:
					direct_link = self.__get_direct_link(cda_embed_url, browser)
				except CaptchaFound:
					direct_link = self.__deal_with_captcha()
				except IncompleteCdaLoad:
					self.__throw_coop_refusal_if_exceeded_timeout(time_start, timeout)
					next
				except UnknownCdaError:
					self.__throw_coop_refusal_if_exceeded_timeout(time_start, timeout)
					next
				if self.__verify_direct_link(direct_link):
					time_start = self.__get_time()
					break
			self.url.append(direct_link)
			print('Cda '+quality+': '+direct_link)

class cda_handler(object):
	def __init__(self, browser, player_url):
		self.url = []
		for url in player_url:
			x = cda_file(url, browser)
			self.url.append(x.url[-1])
