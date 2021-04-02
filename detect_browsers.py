#!/usr/bin/env python3
import sys
from selenium import webdriver
operating_system = sys.platform
if operating_system == 'win32' or operating_system == 'cygwin':
	import winreg
else:
	import subprocess

def test_webdriver(browser):
	return_code = 0
	if browser == 'firefox' :
		options = webdriver.FirefoxOptions()
		options.set_headless()
		try:
			driver = webdriver.Firefox(firefox_options=options)
			driver.close()
		except:
			return_code = 1
	elif browser == 'google-chrome-stable':
		options = webdriver.ChromeOptions()
		options.set_headless()
		try:
			driver = webdriver.Chrome(chrome_options=options)
			driver.close()
		except:
			return_code = 1
	elif browser == 'msedge':
		try:
			driver = webdriver.Edge()
			driver.close()
		except:
			return_code = 1
	else:
		raise ValueError("Unsupported browser: "+browser)
	return return_code

def detect_browsers():
	global operating_system
	browser = ""
# Browsers are stored in order of developer preference.
# Firefox will always be superior by virtue of not being a shady botnet.
	supported_browsers = ["firefox", "google-chrome-stable", "msedge"]
	windows_exes = ["firefox.exe", "chrome.exe", "msedge.exe"]
# Webdrivers must be sorted to match the supported_browsers list.
	supported_drivers = ["geckodriver", "chromedriver", "msedgedriver"]
	detected_browsers = [0]*len(supported_browsers)
	detected_drivers = [0]*len(supported_drivers)
	webdriver_works = [0]*len(supported_drivers)
	counter = 0
	candidates = []
	if operating_system == 'win32' or operating_system == 'cygwin':
		import winreg
		while counter < len(supported_browsers):
			try:
				browser_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\"+windows_exes[counter],0,winreg.KEY_READ)
				browser_exe = winreg.QueryValue(browser_key,None)
				f = open(browser_exe)
				f.close()
			except:
				detected_browsers[counter] = 1
			try:
				f = open(supported_drivers[counter]+".exe")
				f.close()
			except:
				detected_drivers[counter] = 1
			webdriver_works[counter] = test_webdriver(supported_browsers[counter])
			if detected_drivers[counter] + detected_browsers[counter] + webdriver_works[counter] == 0:
				candidates.append(supported_browsers[counter])
			counter = counter+1
	else:
		while counter < len(supported_browsers):
			try:
				process = subprocess.check_output("command -v "+supported_browsers[counter]+" >/dev/null", shell=True)
			except subprocess.CalledProcessError as process_exit_code:
				detected_browsers[counter] = process_exit_code.returncode
			try:
				process = subprocess.check_output("command -v "+supported_drivers[counter]+" >/dev/null", shell=True)
			except subprocess.CalledProcessError as process_exit_code:
				detected_drivers[counter] = process_exit_code.returncode
			webdriver_works[counter] = test_webdriver(supported_browsers[counter])
			if detected_drivers[counter] + detected_browsers[counter] + webdriver_works[counter] == 0:
				candidates.append(supported_browsers[counter])
			counter = counter+1
	if len(candidates) == 0:
		raise ValueError("No supported browser found")
	return candidates
