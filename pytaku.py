#!/usr/bin/env python3

import traceback
from shinden.master import shinden_master_class
from mirrors.cda import CdaRefusesCooperation

debug_mode = False
test_mode = False
try:
	shinden = shinden_master_class(debug_mode=debug_mode, fast_mode=True, test_mode=test_mode)
	while True:
		shinden.search_for_anime()
		shinden.select_anime()
		while True:
			exception_caught = False
			shinden.select_episode()
			while True:
				try:
					if exception_caught == True:
						shinden.reload_episode_page()
					shinden.select_mirror()
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
