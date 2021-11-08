#!/usr/bin/env python3

import re
from prettytable import PrettyTable
from bs4 import BeautifulSoup

supported_mirrors = ['Sibnet', 'Mega', 'Streamtape', 'Dood', 'Streamsb', 'Cda', 'Mp4upload', 'Vidloxtv', 'Vidoza', 'Fb', 'Vk', 'Aparat', 'Dailymotion', 'Yourupload', 'Myviru', 'Mystream', 'Upvid', 'Cloudvideo', 'Crunchyroll', 'Gdrive']
defunct_mirrors = ['Default', 'Vshare', 'Streammoe', 'Estream', 'Clipwatching']

class mirror_object(object):
	def __init__(self, html_soup):
		self.vendor = re.sub("^  \n", "", html_soup.find('td', {'class': 'ep-pl-name'}).text)
		self.quality = html_soup.find('td',{'class':'ep-pl-res'}).text
		self.audio_language = html_soup.find('td', {'class': 'ep-pl-alang'}).find('span', {'class': 'mobile-hidden'}).text
		sub_language = html_soup.find('td', {'class': 'ep-pl-slang'}).findAll('span')
		self.sub_language = "Brak" if(len(sub_language) < 2) else sub_language[1].text
		self.date_added = html_soup.find('td', {'class': 'ep-online-added'}).text
		self.xpath = html_soup.find('td', {'class': 'ep-buttons'}).find('a', {'class': 'change-video-player'}).attrs['id']

class mirror_list(object):
	def __judge_mirror(self, mirror_name):
		return "Tak" if mirror_name in self.supported_mirrors else "Nie"

	def __init__(self, anime_id, episode_id, browser, graphic_interface=False):
		global supported_mirrors
		global defunct_mirrors
		self.graphic_interface = graphic_interface
		self.supported_mirrors = supported_mirrors
		self.episode_url = "https://shinden.pl/episode/"+anime_id+"/view/"+episode_id
		print('opening '+self.episode_url)
		browser.driver.get(self.episode_url)
		browser.accept_gdpr()
		browser.accept_cookies()
		browser.click_invisible_bullshit()
		episode_tags = browser.find_tags_with_multiple_classes('table', ['data-view-table-strips', 'data-view-table-big', 'data-view-hover'])[0].find('tbody')
		self.mirror = []
		count = 0
		self.as_a_table = PrettyTable()
		self.as_a_table.field_names = ['Numer', 'Źródło', 'Jakość', 'Język', 'Napisy', 'Data dodania', 'Wspierany']
		for item in episode_tags.findAll('tr'):
			detected_mirror = mirror_object(item)
			if detected_mirror.vendor not in defunct_mirrors:
				self.mirror.append(detected_mirror)
				self.as_a_table.add_row([str(count+1), self.mirror[count].vendor, self.mirror[count].quality, self.mirror[count].audio_language, self.mirror[count].sub_language, self.mirror[count].date_added, self.__judge_mirror(self.mirror[count].vendor)])
				count += 1
			else:
				print('Skipping defunct mirror: '+detected_mirror.vendor)
		self.mirror_count = count
	
	def list_all(self):
		print(self.as_a_table)

	def get_unsupported_mirrors(self):
		result = []
		for item in self.mirror:
			if self.__judge_mirror(item.vendor) == "Nie" and item.vendor not in result:
				result.append(item)
		return result

	def get_mirror_index_by_name(self, vendor_name):
		count = 0
		for item in self.mirror:
			if self.mirror[count].vendor == vendor_name:
				return count
			count += 1
		return -1

	def __cli_select_mirror(self):
		print('Select 0 to quit safely')
		while True:
			mirror_input = input("Enter mirror number (1-"+str(self.mirror_count)+"): ")
			if re.match('^[0-9]+$', mirror_input):
				break
			else:
				print('Numbers only, buddy')
		mirror_number = int(mirror_input)
		if mirror_number > self.mirror_count or mirror_number < 1:
			if mirror_number == 0:
				return -1
			else:
				print('Mirror number outside of given range')
		else:
			return mirror_number - 1

	def select_mirror(self):
		if self.graphic_interface == False:
			return self.__cli_select_mirror()
		else:
			raise ValueError("GUI not implemented yet")
