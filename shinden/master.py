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

	def __init__(self, debug_mode=False, fast_mode=True, graphic_interface=False, test_mode=False):
		self.debug_mode = debug_mode
		self.graphic_interface = graphic_interface
		self.test_mode = test_mode
		self.browser = browser_engine(debug_mode=self.debug_mode, fast_mode=fast_mode)

	def __cli_search_for_anime(self):
		if self.test_mode == True:
			search_results = shinden_search('JoJo no Kimyou na Bouken: Stardust Crusaders - Egypt-hen', graphic_interface=self.graphic_interface)
			search_results.list_search_results()
			return search_results
		print('What would you like to watch? If nothing, just enter nothing')
		search_term = input("Enter search term: ")
		if search_term == "":
			self.quit_safely()
		try:
			search_results = shinden_search(search_term)
		except:
			self.quit_safely()
		search_results.list_search_results()
		return search_results

	def search_for_anime(self):
		results = ""
		if self.graphic_interface == False:
			results = self.__cli_search_for_anime()
		else:
			raise ValueError("GUI not implemented yet")
		self.search_results = results

	def select_anime(self):
		result = 0
		if self.test_mode == True:
			result = self.search_results.result[0].id
		else:
			result = self.search_results.select_anime()
		if result == -1:
			self.quit_safely()
		self.selected_anime_id = result
		self.episodes = episode_list(self.selected_anime_id, graphic_interface=self.graphic_interface)
		self.episodes.list_all()

	def reload_episode_page(self):
		self.browser.driver.get(self.mirrors.episode_url)
		self.browser.wait_for_document_to_finish_loading()

	def select_episode(self):
		result = 0
		if self.test_mode == False:
			result = self.episodes.select_episode()
		if result == -1:
			self.quit_safely()
		self.selected_episode = self.episodes.id[result]
		self.mirrors = mirror_list(self.selected_anime_id, self.selected_episode, self.browser, graphic_interface=self.graphic_interface)
		self.mirrors.list_all()

	def select_mirror(self):
		result = 0
		if self.test_mode == True:
			result = self.mirrors.get_mirror_index_by_name('Cda')
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
