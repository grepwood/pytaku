#!/usr/bin/env python3

import sys
import getopt
import traceback
from shinden.master import shinden_master_class
from prettytable import PrettyTable

def usage():
	print('Usage: ' + sys.argv[0] + ' parameters')
	print("\t-s\t- search term - will search for this anime")
	return -1

def main():
	tm_search_term = ""
	try:
		opts, argv = getopt.getopt(sys.argv[1:], 's:')
	except getopt.GetoptError:
		traceback.print_exc()
		print("")
		return usage()
	for key, value in opts:
		if key == '-s':
			tm_search_term = value
	if tm_search_term == "":
		print('Finding unsupported mirrors requires an anime title to search for')
		return usage()
	try:
		shinden = shinden_master_class(debug_mode=False, fast_mode=True, test_mode=True)
		shinden.search_for_anime(tm_search_term = tm_search_term)
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

if __name__ == '__main__':
	result = main()
	sys.exit(result)
