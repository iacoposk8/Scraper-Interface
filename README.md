# Scraper Interface
A library to use Selenium even more easily with the addition of functions to generate xml files and upload them online via ftp

## Installation

    git clone https://github.com/iacoposk8/Scraper-Interface
Download chromedriver via  
[https://chromedriver.chromium.org/downloads](https://chromedriver.chromium.org/downloads)
and put it in the folder "Scraper-Interface"
and some `pip install` for dependencies

## Quick start
Import class from a different path

    import sys
    sys.path.insert(1, '/absolute_path/Scraper-Interface')
    from scraper import Scraper
    scraper = Scraper(headless = False)
Get a page

    scraper.get("https://github.com")

Get elements from css selector

    elements = scraper.wait_find("a")

Each elements and get proprieties

    for element in elements:
    	print(element.get_attribute("href"))
    	print(element.text)

## Methods

| Method | Params | Description |
|--|--|--|
| init | `headless`, `each_log` | Initialize the class. `headless` by default is True and hides the chrome interface. `each_log` by default is False and keeps only one log per page |
| close | | close the browser |
| ftp_upload | `server`, `username`, `password`, `localfile`, `remotefile` | Upload a file via ftp |
| get | `url` | open the `url` in the browser |
| scroll_to_bottom | `times`, `wait` | scroll the bottom of the page X `times` and, `wait` for X seconds each time |
| translate | `txt`, `src`, `dest`, `xml` | return a translated string. translate a `txt` from the `src` language to the `dest` language. You can set `xml` value (default is False) to True for the right escape if you want use it in a xml file  |
| wait_find | `locator`, `element` | wait 10 seconds or until the css element `locator` appears and return a Selenium element. `element` default value is False and will search the whole html page. If `element` (obtained from a previous wait_find) is passed, the search will be done only inside this `element` |
| xml_generator | filename, title, link, description, items |  |

to use all other native Selenium commands

    scraper.driver.xxxxxxxx

