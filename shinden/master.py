#!/usr/bin/env python3

from browser.engine import browser_engine
from shinden.search import shinden_search
from shinden.episodes import episode_list
from shinden.mirrors import mirror_list
from shinden.scraper import direct_url

class shinden_master_class(object):
	def quit_safely(self):
		self.browser.quit()
		quit()

	def __get_important_cookie(self):
		while True:
			for cookie in self.browser.driver.get_cookies():
				if cookie['name'] == 'cto_bundle':
					return {cookie['name']: cookie['value']}

	def __init__(self, debug_mode=False, fast_mode=True, graphic_interface=False, test_mode=False):
		self.debug_mode = debug_mode
		self.graphic_interface = graphic_interface
		self.test_mode = test_mode
		self.browser = browser_engine(debug_mode=self.debug_mode, fast_mode=fast_mode)
		self.browser.driver.get('https://forum.shinden.pl')
		self.browser.wait_for_document_to_finish_loading()
		self.browser.driver.get('https://shinden.pl')
		self.browser.wait_for_document_to_finish_loading()
		self.important_cookie = self.__get_important_cookie()

	def __cli_search_for_anime(self, tm_search_term = ""):
		if self.test_mode == True:
			search_results = shinden_search(tm_search_term, self.important_cookie, graphic_interface=self.graphic_interface)
			search_results.list_search_results()
			return search_results
		print('What would you like to watch? If nothing, just enter nothing')
		search_term = input("Enter search term: ")
		if search_term == "":
			self.quit_safely()
		try:
			search_results = shinden_search(search_term, self.important_cookie)
		except:
			self.quit_safely()
		search_results.list_search_results()
		return search_results

	def search_for_anime(self, tm_search_term = ""):
		results = ""
		if self.graphic_interface == False:
			results = self.__cli_search_for_anime(tm_search_term = tm_search_term)
		else:
			raise ValueError("GUI not implemented yet")
		self.search_results = results

	def select_anime(self):
		anime_object = None
		if self.test_mode == True:
			anime_object = self.search_results.result[0]
		else:
			anime_object = self.search_results.select_anime()
		if anime_object is None:
			self.quit_safely()
		self.selected_anime_id = anime_object.full_id
		self.selected_anime_type = anime_object.type
		self.episodes = episode_list(self.selected_anime_id, self.selected_anime_type, self.important_cookie, graphic_interface=self.graphic_interface)
		self.episodes.list_all()

	def reload_episode_page(self):
		self.browser.driver.get(self.mirrors.episode_url)
		self.browser.wait_for_document_to_finish_loading()

	def select_episode(self, episode=-1):
		result = episode
		if episode == -1:
			result = 0
			if self.test_mode == False:
				result = self.episodes.select_episode()
			if result == -1:
				self.quit_safely()
		result -= 1
		self.selected_episode = self.episodes.id[result]
		if self.selected_episode is None:
			self.mirrors = None
		else:
			self.mirrors = mirror_list(self.selected_anime_id, self.selected_episode, self.browser, graphic_interface=self.graphic_interface)
			self.mirrors.list_all()

	def get_episode_url(self):
		return "https://shinden.pl/episode/"+self.selected_anime_id+"/view/"+self.selected_episode

	def select_mirror(self, tm_mirror = -1):
		if self.mirrors is None:
			print('This episode has no mirrors. Try another episode')
		else:
			result = 0
			if self.test_mode == True:
				if type(tm_mirror) is int:
					if tm_mirror != -1:
						result = tm_mirror
					else:
						result = 0
				else:
					result = self.mirrors.get_mirror_index_by_name(tm_mirror)
					if result == -1:
						print('Selecting by name did not work. Using first mirror.')
						result = 0
			else:
				result = self.mirrors.select_mirror()
			if result == -1:
				self.quit_safely()
			self.selected_mirror = result
			self.mirror_to_scrape = self.mirrors.mirror[self.selected_mirror]
		
	def get_direct_url(self):
		self.direct_url = direct_url(self.browser, self.mirror_to_scrape, self.mirrors.supported_mirrors)
