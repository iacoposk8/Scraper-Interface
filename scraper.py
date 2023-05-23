import os, time, urllib.parse, ftplib, html, re, sys, platform 
import traceback
from datetime import datetime
from lxml import etree
from xml.sax import saxutils
import random
from tqdm import tqdm

import imaplib
import email
import socks
import quopri

from langdetect import detect
from googletrans import Translator
translator = Translator()

#get content
import validators
import base64
import requests
from stem import Signal
from stem.control import Controller
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from xml.sax.saxutils import escape as xml_escape

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains

from selenium_stealth import stealth

#from webdriver_manager.firefox import GeckoDriverManager
#from selenium.webdriver.chrome.service import Service as ChromiumService
from webdriver_manager.chrome import ChromeDriverManager
try:
	from webdriver_manager.core.utils import ChromeType
except:
	pass

#from selenium.webdriver.firefox.options import Options as FirefoxOptions
#from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

from pyvirtualdisplay import Display
#import undetected_chromedriver as uc

#DOC: https://seleniumbase.io/help_docs/customizing_test_runs/#pytest-options-for-seleniumbase
from seleniumbase import Driver
#from seleniumbase import page_actions

import re
from threading import Thread
#import inspect

'''
requirements:{
	"selenium.webdriver.common.by": "None",
	"selenium.webdriver.support.ui": "None",
	"selenium.webdriver.support": "None",
	"selenium.webdriver.chrome.options": "None",
	"selenium.webdriver.common.desired_capabilities": "None",
	"selenium.webdriver.common.action_chains": "None"
}
'''

class FtpUploadTracker:
	sizeWritten = 0
	totalSize = 0
	lastShownPercent = 0
	
	'''
	__init__:{
		"ignore_method": 1
	}
	'''
	def __init__(self, totalSize):
		self.totalSize = totalSize
		self.pbar = tqdm(total=100)
	
	'''
	handle:{
		"ignore_method": 1
	}
	'''
	def handle(self, block):
		self.sizeWritten += 1024
		percentComplete = round((self.sizeWritten / self.totalSize) * 100)
		
		'''if (self.lastShownPercent == percentComplete):
			print("close")
			self.pbar.close()'''
		if (self.lastShownPercent != percentComplete):
			self.lastShownPercent = percentComplete
			#print(str(percentComplete) + " percent complete")
			self.pbar.n = percentComplete
			self.pbar.update()

class Scraper():
	'''
	__init__:{
		"headless": "If set to True the script will work without showing any graphical interface",
		"crypt_method": "use undetected_chromedriver",
		"verbose": "Verbose log",
		"webView": "It makes it possible to view the browser even in headless mode via a web interface (to be improved)",
		"mobile": "Enable the mobileEmulation", 
		"tor": "If set to True navigate through the Tor proxy", 
		"proxy": "Use a proxy in the following format: http://xxx.xxx.xxx:xxxx",
		"window_size": "Sets the size of the browser window",
		"user_agent": "Set the user agent", 
		"cookie_storage": "Choose a path to save the cookies", 
		"download_dir": "Choose a path to donload files",
		"log_in_class_folder": "By default the logs are saved in the folder of the script that calls the class. If set to True the logs will be in the folder of the Scraper() class"
	}
	'''
	def __init__(self, headless = True, crypt_method = False, verbose = True, webView = False, mobile = False, tor = False, proxy = False, window_size = "1280x1024", user_agent = False, cookie_storage = False, download_dir = False, log_in_class_folder = False):
		if log_in_class_folder:
			self.current_dir = os.path.dirname(os.path.realpath(__file__))
		else:
			self.current_dir = "./"

		self.webView = webView
		self.verbose = verbose
		self.crypt_method = crypt_method
		self.window_size = window_size
		self.headless = headless
		self.userdatadir = cookie_storage
		self.tor = tor
		self.opt = []

		self.browser_options = Options()

		if self.headless:
			#self.browser_options.add_argument("--headless") 
			self.opt.append("--headless=new")

		if self.window_size != False:
			self.opt.append('window-size=' + self.window_size)

		if user_agent != False:
			self.opt.append("user-agent=" + user_agent) #"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36"
		
		#risolveil problema DevToolsActivePort file doesn't exist
		self.opt.append('--no-sandbox')
		self.opt.append('--disable-dev-shm-usage')
		#La seguente riga è necessaria e serve per far utilizzare allo script un browser ad una certa porta
		#Se la porta è uguale, tutti gli script utilizzeranno lo stesso browser andandosi a intralciare a vicenda
		self.opt.append("--remote-debugging-port=" + str(random.randint(9000, 9999)))

		self.opt.append("--disable-web-security")
		self.opt.append("--allow-running-insecure-content")

		#fix problem from timeout: Timed out receiving message from renderer: 600.000 impor...
		self.opt.append("enable-automation")
		self.opt.append("--disable-extensions")
		self.opt.append("--dns-prefetch-disable")
		self.opt.append("--disable-gpu")

		if mobile:
			mobile_emulation = {
				"deviceMetrics": { "width": 375, "height": 812, "pixelRatio": 3.0 },
				"userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19"
			}
			self.browser_options.add_experimental_option("mobileEmulation", mobile_emulation)

		#permette di fare login sui servizi google
		self.browser_options.add_experimental_option("excludeSwitches", ["enable-automation"])
		self.browser_options.add_experimental_option('useAutomationExtension', False)
		self.opt.append('--disable-blink-features=AutomationControlled')

		#self.browser_options.add_experimental_option("debuggerAddress","localhost:8797")

		if not download_dir:
			download_dir = self.current_dir
		if os.name == 'nt':
			download_dir = download_dir.replace('/','\\')
		self.download_dir = download_dir

		prefs = {
			"profile.default_content_settings.popups": 0, 
			"download.default_directory": r"" + self.download_dir, 
			"directory_upgrade": True,
			"plugins.always_open_pdf_externally": True
		}
		self.browser_options.add_experimental_option("prefs", prefs)

		self.proxy = False
		if self.tor:
			self.proxy = "socks5://localhost:9050"
		if proxy:
			self.proxy = proxy

		if self.userdatadir:
			self.opt.append('--profile-directory=Default')
			self.opt.append("--user-data-dir=" + self.userdatadir)

		for o in self.opt:
			self.browser_options.add_argument(o)

		self.__get_driver(3)

		#self.driver.set_page_load_timeout(30)

		self.tor_controller = False
		try:
			self.tor_controller = Controller.from_port(port=9051)
		except:
			pass

		if webView:
			from subprocess import Popen
			self.webprocess = Popen(('python start.py').split(" "), cwd = os.path.dirname(os.path.realpath(__file__)) + '/WebView') # something long running

			t1 = Thread(target=self.__task_web_view)
			t1.start()
			#t1.join()

	def __task_web_view(self):
		while True:
			f = open(os.path.dirname(os.path.realpath(__file__)) + "/WebView/todo.txt", "r")
			cmd = f.read()
			if cmd.strip() != "":
				if self.verbose:
					print(cmd)
				cmd = cmd.split(" ")
				f.close()
				if cmd[0] == "click":
					ed = ActionChains(self.driver)
					#ed.move_by_offset(0,0).click().perform()
					'''try:
						ed.move_to_element_with_offset(self.driver.find_element(By.TAG_NAME, 'body'), int(cmd[1]), int(cmd[2])).click().perform()
					except:
						#ed.move_by_offset(int(cmd[1]), int(cmd[2])).click().perform()'''
					element = self.driver.execute_script("""
						return document.elementFromPoint(arguments[0], arguments[1]);
					""", int(cmd[1]), int(cmd[2]))
					try:
						element.click()
					except Exception as e:
						print(e)
				if cmd[0] == "keys":
					try:
						for el in self.wait_find("*:focus"):
							el.send_keys(cmd[1])
					except:
						pass
				if cmd[0] == "refresh":
					if self.verbose:
						print("refresh")

				self.__log()

				f = open(os.path.dirname(os.path.realpath(__file__)) + "/WebView/todo.txt", "w")
				f.write("")
				f.close()

			time.sleep(1)

	def __get_driver(self, try_again):
		ext = ""
		if os.name == 'nt':
			ext = ".exe"

		#try:
		#file_driver = current_dir+"/chromedriver_" + re.sub('[^A-Za-z0-9]+', '', platform.uname().node) + ext
		
		#risolve problemi from timeout: Timed out receiving message from renderer: 600.000
		caps = DesiredCapabilities().CHROME
		caps["pageLoadStrategy"] = "normal"  #  complete
		#caps["pageLoadStrategy"] = "eager"  #  interactive
		#caps["pageLoadStrategy"] = "none"

		if self.crypt_method != "uc":
			try:
				file_driver = ChromeDriverManager().install()
			except:
				file_driver = ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()

			self.__obfuscate(file_driver)

		'''self.browser_options.binary_location = file_driver.replace(file_driver.split("/")[-1] + "/","")
		print(self.browser_options.binary_location)
		print("********************") executable_path = '''
		
		#try:
		w_siz = self.window_size.split("x")
		if self.crypt_method == "uc":
			#https://github.com/ultrafunkamsterdam/undetected-chromedriver/issues/743?utm_source=pocket_saves#issuecomment-1366847803
			'''print("****************************")
			print("If it gives an error similar to:")
			print("Message: unknown error: cannot connect to chrome at 127.0.0.1:50276")
			print("Fix: add xvfb-run. Example: xvfb-run python .....")
			print("****************************")'''
			

			if self.headless:
				self.display = Display(visible=0, size=(w_siz[0], w_siz[1]))
				self.display.start()

				f = open(os.path.dirname(os.path.realpath(__file__)) + "/xvfb.txt", "a")
				stack = traceback.extract_stack()
				stack = ''.join(traceback.format_list([stack[0]]))
				filename_origin = self.Regex(stack, '"(.*?)"')[0][1]
				f.write("Open " + filename_origin + "\n")
				f.close()
			
			eval_params = ["headless=self.headless", "uc=True"]
			if self.userdatadir != False:
				eval_params.append('user_data_dir=self.userdatadir')
			if self.proxy != False:
				eval_params.append('proxy = "'+self.proxy+'"')	

			self.driver = eval('Driver('+','.join(eval_params)+')') #chromium_arg = '","'.join(self.opt)
		else:
			try:
				self.driver = webdriver.Chrome(file_driver, options=self.browser_options, desired_capabilities=caps)
			except:
				print(file_driver)
				os.remove(file_driver)
				traceback.print_exc()
				print("-----------------")

			stealth(self.driver,
				languages=["en-US", "en"],
				vendor="Google Inc.",
				platform="Win32",
				webgl_vendor="Intel Inc.",
				renderer="Intel Iris OpenGL Engine",
				fix_hairline=True,
			)
		self.driver.set_window_size(w_siz[0], w_siz[1])

	'''
	get_emails: {
		"description": "This method allows you to scrap through your emails and not a normal web page",
		"username": "Username to access the email account",
		"password": "Password to access the email account",
		"imap_server": "Name of the Imap Server to access the email account",
		"filter_emails": "Filter the emails you want to access, example: {'\"seen\": False, \"from\": \"info@domain.com\"}",
		"box": "Name of the box to access"
	}
	'''
	def get_emails(self, username, password, imap_server, filter_emails, box = "INBOX"):
		ret = []
		if self.tor:
			#self.renew_connection()
			socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, 'localhost', 9050)
			socks.socket.setdefaulttimeout(30)
			socks.wrapmodule(imaplib)
		 
		imap = imaplib.IMAP4_SSL(imap_server)
		imap.login(username, password)
		imap.select(box)

		search_query = ""
		for k, v in filter_emails.items():
			if k == "seen":
				if v:
					search_query += "SEEN "
				else:
					search_query += "UNSEEN "
			else:
				search_query += k.upper() + ' "' + v + '" '

		(retcode, messages) = imap.search(None, '(' + search_query.strip() + ')')
		for num in messages[0].split() :
			res, data = imap.fetch(num, "(RFC822)")
			msg = email.message_from_bytes(data[0][1])

			current_mail = {"body": "", "from": msg['From'], "subject": msg["subject"]}
			for part in msg.walk():
				body_part = part.get_payload()
				if isinstance(body_part, list):
					for bp in body_part:
						current_mail["body"] += quopri.decodestring(str(bp)).decode('ISO-8859-1')

			ret.append(current_mail)
			
		imap.close()
		imap.logout()
		return ret

	'''
	Regex: {
		"description": "This method allows you to search for substrings via Regular expression and return them in a list",
		"test_str": "String where to search",
		"regex": "Regular expression"
	}
	'''
	def Regex(self, test_str, regex):
		ret = []
		matches = re.finditer(regex, test_str, re.MULTILINE | re.IGNORECASE | re.DOTALL)
		for matchNum, match in enumerate(matches, start=1):
			part = []
			part.append(match.group())
			for groupNum in range(0, len(match.groups())):
				groupNum = groupNum + 1
				part.append(match.group(groupNum))
			ret.append(part)
		return ret

	def __obfuscate(self, path):
		#cerca cdc_ e lo sostituisce con dog_ ma potrebbe essere una qualsiasi parola, per rendere meno identificabile lo scraper
		os.system("perl -pi -e 's/cdc_/dog_/g' "+path)

	'''
	get_download: {
		"description": "Return a list with the list of downloads in progress",
		"wait": "Downloads don't start immediately. Wait N seconds before seeing how many downloads are in progress"
	}
	'''
	def get_download(self, wait = 5):
		try:
			self.driver.execute_script("window.open();")
			self.driver.switch_to.window(self.driver.window_handles[-1])
			self.driver.get('chrome://downloads/')

			ret = []
			time.sleep(wait)
			items = self.driver.execute_script("return document.querySelector('downloads-manager').shadowRoot.querySelectorAll('downloads-item')")
			for itm in items:
				name = self.driver.execute_script("return arguments[0].shadowRoot.querySelector('#name').innerHTML", itm)
				description = self.driver.execute_script("return arguments[0].shadowRoot.querySelector('#description').innerHTML", itm)
				complete = False

				try:
					firt_block = ','.join(description.split(",")[:-1]).strip()
					speed = firt_block.split("-")[0].strip()
					partial_block = firt_block.split("-")[1].strip()
					partial_size = partial_block.split(" ")[0] + " " + partial_block.split(" ")[1] 
					total_size = partial_block.split(" ")[-2] + " " + partial_block.split(" ")[-1] 
					remaining_time = description.split(",")[-1].strip()
				except:
					complete = True

				try:
					progress = self.driver.execute_script("return arguments[0].shadowRoot.querySelector('#progress').shadowRoot.querySelector('#primaryProgress').style.transform", itm)
					progress = progress.split("(")[1].split(")")[0]
					progress = str(float(progress) * 100.0) + "%"
				except:
					pass

				if not complete:
					ret.append({
						"name": name,
						"description": description,
						"speed": speed,
						"partial_size": partial_size,
						"total_size": total_size,
						"remaining_time": remaining_time,
						"progress": progress
					})
				else:
					ret.append({
						"name": name,
						"progress": "100%"
					})

			
			self.driver.execute_script("window.close();")
			self.driver.switch_to.window(self.driver.window_handles[-1])
			return ret
		except Exception:
			from pathlib import Path

			time.sleep(wait)
			paths = sorted(Path(self.download_dir).iterdir(), key=os.path.getmtime)
			paths.reverse()
			for i in range(len(paths)):
				filename, file_extension = os.path.splitext(paths[i])
				if file_extension == ".crdownload":
					status = "downloading"
				else:
					status = "download complete"

				name = str(paths[i])
				paths[i] = {
					"status": status,
					"path": name,
					"filename": Path(paths[i]).stem,
					"extension": file_extension,
					"size": os.path.getsize(paths[i]),
					"creation": os.path.getctime(paths[i]),
					"modification": os.path.getmtime(paths[i]),
				}

			return paths

	'''
	screenshot: {
		"description": "Take a screenshot",
		"filename": "Path of the image to save"
	}
	'''
	def screenshot(self, filename):
		try:
			el = self.driver.find_element_by_tag_name('body')
			el.screenshot(filename)
		except:
			self.driver.save_screenshot(filename)

	def __log(self, filename_start = ""):
		save_path = ""
		if filename_start != "":
			sfx = datetime.today()
			save_path = "log/" + filename_start.replace('//', '-') + ''.join(e for e in self.url if e.isalnum())+"_"+str(sfx)+".html"
		if self.webView:
			self.screenshot(os.path.dirname(os.path.realpath(__file__)) + "/WebView/static/page.png")
		if save_path == "":
			return False

		if self.current_dir == "./" and not os.path.exists("log"):
			os.makedirs("log")

		f = open(self.current_dir + "/"+save_path, "w")
		self.screenshot(self.current_dir + "/"+save_path + ".png")
		f.write(self.driver.page_source)
		f.close()

	def get_shadowRoot(self, elem):
		return self.driver.execute_script('return arguments[0].shadowRoot', elem)

	'''
	page_source: {
		"description": "Show the source code of the page"
	}
	'''
	def page_source(self):
		return self.driver.page_source.encode('utf8').decode("utf-8") 

	def __get_session(self):
		#session = requests.session()
		session = requests.Session()
		retry = Retry(connect=3, backoff_factor=0.5)
		adapter = HTTPAdapter(max_retries=retry)
		session.mount('http://', adapter)
		session.mount('https://', adapter)

		if self.tor:
			# Tor uses the 9050 port as the default socks port
			session.proxies = {'http':  'socks5://127.0.0.1:9050',
							   'https': 'socks5://127.0.0.1:9050'}
		return session

	'''
	renew_connection: {
		"description": "If you use Tor with this method you can change ip address",
		"reload_browser": "If set to True it will close the browser and open a new one"
	}
	'''
	def renew_connection(self, reload_browser = False):
		self.close()

		self.tor_controller.authenticate(password="T0rPwd!")
		self.tor_controller.signal(Signal.NEWNYM)

		session = self.__get_session()
		newip = session.get("http://httpbin.org/ip").text
		if self.verbose:
			print(newip)

		'''f = open(self.current_dir + "/ip_bot_detected.log", "a")
		f.write(newip)
		f.close()'''

		if reload_browser:
			self.close()
			self.__get_driver(3)
			self.get(self.url)

	def get_content(self, url, b64 = False):
		attempt = 0
		while True:
			session = self.__get_session()
			try:
				cntnt = session.get(url, timeout=5).content
				if b64:
					return base64.b64encode(cntnt).decode("utf-8")
				else:
					return cntnt
			except Exception as e:
				attempt += 1
				if attempt > 3:
					return ""

				if self.verbose:
					print("get_content error")
					print(e)
				
				if self.tor:
					self.renew_connection()
				
				if self.verbose:
					print("wait 5 seconds")
					time.sleep(5)


	'''
	wait_find: {
		"description": "Gets a web page element",
		"locator": "Css or xpath selector to locate the item",
		"element": "If set to False, the entire document will be searched. Otherwise it will search within the element passed in this parameter",
		"by_type": "css or xpath",
		"log": "If set to True and an error will occur an .html snapshot will be created in the log folder",
		"wait": "With javascript the html page changes dynamically, making an element not accessible at that moment. This method will wait N seconds for the selected element to appear, after which it will generate an error"
	}
	'''
	def wait_find(self, locator, element = False, by_type = "css", log = True, wait = 10): 
		if self.verbose:
			print("Search "+locator)
		if not element:
			element = self.driver
		if by_type == "xpath":
			by_type = By.XPATH
		else:
			by_type = By.CSS_SELECTOR
		try:
			ret = WebDriverWait(element, wait).until(EC.presence_of_all_elements_located((by_type, locator)))
			#self.__log()
			return ret
		except Exception as e:
			if log:
				self.__log("wait_find"+locator)
				raise Exception("Exception wait_find")

	'''
	close: {
		"description": "Close the browser"
	}
	'''
	def close(self):
		self.driver.quit()
		if hasattr(self, "display"):
			self.display.stop()

			f = open(os.path.dirname(os.path.realpath(__file__)) + "/xvfb.txt", "a")
			stack = traceback.extract_stack()
			stack = ''.join(traceback.format_list([stack[0]]))
			filename_origin = self.Regex(stack, '"(.*?)"')[0][1]
			f.write("Close " + filename_origin + "\n")
			f.close()
		if hasattr(self, "webprocess"):
			self.webprocess.terminate()

	def __check_bot(self, url):
		#print(self.driver.page_source)
		if "Backer or bot" in self.driver.page_source or "has banned the autonomous system number" in self.driver.page_source or "has banned the country or region your IP address" in self.driver.page_source:
			self.renew_connection()
			self.close()
			self.__get_driver(3)
			
			self.get("https://www.google.com/search?q=" + url)
			#time.sleep(3)

			self.driver.execute_script("document.querySelector('body').innerHTML='<a href=\"" + url + "\">URL</a>';")
			self.wait_find("a")[0].click()

			time.sleep(1)
			self.driver.refresh()
			self.__check_bot(url)

	'''
	get: {
		"description": "Navigate to a Url",
		"url": "URL to reach",
		"reffer": "Change the referer (the url from which you are landing on the requested page)"
	}
	'''
	def get (self, url, reffer = False):
		self.url = url
		try:
			if validators.url(url):
				if not reffer:
					if self.verbose:
						print("Get "+url)
					self.driver.get(url)
				else:
					if self.verbose:
						print("Get "+url+" with reffer: " + reffer)
					self.driver.get(reffer)
					self.driver.execute_script('window.location.href = "' + url + '";')
			else:
				if self.verbose:
					print("Get from html code")
				self.driver.get("data:text/html;base64," + base64.b64encode(url.encode('utf-8')).decode())
		except Exception as e: 
			os.system("pkill -f chromedriver")
			os.system("pkill -f chromium")
			raise Exception(e) 
		self.__log()
		self.__check_bot(url)

	'''
	focus_last_tab: {
		"description": "Displays the last opened tab"
	}
	'''
	def focus_last_tab(self):
		self.driver.switch_to.window(self.driver.window_handles[-1])

	'''
	new_tab: {
		"description": "Open a new tab"
	}
	'''
	def new_tab(self):
		self.driver.execute_script("window.open('');")
		self.focus_last_tab()

	'''
	close_tab: {
		"description": "Close current tab"
	}
	'''
	def close_tab(self):
		self.driver.close()
		self.focus_last_tab()

	'''
	scroll_to_bottom: {
		"description": "Scroll the page to the bottom",
		"times": "Number of times you want to repeat the scroll",
		"wait": "Waiting time between scrolls"
	}
	'''
	def scroll_to_bottom(self, times = 1, wait = 1):
		for i in range(0, times):
			if self.verbose:
				print("Scroll "+str(i+1)+"/"+str(times))
			self.driver.execute_script("window.scrollTo(0, 999999999999999999999999)")
			time.sleep(wait)

	'''
	get_image_from_google: {
		"description": "Search images from Google images",
		"query": "Keywords to search",
		"size": "s for small, m formedium and l for large"
	}
	'''
	def get_image_from_google(self, query, size = "m"):
		self.get("https://www.google.it/search?tbm=isch&q=" + urllib.parse.quote(query) + "&tbs=isz:" + size)
		try:
			btns = self.wait_find('form[action="https://consent.google.it/save"] button')[1].click()
		except:
			pass
		imgs = self.driver.page_source.split("AF_initDataCallback(")[2].split('["')
		ret = []
		for img in imgs:
			if ".jpg" in img or ".png" in img:
				ret.append(img.split('"')[0])
		return ret
		
	'''
	download_image_from_url: {
		"description": "Download an image from url",
		"url": "Url for download",
		"file_name": "Path to save the image",
		"b64": "If set to True it will return a base64 string"
	}
	'''
	def download_image_from_url(self, url, file_name = "", b64 = False):
		self.get(url)
		script_js = '''
		function toDataURL(src, callback){
			var image = new Image();
			image.crossOrigin = 'Anonymous';
			image.onload = function(){
				var canvas = document.createElement('canvas');
				var context = canvas.getContext('2d');
				canvas.height = this.naturalHeight;
				canvas.width = this.naturalWidth;
				context.drawImage(this, 0, 0);
				var dataURL = canvas.toDataURL('image/jpeg');
				callback(dataURL);
			};
			image.src = src;
		}
		toDataURL("''' + url + '''", function(dataURL){
			const div = document.createElement('div');
			div.id = "base64image";
			div.textContent = dataURL;
			document.body.prepend(div);
		})
		'''
		self.driver.execute_script(script_js)
		imgstring = self.wait_find("#base64image")[0].text.replace("data:image/jpeg;base64,","")
		if b64:
			return imgstring
		imgdata = base64.b64decode(imgstring)
		with open(file_name, 'wb') as f:
			f.write(imgdata)

	'''
	download_file: {
		"description": "Download a file from a url",
		"url": "Url for download",
		"reffer": "Download the file with a referer. Some sites do not allow you to download the file knowing the url, but only if the referer is the site that contains the file"
	}
	'''
	def download_file(self, url, reffer = False):
		self.new_tab()
		self.get(url, reffer = reffer)
		self.focus_last_tab()
		self.close_tab()

	'''
	xml_generator: {
		"description": "Allows you to create an xml file for rss feeds",
		"filename": "File name",
		"title": "Title tag of the xml file",
		"link": "Link tag of the xml file",
		"description": "Description tag of the xml file",
		"items": "List of dicts where each dict has the following keys: link, guid, title, description"
	}
	'''
	def xml_generator(self, filename, title, link, description, items):
		if self.verbose:
			print("Xml generation")
		xml = ""
		for xml_item in items:
			#xml += '''
			#<item>
			#	<title>'''+html.escape(xml_item["title"])+'''</title>
			#	<link>'''+urllib.parse.quote(xml_item["link"])+'''</link>
			#	<guid>'''+urllib.parse.quote(xml_item["guid"])+'''</guid>	
			#	<description>'''+xml_item["description"]+'''</description>
			#</item>'''

			img = ""
			if "img" in xml_item:
				img = '<img src="'+xml_escape(xml_item["img"])+'" /><br />'
				#img = '<media:thumbnail url="'+escape(xml_item["img"])+'" />'

			xml += '''
			<item>
				<title>'''+html.escape(xml_item["title"])+'''</title>
				<link>'''+xml_escape(xml_item["link"])+'''</link>
				<guid>'''+xml_escape(xml_item["guid"])+'''</guid>
				<description>'''+img+xml_item["description"]+'''</description>
			</item>'''

		xmlstring = '<rss version="2.0"><channel><title>'+title+'</title><link>'+link+'</link><description>'+description+'</description><language>it-IT</language>'+xml+'</channel></rss>'
		'''parser = etree.XMLParser(recover=True)
		tree = etree.fromstring(xmlstring, parser=parser)

		for element in tree.iter():
			path = element.getroottree().getpath(element)
			if re.search(r'\/rss\/channel\/item\[(.*?)\]\/link\b', path) or re.search(r'\/rss\/channel\/item\[(.*?)\]\/guid\b', path):
				element.text = urllib.parse.unquote(element.text)'''

		#f = open(filename+".xml", "wb")
		#f.write(etree.tostring(tree))
		f = open(filename+".xml", "w")
		f.write(xmlstring)
		f.close()

	'''
	ftp_upload: {
		"description": "Upload a file via ftp",
		"server": "Ftp server name",
		"username": "Ftp username",
		"password": "Ftp password",
		"localfile": "Local file path",
		"remotefile": "Remove file path"
	}
	'''
	def ftp_upload(self, server, username, password, localfile, remotefile): 
		if self.verbose:
			print("Ftp Upload "+localfile)
		uploadTracker = FtpUploadTracker(os.path.getsize(localfile))
		session = ftplib.FTP(server, username, password)
		file = open(localfile,'rb')
		session.storbinary('STOR '+remotefile, file, 1024, uploadTracker.handle)
		file.close() 
		session.quit()

	'''
	lang_detect: {
		"description": "Identifies the language of a text",
		"txt": "Text to parse"
	}
	'''
	def lang_detect(self, txt):
		return detect(txt)

	'''
	translate: {
		"description": "Translates text from one language to another",
		"txt": "Text to translate",
		"src": "Text language. Allowed value: auto",
		"dest": "Language into which you want to translate the text",
		"xml": "Set to True if you want to encode the response so it can be used inside the xml"
	}
	'''
	def translate(self, txt, src, dest, xml = False):
		txt = html.unescape(txt)
		txt = txt.replace('<![CDATA[', '')
		txt = txt.replace(']]>', '')
		txt = re.sub('<([^<]+?)>', '', txt)
		txt = html.unescape(txt)
		txt = txt.encode('ascii', 'ignore').decode('ascii')
		#txt = txt[0:5000]
		time.sleep(1) #senza questo vengo bannato
		try:
			trad = translator.translate(txt, src=src, dest=dest).text
			if xml:
				return saxutils.escape(trad)
			return trad
		except Exception as e:
			if "'NoneType' object has no attribute 'group'" in str(e):
				self.get("https://pypi.org/project/googletrans/#history")
				for release in self.wait_find(".release__card .release__version"):
					rel = release.text.split(" ")[0]
					if "a" in rel:
						os.system("pip install googletrans==" + rel)

			traceback.print_exc()
			sys.exit()