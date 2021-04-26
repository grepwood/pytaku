#!/usr/bin/env python3

import traceback
from shinden.master import shinden_master_class
from prettytable import PrettyTable

try:
	shinden = shinden_master_class(debug_mode=False, fast_mode=True, test_mode=True)
	shinden.search_for_anime()
	shinden.select_anime()
	episode = 0
	result_table = PrettyTable()
	result_table.field_names = ['Vendor', 'Occurence']
	while episode < shinden.episodes.episode_count:
		shinden.select_episode(episode=episode)
		this_episodes_um = shinden.mirrors.get_unsupported_mirrors()
		for item in this_episodes_um:
			result_table.add_row([item.vendor, shinden.get_episode_url()])
		episode += 1
	print(result_table)

except SystemExit:
	quit()
except:
	traceback.print_exc()
try:
	shinden.browser.quit()
except NameError:
	pass
