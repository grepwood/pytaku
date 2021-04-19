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
import time
import os
import detect_browsers
import pdb
import sys
from prettytable import PrettyTable
#import youtube_dl

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
		self.id = []
		count = 0
		self.as_a_table = PrettyTable()
		self.as_a_table.field_names = ['Numer', 'Tytuł']
		while count < self.episode_count:
			episode_id = re.sub('^.*/view/','',big_tag_matrix[(self.episode_count - count - 1)*6+5].findChild('a')['href'])
			title = big_tag_matrix[(self.episode_count - count - 1)*6+1].get_text(strip=True)
			self.title.append(title)
			self.id.append(episode_id)
			count = count + 1
			self.as_a_table.add_row([str(count), title])
	
	def list_all(self):
		print(self.as_a_table)

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
#			if debug_mode == False:
#				self.options.headless = True
			self.options.headless = True
			self.profile.update_preferences()
			self.driver = webdriver.Firefox(self.profile,options=self.options)
			self.user_agent = self.driver.execute_script("return navigator.userAgent;")
		elif self.preferred_browser == 'google-chrome-stable':
			self.profile = webdriver.ChromeProfile()
			self.options = webdriver.ChromeOptions()
			self.options.addArguments("-lang=pl")
#			if debug_mode == False:
#				self.options.headless = True
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
	
	def wait_for_document_to_finish_loading(self):
		print('Waiting for document to load')
		while self.driver.execute_script("return document.readyState;") != "complete": next
		print('Document finished loading')
	
	def accept_gdpr(self):
		if self.accepted_gdpr == False:
			print('Accepting GDPR')
			self.wait_for_document_to_finish_loading()
			self.wait_for_element_to_appear('//html/body/div[16]/div[1]/div[2]/div/div[2]/button[2]')
			self.driver.find_elements_by_xpath('//html/body/div[16]/div[1]/div[2]/div/div[2]/button[2]')[0].click()
			print('GDPR accepted')
			self.accepted_gdpr = True
	
	def scroll_to_element(self,element):
		actions = ActionChains(browser.driver)
		actions.send_keys_to_element(self.driver.find_elements_by_xpath('//html/body')[0], Keys.HOME).perform()
		self.click_invisible_bullshit()
		while not self.driver.find_elements_by_xpath(element)[0].is_displayed():
			actions.send_keys_to_element(self.driver.find_elements_by_xpath('//html/body')[0], Keys.DOWN).perform()
	
	def click_invisible_bullshit(self):
		bullshit_xpath = '//html/body/div[14]'
		bullshit_style = 'position: fixed; display: block; width: 100%; height: 100%; inset: 0px; background-color: rgba(0, 0, 0, 0); z-index: 300000;'
		bullshit_element = self.driver.find_elements_by_xpath(bullshit_xpath)
		actions = ActionChains(browser.driver)
		print('clicking invisible bullshit')
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
		if self.accepted_cookies == False:
			print('Accepting cookies')
			self.wait_for_document_to_finish_loading()
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
					try:
						self.scroll_to_element('//html/body/div[14]')
						self.driver.find_elements_by_xpath('//html/body/div[14]')[0].click()
					except selenium.common.exceptions.ElementNotInteractableException:
						pdb.set_trace()
			print('Cookies accepted')
			self.accepted_cookies = True
	
	def wait_for_countdown(self):
		while self.driver.find_elements_by_xpath('//*[@id="countdown"]') != []: next
	
	def wait_for_element_to_appear(self, element):
		while self.driver.find_elements_by_xpath(element) == []: next
	
	def get_cookie_even_if_it_takes_time(self, cookie_name):
		cookie_obj = ""
		while True:
			cookie_obj = self.driver.get_cookie(cookie_name)
			if type(cookie_obj) is dict: break
		return cookie_obj
	
	def find_tags_with_multiple_classes(self, type_of_tag, classes):
		results = []
		html_soup = bs4.BeautifulSoup(self.driver.page_source,"html.parser")
		for item in html_soup.findAll(type_of_tag, {'class': re.compile("^.*$")}):
			classes_found = 0
			for each_class in classes:
				classes_found += int(each_class in item.attrs['class'])
			if classes_found == len(classes):
				results.append(item)
		return results

class mirror_object(object):
	def __init__(self, html_soup):
		self.vendor = re.sub("^  \n", "", html_soup.find('td', {'class': 'ep-pl-name'}).text)
		self.quality = html_soup.find('td',{'class':'ep-pl-res'}).text
		self.audio_language = html_soup.find('td', {'class': 'ep-pl-alang'}).find('span', {'class': 'mobile-hidden'}).text
		sub_language = html_soup.find('td', {'class': 'ep-pl-slang'}).findAll('span')
		self.sub_language = "Brak" if(len(sub_language) < 2) else sub_language[1].text
		self.date_added = html_soup.find('td', {'class': 'ep-online-added'}).text
		self.xpath = html_soup.find('td', {'class': 'ep-buttons'}).find('a', {'class': 'change-video-player'}).attrs['id']

class mirror_list(object):
	def __init__(self,anime_id,episode_id,browser):
		print('started mirror_list class')
		episode_url = "https://shinden.pl/episode/"+anime_id+"/view/"+episode_id
		print('opening '+episode_url)
		browser.driver.get(episode_url)
		browser.accept_gdpr()
		browser.accept_cookies()
		browser.click_invisible_bullshit()
		print('searching for episode-player-list section')
		episode_tags = browser.find_tags_with_multiple_classes('table', ['data-view-table-strips', 'data-view-table-big', 'data-view-hover'])[0].find('tbody')
		print('entering result loop')
		self.mirror = []
		count = 0
		self.as_a_table = PrettyTable()
		self.as_a_table.field_names = ['Numer', 'Źródło', 'Jakość', 'Język', 'Napisy', 'Data dodania', 'Wspierany']
		for item in episode_tags.findAll('tr'):
			self.mirror.append(mirror_object(item))
			self.as_a_table.add_row([str(count+1), self.mirror[count].vendor, self.mirror[count].quality, self.mirror[count].audio_language, self.mirror[count].sub_language, self.mirror[count].date_added, judge_mirror(self.mirror[count].vendor)])
			count += 1
	
	def list_all(self):
		print(self.as_a_table)

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
		time.sleep(5)
		if len(browser.driver.find_elements_by_xpath('//*[@id="ampr_progress_msg"]')) > 0:
			browser.wait_for_element_to_appear('//*[@id="ampr_progress_msg"]')
			print('waiting for loader bar to finish')
			while int(browser.driver.find_elements_by_xpath('//*[@id="ampr_progress_percent"]')[0].get_attribute('innerHTML')) != 100: next
			print('closing loader bar')
			while True:
				try:
					browser.driver.find_elements_by_xpath('//*[@id="ampr_close"]')[0].click()
					break
				except:
					next
		else:
			print('it appears that loader bar did not appear at all')
	
	def __click_until_it_is_ready(self, browser):
		print('clicking play button')
		actions = ActionChains(browser.driver)
		actions.send_keys_to_element(browser.driver.find_elements_by_xpath('//html/body/div[1]/div/div[6]')[0], Keys.SPACE).perform()
		self.__skip_bar(browser)
		print('clicking play button AGAIN')
		while True:
			try:
				actions.send_keys_to_element(browser.driver.find_elements_by_xpath('//html/body/div[1]/div/div[6]')[0], Keys.SPACE).perform()
				break
			except selenium.common.exceptions.WebDriverException:
				next
	
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
		self.url = []
		for url in sibnet_url:
			self.__goto_sibnet(browser, url)
			sibnet_secondary_url = self.__retrieve_secondary_url(browser)
			self.__click_until_it_is_ready(browser)
			self.url.append(self.__request_dance(browser.user_agent, url, sibnet_secondary_url))

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
		self.url = []
		for url in streamtape_url:
			self.__goto_streamtape(browser, url)
			self.__click_play(browser)
			cookies_dict = self.__get_cookies(browser)
			url_to_obtain_direct_link = self.__get_request_url(browser)
			rq_headers = { 'User-Agent': browser.user_agent, 'referer': url }
			self.url.append(self.__get_url(url_to_obtain_direct_link, cookies_dict, rq_headers))

class dood_handler(object):
	def __goto_streamtape(self, browser, dood_url):
		browser.driver.get(dood_url)
		browser.wait_for_document_to_finish_loading()
	
	def __get_url(self, browser):
		soup = bs4.BeautifulSoup(browser.driver.page_source,"html.parser")
		return soup.findAll('video')[0].attrs['src']
	
	def __init__(self, browser, dood_url):
		self.url = []
		for url in player_url:
			self.__goto_streamtape(browser, dood_url)
			self.url.append(self.__get_url(browser))

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
	
	def __get_url_from_menu(self, browser, intermediate_url, mirror_vendor):
		browser.driver.get(intermediate_url)
		browser.wait_for_document_to_finish_loading()
		result = ""
		if mirror_vendor in ['Vidlox', 'Vidoza']:
			result = browser.driver.find_elements_by_xpath('//html/body/div[1]/div[3]/div/a[2]')[0].get_attribute('href')
		elif mirror_vendor == 'Streamsb':
			result = browser.driver.find_elements_by_xpath('//html/body/div[1]/div[3]/div/a[3]')[0].get_attribute('href')
		else:
			raise MirrorVendorUnsupported
		return result
	
	def __init__(self, browser, player_url, mirror_vendor):
		self.__goto_gd_apicode_cc(browser)
		intermediate_url = self.__get_url_from_form(browser, player_url, mirror_vendor)
		self.url = self.__get_url_from_menu(browser, intermediate_url, mirror_vendor)

class streamsb_handler(object):
	def __init__(self, browser, player_url, mirror_vendor):
		self.url = []
		for url in player_url:
			self.url.append(gd_apicode_cc_handler(browser, url, mirror_vendor).url)

class cda_handler(object):
	def __goto_cda(self, browser, player_url):
		browser.driver.get(player_url)
		browser.wait_for_document_to_finish_loading()
	
	def __init__(self, browser, player_url):
		self.url = []
		for url in player_url:
			self.__goto_cda(browser, url)
			self.url.append(browser.driver.find_elements_by_xpath('//html/body/div/div[1]/div/div/div/div/div/div/span[3]/span[1]/span/span[1]/video')[0].get_attribute('src'))

class mp4upload_handler(object):
	def __is_mirror_dead(self, player_url):
		response = self.__session.get(player_url)
		return response.status_code == 404
	
	def __goto_mp4upload(self, browser, player_url):
		browser.driver.get(player_url)
		browser.wait_for_document_to_finish_loading()
	
	def __init__(self, browser, player_url):
		self.url = []
		self.__session = requests
		for url in player_url:
			if self.__is_mirror_dead(url) == True:
				raise DeadMirror
			self.__goto_mp4upload(browser, url)
			self.url.append(browser.driver.find_elements_by_xpath('//*[@id="player_html5_api"]')[0].get_attribute('src'))

class MirrorVendorUnsupported(Exception):
	"""Raised when mirror vendor is unsupported. Let us know by filing an issue."""
	pass

class DeadMirror(Exception):
	"""Raised when mirror is listed, but turns out to be dead."""
	pass

class cloud9_handler(object):
	def __is_mirror_dead(self):
		response = self.__session.get(player_url)
		return response.status_code == 404
	
	def __init__(self, browser, player_url):
		self.url = []
		self.__session = requests
		for url in player_url:
			if self.__is_mirror_dead(url) == True:
				raise DeadMirror
			browser.driver.get(player_url)
			browser.wait_for_document_to_finish_loading()
			self.url.append("")

class vidlox_handler(object):
	def __init__(self, browser, player_url):
		self.url = []
		for url in player_url:
			self.url.append(gd_apicode_cc_handler(browser, url, 'Vidlox').url)

class vidoza_handler(object):
	def __init__(self, browser, player_url, mirror_vendor):
		self.url = []
		for url in player_url:
			self.url.append(gd_apicode_cc_handler(browser, url, mirror_vendor).url)

class facebook_handler(object):
	def __init__(self, browser, player_url):
		self.url = []
		for url in player_url:
			browser.driver.get(url)
			browser.wait_for_document_to_finish_loading()
			page_source = browser.driver.page_source
			soup = bs4.BeautifulSoup(page_source, "html.parser")
			self.url.append(soup.findAll('video')[0].attrs['src'])

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

class aparat_handler(object):
	def __is_mirror_dead(self, player_url):
		death_indicator = '<html><body style="width:100%;height:100%;padding:0;margin:0;">\r\n<center>\r\n<div style="position: absolute;top:50%;width:100%;text-align:center;font: 15px Verdana;">File is no longer available as it expired or has been deleted.</div>\r\n</center>\r\n\r\n<img src="/images/player_blank.jpg" style="position:absolute;width:100%;height:100%" id="over" onclick="document.getElementById(\'over\').style.display = \'none\';">\r\n\r\n</body></html>'
		self.__response = self.__session.get(player_url)
		return self.__response.text == death_indicator
	
	def __extract_primary_url(self):
		soup = bs4.BeautifulSoup(self.__response.text, "html.parser")
		javascript_mess = soup.findAll('script')[-4]
		without_newlines = re.sub("\n", "", str(javascript_mess))
		without_location_definition = re.sub("^.*window.top.location.href = \'", "", without_newlines)
		without_garbage = re.sub("\'.*$", "", without_location_definition)
		return without_garbage
		
	def __generate_secondary_url(self, primary_url):
		self.__response = self.__session.get(primary_url)
		soup = bs4.BeautifulSoup(self.__response.text, "html.parser")
		parameter_soup = soup.findAll('a')[-5].attrs['onclick']
		without_beginning_parentheses = re.sub("^.*\('", "", parameter_soup)
		without_ending_parentheses = re.sub("'\)", "", without_beginning_parentheses)
		parameters = re.sub("'", "", without_ending_parentheses).split(',')
		return 'https://wolfstream.tv/dl?op=download_orig&id='+parameters[0]+'&mode='+parameters[1]+'&hash='+parameters[2]
	
	def __generate_direct_link(self, secondary_url):
		self.__response = self.__session.get(secondary_url)
		soup = bs4.BeautifulSoup(self.__response.text, "html.parser")
		return soup.findAll('a')[-3].attrs['href']
	
	def __init__(self, player_url):
		self.url = []
		self.__session = requests
		for url in player_url:
			if self.__is_mirror_dead(url) == True:
				raise DeadMirror
			primary_url = self.__extract_primary_url()
			secondary_url = self.__generate_secondary_url(primary_url)
			final_url = self.__generate_direct_link(secondary_url)
			self.url.append(final_url)

class dailymotion_handler(object):
	def __init__(self, player_url):
		self.url = []
		print('Dailymotion is only available for download through youtube-dl')
		for url in player_url:
			self.url.append(url)

class youtube_handler(object):
	def __init__(self, player_url):
		self.url = []
		print('Youtube is only available for download through youtube-dl')
		for url in player_url:
			self.url.append(url)

class yourupload_handler(object):
	def __init__(self, player_url):
		self.url = []
		self.referer = []
		self.__session = requests
		for url in player_url:
			self.referer.append(url)
			self.__response = self.__session.get(url)
			self.__soup = bs4.BeautifulSoup(self.__response.text, "html.parser")
			self.url.append(self.__soup.find('meta', {'property': 'og:video'}).attrs['content'])

class myviru_handler(object):
	def __init__(self, player_url):
		self.url = []
		self.cookie = []
		session = requests
		for url in player_url:
			response = session.get(url)
			soup = bs4.BeautifulSoup(response.text, "html.parser")
			mess = str(soup.findAll('script')[-2]).split(", ")[0]
			mess = re.sub("\n", "", mess)
			mess = re.sub("\r", "", mess)
			mess = re.sub("^.*v=", "", mess)
			mess = re.sub("\\\\u0026.*$", "", mess)
			mess = re.sub("%3a", ":", mess)
			mess = re.sub("%2f", "/", mess)
			mess = re.sub("%26", "&", mess)
			mess = re.sub("%3d", "=", mess)
			mess = re.sub("%3f", "?", mess)
			cookie_dict = {'UniversalUserID': response.cookies.get_dict()['UniversalUserID']}
			response = session.get(mess, allow_redirects=False, cookies=cookie_dict)
			self.url.append(response.headers['Location'])
			self.cookie.append(cookie_dict)

class tunepk_handles(object):
	def __is_mirror_dead(self, browser, player_url):
		browser.driver.get(player_url)
		browser.wait_for_document_to_finish_loading()
		possible_death_soup = browser.find_tags_with_multiple_classes('p', ['subheading', 'mb-5'])
		if len(possible_death_soup) != 0:
			if possible_death_soup[0].text == 'Unable to find video':
				raise DeadMirror
	
	def __init__(self, browser, player_url):
		self.url = []
		for url in player_url:
			if self.__is_mirror_dead(browser, url):
				raise DeadMirror
			self.url.append(url)

class shinden_direct_url(object):
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
		soup = bs4.BeautifulSoup(page_source,"html.parser")
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
			result = sibnet_handler(browser, player_url).url
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
			result = facebook_handler(browser, player_url).url
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
	
	def __init__(self, browser, mirror):
		self.compatible_with_watchtogether = False
		self.download_possible = False
		self.requires_referer = False
		self.requires_browser_identity = False
		global supported_mirrors
		self.__compatible_mirror_types = supported_mirrors
#		self.__compatible_mirror_types = ['Sibnet', 'Mega', 'Streamtape', 'Dood', 'Streamsb', 'Cda', 'Mp4upload', 'Vidloxtv', 'Vidoza', 'Fb', 'Vk', 'Aparat', 'Myviru']
		try:
			self.url = self.__get_url(browser, mirror)
		except DeadMirror:
			self.url = ['DEAD URL']
		count = 0
		for url in self.url:
			print('Received URL #'+str(count+1)+': '+self.url[count])
			count += 1

supported_mirrors = ['Sibnet', 'Mega', 'Streamtape', 'Dood', 'Streamsb', 'Cda', 'Mp4upload', 'Vidloxtv', 'Vidoza', 'Fb', 'Vk', 'Aparat', 'Dailymotion', 'Yourupload', 'Myviru']

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

class ShindenDowntime(Exception):
	"""
	Thrown when Shinden is down
	"""
	pass

class ShindenUnknownException(Exception):
	"""
	Pass when Shinden behaves in ways we cannot expect
	"""
	pass

def detect_shinden_downtime_from_soup(soup):
	error_msg = soup.find('p', {'class': 'enormous-font bree-font'}).text
	if error_msg == ' 500 ':
		raise ShindenDowntime
	else:
		raise UnknownException

class shinden_search(object):
	def __make_string_url_friendly(self, input_text):
		return re.sub(" ", "+", input_text)
	
	def __init__(self, search_term):
		url = 'https://shinden.pl/series?search='+self.__make_string_url_friendly(search_term)
		session = requests
		response = session.get(url)
		soup = bs4.BeautifulSoup(response.text, "html.parser")
		try:
			crazy_table = soup.findAll('section', attrs={'class', 'title-table'})[0].findAll('article')[0]
		except IndexError:
			try:
				detect_shinden_downtime_from_soup(soup)
			except ShindenDowntime:
				print('Shinden is down. Nothing we can do about it. Try again later.')
				quit_safely()
		anime_html_list = crazy_table.findAll('ul', attrs={'class', 'div-row'})
		self.count = len(anime_html_list)
		self.result = []
		count = 0
		self.as_a_table = PrettyTable()
		self.as_a_table.field_names = ['Numer', 'Tytuł', 'Odcinki', 'Emisja', 'Ogółem', 'Fabuła', 'Grafika', 'Muzyka', 'Postacie', 'TOP', 'Tagi']
		while count < self.count:
			self.result.append(search_result_class(anime_html_list[count]))
			self.as_a_table.add_row([str(count+1), self.result[count].title, self.result[count].episode_count, self.result[count].broadcast, self.result[count].ratings.overall, self.result[count].ratings.storyline, self.result[count].ratings.graphics, self.result[count].ratings.music, self.result[count].ratings.characters, self.result[count].ratings.top, self.result[count].tags ])
			count += 1
	
	def list_search_results(self):
		print(self.as_a_table)

def search_for_anime():
	global debug_mode
	if debug_mode == True:
		search_results = shinden_search('jojo')
		search_results.list_search_results()
		return search_results
	print('What would you like to watch? If nothing, just enter nothing')
	search_term = input("Enter search term: ")
	if search_term == "":
		quit_safely()
	search_results = shinden_search(search_term)
	search_results.list_search_results()
	return search_results

def quit_safely():
	global browser
	browser.quit()
	quit()

def retrieve_anime_id_from_selection(search_results):
	global debug_mode
	if debug_mode == True:
		return search_results.result[0].id
	while True:
		print('Select 0 to quit safely')
		selected_anime = int(input("Select anime from above list (1-"+str(search_results.count)+"): "))
		if selected_anime < 1 or selected_anime > search_results.count:
			if selected_anime == 0:
				quit_safely()
		else:
			selected_anime -= 1
			if search_results.result[selected_anime].episode_count != 0:
				return search_results.result[selected_anime].id
			else:
				print('This anime has no episodes. Choose something else.')

def select_episode(episodes):
	global debug_mode
	if debug_mode == True:
		return 0
	while True:
		max_episode = len(episodes.id)
		print('Select 0 to quit safely')
		episode_number = int(input("Enter episode number (1-"+str(max_episode)+"): "))
		if episode_number > max_episode or episode_number < 1:
			if episode_number == 0:
				quit_safely()
			print('Episode number outside of given range')
		else:
			return episode_number - 1

def judge_mirror(mirror_name):
	global supported_mirrors
	return "Tak" if mirror_name in supported_mirrors else "Nie"

def select_mirror(mirrors):
	global debug_mode
	if debug_mode == True:
		return 0
	while True:
		max_mirror = len(mirrors.mirror)
		print('Select 0 to quit safely')
		mirror_number = int(input("Enter mirror number (1-"+str(max_mirror)+"): "))
		if mirror_number > max_mirror or mirror_number < 1:
			if mirror_number == 0:
				quit_safely()
			if mirror_number == -2:
				return -2
			else:
				print('Mirror number outside of given range')
		else:
			return mirror_number - 1

debug_mode = False
extreme_debug_mode = False

print('Starting browser engine')
browser = browser_engine()
print('Browser engine successfully initialized')
while True:
	search_results = search_for_anime()
	anime_id = retrieve_anime_id_from_selection(search_results)
	episodes = episode_list(anime_id)
	episodes.list_all()
	while True:
		episode_number = select_episode(episodes)
		mirrors = mirror_list(anime_id,episodes.id[episode_number],browser)
		mirrors.list_all()
		mirror_number = select_mirror(mirrors)
		if mirror_number != -2:
			try:
				file_url = shinden_direct_url(browser,mirrors.mirror[mirror_number])
			except MirrorVendorUnsupported:
				print('Unsupported mirror vendor: '+mirrors.mirror[mirror_number].vendor)
		if extreme_debug_mode == True:
			break
	if extreme_debug_mode == True:
		break
browser.quit()
