[![Support me](https://iacoposk8.github.io/img/buymepizza.png)](https://buymeacoffee.com/iacoposk8)

# Scraper Interface
A library to use Selenium even more easily with the addition of functions to generate xml files and upload them online via ftp

## Installation

    git clone https://github.com/iacoposk8/Scraper-Interface
    cd Scraper-Interface
    pip install requirements.txt

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

to use all other native Selenium commands

    scraper.driver.xxxxxxxx

## Constructor

|Parameter|Description|Type|Default value
|--|--|--|--|
|headless|If set to True the script will work without showing any graphical interface||True
|crypt_method|use undetected_chromedriver||False
|verbose|Verbose log||True
|webView|It makes it possible to view the browser even in headless mode via a web interface (to be improved)||False
|mobile|Enable the mobileEmulation||False
|tor|If set to True navigate through the Tor proxy||False
|proxy|Use a proxy in the following format: http://xxx.xxx.xxx:xxxx||False
|window_size|Sets the size of the browser window||"1280x1024"
|user_agent|Set the user agent||False
|cookie_storage|Choose a path to save the cookies||False
|download_dir|Choose a path to donload files||False
|log_in_class_folder|By default the logs are saved in the folder of the script that calls the class. If set to True the logs will be in the folder of the Scraper() class||False
## get_emails
This method allows you to scrap through your emails and not a normal web page
|Parameter|Description|Type|Default value
|--|--|--|--|
|username|Username to access the email account||
|password|Password to access the email account||
|imap_server|Name of the Imap Server to access the email account||
|filter_emails|Filter the emails you want to access, example: {'"seen": False, "from": "info@domain.com"||
|box|Name of the box to access||"INBOX"
## Regex
This method allows you to search for substrings via Regular expression and return them in a list
|Parameter|Description|Type|Default value
|--|--|--|--|
|test_str|String where to search||
|regex|Regular expression||
## get_download
Return a list with the list of downloads in progress
|Parameter|Description|Type|Default value
|--|--|--|--|
|wait|Downloads don't start immediately. Wait N seconds before seeing how many downloads are in progress||5
## screenshot
Take a screenshot
|Parameter|Description|Type|Default value
|--|--|--|--|
|filename|Path of the image to save||
## get_shadowRoot
Gets the ShadowRoot of an element
|Parameter|Description|Type|Default value
|--|--|--|--|
|elem|Dom element where to look for the ShadowRoot||
## page_source
Show the source code of the page

## renew_connection
If you use Tor with this method you can change ip address
|Parameter|Description|Type|Default value
|--|--|--|--|
|reload_browser|If set to True it will close the browser and open a new one||False
## wait_find
Gets a web page element
|Parameter|Description|Type|Default value
|--|--|--|--|
|locator|Css or xpath selector to locate the item||
|element|If set to False, the entire document will be searched. Otherwise it will search within the element passed in this parameter||False
|by_type|css or xpath||"css"
|log|If set to True and an error will occur an .html snapshot will be created in the log folder||True
|wait|With javascript the html page changes dynamically, making an element not accessible at that moment. This method will wait N seconds for the selected element to appear, after which it will generate an error||10
## close
Close the browser

## get
Navigate to a Url
|Parameter|Description|Type|Default value
|--|--|--|--|
|url|URL to reach||
|reffer|Change the referer (the url from which you are landing on the requested page)||False
## focus_last_tab
Displays the last opened tab

## new_tab
Open a new tab

## close_tab
Close current tab

## scroll_to_bottom
Scroll the page to the bottom
|Parameter|Description|Type|Default value
|--|--|--|--|
|times|Number of times you want to repeat the scroll||1
|wait|Waiting time between scrolls||1
## get_image_from_google
Search images from Google images
|Parameter|Description|Type|Default value
|--|--|--|--|
|query|Keywords to search||
|size|s for small, m formedium and l for large||"m"
## download_image_from_url
Download an image from url
|Parameter|Description|Type|Default value
|--|--|--|--|
|url|Url for download||
|file_name|Path to save the image||""
|b64|If set to True it will return a base64 string||False
## download_file
Download a file from a url
|Parameter|Description|Type|Default value
|--|--|--|--|
|url|Url for download||
|reffer|Download the file with a referer. Some sites do not allow you to download the file knowing the url, but only if the referer is the site that contains the file||False
## xml_generator
Description tag of the xml file
|Parameter|Description|Type|Default value
|--|--|--|--|
|filename|File name||
|title|Title tag of the xml file||
|link|Link tag of the xml file||
|description|Description tag of the xml file||
|items|List of dicts where each dict has the following keys: link, guid, title, description||
## ftp_upload
Upload a file via ftp
|Parameter|Description|Type|Default value
|--|--|--|--|
|server|Ftp server name||
|username|Ftp username||
|password|Ftp password||
|localfile|Local file path||
|remotefile|Remove file path||
## lang_detect
Identifies the language of a text
|Parameter|Description|Type|Default value
|--|--|--|--|
|txt|Text to parse||
## translate
Translates text from one language to another
|Parameter|Description|Type|Default value
|--|--|--|--|
|txt|Text to translate||
|src|Text language. Allowed value: auto||
|dest|Language into which you want to translate the text||
|xml|Set to True if you want to encode the response so it can be used inside the xml||False
