#!/usr/bin/env python3

import requests
import re
from bs4 import BeautifulSoup
from mirrors.exceptions.dead import DeadMirror

class aparat_handler(object):
	def __is_mirror_dead(self, player_url):
		self.__response = self.__session.get(player_url)
		return self.__response.text == self.__death_indicator

	def __extract_primary_url(self):
		soup = bs4.BeautifulSoup(self.__response.text, "html.parser")
		javascript_mess = soup.findAll('script')[-4]
		without_newlines = re.sub("\n", "", str(javascript_mess))
		without_location_definition = re.sub("^.*window.top.location.href = \'", "", without_newlines)
		without_garbage = re.sub("\'.*$", "", without_location_definition)
		return without_garbage

	def __generate_secondary_url(self, primary_url):
		self.__response = self.__session.get(primary_url)
		soup = BeautifulSoup(self.__response.text, "html.parser")
		parameter_soup = soup.findAll('a')[-5].attrs['onclick']
		without_beginning_parentheses = re.sub("^.*\('", "", parameter_soup)
		without_ending_parentheses = re.sub("'\)", "", without_beginning_parentheses)
		parameters = re.sub("'", "", without_ending_parentheses).split(',')
		return 'https://wolfstream.tv/dl?op=download_orig&id='+parameters[0]+'&mode='+parameters[1]+'&hash='+parameters[2]

	def __generate_direct_link(self, secondary_url):
		self.__response = self.__session.get(secondary_url)
		soup = BeautifulSoup(self.__response.text, "html.parser")
		return soup.findAll('a')[-3].attrs['href']

	def __init__(self, player_url):
		self.url = []
		self.__session = requests
		self.__death_indicator = '<html><body style="width:100%;height:100%;padding:0;margin:0;">\r\n<center>\r\n<div style="position: absolute;top:50%;width:100%;text-align:center;font: 15px Verdana;">File is no longer available as it expired or has been deleted.</div>\r\n</center>\r\n\r\n<img src="/images/player_blank.jpg" style="position:absolute;width:100%;height:100%" id="over" onclick="document.getElementById(\'over\').style.display = \'none\';">\r\n\r\n</body></html>'
		for url in player_url:
			if self.__is_mirror_dead(url) == True:
				raise DeadMirror
			primary_url = self.__extract_primary_url()
			secondary_url = self.__generate_secondary_url(primary_url)
			final_url = self.__generate_direct_link(secondary_url)
			self.url.append(final_url)
		self.compatible_with_watchtogether = False
		self.download_possible = True
