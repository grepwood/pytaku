#!/usr/bin/env python3

from mirrors.exceptions.dead import DeadMirror

class tunepk_handler(object):
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
