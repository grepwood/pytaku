#!/usr/bin/env python3

import re
import requests
from bs4 import BeautifulSoup
from mirrors.exceptions.dead import DeadMirror

class SchrodingersMirror(Exception):
	"""Raised when we are not sure if Cloudvideo mirror is dead or alive."""
	pass

class cloudvideo_handler(object):
	def __detect_death(self, soup):
		death_text = 'The media could not be loaded, either because the server or network failed or because the format is not supported.'
		item = soup.find('div', attrs={'class': 'vjs-modal-dialog-content', 'role': 'document'})
		if item is None:
			return False
		else:
			try:
				if item.text == death_text:
					return True
				else:
					raise SchrodingersMirror
			except:
				raise SchrodingersMirror

	def __find_magic_script(self, soup):
		for script in soup.findAll('script', attrs={'type': 'text/javascript'}):
			candidate = str(script)
			if re.match('^<script type="text/javascript">eval\(function\(p,a,c,k,e,d\)', candidate):
				return candidate
		return None

	def __find_video_url(self, magic_script):
		result = re.sub("'.split\('\|'\)\)\)\n</script>", "", magic_script)
		result = re.sub("^.*'", "", result)
		count = -1
		beginning_markers = ['autoplay', 'sources', 'src']
		ending_markers = 'type'
		messy_array = result.split('|')
		while messy_array[count] in beginning_markers:
			count -= 1
		result = 'https://'
		while messy_array[count] != 'hls':
			result += messy_array[count]
			if messy_array[count-1] == 'hls':
				result += '/'
			else:
				result += '.'
			count -= 1
		result += messy_array[count] + '/'
		result += ',' + messy_array[count-1] + ',.' + messy_array[count-2] + '/' + messy_array[count-3] + '.' + messy_array[count-4]
		return result


	def __init__(self, player_url):
		self.url = []
		session = requests
		close_header = {'Connection':'close'}
		for url in player_url:
			response = session.get(url)
			soup = BeautifulSoup(response.text, "html.parser")
			session.post(url, headers=close_header)
			if self.__detect_death(soup) == True:
				raise DeadMirror
			magic_script = self.__find_magic_script(soup)
			video_url = self.__find_video_url(magic_script)
			self.url.append(video_url)
		self.compatible_with_watchtogether = False
		self.download_possible = True
		self.is_m3u8 = True
