#!/usr/bin/env python3

import browser.test as detect_browsers
from bs4 import BeautifulSoup
import selenium
import re

import traceback

import sys
import itertools
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

class browser_engine(object):
	def __init__(self, debug_mode=False, fast_mode=True, preferred_browser = None):
		print('Starting browser engine')
		if type(preferred_browser) is str:
			self.preferred_browser = preferred_browser
		else:
			self.preferred_browser = detect_browsers.detect_browsers(fast_mode=fast_mode)[0]
		self.profile = ""
		self.options = ""
		self.driver = ""
		self.debug_mode = debug_mode
		self.operating_system = sys.platform
		if self.preferred_browser == 'firefox':
			self.profile = webdriver.FirefoxProfile()
			self.options = webdriver.FirefoxOptions()
			self.profile.set_preference("intl.accept_languages", "pl")
			self.options.headless = not self.debug_mode
			self.profile.update_preferences()
			if self.operating_system == 'darwin':
				self.driver = webdriver.Firefox(self.profile, options=self.options, executable_path='./geckodriver')
			else:
				self.driver = webdriver.Firefox(self.profile, options=self.options)
		elif self.preferred_browser == 'google-chrome-stable':
			self.options = webdriver.ChromeOptions()
			self.options.add_argument("-lang=pl")
			self.options.headless = not self.debug_mode
			if self.operating_system == 'darwin':
				self.driver = webdriver.Chrome(options=self.options, executable_path='./chromedriver')
			else:
				self.driver = webdriver.Chrome(options=self.options)
#		elif self.preferred_browser == 'msedge':
#			self.options = webdriver.EdgeOptions()
#			self.options.add_argument("-lang=pl")
#			self.options.headless = not self.debug_mode
#			if self.operating_system == 'darwin':
#				self.driver = webdriver.Edge(options=self.options, executable_path='./chromedriver')
#			else:
#				self.driver = webdriver.Edge(options=self.options)
		else:
			raise ValueError("Unsupported browser")
		self.user_agent = self.driver.execute_script("return navigator.userAgent;")
		self.accepted_gdpr = False
		self.accepted_cookies = False
		print('Browser engine successfully initialized')

	def handle_captcha(self, captcha_name):
		print('ATTENTION! USER MUST SOLVE CAPTCHA!')
		current_url = self.driver.current_url
		temporary_browser = browser_engine(debug_mode=True, preferred_browser = self.preferred_browser)
		temporary_browser.driver.get(current_url)
		temporary_browser.wait_for_document_to_finish_loading(verbose=False)
		while True:
			x = temporary_browser.driver.title
			if x != captcha_name:
				break
		print('Captcha solved')
		temporary_browser.wait_for_document_to_finish_loading(verbose=False)
		result = BeautifulSoup(temporary_browser.driver.page_source, "html.parser")
		temporary_browser.quit()
		return result

	def quit(self):
		self.driver.quit()
		self.accepted_gpdr = False
		self.accepted_cookies = False

	def wait_for_document_to_finish_loading(self, verbose=True):
		if verbose == True: print('Waiting for document to load')
		while self.driver.execute_script("return document.readyState;") != "complete": next
		if verbose == True: print('Document finished loading')
	
	def accept_gdpr(self):
		if self.accepted_gdpr == False:
			print('Accepting GDPR')
			self.wait_for_document_to_finish_loading()
			while True:
				try:
					nasty_div = self.find_xpath_by_text('Zaakceptuj wszystko')
					break
				except ModuleNotFoundError:
					traceback.print_exc()
					self.quit()
				except:
					next
			print('Found GDPR accept button in xpath ' + nasty_div)
			self.driver.find_elements_by_xpath(nasty_div)[0].click()
			print('GDPR accepted')
			self.accepted_gdpr = True

	def find_xpath_by_text(self, txt):
		soup = BeautifulSoup(self.driver.page_source, "html.parser")
		element = soup.find(string=txt)
		components = []
		child = element if element.name else element.parent
		for parent in child.parents:
			previous = itertools.islice(parent.children, 0, parent.contents.index(child))
			xpath_tag = child.name
			xpath_index = sum(1 for i in previous if i.name == xpath_tag) + 1
			components.append(xpath_tag if xpath_index == 1 else '%s[%d]' % (xpath_tag, xpath_index))
			child = parent
		components.reverse()
		return '//%s' % '/'.join(components)

	def scroll_to_element(self,element):
		actions = ActionChains(self.driver)
		actions.send_keys_to_element(self.driver.find_elements_by_xpath('//html/body')[0], Keys.HOME).perform()
		self.click_invisible_bullshit()
		while not self.driver.find_elements_by_xpath(element)[0].is_displayed():
			actions.send_keys_to_element(self.driver.find_elements_by_xpath('//html/body')[0], Keys.DOWN).perform()

	def get_xpath_from_element(self, element):
		components = []
		child = element if element.name else element.parent
		for parent in child.parents:
			siblings = parent.find_all(child.name, recursive=False)
			components.append(
				child.name
				if siblings == [child] else
				'%s[%d]' % (child.name, 1 + siblings.index(child))
			)
			child = parent
		components.reverse()
		return '//%s' % '/'.join(components)

	def click_invisible_bullshit(self):
		bullshit_style = 'position: fixed; display: block; width: 100%; height: 100%; inset: 0px; background-color: rgba(0, 0, 0, 0); z-index: 300000;'
		soup = BeautifulSoup(self.driver.page_source, "html.parser")
		bullshit_div = soup.find('div', attrs={'style': bullshit_style})
		if bullshit_div is None:
			print('Bullshit has not been detected')
			return
		bullshit_xpath = self.get_xpath_from_element(bullshit_div)
		bullshit_element = self.driver.find_elements_by_xpath(bullshit_xpath)
		actions = ActionChains(self.driver)
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
		return
	
	def accept_cookies(self):
		if self.accepted_cookies == False:
			try:
				print('Accepting cookies')
				self.wait_for_document_to_finish_loading()
				cookie_accept_button_xpath = self.find_xpath_by_text('Akceptuję')
				self.wait_for_element_to_appear(cookie_accept_button_xpath)
				while True:
					try:
						self.driver.find_elements_by_xpath(cookie_accept_button_xpath)[0].click()
						break
					except selenium.common.exceptions.ElementClickInterceptedException:
						try:
							self.click_invisible_bullshit()
						except selenium.common.exceptions.StaleElementReferenceException:
							print('bullshit element is stale, it is ok to accept cookies')
						try:
							self.click_invisible_bullshit()
						except selenium.common.exceptions.ElementNotInteractableException:
							self.driver.find_elements_by_xpath(cookie_accept_button_xpath)[0].click()
				print('Cookies accepted')
			except:
				traceback.print_exc()
				pdb.set_trace()
			self.accepted_cookies = True
	
	def wait_for_countdown(self):
		while self.driver.find_elements_by_xpath('//*[@id="countdown"]') != []: next
	
	def wait_for_element_to_appear(self, element):
		print('Waiting for element to appear: ' + element)
		while self.driver.find_elements_by_xpath(element) == []: next
		print('Element appeared')
	
	def get_cookie_even_if_it_takes_time(self, cookie_name):
		cookie_obj = ""
		while True:
			cookie_obj = self.driver.get_cookie(cookie_name)
			if type(cookie_obj) is dict: break
		return cookie_obj
	
	def find_tags_with_multiple_classes(self, type_of_tag, classes):
		results = []
		html_soup = BeautifulSoup(self.driver.page_source,"html.parser")
		for item in html_soup.findAll(type_of_tag, {'class': re.compile("^.*$")}):
			classes_found = 0
			for each_class in classes:
				classes_found += int(each_class in item.attrs['class'])
			if classes_found == len(classes):
				results.append(item)
		return results
