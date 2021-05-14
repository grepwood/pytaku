#!/usr/bin/env python3

class dailymotion_handler(object):
	def __init__(self, player_url):
		print('Dailymotion is only available for download through youtube-dl')
		self.url = player_url
		self.compatible_with_watchtogether = True
		self.download_possible = True
