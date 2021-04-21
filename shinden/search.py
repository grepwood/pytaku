#!/usr/bin/env python3

import re
import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable

from shinden.ratings import shinden_ratings

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

class shinden_search(object):
	def __detect_shinden_downtime_from_soup(soup):
		error_msg = soup.find('p', {'class': 'enormous-font bree-font'}).text
		if error_msg == ' 500 ':
			raise ShindenDowntime
		else:
			raise ShindenUnknownException

	def __make_string_url_friendly(self, input_text):
		return re.sub(" ", "+", input_text)
	
	def __init__(self, search_term, graphic_interface=False):
		self.graphic_interface = graphic_interface
		url = 'https://shinden.pl/series?search='+self.__make_string_url_friendly(search_term)
		session = requests
		response = session.get(url)
		soup = BeautifulSoup(response.text, "html.parser")
		try:
			crazy_table = soup.findAll('section', attrs={'class', 'title-table'})[0].findAll('article')[0]
		except IndexError:
			try:
				self.__detect_shinden_downtime_from_soup(soup)
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

	def __cli_select_anime(self):
		while True:
			print('Select 0 to quit safely')
			selected_anime = int(input("Select anime from above list (1-"+str(self.count)+"): "))
			if selected_anime < 1 or selected_anime > self.count:
				if selected_anime == 0:
					return -1
			else:
				selected_anime -= 1
				if self.result[selected_anime].episode_count != 0:
					return self.result[selected_anime].id
				else:
					print('This anime has no episodes. Choose something else.')

	def select_anime(self):
		if self.graphic_interface == False:
			return self.__cli_select_anime()
		else:
			raise ValueError("GUI not implemented yet")
