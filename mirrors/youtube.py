#!/usr/bin/env python3

class youtube_handler(object):
	def __init__(self, player_url):
		self.url = []
		print('Youtube is only available for download through youtube-dl')
		for url in player_url:
			self.url.append(url)
