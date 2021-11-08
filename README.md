# Pytaku

Pytaku is for the moment an interactive command-line program that enables the user to retrieve direct links to anime episodes from places like Shinden.

# Purpose

The purpose of this software is to enable watching anime in groups on services that can stream from direct links to multiple users simultaneously, for example WatchTogether (w2g.tv).
It can also enable to user to download said anime episodes for offline watching, but that is an unavoidable side-effect of retrieving the links.

# How to use

For now, the program can only run from the terminal. Sorry. If you intend to run this program, please always make sure that you run it from your favorite terminal or from cmd.exe or PowerShell if you're feeling fancy. I'm considering PyQt for this project.

On anything but Windows:
1. Install a supported browser.
2. Install its webdriver.
3. Install packages that provide modules listed in requirements.txt. Some of them might not be available through the package manager, so once you've done your best, do `python3 -m pip install --user -r requirements.txt`
4. `./pytaku.py`

On Windows:
1. Install Gentoo. Shinden took care of not supporting your OS. Sorry, I tried to prevent this.
2. If you cannot install Gentoo, consider Windows Subsystem For Linux.

On MacOS:
1. Install a supported browser.
2. `python3 -m pip install --user -r requirements.txt`
3. `./pytaku.py`

Supported browsers:
- Mozilla Firefox
- Google Chrome

This program was developed on Gentoo Linux and MacOS Big Sur on Python 3.9 but it should work with other setups just as well. If something doesn't work, let me know in the issues so I can actually track them. Windows support is off limits until it supports Xvfb.
