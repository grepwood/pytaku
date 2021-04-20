#!/usr/bin/env python3

from util.gd_apicode_cc import gd_apicode_cc_handler

class vidoza_handler(object):
	def __init__(self, browser, player_url, mirror_vendor):
		self.url = []
		for url in player_url:
			self.url.append(gd_apicode_cc_handler(browser, url, mirror_vendor).url)
