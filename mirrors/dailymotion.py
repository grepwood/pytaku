#!/usr/bin/env python3

class dailymotion_handler(object):
	def __init__(self, player_url):
		self.url = []
		print('Dailymotion is only available for download through youtube-dl')
		for url in player_url:
			self.url.append(url)
