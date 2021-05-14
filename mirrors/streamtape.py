#!/usr/bin/env python3

import re
import json
import requests
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

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
		self.compatible_with_watchtogether = True
		self.download_possible = True
