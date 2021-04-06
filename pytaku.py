#!/usr/bin/env python3
import requests
import re
import bs4
import selenium
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from mega import Mega
import json
import os
import detect_browsers
import pdb
import sys

class episode_list(object):
	def __init__(self, anime_id):
		query_url = "https://shinden.pl/series/"+anime_id+"/all-episodes"
		req = requests.get(query_url)
		html_page = req.content
		soup = bs4.BeautifulSoup(html_page, "html.parser")
# For whatever reason, reversing big_tag_matrix doesn't work

		big_tag_matrix = soup.findAll('tbody', attrs={'class','list-episode-checkboxes'})[0].findAll('td')
		self.episode_count = int(len(big_tag_matrix)/6)
		self.title = []
# These parameters require selenium. We cannot afford this kind of overhaul right now.
#		self.available = []
#		self.languages = []
		self.id = []
		count = 0
		while count < self.episode_count:
			episode_id = re.sub('^.*/view/','',big_tag_matrix[(self.episode_count - count - 1)*6+5].findChild('a')['href'])
			title = big_tag_matrix[(self.episode_count - count - 1)*6+1].get_text(strip=True)
			self.title.append(title)
			self.id.append(episode_id)
			count = count + 1
	def list_all(self):
		count = 0
		while count < self.episode_count:
			print(str(count+1)+" : "+self.title[count]+" : "+str(self.id[count]))
			count = count + 1

class browser_engine(object):
	def __init__(self):
		self.preferred_browser = detect_browsers.detect_browsers()[0]
		self.profile = ""
		self.options = ""
		self.driver = ""
		global debug_mode
		if self.preferred_browser == 'firefox':
			self.profile = webdriver.FirefoxProfile()
			self.options = webdriver.FirefoxOptions()
			self.profile.set_preference("intl.accept_languages", "pl")
			if debug_mode == False:
				self.options.headless = True
			self.profile.update_preferences()
			self.driver = webdriver.Firefox(self.profile,options=self.options)
			self.user_agent = self.driver.execute_script("return navigator.userAgent;")
		elif self.preferred_browser == 'google-chrome-stable':
			self.profile = webdriver.ChromeProfile()
			self.options = webdriver.ChromeOptions()
			self.options.addArguments("-lang=pl")
			if debug_mode == False:
				self.options.headless = True
			self.driver = webdriver.Chrome(self.profile,options=self.options)
			self.user_agent = re.sub('Headless','',self.driver.execute_script("return navigator.userAgent;"))
			self.options.addArguments("user-agent="+self.user_agent)
			self.driver.close()
			self.driver = webdriver.Chrome(self.options)
		elif self.preferred_browser == 'msedge':
			raise ValueError("idk how to do this on msedge sorry")
		else:
			raise ValueError("Unsupported browser")
		self.accepted_gdpr = False
		self.accepted_cookies = False
	
	def quit(self):
		self.driver.quit()
		self.accepted_gpdr = False
		self.accepted_cookies = False
		
	def start_again(self):
		if self.preferred_browser == 'firefox':
			self.driver = webdriver.Firefox(self.profile)
		elif self.preferred_browser == 'google-chrome-stable':
			self.driver = webdriver.Chrome(self.profile)
		elif self.preferred_browser == 'msedge':
			raise ValueError("idk how to do this on msedge sorry")
		else:
			raise ValueError("Unsupported browser")
	
#	def wait_for_document_to_finish_loading(self):
#		while True:
#			if self.driver.execute_script("return document.readyState;") == "complete": break
	def wait_for_document_to_finish_loading(self):
		while self.driver.execute_script("return document.readyState;") != "complete": next
	
	def accept_gdpr(self):
		self.wait_for_document_to_finish_loading()
		if self.accepted_gdpr == False:
			self.wait_for_element_to_appear('//html/body/div[16]/div[1]/div[2]/div/div[2]/button[2]')
			self.driver.find_elements_by_xpath('//html/body/div[16]/div[1]/div[2]/div/div[2]/button[2]')[0].click()
			self.accepted_gdpr = True
	
	def scroll_to_element(self,element):
		actions = ActionChains(browser.driver)
		actions.send_keys_to_element(self.driver.find_elements_by_xpath('//html/body')[0], Keys.HOME).perform()
		self.click_invisible_bullshit()
		while not self.driver.find_elements_by_xpath(element)[0].is_displayed():
			actions.send_keys_to_element(self.driver.find_elements_by_xpath('//html/body')[0], Keys.DOWN).perform()
#		while True:
#			if self.driver.find_elements_by_xpath(element)[0].is_displayed() == True: break
#			else:
#				actions.send_keys_to_element(self.driver.find_elements_by_xpath('//html/body')[0], Keys.DOWN).perform()
	
	def click_invisible_bullshit(self):
		bullshit_xpath = '//html/body/div[14]'
		bullshit_style = 'position: fixed; display: block; width: 100%; height: 100%; inset: 0px; background-color: rgba(0, 0, 0, 0); z-index: 300000;'
		bullshit_element = self.driver.find_elements_by_xpath(bullshit_xpath)
		actions = ActionChains(browser.driver)
		while True:
			if bullshit_element != []:
				print('bullshit could exist')
				if bullshit_element[0].get_attribute('style') != bullshit_style: break
				else:
					print('clicking bullshit')
					try:
						actions.send_keys_to_element(self.driver.find_elements_by_xpath('//html/body')[0], Keys.HOME).perform()
						bullshit_element[0].click()
					except selenium.common.exceptions.StaleElementReferenceException:
						print('bullshit disappeared before clicking it')
						break
			else:
				print('bullshit not found by xpath')
				break
	
	def accept_cookies(self):
		self.wait_for_document_to_finish_loading()
		if self.accepted_cookies == False:
			self.wait_for_element_to_appear('//html/body/div[3]/p/a[1]')
			while True:
				try:
					self.driver.find_elements_by_xpath('//html/body/div[3]/p/a[1]')[0].click()
					break
				except selenium.common.exceptions.ElementClickInterceptedException:
					try:
						self.click_invisible_bullshit()
					except selenium.common.exceptions.StaleElementReferenceException:
						print('bullshit element is stale, it is ok to accept cookies')
					self.scroll_to_element('//html/body/div[14]')
					self.driver.find_elements_by_xpath('//html/body/div[14]')[0].click()
			self.accepted_cookies = True
	
	def wait_for_countdown(self):
		while self.driver.find_elements_by_xpath('//*[@id="countdown"]') != []: next
#		while True:
#			if self.driver.find_elements_by_xpath('//*[@id="countdown"]') == []: break
	
	def wait_for_element_to_appear(self, element):
		while self.driver.find_elements_by_xpath(element) == []: next
#		while True:
#			if self.driver.find_elements_by_xpath(element) != []: break
	
	def get_cookie_even_if_it_takes_time(self, cookie_name):
		cookie_obj = ""
		while True:
			cookie_obj = self.driver.get_cookie(cookie_name)
			if type(cookie_obj) is dict: break
		return cookie_obj

class mirror_list(object):
	def __init__(self,anime_id,episode_id,browser):
		print('started mirror_list class')
		episode_url = "https://shinden.pl/episode/"+anime_id+"/view/"+episode_id
		print('opening '+episode_url)
		browser.driver.get(episode_url)
		print('waiting for document to load')
		browser.wait_for_document_to_finish_loading()
		if browser.accepted_gdpr == False:
			print('accepting gpdr')
			browser.accept_gdpr()
		if browser.accepted_cookies == False:
			print('accepting cookies')
			browser.accept_cookies()
		print('clicking invisible bullshit')
		browser.click_invisible_bullshit()
		print('parsing html')
		soup = bs4.BeautifulSoup(browser.driver.page_source,"html.parser")
		episode_tags = []
		print('searching for episode-player-list section')
		for item in soup.findAll('section', {"class": re.compile("^.*$")}):
			if 'box' in item.attrs['class'] and 'episode-player-list' in item.attrs['class']:
				episode_tags.append(item)
		if len(episode_tags) != 1:
			raise ValueError("Incorrect number of sections with classes box and episode-player-list: "+len(episode_tags))
		skip_entry = True
		self.vendor = []
		self.quality = []
		self.audio_language = []
		self.sub_language = []
		self.date_added = []
		self.xpath = []
		print('entering result loop')
		for item in episode_tags[0].findAll('tr'):
			if skip_entry == True:
				skip_entry = False
			else:
				for m in item.findAll('td',{'class':'ep-pl-name'}):
					print('adding '+m.text)
					self.vendor.append(m.text)
				for q in item.findAll('td',{'class':'ep-pl-res'}):
					print('adding '+q.text)
					self.quality.append(q.text)
				for al in item.findAll('td',{'class':'ep-pl-alang'}):
					print('adding '+al.findAll('span')[1].text)
					self.audio_language.append(al.findAll('span')[1].text)
				for sl in item.findAll('td',{'class':'ep-pl-slang'}):
					subtitle_language_html = sl.findAll('span')
					if len(subtitle_language_html) < 2:
						subtitle_language = "Brak"
					else:
						subtitle_language = subtitle_language_html[1].text
					print('adding '+subtitle_language)
					self.sub_language.append(subtitle_language)
				for da in item.findAll('td',{'class':'ep-online-added'}):
					print('adding '+da.text)
					self.date_added.append(da.text)
				for xpath in item.findAll('a'):
					self.xpath.append(item.findAll('a', {'class', 'change-video-player'})[0].attrs['id'])

class sibnet_handler(object):
	def __goto_sibnet(self, browser, sibnet_primary_url):
		print('going to sibnet')
		browser.driver.get(sibnet_primary_url)
		print('waiting for document to finish loading')
		browser.wait_for_document_to_finish_loading()
	
	def __retrieve_secondary_url(self, browser):
		print('parsing sibnet page')
		soup = bs4.BeautifulSoup(browser.driver.page_source,"html.parser")
		print('scooping secondary url')
		return "https://video.sibnet.ru"+soup.findAll('video')[0].attrs['src']
	
	def __skip_bar(self, browser):
		print('waiting for loader bar to appear')
		browser.wait_for_element_to_appear('//*[@id="ampr_progress_msg"]')
		while browser.driver.find_elements_by_xpath('//*[@id="ampr_progress_msg"]') == []: next
		print('waiting for loader bar to finish')
		while int(browser.driver.find_elements_by_xpath('//*[@id="ampr_progress_percent"]')[0].get_attribute('innerHTML')) != 100: next
		print('closing loader bar')
		while True:
			try:
				browser.driver.find_elements_by_xpath('//*[@id="ampr_close"]')[0].click()
				break
			except:
				next
	
	def __click_until_it_is_ready(self, browser):
		print('clicking play button')
		actions = ActionChains(browser.driver)
		actions.send_keys_to_element(browser.driver.find_elements_by_xpath('//html/body/div[1]/div/div[6]')[0], Keys.SPACE).perform()
		self.__skip_bar(browser)
		print('clicking play button AGAIN')
		actions.send_keys_to_element(browser.driver.find_elements_by_xpath('//html/body/div[1]/div/div[6]')[0], Keys.SPACE).perform()
	
	def __request_dance(self, user_agent, sibnet_primary_url, sibnet_secondary_url):
		print('setting up request dance to retrieve direct sibnet URL')
		rq_session = requests
		rq_headers = { 'User-Agent': user_agent, 'referer': sibnet_primary_url }
		sibnet_next_url = sibnet_secondary_url
		rq_response = ""
		result = ""
		print('entering request dance')
		while True:
			rq_response = rq_session.get(sibnet_next_url, allow_redirects=False, headers=rq_headers)
			print('received response '+str(rq_response.status_code))
			if not re.match('^//',rq_response.headers['Location']) and rq_response.status_code == 302:
				result = rq_response.headers['Location']
				break
			else:
				sibnet_next_url = re.sub('^//','https://',rq_response.headers['Location'])
		return result
	
	def __init__(self, browser, sibnet_url):
		self.__goto_sibnet(browser, sibnet_url)
		sibnet_secondary_url = self.__retrieve_secondary_url(browser)
		self.__click_until_it_is_ready(browser)
		self.url = self.__request_dance(browser.user_agent, sibnet_url, sibnet_secondary_url)

class streamtape_handler(object):
	def __goto_streamtape(self, browser, streamtape_url):
		browser.driver.get(streamtape_url)
		browser.wait_for_document_to_finish_loading()
	
	def __click_play(self, browser):
		print('simulate clicking play')
		actions = ActionChains(browser.driver)
		actions.send_keys_to_element(browser.driver.find_elements_by_xpath('//html/body/div[2]/div[1]')[0], Keys.ENTER).perform()
		browser.driver.find_elements_by_xpath('//html/body/div[2]/div[2]/button')[0].click()
	
	def __get_cookies(self, browser):
		cookie_b = browser.get_cookie_even_if_it_takes_time('_b')
		cookie_cloudflare = browser.get_cookie_even_if_it_takes_time('__cfduid')
		cookie_ym_d = browser.get_cookie_even_if_it_takes_time('_ym_d')
		cookie_ym_isad = browser.get_cookie_even_if_it_takes_time('_ym_isad')
		cookie_ym_uid = browser.get_cookie_even_if_it_takes_time('_ym_uid')
		return { cookie_b['name']: cookie_b['value'], cookie_cloudflare['name']: cookie_cloudflare['value'], cookie_ym_d['name']: cookie_ym_d['value'], cookie_ym_isad['name']: cookie_ym_isad['value'], cookie_ym_uid['name']: cookie_ym_uid['value'] }
	
	def __get_request_url(self, browser):
		html_hint = browser.driver.find_elements_by_xpath('//html/body/script[6]')[0].get_attribute('innerHTML')
		without_tabs = re.sub('\\t','',html_hint)
		without_newlines = re.sub('\\n','',without_tabs)
		without_code = re.sub(';.*$','',without_newlines)
		without_code_declarations = re.sub('^.* = ','',without_code)
		json_data = json.loads(without_code_declarations)
#		alternate method: media_id = streamtape_url.split('/')[-2]
		media_id = json_data['id']
		request_parameters = json_data['cors'].split('/')[-1]
		return 'https://streamtape.com/get_video?id='+media_id+'&'+request_parameters
	
	def __get_url(self, url_to_obtain_direct_link, cookie_dict, rq_headers):
		rq_session = requests
		print('requesting URL '+url_to_obtain_direct_link)
		rq_response = rq_session.get(url_to_obtain_direct_link, allow_redirects=False, cookies=cookie_dict, headers=rq_headers)
		return rq_response.headers['Location']
	
	def __init__(self, browser, streamtape_url):
		self.__goto_streamtape(browser, streamtape_url)
		self.__click_play(browser)
		cookies_dict = self.__get_cookies(browser)
		url_to_obtain_direct_link = self.__get_request_url(browser)
		rq_headers = { 'User-Agent': browser.user_agent, 'referer': streamtape_url }
		self.url = self.__get_url(url_to_obtain_direct_link, cookies_dict, rq_headers)

class dood_handler(object):
	def __goto_streamtape(self, browser, dood_url):
		browser.driver.get(dood_url)
		browser.wait_for_document_to_finish_loading()
	
	def __get_url(self, browser):
		soup = bs4.BeautifulSoup(browser.driver.page_source,"html.parser")
		return soup.findAll('video')[0].attrs['src']
	
	def __init__(self, browser, dood_url):
		self.__goto_streamtape(self, browser, dood_url)
		self.url = self.__get_url(browser)

class gd_apicode_cc_handler(object):
	def __goto_gd_apicode_cc(self, browser):
		browser.driver.get('https://gd.apicode.cc')
		browser.wait_for_document_to_finish_loading()
	
	def __get_url_from_form(self, browser, player_url, mirror_vendor):
		drop = Select(browser.driver.find_elements_by_xpath('//html/body/div[1]/div[1]/div/form/div[1]/div/select')[0])
		drop.select_by_value(mirror_vendor.lower())
		browser.driver.find_elements_by_xpath('//*[@id="id"]')[0].send_keys(player_url)
		browser.wait_for_document_to_finish_loading()
		browser.driver.find_elements_by_xpath('//*[@id="submit"]')[0].click()
		browser.wait_for_document_to_finish_loading()
		browser.driver.find_elements_by_xpath('//*[@id="dl-tab"]')[0].click()
		browser.wait_for_document_to_finish_loading()
		return browser.driver.find_elements_by_xpath('//*[@id="txtDl"]')[0].get_attribute('innerHTML')
	
	def __get_url_from_menu(self, browser, intermediate_url):
		browser.driver.get(intermediate_url)
		browser.wait_for_document_to_finish_loading()
		return browser.driver.find_elements_by_xpath('//html/body/div[1]/div[3]/div/a[3]')[0].get_attribute('href')
	
	def __init__(self, browser, player_url, mirror_vendor):
		self.__goto_gd_apicode_cc(browser)
		intermediate_url = self.__get_url_from_form(browser, player_url, mirror_vendor)
		self.url = self.__get_url_from_menu(browser, intermediate_url)

class streamsb_handler(object):
	def __init__(self, browser, player_url, mirror_vendor):
		self.url = gd_apicode_cc_handler(browser, player_url, mirror_vendor).url

class cda_handler(object):
	def __goto_cda(self, browser, player_url):
		browser.driver.get(player_url)
		browser.wait_for_document_to_finish_loading()
	
	def __init__(self, browser, player_url):
		self.__goto_cda(browser, player_url)
		self.url = browser.driver.find_elements_by_xpath('//html/body/div/div[1]/div/div/div/div/div/div/span[3]/span[1]/span/span[1]/video')[0].get_attribute('src')

class mp4upload_handler(object):
	def __goto_mp4upload(self, browser, player_url):
		browser.driver.get(player_url)
		browser.wait_for_document_to_finish_loading()
	
	def __init__(self, browser, player_url):
		self.__goto_mp4upload(browser, player_url)
		self.url = browser.driver.find_elements_by_xpath('//*[@id="player_html5_api"]')[0].get_attribute('src')

class MirrorVendorUnsupported(Exception):
	"""Raised when mirror vendor is unsupported. Let us know by filing an issue."""
	pass

class shinden_direct_url(object):
	def __get_player_html(self, browser, mirrors, selected_mirror):
		actions = ActionChains(browser.driver)
		print('trying to snoop for '+mirrors.vendor[selected_mirror]+' player on shinden')
		browser.scroll_to_element('//*[@id="'+mirrors.xpath[selected_mirror]+'"]')
		browser.click_invisible_bullshit()
		while True:
			try:
				browser.driver.find_elements_by_xpath('//*[@id="'+mirrors.xpath[selected_mirror]+'"]')[0].click()
				break
			except selenium.common.exceptions.ElementClickInterceptedException:
				actions.send_keys_to_element(browser.driver.find_elements_by_xpath('//html/body')[0], Keys.DOWN).perform()
		print('waiting for countdown')
		browser.wait_for_countdown()
		print('parsing player element')
		page_source = browser.driver.find_elements_by_xpath('//html/body/div[4]/div/article/div[2]')[0].get_attribute('innerHTML')
		soup = bs4.BeautifulSoup(page_source,"html.parser")
		return soup
	
	def __get_player_url(self, browser, mirrors, selected_mirror):
		result = ""
		player_url = ""
		print('retrieving player URL')
		while player_url == "":
			soup = self.__get_player_html(browser,mirrors, selected_mirror)
			try:
				base_referant = soup.findAll('iframe')[0].attrs['src']
				if mirrors.vendor[selected_mirror] == 'Sibnet':
					player_url = 'https://video.sibnet.ru/shell.php?videoid='+re.sub("^.*=","",base_referant)
				elif mirrors.vendor[selected_mirror] == 'Mega':
					player_url = "https://mega.co.nz/#!"+base_referant.split('#!')[1]
				elif mirrors.vendor[selected_mirror] == 'Cda' or mirrors.vendor[selected_mirror] == 'Mp4upload':
					player_url = re.sub('^//','https://',base_referant)
				else:
					player_url = base_referant
				break
			except IndexError:
				print('error occurred on shinden, retryting')
#				possible location: /html/body/div[4]/div/article/div[2]/div/div[2]/div
				browser.driver.refresh()
				browser.wait_for_document_to_finish_loading()
		return player_url
	
	def __get_url(self, browser, mirrors, selected_mirror):
		if not mirrors.vendor[selected_mirror] in self.__compatible_mirror_types:
			print('Unsupported mirror of type '+mirrors.vendor[selected_mirror])
			raise MirrorVendorUnsupported
		player_url = self.__get_player_url(browser, mirrors, selected_mirror)
		shinden_url = browser.driver.current_url
		result = ""
		if mirrors.vendor[selected_mirror] == 'Sibnet':
			self.compatible_with_watchtogether = True
			self.download_possible = True
			self.requires_referer = False
			self.requires_redirect = False
			self.requires_browser_identity = False
			self.requires_raw_data = False
			result = sibnet_handler(browser, player_url).url
			self.referer = ""
			self.user_agent = ""
			self.raw_data = ""
		elif mirrors.vendor[selected_mirror] == 'Mega':
			self.compatible_with_watchtogether = False
			self.download_possible = True
			self.requires_referer = False
			self.requires_redirect = False
			self.requires_browser_identity = False
			self.requires_raw_data = False
			result = player_url
			self.referer = ""
			self.user_agent = ""
			self.raw_data = ""
		elif mirrors.vendor[selected_mirror] == 'Streamtape':
			self.compatible_with_watchtogether = True
			self.download_possible = True
			self.requires_referer = False
			self.requires_redirect = False
			self.requires_browser_identity = False
			result = streamtape_handler(browser, player_url).url
			self.referer = ""
			self.user_agent = ""
			self.raw_data = ""
		elif mirrors.vendor[selected_mirror] == 'Dood':
			self.compatible_with_watchtogether = False
			self.download_possible = True
			self.requires_referer = True
			self.requires_redirect = False
			self.requires_browser_identity = False
			self.requires_raw_data = False
			result = dood_handler(browser, player_url).url
			self.referer = player_url
			self.user_agent = ""
			self.raw_data = ""
		elif mirrors.vendor[selected_mirror] == 'Streamsb':
			self.compatible_with_watchtogether = False
			self.download_possible = True
			self.requires_referer = False
			self.requires_redirect = False
			self.requires_browser_identity = False
			self.requires_raw_data = False
			result = streamsb_handler(browser, player_url, mirrors.vendor[selected_mirror]).url
			self.referer = ""
			self.user_agent = ""
			self.raw_data = ""
		elif mirrors.vendor[selected_mirror] == 'Cda':
			self.compatible_with_watchtogether = True
			self.download_possible = True
			self.requires_referer = False
			self.requires_redirect = False
			self.requires_browser_identity = True
			self.requires_raw_data = False
			result = cda_handler(browser, player_url).url
			self.referer = ""
			self.user_agent = browser.user_agent
			self.raw_data = ""
		elif mirrors.vendor[selected_mirror] == 'Mp4upload':
			self.compatible_with_watchtogether = False
			self.download_possible = True
			self.requires_referer = True
			self.requires_redirect = True
			self.requires_browser_identity = True
			self.requires_tls_compromise = True
			self.requires_raw_data = True
			result = mp4upload_handler(browser, player_url).url
			self.referer = ""
			self.user_agent = ""
			self.raw_data = 'op=download2&id=ww8lzr8l1erp&rand=&referer=https%3A%2F%2Fwww.mp4upload.com%2Fembed-ww8lzr8l1erp.html&method_free=+&method_premium='
		browser.driver.get(shinden_url)
		browser.wait_for_document_to_finish_loading()
		return result
	
	def __init__(self, browser, mirrors, mirror_number):
		self.compatible_with_watchtogether = False
		self.download_possible = False
		self.requires_referer = False
		self.requires_browser_identity = False
		self.__compatible_mirror_types = ['Sibnet', 'Mega', 'Streamtape', 'Dood', 'Streamsb', 'Cda', 'Mp4upload']
		self.url = self.__get_url(browser, mirrors, mirror_number)
		print('Received URL: '+self.url)

class search_result(object):
	def __init__(self, title, type_of_broadcast, episode_count, id_of_anime):
		self.title = title
		self.type_of_broadcast = type_of_broadcast
		self.episode_count = episode_count
		self.id_of_anime = id_of_anime

class shinden_ratings(object):
	def __init__(self, html_soup):
		dlugi_tekst = re.sub("\n", "", html_soup.findAll('li', attrs={'class', 'ratings-col'})[0].text)
		if dlugi_tekst != '':
			worek = re.sub(":", "", re.sub(",", ".", dlugi_tekst)).split(" ")
			self.overall = worek[1]
			self.storyline = worek[3]
			self.graphics = worek[5]
			self.music = worek[7]
			self.characters = worek[9]
		else:
# Tutaj trafiają animce które nie mają jeszcze ocen bo np. zostały zapowiedziane ale jeszcze ich nie ma na shindenie
			self.overall = 'Brak'
			self.storyline = 'Brak'
			self.graphics = 'Brak'
			self.music = 'Brak'
			self.characters = 'Brak'
			self.top = 'Brak'
		self.top = re.sub(",", ".", html_soup.findAll('li', attrs={'class', 'rate-top'})[0].text)
	
	def list_all(self):
		print('Ogółem: '+self.overall)
		print('Fabuła: '+self.storyline)
		print('Grafika: '+self.graphics)
		print('Muzyka: '+self.music)
		print('Postacie: '+self.characters)
		print('TOP: '+self.top)

class search_result_class(object):
	def __init__(self, html_soup):
		self.id = re.sub("^.*/", "", re.sub("-.*$", "", str(html_soup.findAll('h3')[0])))
		self.title = re.sub("^ *", "", html_soup.findAll('h3')[0].text)
		self.broadcast = html_soup.findAll('li', attrs={'class', 'title-kind-col'})[0].text
		self.episode_count = int(re.sub(" *$", "", html_soup.findAll('li', attrs={'class', 'episodes-col'})[0].text))
		self.ratings = shinden_ratings(html_soup)
		self.tags = re.sub("\n$", "", re.sub("^\n", "", html_soup.findAll('ul', attrs={'class', 'tags'})[0].text)).split("\n")
		print(self.id)
		print(self.title)
		print(self.broadcast)
		print(str(self.episode_count))
		self.ratings.list_all()
		print(self.tags)

class sibnet_search(object):
	def __make_string_url_friendly(self, input_text):
		return re.sub(" ", "+", input_text)
	
	def __init__(self, search_term):
		url = 'https://shinden.pl/series?search='+self.__make_string_url_friendly(search_term)
		session = requests
		response = session.get(url)
		soup = bs4.BeautifulSoup(response.text, "html.parser")
		crazy_table = soup.findAll('section', attrs={'class', 'title-table'})[0].findAll('article')[0]
		anime_html_list = crazy_table.findAll('ul', attrs={'class', 'div-row'})
		self.count = len(anime_html_list)
		self.result = []
		count = 0
		while count < self.count:
			print("count: "+str(count))
			self.result.append(search_result_class(anime_html_list[count]))
			count = count + 1
	
	def list_search_results(self):
		count = 0
		if self.count == 0:
			return
		print("Lp.\tTytuł\tOdcinki\tEmisja\tOceny\tTOP")
		while count < self.count:
			print(str(count+1)+": "+self.result[count].title+"\t"+str(self.result[count].episode_count)+"\t"+self.result[count].broadcast+"\t"+self.result[count].ratings.top)
			count = count + 1


debug_mode = False
graphic_interface = False

print('Starting browser engine')
browser = browser_engine()
print('Browser engine successfully initialized')

while True:
# W tej pętli wybieramy anime z wyników na shindenie
	print('What would you like to watch? If nothing, just enter nothing')
	search_term = input("Enter search term: ")
	if search_term == "":
		break
	search_results = sibnet_search(search_term)
	search_results.list_search_results()
# Wybieramy anime z wyników wyszukiwania
	anime_id = ""
	while True:
		print("If you select 0, the program will exit safely")
		selected_anime = int(input("Select anime from above list by Lp. number (1-"+str(search_results.count)+"): "))
		if selected_anime < 1 or selected_anime > search_results.count:
			if selected_anime == 0:
				browser.quit()
				quit()
		else:
			anime_id = search_results.result[selected_anime-1].id
			break
	episodes = episode_list(anime_id)
	while True:
# W tej pętli wybieramy odcinek
		if graphic_interface == False:
			while True:
				max_episode = len(episodes.id)
				print('Just so you know, you can quit by selecting 0 in the episode choice')
				episode_number = int(input("Enter episode number (1-"+str(max_episode)+"): "))
				if episode_number > max_episode or episode_number < 1:
					if episode_number == 0:
						browser.quit()
						quit()
					print('Episode number outside of given range')
				else:
					episode_number = episode_number - 1
					break

		mirrors = mirror_list(anime_id,episodes.id[episode_number],browser)
# Przejebane że nie wiem jak sie zabrać za rozdzielenie tego na gui i cli xD
		if graphic_interface == False:
# W tej pętli wybieramy mirror odcinka
			while True:
				max_mirror = len(mirrors.vendor)
				mirror_number = int(input("Enter mirror number (1-"+str(max_mirror)+"): "))
				if mirror_number > max_mirror or mirror_number < 1:
					print('Mirror number outside of given range')
				else:
					mirror_number = mirror_number - 1
					break

		try:
			file_url = shinden_direct_url(browser,mirrors,mirror_number)
		except MirrorVendorUnsupported:
			print('Unsupported mirror vendor: '+mirrors.vendor[mirror_number])

browser.quit()
