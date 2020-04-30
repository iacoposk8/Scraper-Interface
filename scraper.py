import os, time, urllib.parse, ftplib, html, re, sys
import traceback
from datetime import datetime
from lxml import etree
from xml.sax import saxutils

from googletrans import Translator
translator = Translator()

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class Scraper():
	def __init__(self, headless = True, each_log = False):
		self.each_log = each_log
		WINDOW_SIZE = "800,600"
		chrome_options = Options()
		if headless:
			chrome_options.add_argument("--headless") 
		chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
		current_dir = os.path.dirname(os.path.realpath(__file__))
		prefs = {
			"profile.default_content_settings.popups": 0, 
			"download.default_directory": r""+current_dir, 
			"directory_upgrade": True
		}
		chrome_options.add_experimental_option("prefs", prefs)

		try:
			self.driver = webdriver.Chrome(options=chrome_options)
		except Exception:
			ext = ""
			if os.name == 'nt':
				ext = "exe"
			else:
				self.driver = webdriver.Chrome(current_dir+"/chromedriver"+ext, options=chrome_options)

	def log(self):
		sfx = ""
		if self.each_log:
			sfx = datetime.today()
		f = open(os.path.dirname(os.path.abspath(__file__)) + "/log/"+''.join(e for e in self.url if e.isalnum())+"_"+str(sfx)+".html", "w")
		f.write(self.driver.page_source)
		f.close()

	def wait_find(self, locator, element = False):
		print("Search "+locator)
		if not element:
			element = self.driver

		try:
			ret = WebDriverWait(element, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, locator)))
			self.log()
			return ret
		except Exception as e:
			self.log()
			raise Exception("Exception")

	def close(self):
		self.driver.quit()

	def get(self, url):
		print("Get "+url)
		self.url = url
		self.driver.get(url)
		self.log()

	def scroll_to_bottom(self, times, wait):
		for i in range(0, times):
			print("Scroll "+str(i+1)+"/"+str(times))
			self.driver.execute_script("window.scrollTo(0, 999999999999999999999999)")
			time.sleep(wait)

	def xml_generator(self, filename, title, link, description, items):
		print("Xml generation")
		xml = ""
		for xml_item in items:
			xml += '<item><title>'+html.escape(xml_item["title"])+'</title><link>'+urllib.parse.quote(xml_item["link"])+'</link><guid>'+urllib.parse.quote(xml_item["guid"])+'</guid><description>'+xml_item["description"]+'</description></item>'

		xmlstring = '<rss version="2.0"><channel><title>'+title+'</title><link>'+link+'</link><description>'+description+'</description><language>it-IT</language>'+xml+'</channel></rss>'
		parser = etree.XMLParser(recover=True)
		tree = etree.fromstring(xmlstring, parser=parser)

		for element in tree.iter():
			path = element.getroottree().getpath(element)
			if re.search(r'\/rss\/channel\/item\[(.*?)\]\/link\b', path) or re.search(r'\/rss\/channel\/item\[(.*?)\]\/guid\b', path):
				element.text = urllib.parse.unquote(element.text)

		f = open(filename+".xml", "wb")
		f.write(etree.tostring(tree))
		f.close()

	def ftp_upload(self, server, username, password, localfile, remotefile): 
		print("Ftp Upload "+localfile)
		session = ftplib.FTP(server, username, password)
		file = open(localfile,'rb')
		session.storbinary('STOR '+remotefile, file)
		file.close() 
		session.quit()

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
			traceback.print_exc()
			sys.exit()