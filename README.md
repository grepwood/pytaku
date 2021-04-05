# Pytaku

Pytaku is for the moment an interactive command-line program that enables the user to retrieve direct links to anime episodes from places like Shinden.

# Purpose

The purpose of this software is to enable watching anime in groups on services that can stream from direct links to multiple users simultaneously, for example WatchTogether (w2g.tv).
It can also enable to user to download said anime episodes for offline watching, but that is an unavoidable side-effect of retrieving the links.

# How to use

For now, the program can only run from the terminal. Sorry. If you intend to run this program, please always make sure that you run it from your favorite terminal or from cmd.exe or PowerShell if you're feeling fancy. I'm considering PyQt for this project.

On anything but Windows:
1. Install your favorite web browser. As long as it's Firefox or Chrome, it should work. I'm working on other browsers as well.
2. Install your browser's webdriver. If your browser does not have a webdriver, go back to step 1 and pick another favorite browser.
3. Install Python 3, preferably 3.8.
4. Install dependencies. Either from your package manager or pip or both. I'm pretty sure everything except mega.py is packaged in most distros. If you insist on using a package manager, you can help yourself by listing requirements.txt and looking if your distro packages those.
5. Run pytaku.py. It should always communicate your choices to you via terminal. You just pick the numbers with your keyboard. It is also to safely quit the program at any time it asks for input by pressing 0.

On Windows:
1. See 'On anything but Windows'.
2. Since webdrivers are not packaged into installers on Windows, you will have to pick a webdriver compatible with your browser and download it where you downloaded pytaku. This could be improved either by webdriver devs actually making installers, or by me doing an evil workaround that downloads one for you.
3. See 'On anything but Windows'.
4. Install dependencies. You are doomed to use pip unfortunately, but there's a nice requirements.txt file to make it less painful for you. Try the following command:
`pip install -r requirements.txt`
5. See 'On anything but Windows'.

On Mac:
1. Give me SSH access to a Mac and we'll see what I can do. To be honest I haven't tested it there cause I don't have one.

This program was developed on Gentoo Linux on Python 3.8 but it should work with other setups just as well. If something doesn't work, let me know in the issues so I can actually track them.
