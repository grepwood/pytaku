#!/usr/bin/env python3

import requests
import bs4
import time
import re
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

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
