#!/usr/bin/env python3
import sys
import os
import tarfile
from zipfile import ZipFile
from bs4 import BeautifulSoup
import re
import difflib
import requests
operating_system = sys.platform
if operating_system == 'darwin':
	import subprocess
	import platform
	import stat
else:
	import winreg

class supplement_webdriver(object):
	def __init__(self, browser_type):
		self.__nsa_botnet = ['win32', 'cygwin']
		global operating_system
		self.__operating_system = operating_system
		self.__webdriver_exe = browser_type.windows_webdriver if self.__operating_system in self.__nsa_botnet else browser_type.webdriver
		self.__browser_exe = browser_type.windows_exe if self.__operating_system in self.__nsa_botnet else browser_type.exe
		self.__browser_name = browser_type.name

	def download(self):
		self.__supplement_missing_webdrivers_on_compromised_systems()
		return True

	def __is_64bit(self) -> bool:
		return sys.maxsize > 2**32

	def __get_chrome_version(self):
		version = None
		if self.__operating_system in self.__nsa_botnet:
			browser_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\"+self.__browser_exe,0,winreg.KEY_READ)
			exe_file = winreg.QueryValue(browser_key,None)
			chrome_install_dir = re.sub("chrome\.exe$", "", exe_file)
			for entity in os.listdir(chrome_install_dir):
				if re.match("^([0-9]*\.)*[0-9]*$", entity):
					version = entity
					break
		elif self.__operating_system == 'darwin':
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
		if self.__operating_system in self.__nsa_botnet:
			winarch = 'win' + str(32 + 32 * int(self.__is_64bit()))
			geckodriver_url = 'https://github.com/mozilla/geckodriver/releases/download/v' + geckodriver_version + '/geckodriver-v' + geckodriver_version + '-' + winarch + '.zip'
		elif self.__operating_system == 'darwin':
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
		if self.__operating_system == 'darwin':
			result += '/chromedriver_mac64'
			if platform.machine() != 'x86_64':
				result += '_m1'
		elif self.__operating_system in self.__nsa_botnet:
			result += '/chromedriver_win32'
		result += '.zip'
		return result

	def __download_webdriver(self, url):
		myfile = requests.get(url)
		filename = url.split('/')[-1]
		open(filename, 'wb').write(myfile.content)

	def __unpack_webdriver(self, filename):
		if filename.split('.')[-1] == 'zip':
			with ZipFile(filename, 'r') as zipObj:
				zipObj.extractall(path='.', members=[self.__webdriver_exe])
			if self.__operating_system == 'darwin':
				st = os.stat(self.__webdriver_exe)
				os.chmod(self.__webdriver_exe, st.st_mode | stat.S_IEXEC)
		else:
			my_tar = tarfile.open(filename)
			my_tar.extract(self.__webdriver_exe,'.')
			my_tar.close()

	def __supplement_missing_webdrivers_on_compromised_systems(self):
		webdriver_url = None
		if self.__browser_name == 'Mozilla Firefox':
			webdriver_url = self.__get_geckodriver_url()
		elif self.__browser_name == 'Google Chrome':
			webdriver_url = self.__get_chromedriver_url()
		self.__download_webdriver(webdriver_url)
		filename = webdriver_url.split('/')[-1]
		self.__unpack_webdriver(filename)
		os.remove(filename)
		self.tried_supplementing = True
