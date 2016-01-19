from lxml import html
import requests
from urllib.parse import urlparse
from urllib.parse import urljoin
import urllib
import sqlite3
import sys
import time
import re
import string
import os.path


_user_agent='Mozilla/5.0 (Windows NT 10.0; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0.4'

class LinkExtractor(object):
	htmltext = ''
	url = ''
	links = []
	images = []
	cookiestr=''
	filter=''
	def __init__(self, url, cookiestr='', filter=''):
		self.links = []
		self.url = url
		self.cookiestr = cookiestr
		self.filter = filter

	def load_links(self):
		self.links = []
		if(len(self.cookiestr)>0):
			headers = {'Cookie': self.cookiestr, 'User-Agent': _user_agent}
			page = requests.get(self.url, headers = headers)
		else:
			headers = {'User-Agent': _user_agent}
			page = requests.get(self.url, headers = headers)
		self.htmltext = page.text
		tree = html.fromstring(self.htmltext)
		
		if(len(self.filter)==0):
			self.links = tree.xpath('//a/@href')
		else:
			filterparts = self.filter.split('|')
			for fl in filterparts:
				self.links.extend(tree.xpath('//a[contains(@href,\''+fl+'\')]/@href'))
			
		for i, s in enumerate(self.links):
			self.links[i] = urljoin(self.url, self.links[i])

	def load_images(self):
		self.images = []
		if(len(self.cookiestr)>0):
			headers = {'Cookie': self.cookiestr, 'User-Agent': _user_agent}
			page = requests.get(self.url, headers = headers)
		else:
			headers = {'User-Agent': _user_agent}
			page = requests.get(self.url, headers = headers)
		self.htmltext = page.text
		tree = html.fromstring(self.htmltext)
		if(len(self.filter)==0):
			self.links = tree.xpath('//img/@src')
		else:
			filterparts = self.filter.split('|')
			for fl in filterparts:
				self.links.extend(tree.xpath('//a[contains(@href,\''+fl+'\')]/@href'))
			
		for i, s in enumerate(self.images):
			self.images[i] = urljoin(self.url, self.images[i])

	def save_links(self, filename):
		f = open(filename, 'w')
		for link in self.links:
			f.write(link + '\n')
		f.close()
	
class CookieUtils(object):
	url = ''
	hostchecks = []
	cookie_header = ''
	cookieheader = ''
	cookiefile = ''
	def __init__(self, url, cookiefile):
		self.url = url
		self.hostchecks = []
		self.cookiefile = cookiefile

		if(self.cookiefile):
			self.extract_cookie_checks()
			self.load_cookies()
		
	def extract_cookie_checks(self):
		o = urlparse(self.url)
		hostname = o.hostname;

		hostparts = hostname.split('.')
		tmp=''
		self.hostchecks.append(hostname)
		self.hostchecks.append('.'+hostname)
		if(len(hostparts)>1):
			tmp = hostparts[len(hostparts)-2]+'.'+hostparts[len(hostparts)-1]
			if tmp not in self.hostchecks:
				self.hostchecks.append(tmp)
			if '.'+tmp not in self.hostchecks:
				self.hostchecks.append('.'+tmp)
		if(len(hostparts)>2):
			tmp = hostparts[len(hostparts)-3]+'.'+hostparts[len(hostparts)-2]+'.'+hostparts[len(hostparts)-1]
			if tmp not in self.hostchecks:
				self.hostchecks.append(tmp)
			if '.'+tmp not in self.hostchecks:
				self.hostchecks.append('.'+tmp)
		if(len(hostparts)>3):
			tmp = hostparts[len(hostparts)-4]+'.'+hostparts[len(hostparts)-3]+'.'+hostparts[len(hostparts)-2]+'.'+hostparts[len(hostparts)-1]
			if tmp not in self.hostchecks:
				self.hostchecks.append(tmp)
			if '.'+tmp not in self.hostchecks:
				self.hostchecks.append('.'+tmp)
		if(len(hostparts)>4):
			tmp = hostparts[len(hostparts)-5]+'.'+hostparts[len(hostparts)-4]+'.'+hostparts[len(hostparts)-3]+'.'+hostparts[len(hostparts)-2]+'.'+hostparts[len(hostparts)-1]
			if tmp not in self.hostchecks:
				self.hostchecks.append(tmp)
			if '.'+tmp not in self.hostchecks:
				self.hostchecks.append('.'+tmp)
	
	def load_cookies(self):
		o = urlparse(self.url)
		hostcount = len(self.hostchecks)
		isfirst = True


		if(self.cookiefile.endswith('cookies.sqlite')):
			query = 'SELECT name, value FROM moz_cookies WHERE ('
			for host in self.hostchecks:
				if isfirst == True:
					query = query + 'host=? '
					isfirst = False
				else:
					query = query + 'OR host=? '
			
			if o.scheme=='http':
				query = query + ') AND (path=? OR path=\'/\') AND isSecure=0;'
			elif o.scheme=='https':
				query = query + ') AND (path=? OR path=\'/\');'

			sqlParams = self.hostchecks
			sqlParams.append(o.path)
			conn = sqlite3.connect(self.cookiefile)
			c = conn.cursor()		
			c.execute(query, sqlParams)
			self.cookieheader = ''
		
			for row in c:
				self.cookieheader = self.cookieheader + row[0] + '=' + row[1] + '; '
		
			conn.close()

		elif(self.cookiefile.endswith('Cookies')):
			query = 'SELECT name, value FROM cookies WHERE ('
			for host in self.hostchecks:
				if isfirst == True:
					query = query + 'host_key=? '
					isfirst = False
				else:
					query = query + 'OR host_key=? '
			
			if o.scheme=='http':
				query = query + ') AND (path=? OR path=\'/\') AND secure=0;'
			elif o.scheme=='https':
				query = query + ') AND (path=? OR path=\'/\');'

			sqlParams = self.hostchecks
			sqlParams.append(o.path)
			conn = sqlite3.connect(self.cookiefile)
			c = conn.cursor()		
			c.execute(query, sqlParams)
			self.cookieheader = ''
		
			for row in c:
				self.cookieheader = self.cookieheader + row[0] + '=' + row[1] + '; '
			
			conn.close()


		
		self.cookieheader = self.cookieheader.strip()
	
class Downloader(object):
	def __init__(self):#, url, filename=''):
		i=0
	def download(self, url, filename=''):
		if(len(filename)>0):
			local_filename = filename
		else:
			local_filename = url.split('/')[-1]
		r = requests.get(url, stream=True)
		with open(local_filename, 'wb') as f:
			for chunk in r.iter_content(chunk_size=32768): 
				if chunk: # filter out keep-alive new chunks
					f.write(chunk)
					f.flush()
					print('#',end="",flush=True)
			f.close()
		return local_filename

	def downloadFile(self, url, directory, cookieheader=''):
		
		r = requests.head(url, allow_redirects=True)
		headers = {}
		if(len(cookieheader)>0):
			headers = {'Cookie': cookieheader, 'User-Agent': _user_agent}
		else:
			headers = {'User-Agent': _user_agent}

		dl = 0
		start = time.clock()
		r = requests.get(url, stream=True, headers = headers)

		contentdisposotion = r.headers.get('content-disposition')
		if contentdisposotion is None:
			filename = url.split('/')[-1].split('#')[0].split('?')[0]
		else:
			matches=re.findall(r'\"(.+?)\"',contentdisposotion)
			if(len(matches)>0) and (contentdisposotion.find('attachment') != -1):
				filename = matches[0]
			else:
				filename = url.split('/')[-1].split('#')[0].split('?')[0]
			
		total_length = r.headers.get('content-length')
		filesizestr = ''
		if(total_length is not None):
			filesizestr = ' / Size: ' + total_length
			
		localFilename = filename
		
		if(os.path.isfile(directory + '/' + localFilename)):
			return -1

		print('File: ' + localFilename + filesizestr)
		
		with open(directory + '/' + localFilename, 'wb') as f:
			if total_length is None: # no content length header
				f.write(r.content)
			else:
				filelen = int(total_length)
				for chunk in r.iter_content(32768):
					dl += len(chunk)
					f.write(chunk)
					done = int(50 * dl / filelen)
					sys.stdout.write("\r[%s%s] %s kb/s" % ('=' * done, ' ' * (50-done), (dl /1024) //(time.clock() - start)))
				
		print('')
		return (time.clock() - start)

class TSectionMatch(object):
	StartNum=0
	EndNum=0
	Increment=1
	UrlCount=0
	IsFilled=False
	SectionText=''
	MinIntegerWidth=0
	IsLeadingZeroes=False
	def __init__(self):
		self.EndNum = 0
		
class SectionExpander(object):
	strs=[]
	url=''
	def __init__(self, url):
		self.url=url
		
	def RegexpGetMatchCount(self, s, pattern):
		return len(re.findall(pattern, s))
	
	def GetSectionCount(self, s):
		return self.RegexpGetMatchCount(s, '\{([0-9]*)\-([0-9]*)\ *\,([0-9]*)\ *\}')
		
	def StringContainsSection(self, s):
		return len(re.findall('\{([0-9]*)\-([0-9]*)\ *\,([0-9]*)\ *\}', s))>0
		
	def GetSectionFromString(self, s, i):
		matches = re.findall('\{([0-9]*)\-([0-9]*)\ *\,([0-9]*)\ *\}', s)
		matcheslit = re.findall('\{[0-9]*\-[0-9]*\ *\,[0-9]*\ *\}', s)
		
		if len(matches)>i:
			start = int(matches[i][0])
			end = int(matches[i][1])
			inc = int(matches[i][2])
			
			m = TSectionMatch()
			m.StartNum = start
			m.EndNum = end
			m.Increment = inc
			m.MinIntegerWidth = len(matches[i][0])
			m.IsLeadingZeroes = (matches[i][0][0] == '0')
			m.SectionText = matcheslit[0]
			m.UrlCount = int(int(m.EndNum - m.StartNum) / inc) + 1
			m.IsFilled=True;
			return m
		else:
			return None
		
	def GetTotalExpansionSize(self, url):
		c=self.GetSectionCount(url)
		total=1
		
		for index in range(c):
			sect=self.GetSectionFromString(url, index)
			if sect is not None:
				total=total*sect.UrlCount
			else:
				return total
		return total
		
	def ExpandFirstSection(self, formatted_urltext, urlHolder, sect):
		i=0
		if sect.IsFilled:
			for index in range(sect.UrlCount):
				urlHolder.append(formatted_urltext.replace('%d', str(sect.StartNum + (i*sect.Increment))  ))
		return urlHolder
	
	def ReplaceStrings(self, urls, OldPattern, NewPattern):
		for index in range(len(urls)):
			urls[index]=urls[index].replace(OldPattern, NewPattern,1)
	
	def PadInt(self, i, minwidth):
		s=str(i);
		if len(s) >= minwidth:
			return s
		else:
			n=minwidth-len(s)
			for i in range(n):
				s='0'+s
			return s
	
	def ExpandSections(self, urls, sect):
		urlHolder = []
		if sect.IsFilled:
			if(sect.IsLeadingZeroes):
				self.ReplaceStrings(urls, sect.SectionText, '%s');
			else:
				self.ReplaceStrings(urls, sect.SectionText, '%d');

		for j in range(len(urls)):
			for i in range(sect.UrlCount):
				if(sect.IsLeadingZeroes==True):
					urlHolder.append(urls[j].replace('%s',   self.PadInt( sect.StartNum + (i*sect.Increment), sect.MinIntegerWidth) ))
				else:
					urlHolder.append(urls[j].replace('%d',   str(sect.StartNum + (i*sect.Increment) ) ))
		return urlHolder
		
	def TotallyExpandString(self):
		self.strs = []
		self.strs.append(self.url)
		#sect = GetSectionFromString(url, 0)
		while(self.GetSectionFromString(self.strs[0], 0) is not None):
			sect = self.GetSectionFromString(self.strs[0], 0)
			self.strs = self.ExpandSections(self.strs, sect)

