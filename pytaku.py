#!/usr/bin/env python3

import sys
import getopt
import traceback
from shinden.master import shinden_master_class
from mirrors.cda import CdaRefusesCooperation
from shinden.mirrors import supported_mirrors as supported_mirrors

def usage():
	print('Usage: ' + sys.argv[0] + ' parameters')
	print('Do not supply any parameters if you want an interactive mode')
	print("\t-d\t- debug mode - browsers will not be headless to let the user see what's going on")
	print("\t-f\t- fast mode - browser tests will cease as soon as the first working browser is found")
	print("\t-t\t- test mode - will run a single test to fetch a URL")
	print("\t-s\t- search term - will search for this in test mode")
	print("\t-e\t- episode number - chosen episode in test mode")
	print("\t-m\t- mirror number or vendor - chosen mirror number or vendor; note that specifying by vendor will return the first matching result")
	return -1

def main():
	debug_mode = False
	test_mode = False
	fast_mode = False
	tm_search_term = ""
	tm_episode_number = -1
	tm_mirror = 0
	tm_flags = 0
	try:
		opts, argv = getopt.getopt(sys.argv[1:], 'dfts:e:m:')
	except getopt.GetoptError:
		traceback.print_exc()
		print("")
		return usage()
	for key, value in opts:
		if key == '-d':
			debug_mode = True
		if key == '-f':
			fast_mode = True
		if key == '-t':
			test_mode = True
			tm_flags |= 1
		if key == '-s':
			tm_search_term = value
			tm_flags |= 2
		if key == '-e':
			if not value.isnumeric():
				print('Episode number must be a number')
				return usage()
			if '.' in value or int(value) < 0:
				print('Episode number must be a non-negative integer')
				return usage()
			tm_episode_number = int(value)
			tm_flags |= 4
		if key == '-m':
			global supported_mirrors
			if value.isnumeric():
				if '.' in value or int(value) < 0:
					print('Mirror number must be a non-negative integer')
					return usage()
				tm_mirror = int(value)
			elif value not in supported_mirrors:
				print('Cannot select mirror vendor that is not supported. Keep in mind, mirror vendors must be specified as they appear in supported_mirrors array in shinden/mirrors.py')
				return usage()
			else:
				tm_mirror = value
			tm_flags |= 8
	if tm_flags != 0 and tm_flags != 15:
		print('Test mode requires search term, episode number and mirror number/vendor to be specified')
		print('tm_flags: ' + str(tm_flags))
		return usage()
	try:
		shinden = shinden_master_class(debug_mode=debug_mode, fast_mode=fast_mode, test_mode=test_mode)
		while True:
			shinden.search_for_anime(tm_search_term = tm_search_term)
			shinden.select_anime()
			while True:
				exception_caught = False
				shinden.select_episode(episode = tm_episode_number)
				while True:
					try:
						if exception_caught == True:
							shinden.reload_episode_page()
						shinden.select_mirror(tm_mirror = tm_mirror)
						if exception_caught == True:
							shinden.mirrors.list_all()
						shinden.get_direct_url()
						break
					except CdaRefusesCooperation:
						print('Cda refuses cooperation. Please choose another mirror AND avoid using Cda altogether during this session of pytaku.')
						if test_mode == True:
							break
						exception_caught = True
						next
				if test_mode == True:
					break
			if test_mode == True:
				break
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
