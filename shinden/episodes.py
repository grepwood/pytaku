#!/usr/bin/env python3

import requests
import re
from bs4 import BeautifulSoup
from prettytable import PrettyTable

class episode_list(object):
	def __init__(self, anime_id, graphic_interface=False):
		self.graphic_interface = graphic_interface
		query_url = "https://shinden.pl/series/"+anime_id+"/all-episodes"
		req = requests.get(query_url)
		soup = BeautifulSoup(req.content, "html.parser")
		big_tag_matrix = soup.findAll('tbody', attrs={'class','list-episode-checkboxes'})[0].findAll('td')
		self.episode_count = int(len(big_tag_matrix)/6)
		self.title = []
		self.id = []
		count = 0
		self.as_a_table = PrettyTable()
		self.as_a_table.field_names = ['Numer', 'Tytuł']
		while count < self.episode_count:
			episode_id = re.sub('^.*/view/','',big_tag_matrix[(self.episode_count - count - 1)*6+5].findChild('a')['href'])
			title = big_tag_matrix[(self.episode_count - count - 1)*6+1].get_text(strip=True)
			self.title.append(title)
			self.id.append(episode_id)
			count += 1
			self.as_a_table.add_row([str(count), title])
	
	def list_all(self):
		print(self.as_a_table)

	def __cli_select_episode(self):
		while True:
			print('Select 0 to quit safely')
			episode_number = int(input("Enter episode number (1-"+str(self.episode_count)+"): "))
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
