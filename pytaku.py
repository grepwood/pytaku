#!/usr/bin/env python3
import requests
import re
import bs4
import selenium
from browser.engine import browser_engine
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from mega import Mega
import pdb
from prettytable import PrettyTable
import traceback

from mirrors.aparat import aparat_handler
from mirrors.cda import cda_handler
from mirrors.cloud9 import cloud9_handler
from mirrors.dailymotion import dailymotion_handler
from mirrors.dood import dood_handler
from mirrors.facebook import facebook_handler
from mirrors.mp4upload import mp4upload_handler
from mirrors.sibnet import sibnet_handler
from mirrors.streamsb import streamsb_handler
from mirrors.streamtape import streamtape_handler
from mirrors.tunepk import tunepk_handler
from mirrors.youtube import youtube_handler
from mirrors.yourupload import yourupload_handler
from mirrors.myviru import myviru_handler
from mirrors.vidlox import vidlox_handler
from mirrors.vidoza import vidoza_handler
from mirrors.vkontakte import vkontakte_handler
from mirrors.exceptions.dead import DeadMirror

class episode_list(object):
	def __init__(self, anime_id):
		query_url = "https://shinden.pl/series/"+anime_id+"/all-episodes"
		req = requests.get(query_url)
		html_page = req.content
		soup = bs4.BeautifulSoup(html_page, "html.parser")
# For whatever reason, reversing big_tag_matrix doesn't work
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
	def __init__(self,anime_id,episode_id,browser):
		print('started mirror_list class')
		episode_url = "https://shinden.pl/episode/"+anime_id+"/view/"+episode_id
		print('opening '+episode_url)
		browser.driver.get(episode_url)
		browser.accept_gdpr()
		browser.accept_cookies()
		browser.click_invisible_bullshit()
		print('searching for episode-player-list section')
		episode_tags = browser.find_tags_with_multiple_classes('table', ['data-view-table-strips', 'data-view-table-big', 'data-view-hover'])[0].find('tbody')
		print('entering result loop')
		self.mirror = []
		count = 0
		self.as_a_table = PrettyTable()
		self.as_a_table.field_names = ['Numer', 'Źródło', 'Jakość', 'Język', 'Napisy', 'Data dodania', 'Wspierany']
		for item in episode_tags.findAll('tr'):
			self.mirror.append(mirror_object(item))
			self.as_a_table.add_row([str(count+1), self.mirror[count].vendor, self.mirror[count].quality, self.mirror[count].audio_language, self.mirror[count].sub_language, self.mirror[count].date_added, judge_mirror(self.mirror[count].vendor)])
			count += 1
	
	def list_all(self):
		print(self.as_a_table)

	def get_mirror_index_by_name(self, vendor_name):
		count = 0
		for item in self.mirror:
			if self.mirror[count].vendor == vendor_name:
				return count
			count += 1
		return -1

class MirrorVendorUnsupported(Exception):
	"""Raised when mirror vendor is unsupported. Let us know by filing an issue."""
	pass

class shinden_direct_url(object):
	def __get_player_html(self, browser, mirror):
		actions = ActionChains(browser.driver)
		print('trying to snoop for '+mirror.vendor+' player on shinden')
		browser.scroll_to_element('//*[@id="'+mirror.xpath+'"]')
		browser.click_invisible_bullshit()
		while True:
			try:
				print('Clicking xpath '+mirror.xpath)
				browser.driver.find_elements_by_xpath('//*[@id="'+mirror.xpath+'"]')[0].click()
				break
			except selenium.common.exceptions.ElementClickInterceptedException:
				actions.send_keys_to_element(browser.driver.find_elements_by_xpath('//html/body')[0], Keys.DOWN).perform()
		print('waiting for countdown')
		browser.wait_for_countdown()
		print('parsing player element')
		page_source = browser.driver.find_elements_by_xpath('//html/body/div[4]/div/article/div[2]')[0].get_attribute('innerHTML')
		soup = bs4.BeautifulSoup(page_source,"html.parser")
		return soup
	
	def __get_player_url_list(self, browser, mirror):
		player_url_list = []
		print('retrieving player URL')
		while player_url_list == []:
			soup = self.__get_player_html(browser,mirror)
			try:
				if mirror.vendor in ['Yourupload']:
					players = soup.findAll('a', {'class': 'button-player'})
					attribute_to_look_for = 'href'
				elif mirror.vendor in ['Tunepk']:
					players = soup.findAll('a', {'class': 'player-external-link'})
					attribute_to_look_for = 'href'
				else:
					players = soup.findAll('iframe')
					attribute_to_look_for = 'src'
				for player in players:
					base_referant = player.attrs[attribute_to_look_for]
					if mirror.vendor == 'Sibnet':
						player_url = 'https://video.sibnet.ru/shell.php?videoid='+re.sub("^.*=","",base_referant)
					elif mirror.vendor == 'Mega':
						player_url = "https://mega.co.nz/#!"+base_referant.split('#!')[1]
					elif mirror.vendor in ['Cda', 'Mp4upload', 'Vidloxtv', 'Vk', 'Dailymotion', 'Yourupload', 'Myviru']:
						player_url = re.sub('^//','https://',base_referant)
					else:
						player_url = base_referant
					player_url_list.append(player_url)
				break
			except IndexError:
				print('error occurred on shinden, retryting')
#				possible location: /html/body/div[4]/div/article/div[2]/div/div[2]/div
				browser.driver.refresh()
				browser.wait_for_document_to_finish_loading()
		return player_url_list
	
	def __get_url(self, browser, mirror):
		if not mirror.vendor in self.__compatible_mirror_types:
			raise MirrorVendorUnsupported
		player_url = self.__get_player_url_list(browser, mirror)
		shinden_url = browser.driver.current_url
		result = ""
		if mirror.vendor == 'Sibnet':
			self.compatible_with_watchtogether = True
			self.download_possible = True
			self.requires_referer = False
			self.requires_redirect = False
			self.requires_browser_identity = False
			self.requires_raw_data = False
			self.requires_cookie = False
			result = sibnet_handler(browser.user_agent, player_url).url
			self.referer = ""
			self.user_agent = ""
			self.raw_data = ""
		elif mirror.vendor == 'Mega':
			self.compatible_with_watchtogether = False
			self.download_possible = True
			self.requires_referer = False
			self.requires_redirect = False
			self.requires_browser_identity = False
			self.requires_raw_data = False
			self.requires_cookie = False
			result = player_url
			self.referer = ""
			self.user_agent = ""
			self.raw_data = ""
		elif mirror.vendor == 'Streamtape':
			self.compatible_with_watchtogether = True
			self.download_possible = True
			self.requires_referer = False
			self.requires_redirect = False
			self.requires_browser_identity = False
			self.requires_cookie = False
			result = streamtape_handler(browser, player_url).url
			self.referer = ""
			self.user_agent = ""
			self.raw_data = ""
		elif mirror.vendor == 'Dood':
			self.compatible_with_watchtogether = False
			self.download_possible = True
			self.requires_referer = True
			self.requires_redirect = False
			self.requires_browser_identity = False
			self.requires_raw_data = False
			self.requires_cookie = False
			result = dood_handler(browser, player_url).url
			self.referer = player_url
			self.user_agent = ""
			self.raw_data = ""
		elif mirror.vendor == 'Streamsb':
			self.compatible_with_watchtogether = False
			self.download_possible = True
			self.requires_referer = False
			self.requires_redirect = False
			self.requires_browser_identity = False
			self.requires_raw_data = False
			self.requires_cookie = False
			result = streamsb_handler(browser, player_url, mirrors.vendor).url
			self.referer = ""
			self.user_agent = ""
			self.raw_data = ""
		elif mirror.vendor == 'Cda':
			self.compatible_with_watchtogether = True
			self.download_possible = True
			self.requires_referer = False
			self.requires_redirect = False
			self.requires_browser_identity = True
			self.requires_raw_data = False
			self.requires_cookie = False
			result = cda_handler(browser, player_url).url
			self.referer = ""
			self.user_agent = browser.user_agent
			self.raw_data = ""
		elif mirror.vendor == 'Mp4upload':
			self.compatible_with_watchtogether = False
			self.download_possible = True
			self.requires_referer = True
			self.requires_redirect = False
			self.requires_browser_identity = False
			self.requires_tls_compromise = True
			self.requires_raw_data = False
			self.requires_cookie = False
			result = mp4upload_handler(browser, player_url).url
			self.referer = ""
			self.user_agent = ""
			self.raw_data = ''
		elif mirror.vendor == 'Vidloxtv':
			self.compatible_with_watchtogether = False
			self.download_possible = True
			self.requires_referer = False
			self.requires_redirect = False
			self.requires_browser_identity = False
			self.requires_raw_data = False
			self.requires_cookie = False
			result = vidlox_handler(browser, player_url).url
			self.referer = ""
			self.user_agent = ""
			self.raw_data = ""
		elif mirror.vendor == 'Vidoza':
			self.compatible_with_watchtogether = False
			self.download_possible = True
			self.requires_referer = False
			self.requires_redirect = False
			self.requires_browser_identity = False
			self.requires_raw_data = False
			self.requires_cookie = False
			result = vidoza_handler(browser, player_url, mirrors.vendor).url
			self.referer = ""
			self.user_agent = ""
			self.raw_data = ""
		elif mirror.vendor == 'Fb':
			self.compatible_with_watchtogether = False
			self.download_possible = True
			self.requires_referer = False
			self.requires_redirect = False
			self.requires_browser_identity = False
			self.requires_raw_data = False
			self.requires_cookie = False
			result = facebook_handler(player_url).url
			self.referer = ""
			self.user_agent = ""
			self.raw_data = ""
		elif mirror.vendor == 'Vk':
			self.compatible_with_watchtogether = False
			self.download_possible = True
			self.requires_referer = False
			self.requires_redirect = False
			self.requires_browser_identity = False
			self.requires_raw_data = False
			self.requires_cookie = False
			result = vkontakte_handler(browser, player_url).url
			self.referer = ""
			self.user_agent = ""
			self.raw_data = ""
		elif mirror.vendor == 'Aparat':
			self.compatible_with_watchtogether = False
			self.download_possible = True
			self.requires_referer = False
			self.requires_redirect = False
			self.requires_browser_identity = False
			self.requires_raw_data = False
			self.requires_cookie = False
			result = aparat_handler(player_url).url
			self.referer = ""
			self.user_agent = ""
			self.raw_data = ""
		elif mirror.vendor == 'Dailymotion':
			self.compatible_with_watchtogether = True
			self.download_possible = True
			self.requires_referer = False
			self.requires_redirect = False
			self.requires_browser_identity = False
			self.requires_raw_data = False
			self.requires_cookie = False
			result = dailymotion_handler(player_url).url
			self.referer = ""
			self.user_agent = ""
			self.raw_data = ""
		elif mirror.vendor == 'Yourupload':
			self.compatible_with_watchtogether = False
			self.download_possible = True
			self.requires_referer = True
			self.requires_redirect = False
			self.requires_browser_identity = False
			self.requires_raw_data = False
			self.requires_cookie = False
			tmp = yourupload_handler(player_url)
			result = tmp.url
			self.referer = tmp.referer
			self.user_agent = ""
			self.raw_data = ""
		elif mirror.vendor == 'Myviru':
			self.compatible_with_watchtogether = False
			self.download_possible = True
			self.requires_referer = False
			self.requires_redirect = False
			self.requires_browser_identity = False
			self.requires_raw_data = False
			self.requires_cookie = True
			tmp = myviru_handler(player_url)
			result = tmp.url
			self.cookie = tmp.cookie
			self.user_agent = ""
			self.raw_data = ""
		browser.driver.get(shinden_url)
		browser.wait_for_document_to_finish_loading()
		return result
	
	def __init__(self, browser, mirror):
		self.compatible_with_watchtogether = False
		self.download_possible = False
		self.requires_referer = False
		self.requires_browser_identity = False
		global supported_mirrors
		self.__compatible_mirror_types = supported_mirrors
		try:
			self.url = self.__get_url(browser, mirror)
		except DeadMirror:
			self.url = ['DEAD URL']
		count = 0
		for url in self.url:
			print('Received URL #'+str(count+1)+': '+self.url[count])
			count += 1

supported_mirrors = ['Sibnet', 'Mega', 'Streamtape', 'Dood', 'Streamsb', 'Cda', 'Mp4upload', 'Vidloxtv', 'Vidoza', 'Fb', 'Vk', 'Aparat', 'Dailymotion', 'Yourupload', 'Myviru']

class search_result(object):
	def __init__(self, title, type_of_broadcast, episode_count, id_of_anime):
		self.title = title
		self.type_of_broadcast = type_of_broadcast
		self.episode_count = episode_count
		self.id_of_anime = id_of_anime

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
# Tutaj trafiają animce które nie mają jeszcze ocen bo np. zostały zapowiedziane ale jeszcze ich nie ma na shindenie
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

def detect_shinden_downtime_from_soup(soup):
	error_msg = soup.find('p', {'class': 'enormous-font bree-font'}).text
	if error_msg == ' 500 ':
		raise ShindenDowntime
	else:
		raise UnknownException

class shinden_search(object):
	def __make_string_url_friendly(self, input_text):
		return re.sub(" ", "+", input_text)
	
	def __init__(self, search_term):
		url = 'https://shinden.pl/series?search='+self.__make_string_url_friendly(search_term)
		session = requests
		response = session.get(url)
		soup = bs4.BeautifulSoup(response.text, "html.parser")
		try:
			crazy_table = soup.findAll('section', attrs={'class', 'title-table'})[0].findAll('article')[0]
		except IndexError:
			try:
				detect_shinden_downtime_from_soup(soup)
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

def search_for_anime():
	global debug_mode
	if debug_mode == True:
		search_results = shinden_search('JoJo no Kimyou na Bouken: Stardust Crusaders - Egypt-hen')
		search_results.list_search_results()
		return search_results
	print('What would you like to watch? If nothing, just enter nothing')
	search_term = input("Enter search term: ")
	if search_term == "":
		quit_safely()
	search_results = shinden_search(search_term)
	search_results.list_search_results()
	return search_results

def quit_safely():
	global browser
	browser.quit()
	quit()

def retrieve_anime_id_from_selection(search_results):
	global debug_mode
	if debug_mode == True:
		return search_results.result[0].id
	while True:
		print('Select 0 to quit safely')
		selected_anime = int(input("Select anime from above list (1-"+str(search_results.count)+"): "))
		if selected_anime < 1 or selected_anime > search_results.count:
			if selected_anime == 0:
				quit_safely()
		else:
			selected_anime -= 1
			if search_results.result[selected_anime].episode_count != 0:
				return search_results.result[selected_anime].id
			else:
				print('This anime has no episodes. Choose something else.')

def select_episode(episodes):
	global debug_mode
	if debug_mode == True:
		return 0
	while True:
		max_episode = len(episodes.id)
		print('Select 0 to quit safely')
		episode_number = int(input("Enter episode number (1-"+str(max_episode)+"): "))
		if episode_number > max_episode or episode_number < 1:
			if episode_number == 0:
				quit_safely()
			print('Episode number outside of given range')
		else:
			return episode_number - 1

def judge_mirror(mirror_name):
	global supported_mirrors
	return "Tak" if mirror_name in supported_mirrors else "Nie"

def select_mirror(mirrors):
	global debug_mode
	if debug_mode == True:
		return mirrors.get_mirror_index_by_name('Cda')
	while True:
		max_mirror = len(mirrors.mirror)
		print('Select 0 to quit safely')
		mirror_number = int(input("Enter mirror number (1-"+str(max_mirror)+"): "))
		if mirror_number > max_mirror or mirror_number < 1:
			if mirror_number == 0:
				quit_safely()
			elif mirror_number == -2:
				return -2
			else:
				print('Mirror number outside of given range')
		else:
			return mirror_number - 1

debug_mode = False
extreme_debug_mode = False

print('Starting browser engine')
browser = browser_engine(debug_mode=False, fast_mode=True)
print('Browser engine successfully initialized')
while True:
	search_results = search_for_anime()
	anime_id = retrieve_anime_id_from_selection(search_results)
	episodes = episode_list(anime_id)
	episodes.list_all()
	while True:
		episode_number = select_episode(episodes)
		mirrors = mirror_list(anime_id,episodes.id[episode_number],browser)
		mirrors.list_all()
		mirror_number = select_mirror(mirrors)
		if mirror_number != -2:
			try:
				file_url = shinden_direct_url(browser,mirrors.mirror[mirror_number])
			except MirrorVendorUnsupported:
				print('Unsupported mirror vendor: '+mirrors.mirror[mirror_number].vendor)
			except:
				traceback.print_exc()
				quit_safely()
		if extreme_debug_mode == True:
			break
	if extreme_debug_mode == True:
		break
browser.quit()
