#!/usr/bin/env python3

import traceback
from shinden.master import shinden_master_class

debug_mode = False
test_mode = False
shinden = shinden_master_class(debug_mode=debug_mode, fast_mode=True, test_mode=test_mode)
try:
	while True:
		shinden.search_for_anime()
		shinden.select_anime()
		while True:
			shinden.select_episode()
			shinden.select_mirror()
			shinden.get_direct_url()
			if test_mode == True:
				break
		if test_mode == True:
			break
except SystemExit:
	quit()
except:
	traceback.print_exc()
shinden.browser.quit()
