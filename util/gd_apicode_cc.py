#!/usr/bin/env python3

from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from mirrors.exceptions.unsupported import MirrorVendorUnsupported

class gd_apicode_cc_handler(object):
	def __goto_gd_apicode_cc(self, browser):
		browser.driver.get('https://gd.apicode.cc')
		browser.wait_for_document_to_finish_loading()
	
	def __get_url_from_form(self, browser, player_url, mirror_vendor):
		drop = Select(browser.driver.find_element(By.XPATH, '//html/body/div[1]/div[1]/div/form/div[1]/div/select'))
		drop.select_by_value(mirror_vendor.lower())
		browser.driver.find_element(By.XPATH, '//*[@id="id"]').send_keys(player_url)
		browser.wait_for_document_to_finish_loading()
		browser.driver.find_element(By.XPATH, '//*[@id="submit"]').click()
		browser.wait_for_document_to_finish_loading()
		browser.driver.find_element(By.XPATH, '//*[@id="dl-tab"]').click()
		browser.wait_for_document_to_finish_loading()
		return browser.driver.find_element(By.XPATH, '//*[@id="txtDl"]').get_attribute('innerHTML')
	
	def __get_url_from_menu(self, browser, intermediate_url, mirror_vendor):
		browser.driver.get(intermediate_url)
		browser.wait_for_document_to_finish_loading()
		result = ""
		if mirror_vendor in ['Vidlox', 'Vidoza']:
			result = browser.driver.find_element(By.XPATH, '//html/body/div[1]/div[3]/div/a[2]').get_attribute('href')
		elif mirror_vendor == 'Streamsb':
			result = browser.driver.find_element(By.XPATH, '//html/body/div[1]/div[3]/div/a[3]').get_attribute('href')
		else:
			raise MirrorVendorUnsupported
		return result
	
	def __init__(self, browser, player_url, mirror_vendor):
		self.__goto_gd_apicode_cc(browser)
		intermediate_url = self.__get_url_from_form(browser, player_url, mirror_vendor)
		self.url = self.__get_url_from_menu(browser, intermediate_url, mirror_vendor)
