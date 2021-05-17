#!/usr/bin/env python3
import sys
from selenium import webdriver
import traceback
import subprocess
operating_system = sys.platform
nsa_botnet = ['win32', 'cygwin']
if operating_system in nsa_botnet:
	import winreg
if operating_system in nsa_botnet or operating_system == 'darwin':
	from browser.supplement_webdriver import supplement_webdriver

class browser_type(object):
	def __init__(self, name, exe, windows_exe, macos_name, webdriver, windows_webdriver):
		self.name = name
		self.exe = exe
		self.windows_exe = windows_exe
		self.macos_name = macos_name
		self.webdriver = webdriver
		self.windows_webdriver = windows_webdriver
		self.errors = 0
		self.tried_supplementing = False

	def test_browser_exe(self):
		global operating_system
		global nsa_botnet
		try:
			if operating_system in nsa_botnet:
				browser_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\"+self.windows_exe,0,winreg.KEY_READ)
				exe_file = winreg.QueryValue(browser_key,None)
				f = open(exe_file)
				f.close()
			elif operating_system == 'darwin':
				process = subprocess.check_output("osascript -e 'id of application " + '"' +self.macos_name + '"' + "' >/dev/null", shell=True)
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
				command = "command -v "+self.webdriver+" >/dev/null"
				if operating_system == 'darwin':
					command = "command -v ./"+self.webdriver+" >/dev/null"
				process = subprocess.check_output(command, shell=True)
			print('Detected webdriver: '+self.name)
		except subprocess.CalledProcessError:
			if self.tried_supplementing == False:
				print('Supplementing missing webdriver for: ' + self.name)
				self.tried_supplementing = supplement_webdriver(self).download()
			else:
				print('Supplementing failed')
				self.errors += 2
		except FileNotFoundError:
			if self.tried_supplementing == False:
				print('Supplementing missing webdriver for: ' + self.name)
				self.tried_supplementing = supplement_webdriver(self).download()
			else:
				print('Supplementing failed')
				self.errors += 2
		except:
			traceback.print_exc()
			if operating_system in nsa_botnet:
				print('Could not detect webdriver: '+self.windows_webdriver)
			else:
				print('Could not detect webdriver: '+self.webdriver)
			print('If '+self.name+' is the browser you want to use, then:')
			print("\tWindows: download that exe and store it with the program")
			print("\tMacOS: download geckodriver and store it with the program")
			print("\tOthers: use your package manager")
			self.errors += 2
	
	def test_webdriver(self):
		global operating_system	
		if self.name == 'Mozilla Firefox':
			options = webdriver.FirefoxOptions()
			options.headless = True
			try:
				if operating_system == 'darwin':
					driver = webdriver.Firefox(firefox_options=options, executable_path='./geckodriver')
				else:
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
				if operating_system == 'darwin':
					driver = webdriver.Chrome(chrome_options=options, executable_path='./chromedriver')
				else:
					driver = webdriver.Chrome(chrome_options=options)
				driver.quit()
				print('Successful test of webdriver for '+self.name)
			except:
				print('Unable to start webdriver for '+self.name)
				self.errors += 4
#		elif self.name == 'Apple Safari':
#			options = webdriver.SafariOptions()
#			options.headless = True
#			try:
#				driver = webdriver.Safari(safari_options=options)
#				driver.quit()
#			except:
#				traceback.print_exc()
#				print('Unable to start webdriver for '+self.name)
#				self.errors += 4
#		elif self.name == 'Microsoft Edge':
#			options = webdriver.EdgeOptions()
#			options.headless = True
#			try:
#				if operating_system == 'darwin':
#					driver = webdriver.Edge(edge_options=options, executable_path='./msedgedriver')
#				else:
#					driver = webdriver.Edge(edge_options=options)
#				driver.quit()
#				print('Successful test of webdriver for '+self.name)
#			except:
#				print('Unable to start webdriver for '+self.name)
#				self.errors += 4
		else:
			raise ValueError("Unsupported browser: "+self.name)

def detect_browsers(fast_mode=True):
	global operating_system
	browser = ""
# Browsers are stored in order of developer preference.
# Firefox will always be superior by virtue of not being a shady botnet.
# However on MacOS, we will try to give Safari a chance since it comes pre-installed.
	supported_browsers = []
#	if operating_system == 'darwin':
#		supported_browsers.append(browser_type('Apple Safari', 'safari', '', 'Safari' 'safaridriver', ''))
	supported_browsers.append(browser_type('Mozilla Firefox', 'firefox', 'firefox.exe', 'Firefox', 'geckodriver', 'geckodriver.exe'))
	supported_browsers.append(browser_type('Google Chrome', 'google-chrome-stable', 'chrome.exe', 'Google Chrome', 'chromedriver', 'chromedriver.exe'))
#	supported_browsers.append(browser_type('Microsoft Edge', 'msedge', 'msedge.exe', 'Microsoft Edge', 'msedgedriver', 'msedgedriver.exe'))
	counter = 0
	candidates = []
	while counter < len(supported_browsers):
		supported_browsers[counter].test_browser_exe()
		supported_browsers[counter].test_webdriver_exe()
		supported_browsers[counter].test_webdriver()
		if supported_browsers[counter].errors == 0:
			candidates.append(supported_browsers[counter].exe)
			if fast_mode == True:
				break
		counter += 1
	if len(candidates) == 0:
		raise ValueError("No supported browser found")
	return candidates
