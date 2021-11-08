#!/usr/bin/env python3

import re
from bs4 import BeautifulSoup
import selenium
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from mirrors.aparat import aparat_handler
from mirrors.cda import cda_handler
from mirrors.cloud9 import cloud9_handler
from mirrors.cloudvideo import cloudvideo_handler
from mirrors.crunchyroll import crunchyroll_handler
from mirrors.dailymotion import dailymotion_handler
from mirrors.dood import dood_handler
from mirrors.facebook import facebook_handler
from mirrors.gdrive import gdrive_handler
from mirrors.mega import mega_handler
from mirrors.mp4upload import mp4upload_handler
from mirrors.mystream import mystream_handler
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
from mirrors.upvid import upvid_handler
from mirrors.exceptions.dead import DeadMirror
from mirrors.exceptions.unsupported import MirrorVendorUnsupported

class direct_url(object):
	def __get_player_html(self, browser, mirror):
		actions = ActionChains(browser.driver)
		print('trying to snoop for '+mirror.vendor+' player on shinden')
		while browser.driver.find_elements_by_xpath('//*[@id="'+mirror.xpath+'"]') == 0:
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
		print('finished parsing player element')
		soup = BeautifulSoup(page_source,"html.parser")
		return soup
	
	def __get_player_url_list(self, browser, mirror):
		player_url_list = []
		print('retrieving player URL')
		while player_url_list == []:
			soup = self.__get_player_html(browser,mirror)
			try:
				if mirror.vendor in ['Yourupload', 'Crunchyroll']:
					players = soup.findAll('a', {'class': 'button-player'})
					attribute_to_look_for = 'href'
				elif mirror.vendor in ['Tunepk', 'Clipwatching']:
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
				browser.driver.refresh()
				browser.wait_for_document_to_finish_loading()
		return player_url_list

	def __fill_out_blanks(self, result):
		test = None
		try:
			test = result.requires_referer
		except AttributeError:
			result.requires_referer = False
			result.referrer = []
		try:
			test = result.requires_redirect
		except AttributeError:
			result.requires_redirect = False
		try:
			test = result.requires_browser_identity
		except AttributeError:
			result.requires_browser_identity = False
			result.user_agent = ""
		try:
			test = result.requires_raw_data
		except AttributeError:
			result.requires_raw_data = False
		try:
			test = result.requires_cookie
		except AttributeError:
			result.requires_cookie = False
			result.cookie = {}
		try:
			test = result.requires_tls_compromise
		except AttributeError:
			result.requires_tls_compromise = False
		try:
			test = result.is_m3u8
		except AttributeError:
			result.is_m3u8 = False

	def __get_url(self, browser, mirror):
		if not mirror.vendor in self.__compatible_mirror_types:
			raise MirrorVendorUnsupported
		player_url = self.__get_player_url_list(browser, mirror)
		shinden_url = browser.driver.current_url
		result = ""
		if mirror.vendor == 'Sibnet':
			result = sibnet_handler(browser.user_agent, player_url)
		elif mirror.vendor == 'Mega':
			result = mega_handler(player_url)
		elif mirror.vendor == 'Streamtape':
			result = streamtape_handler(browser, player_url)
		elif mirror.vendor == 'Dood':
			result = dood_handler(browser, player_url)
		elif mirror.vendor == 'Streamsb':
			result = streamsb_handler(browser, player_url, mirrors.vendor)
		elif mirror.vendor == 'Cda':
			result = cda_handler(browser, player_url)
		elif mirror.vendor == 'Mp4upload':
			result = mp4upload_handler(browser, player_url)
		elif mirror.vendor == 'Vidloxtv':
			result = vidlox_handler(browser, player_url)
		elif mirror.vendor == 'Vidoza':
			result = vidoza_handler(browser, player_url, mirrors.vendor)
		elif mirror.vendor == 'Fb':
			result = facebook_handler(player_url)
		elif mirror.vendor == 'Vk':
			result = vkontakte_handler(browser, player_url)
		elif mirror.vendor == 'Aparat':
			result = aparat_handler(player_url)
		elif mirror.vendor == 'Dailymotion':
			result = dailymotion_handler(player_url)
		elif mirror.vendor == 'Yourupload':
			tmp = yourupload_handler(player_url)
		elif mirror.vendor == 'Myviru':
			tmp = myviru_handler(player_url)
		elif mirror.vendor == 'Mystream':
			result = mystream_handler(browser, player_url)
		elif mirror.vendor == 'Upvid':
			result = upvid_handler(browser, player_url)
		elif mirror.vendor == 'Cloudvideo':
			result = cloudvideo_handler(player_url)
		elif mirror.vendor == 'Crunchyroll':
			result = crunchyroll_handler(player_url)
		elif mirror.vendor == 'Gdrive':
			result = gdrive_handler(player_url)
		self.__fill_out_blanks(result)
		browser.driver.get(shinden_url)
		browser.wait_for_document_to_finish_loading()
		return result

	def __init__(self, browser, mirror, supported_mirrors):
		self.__compatible_mirror_types = supported_mirrors
		everything_went_fine = False
		self.mirror_info = None
		try:
			self.mirror_info = self.__get_url(browser, mirror)
			everything_went_fine = True
		except DeadMirror:
			pass
		count = 0
		if everything_went_fine == True:
			for url in self.mirror_info.url:
				print('Received URL #'+str(count+1)+': '+self.mirror_info.url[count])
				count += 1
		else:
			print('DEAD URL')
