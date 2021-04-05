#!/usr/bin/env python3
import sys
from selenium import webdriver
operating_system = sys.platform
nsa_botnet = ['win32', 'cygwin']
if operating_system in nsa_botnet:
	import winreg
else:
	import subprocess

class browser_type(object):
	def __init__(self, name, exe, windows_exe, webdriver, windows_webdriver):
		self.name = name
		self.exe = exe
		self.windows_exe = windows_exe
		self.webdriver = webdriver
		self.windows_webdriver = windows_webdriver
		self.errors = 0

	def test_browser_exe(self):
		global operating_system
		global nsa_botnet
		try:
			if operating_system in nsa_botnet:
				browser_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\"+self.windows_exe,0,winreg.KEY_READ)
				exe_file = winreg.QueryValue(browser_key,None)
				f = open(browser_exe)
				f.close()
			else:
				process = subprocess.check_output("command -v "+self.exe+" >/dev/null", shell=True)
			print('Detected browser: '+self.name)
		except:
			print('Could not detect: '+self.name)
			self.errors += 1
	
	def test_webdriver_exe(self):
		global operating_system
		global nsa_botnet
		try:
			if operating_system in nsa_botnet:
				f = open(self.windows_webdriver)
				f.close()
			else:
				process = subprocess.check_output("command -v "+self.webdriver+" >/dev/null", shell=True)
			print('Detected webdriver: '+self.name)
		except:
			print('Could not detect webdriver: '+self.windows_webdriver)
			print('If '+self.name+' is the browser you want to use, then:')
			print("\tWindows: download that exe and store it with the program")
			print("\tOthers: use your package manager")
			self.errors += 2
	
	def test_webdriver(self):
		if self.name == 'Mozilla Firefox':
			options = webdriver.FirefoxOptions()
			options.headless = True
			try:
				driver = webdriver.Firefox(firefox_options=options)
				driver.quit()
				print('Successful test of webdriver for '+self.name)
			except:
				print('Unable to start webdriver for '+self.name)
				self.errors += 4
		elif self.name == 'Google Chrome':
			options = webdriver.ChromeOptions()
			options.headless = True
			try:
				driver = webdriver.Chrome(chrome_options=options)
				driver.quit()
				print('Successful test of webdriver for '+self.name)
			except:
				print('Unable to start webdriver for '+self.name)
				self.errors += 4
		elif self.name == 'Microsoft Edge':
			try:
				driver = webdriver.Edge()
				driver.quit()
				print('Successful test of webdriver for '+self.name)
			except:
				print('Unable to start webdriver for '+self.name)
				self.errors += 4
		else:
			raise ValueError("Unsupported browser: "+self.name)

def detect_browsers():
	global operating_system
	browser = ""
# Browsers are stored in order of developer preference.
# Firefox will always be superior by virtue of not being a shady botnet.
	supported_browsers = []
	supported_browsers.append(browser_type('Mozilla Firefox', 'firefox', 'firefox.exe', 'geckodriver', 'geckodriver.exe'))
	supported_browsers.append(browser_type('Google Chrome', 'google-chrome-stable', 'chrome.exe', 'chromedriver', 'chromedriver.exe'))
	supported_browsers.append(browser_type('Microsoft Edge', 'msedge', 'msedge.exe', 'msedgedriver', 'msedgedriver.exe'))
	counter = 0
	candidates = []
	while counter < len(supported_browsers):
		supported_browsers[counter].test_browser_exe()
		supported_browsers[counter].test_webdriver_exe()
		supported_browsers[counter].test_webdriver()
		if supported_browsers[counter].errors == 0:
			candidates.append(supported_browsers[counter].exe)
		counter += 1
	if len(candidates) == 0:
		raise ValueError("No supported browser found")
	return candidates
