#!/usr/bin/env python3

class crunchyroll_handler(object):
	def __init__(self, player_url):
		print('Crunchyroll is a browser-only mirror. It cannot be downloaded nor shared.')
		self.url = player_url
		self.compatible_with_watchtogether = False
		self.download_possible = False
