#!/usr/bin/env python3
import sys
from selenium import webdriver
import traceback
import subprocess
import os
operating_system = sys.platform
nsa_botnet = ['win32', 'cygwin']
if operating_system in nsa_botnet:
	import winreg
if operating_system in nsa_botnet or operating_system == 'darwin':
	import re
	import difflib
	import requests
	import tarfile
	from zipfile import ZipFile
	import os
	from bs4 import BeautifulSoup
if operating_system == 'darwin':
	import platform
	import stat

class browser_type(object):
	def is_64bit(self) -> bool:
		return sys.maxsize > 2**32

	def __get_chrome_version(self):
		version = None
		if operating_system in nsa_botnet:
			browser_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\"+self.windows_exe,0,winreg.KEY_READ)
			exe_file = winreg.QueryValue(browser_key,None)
			chrome_install_dir = re.sub("chrome\.exe$", "", exe_file)
			for entity in os.listdir(chrome_install_dir):
				if re.match("^([0-9]*\.)*[0-9]*$", entity):
					version = entity
					break
		elif operating_system == 'darwin':
			magic_cmd = '/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version'
			response = subprocess.check_output(magic_cmd, shell=True).decode("UTF-8")
			version = re.sub("\ $\n", "", response)
			version = re.sub("^.*\ ", "", version)
		return version

	def __get_geckodriver_url(self):
		session = requests
		response = session.get('https://github.com/mozilla/geckodriver/releases/latest', allow_redirects=False)
		geckodriver_version = re.sub("^.*/v", "", response.headers['Location'])
		geckodriver_url = None
		if operating_system in nsa_botnet:
			winarch = 'win' + str(32 + 32 * int(self.is_64bit()))
			geckodriver_url = 'https://github.com/mozilla/geckodriver/releases/download/v' + geckodriver_version + '/geckodriver-v' + geckodriver_version + '-' + winarch + '.zip'
		elif operating_system == 'darwin':
			geckodriver_url = 'https://github.com/mozilla/geckodriver/releases/download/v' + geckodriver_version + '/geckodriver-v' + geckodriver_version + '-macos'
			if platform.machine() != 'x86_64':
				geckodriver_url += '-aarch64'
			geckodriver_url += '.tar.gz'
		return geckodriver_url

	def __curate_xhr_chromedriver_list(self, soup):
		versions = []
		for item in soup.findAll('prefix'):
			processed_item = re.sub('/$', '', item.text)
			if re.match("^([0-9]*\.)*[0-9]*$", processed_item) and processed_item != '':
				versions.append(processed_item)
		return versions

	def __get_chromedriver_version(self, chrome_version):
		session = requests
		good_fit = None
		response = session.get('https://chromedriver.storage.googleapis.com/?delimiter=/&prefix=')
		soup = BeautifulSoup(response.text, "html.parser")
		available_chromedriver_versions = self.__curate_xhr_chromedriver_list(soup)
		matching_versions = difflib.get_close_matches(chrome_version, available_chromedriver_versions)
		if len(matching_versions) != 0:
			possible_match_atoms = matching_versions[0].split('.')
			chrome_version_atoms = chrome_version.split('.')
			if possible_match_atoms[0] == chrome_version_atoms[0] and possible_match_atoms[1] == chrome_version_atoms[1]:
				good_fit = matching_versions[0]
		return good_fit

	def __get_chromedriver_url(self):
		chrome_version = self.__get_chrome_version()
		chromedriver_version = self.__get_chromedriver_version(chrome_version)
		result = 'https://chromedriver.storage.googleapis.com/' + chromedriver_version
		if operating_system == 'darwin':
			result += '/chromedriver_mac64'
			if platform.machine() != 'x86_64':
				result += '_m1'
		elif operating_system in nsa_botnet:
			result += '/chromedriver_win32'
		result += '.zip'
		return result

	def __download_webdriver(self, url):
		myfile = requests.get(url)
		filename = url.split('/')[-1]
		open(filename, 'wb').write(myfile.content)

	def __unpack_webdriver(self, filename):
		file_we_want = None
		if operating_system in nsa_botnet:
			file_we_want = self.windows_webdriver
		elif operating_system == 'darwin':
			file_we_want = self.webdriver
		if filename.split('.')[-1] == 'zip':
			with ZipFile(filename, 'r') as zipObj:
				zipObj.extractall(path='.', members=[file_we_want])
			if operating_system == 'darwin':
				st = os.stat(file_we_want)
				os.chmod(file_we_want, st.st_mode | stat.S_IEXEC)
		else:
			my_tar = tarfile.open(filename)
			my_tar.extract(file_we_want,'.')
			my_tar.close()

	def __supplement_missing_webdrivers_on_compromised_systems(self):
		webdriver_url = None
		if self.name == 'Mozilla Firefox':
			webdriver_url = self.__get_geckodriver_url()
		elif self.name == 'Google Chrome':
			webdriver_url = self.__get_chromedriver_url()
		self.__download_webdriver(webdriver_url)
		filename = webdriver_url.split('/')[-1]
		self.__unpack_webdriver(filename)
		os.remove(filename)
		self.tried_supplementing = True

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
				self.__supplement_missing_webdrivers_on_compromised_systems()
			else:
				print('Supplementing failed')
				self.errors += 2
		except FileNotFoundError:
			if self.tried_supplementing == False:
				print('Supplementing missing webdriver for: ' + self.name)
				self.__supplement_missing_webdrivers_on_compromised_systems()
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
