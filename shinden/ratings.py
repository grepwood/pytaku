#!/usr/bin/env python3

import re
from bs4 import BeautifulSoup

class shinden_ratings(object):
	def __init__(self, html_soup):
		dlugi_tekst = re.sub("\n", "", html_soup.findAll('li', attrs={'class', 'ratings-col'})[0].text)
		if dlugi_tekst != '':
			worek = re.sub(":", "", re.sub(",", ".", dlugi_tekst)).split(" ")
			self.overall = worek[1]
			self.storyline = worek[3]
			self.graphics = worek[5]
			self.music = worek[7]
			self.characters = worek[9]
		else:
			self.overall = 'Brak'
			self.storyline = 'Brak'
			self.graphics = 'Brak'
			self.music = 'Brak'
			self.characters = 'Brak'
			self.top = 'Brak'
		self.top = re.sub(",", ".", html_soup.findAll('li', attrs={'class', 'rate-top'})[0].text)
	
	def list_all(self):
		print('Ogółem: '+self.overall)
		print('Fabuła: '+self.storyline)
		print('Grafika: '+self.graphics)
		print('Muzyka: '+self.music)
		print('Postacie: '+self.characters)
		print('TOP: '+self.top)
