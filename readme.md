# remarkableAutomation
This repo contains a script I run daily to do 'stuff' with my remarkable. Currently this just runs on a Raspberry Pi, which works well.

Currently it does the following things on workdays:
  1. Download the [newspaper](https://www.nrc.nl/)
  2. Upload it to the ReMarkable Cloud
  3. Make a new subfolder with the date as name to my labjournal folder.

Step 3 is skipped in the weekend. On Sundays, there is no newspaper, and thus no download.

## Components
Currently the following components are in the repo:
  * `nrc.py`: for dealing with downloading an doing stuff with the newspaper.
  * `remarkable.py`: abstraction layer between me and rmapy with various basic cloud operations.
  * `messaging`: sending messages via Telegram if something goes wrong or something.
  * `rm_daily_run.py`: thing that runs everyday.

## Using this
By making a `options.json` file, you can run this code as you like, with your own settings. Also see `options.json.example`.

## Requirements
  * [`rmapy`](https://github.com/subutux/rmapy/): for ReMarakable cloud connection
  * `PyPDF4`: for newspaper handling
  * For downloading the newspaper
    * with `pip3`: [`selenium`](https://selenium-python.readthedocs.io/) & `pyvirtualdisplay`
    * with `apt`: `chromium`, `chromium-chromedriver` & `xvfb`
    
## Goals for the future
  * Initialize empty notes file every day (currently not working because of rmapy (I suspect)).
  * Think of some other cool ideas.
