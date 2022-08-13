#!/usr/bin/env python3

import requests
import re
from bs4 import BeautifulSoup
from prettytable import PrettyTable

class episode_list(object):
	def __init__(self, anime_id, anime_type, cookie_dict, graphic_interface=False):
		self.graphic_interface = graphic_interface
		query_url = "https://shinden.pl/" + anime_type + "/" + anime_id + "/all-episodes"
		print('Listing episodes from: ' + query_url)
		session = requests
		close_header = {'Connection':'close'}
		req = session.get(query_url, cookies=cookie_dict)
		session.post(query_url, cookies=cookie_dict, headers=close_header)
		soup = BeautifulSoup(req.content, "html.parser")
		big_tag_matrix = soup.find('tbody', attrs={'class': 'list-episode-checkboxes'})
		episode_tag_array = big_tag_matrix.findChildren('tr')[::-1]
		self.episode_count = len(episode_tag_array)
		self.title = []
		self.id = []
		count = 0
		self.as_a_table = PrettyTable()
		self.as_a_table.field_names = ['Numer', 'Tytuł', 'Ma mirrory']
		while count < self.episode_count:
			episode_number = episode_tag_array[count].findChild('td').text
			episode_id = None
			episode_button = episode_tag_array[count].findChild('td', attrs={'class': 'button-group'})
			has_mirrors = 'Nie'
			if not (episode_button is None):
				episode_id = episode_button.findChild('a')['href'].split('/')[-1]
				has_mirrors = 'Tak'
			title = episode_tag_array[count].findChild('td', attrs={'class': 'ep-title'}).text
			self.title.append(title)
			self.id.append(episode_id)
			self.as_a_table.add_row([episode_number, title, has_mirrors])
			count += 1

	def list_all(self):
		print(self.as_a_table)

	def __cli_select_episode(self):
		while True:
			print('Select 0 to quit safely')
			while True:
				input_episode = input("Enter episode number (1-"+str(self.episode_count)+"): ")
				if re.match('^[0-9]+$', input_episode):
					break
				else:
					print('Numbers only, buddy')
			episode_number = int(input_episode)
			if episode_number > self.episode_count or episode_number < 1:
				if episode_number == 0:
					return -1
				print('Episode number outside of given range')
			else:
				return episode_number - 1

	def select_episode(self):
		if self.graphic_interface == False:
			return self.__cli_select_episode()
		else:
			raise ValueError("GUI not implemented yet")
