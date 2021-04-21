#!/usr/bin/env python3

from selenium.webdriver.support.ui import Select
from mirrors.exceptions.unsupported import MirrorVendorUnsupported

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
