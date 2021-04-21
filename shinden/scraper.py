#!/usr/bin/env python3

import re
from bs4 import BeautifulSoup
import selenium
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from mirrors.aparat import aparat_handler
from mirrors.cda import cda_handler
from mirrors.cloud9 import cloud9_handler
from mirrors.dailymotion import dailymotion_handler
from mirrors.dood import dood_handler
from mirrors.facebook import facebook_handler
from mirrors.mp4upload import mp4upload_handler
from mirrors.myviru import myviru_handler
from mirrors.sibnet import sibnet_handler
from mirrors.streamsb import streamsb_handler
from mirrors.streamtape import streamtape_handler
from mirrors.tunepk import tunepk_handler
from mirrors.youtube import youtube_handler
from mirrors.yourupload import yourupload_handler
from mirrors.vidlox import vidlox_handler
from mirrors.vidoza import vidoza_handler
from mirrors.vkontakte import vkontakte_handler
from mirrors.exceptions.dead import DeadMirror
from mirrors.exceptions.unsupported import MirrorVendorUnsupported

class direct_url(object):
	def __get_player_html(self, browser, mirror):
		actions = ActionChains(browser.driver)
		print('trying to snoop for '+mirror.vendor+' player on shinden')
		browser.scroll_to_element('//*[@id="'+mirror.xpath+'"]')
		browser.click_invisible_bullshit()
		while True:
			try:
				print('Clicking xpath '+mirror.xpath)
				browser.driver.find_elements_by_xpath('//*[@id="'+mirror.xpath+'"]')[0].click()
				break
			except selenium.common.exceptions.ElementClickInterceptedException:
				actions.send_keys_to_element(browser.driver.find_elements_by_xpath('//html/body')[0], Keys.DOWN).perform()
		print('waiting for countdown')
		browser.wait_for_countdown()
		print('parsing player element')
		page_source = browser.driver.find_elements_by_xpath('//html/body/div[4]/div/article/div[2]')[0].get_attribute('innerHTML')
		soup = BeautifulSoup(page_source,"html.parser")
		return soup
	
	def __get_player_url_list(self, browser, mirror):
		player_url_list = []
		print('retrieving player URL')
		while player_url_list == []:
			soup = self.__get_player_html(browser,mirror)
			try:
				if mirror.vendor in ['Yourupload']:
					players = soup.findAll('a', {'class': 'button-player'})
					attribute_to_look_for = 'href'
				elif mirror.vendor in ['Tunepk']:
					players = soup.findAll('a', {'class': 'player-external-link'})
					attribute_to_look_for = 'href'
				else:
					players = soup.findAll('iframe')
					attribute_to_look_for = 'src'
				for player in players:
					base_referant = player.attrs[attribute_to_look_for]
					if mirror.vendor == 'Sibnet':
						player_url = 'https://video.sibnet.ru/shell.php?videoid='+re.sub("^.*=","",base_referant)
					elif mirror.vendor == 'Mega':
						player_url = "https://mega.co.nz/#!"+base_referant.split('#!')[1]
					elif mirror.vendor in ['Cda', 'Mp4upload', 'Vidloxtv', 'Vk', 'Dailymotion', 'Yourupload', 'Myviru']:
						player_url = re.sub('^//','https://',base_referant)
					else:
						player_url = base_referant
					player_url_list.append(player_url)
				break
			except IndexError:
				print('error occurred on shinden, retryting')
#				possible location: /html/body/div[4]/div/article/div[2]/div/div[2]/div
				browser.driver.refresh()
				browser.wait_for_document_to_finish_loading()
		return player_url_list
	
	def __get_url(self, browser, mirror):
		if not mirror.vendor in self.__compatible_mirror_types:
			raise MirrorVendorUnsupported
		player_url = self.__get_player_url_list(browser, mirror)
		shinden_url = browser.driver.current_url
		result = ""
		if mirror.vendor == 'Sibnet':
			self.compatible_with_watchtogether = True
			self.download_possible = True
			self.requires_referer = False
			self.requires_redirect = False
			self.requires_browser_identity = False
			self.requires_raw_data = False
			self.requires_cookie = False
			result = sibnet_handler(browser.user_agent, player_url).url
			self.referer = ""
			self.user_agent = ""
			self.raw_data = ""
		elif mirror.vendor == 'Mega':
			self.compatible_with_watchtogether = False
			self.download_possible = True
			self.requires_referer = False
			self.requires_redirect = False
			self.requires_browser_identity = False
			self.requires_raw_data = False
			self.requires_cookie = False
			result = player_url
			self.referer = ""
			self.user_agent = ""
			self.raw_data = ""
		elif mirror.vendor == 'Streamtape':
			self.compatible_with_watchtogether = True
			self.download_possible = True
			self.requires_referer = False
			self.requires_redirect = False
			self.requires_browser_identity = False
			self.requires_cookie = False
			result = streamtape_handler(browser, player_url).url
			self.referer = ""
			self.user_agent = ""
			self.raw_data = ""
		elif mirror.vendor == 'Dood':
			self.compatible_with_watchtogether = False
			self.download_possible = True
			self.requires_referer = True
			self.requires_redirect = False
			self.requires_browser_identity = False
			self.requires_raw_data = False
			self.requires_cookie = False
			result = dood_handler(browser, player_url).url
			self.referer = player_url
			self.user_agent = ""
			self.raw_data = ""
		elif mirror.vendor == 'Streamsb':
			self.compatible_with_watchtogether = False
			self.download_possible = True
			self.requires_referer = False
			self.requires_redirect = False
			self.requires_browser_identity = False
			self.requires_raw_data = False
			self.requires_cookie = False
			result = streamsb_handler(browser, player_url, mirrors.vendor).url
			self.referer = ""
			self.user_agent = ""
			self.raw_data = ""
		elif mirror.vendor == 'Cda':
			self.compatible_with_watchtogether = True
			self.download_possible = True
			self.requires_referer = False
			self.requires_redirect = False
			self.requires_browser_identity = True
			self.requires_raw_data = False
			self.requires_cookie = False
			result = cda_handler(browser, player_url).url
			self.referer = ""
			self.user_agent = browser.user_agent
			self.raw_data = ""
		elif mirror.vendor == 'Mp4upload':
			self.compatible_with_watchtogether = False
			self.download_possible = True
			self.requires_referer = True
			self.requires_redirect = False
			self.requires_browser_identity = False
			self.requires_tls_compromise = True
			self.requires_raw_data = False
			self.requires_cookie = False
			result = mp4upload_handler(browser, player_url).url
			self.referer = ""
			self.user_agent = ""
			self.raw_data = ''
		elif mirror.vendor == 'Vidloxtv':
			self.compatible_with_watchtogether = False
			self.download_possible = True
			self.requires_referer = False
			self.requires_redirect = False
			self.requires_browser_identity = False
			self.requires_raw_data = False
			self.requires_cookie = False
			result = vidlox_handler(browser, player_url).url
			self.referer = ""
			self.user_agent = ""
			self.raw_data = ""
		elif mirror.vendor == 'Vidoza':
			self.compatible_with_watchtogether = False
			self.download_possible = True
			self.requires_referer = False
			self.requires_redirect = False
			self.requires_browser_identity = False
			self.requires_raw_data = False
			self.requires_cookie = False
			result = vidoza_handler(browser, player_url, mirrors.vendor).url
			self.referer = ""
			self.user_agent = ""
			self.raw_data = ""
		elif mirror.vendor == 'Fb':
			self.compatible_with_watchtogether = False
			self.download_possible = True
			self.requires_referer = False
			self.requires_redirect = False
			self.requires_browser_identity = False
			self.requires_raw_data = False
			self.requires_cookie = False
			result = facebook_handler(player_url).url
			self.referer = ""
			self.user_agent = ""
			self.raw_data = ""
		elif mirror.vendor == 'Vk':
			self.compatible_with_watchtogether = False
			self.download_possible = True
			self.requires_referer = False
			self.requires_redirect = False
			self.requires_browser_identity = False
			self.requires_raw_data = False
			self.requires_cookie = False
			result = vkontakte_handler(browser, player_url).url
			self.referer = ""
			self.user_agent = ""
			self.raw_data = ""
		elif mirror.vendor == 'Aparat':
			self.compatible_with_watchtogether = False
			self.download_possible = True
			self.requires_referer = False
			self.requires_redirect = False
			self.requires_browser_identity = False
			self.requires_raw_data = False
			self.requires_cookie = False
			result = aparat_handler(player_url).url
			self.referer = ""
			self.user_agent = ""
			self.raw_data = ""
		elif mirror.vendor == 'Dailymotion':
			self.compatible_with_watchtogether = True
			self.download_possible = True
			self.requires_referer = False
			self.requires_redirect = False
			self.requires_browser_identity = False
			self.requires_raw_data = False
			self.requires_cookie = False
			result = dailymotion_handler(player_url).url
			self.referer = ""
			self.user_agent = ""
			self.raw_data = ""
		elif mirror.vendor == 'Yourupload':
			self.compatible_with_watchtogether = False
			self.download_possible = True
			self.requires_referer = True
			self.requires_redirect = False
			self.requires_browser_identity = False
			self.requires_raw_data = False
			self.requires_cookie = False
			tmp = yourupload_handler(player_url)
			result = tmp.url
			self.referer = tmp.referer
			self.user_agent = ""
			self.raw_data = ""
		elif mirror.vendor == 'Myviru':
			self.compatible_with_watchtogether = False
			self.download_possible = True
			self.requires_referer = False
			self.requires_redirect = False
			self.requires_browser_identity = False
			self.requires_raw_data = False
			self.requires_cookie = True
			tmp = myviru_handler(player_url)
			result = tmp.url
			self.cookie = tmp.cookie
			self.user_agent = ""
			self.raw_data = ""
		browser.driver.get(shinden_url)
		browser.wait_for_document_to_finish_loading()
		return result
	
	def __init__(self, browser, mirror, supported_mirrors):
		self.compatible_with_watchtogether = False
		self.download_possible = False
		self.requires_referer = False
		self.requires_browser_identity = False
		self.__compatible_mirror_types = supported_mirrors
		try:
			self.url = self.__get_url(browser, mirror)
		except DeadMirror:
			self.url = ['DEAD URL']
		count = 0
		for url in self.url:
			print('Received URL #'+str(count+1)+': '+self.url[count])
			count += 1
