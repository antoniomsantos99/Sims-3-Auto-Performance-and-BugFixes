# Sims 3 Auto Performance and BugFixes (Name not final)

# ⚠️ - This software is still in development! Expect crashes and while the program tries to backup important files currently a manual backup is advised.

Ever get the itch to play The Sims 3, but the hassle of tweaking settings and installing mods just put you off? Same here! Instead of spending 20 minutes doing it manually, I ended up spending a week automating it. So, now you can keep your game running smoothly by 2024 standards with hardly any effort!

This software currently executes the steps defined in the following [guide](https://steamcommunity.com/sharedfiles/filedetails/?id=1131162350) (thanks to [Anime_Boom](https://steamcommunity.com/profiles/76561198115872149)).

## Features
* Auto detection of the game's user files
* Automatic detection of installed expansions
* Smart selection of options given the installed expansions and current configuration.
* All available options are selectable to ensure a more personalized experience - Change only what you want to

## Roadmap
I do not consider the current version as finished and still plan to do the following things:
- [ ] Refactor Code
- [x] Automatically detect game files location if possible
- [ ] Release a self-contained executable
- [ ] Add support for multiple languages (maybe?)
- [x] Add support for EA App version (Need tester)
- [ ] Add support for MacOS and Linux (Need testers)

## How to run? (In development)
Currently as there are no compiled binaries (exe) for this software (which is also not optimal since its a python project). You will have to install Python and its dependencies manually, however it is a straightforward process.

Python 3.6 or newer is required and currently this software is only available on windows.

* Install [Python](https://www.python.org/ftp/python/3.13.0/python-3.13.0-amd64.exe)
* Install dependencies by running the following command: `pip install -r requirements.txt`
* Run GUI.py: `python GUI.py`

## Project status
This project is currently in:

**Development mode - My main focus is to develop new features.**

~~Maintenance mode - My main focus is to refactor the code and fix bugs.~~


## Contribute
Looking to contribute? Currently there are not many rules!

* If looking to contribute in the development just create a pull request and i'll review it.
* If you found a bug then create an issue with the steps to reproduce it and i'll try to squash it away!

## Credits (In development)
This program would not be possible without the work of the following people:
### Information

<div align="center">
<img src="https://images.weserv.nl/?url=https://avatars.fastly.steamstatic.com/1834c2e80adbf31db81bda76d958c1d7438d8f40_full.jpg?v=4&h=100&w=100&fit=cover&mask=circle&maxage=7d"/>
Anime_Boom : Author of the guide used in this program.
</div>

### Mod developers
