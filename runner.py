import argparse
from CookieJar import *

#python runner.py http://google.com/file{0-100,5}.zip --cookiejar cookies.sqlite
#python runner.py http://google.com/file{0-100,5}.zip --cookiejar 'Safe Browsing Cookies'

parser = argparse.ArgumentParser()
parser.add_argument("url", help="The URL, containing optional {a-b,inc} formatted sections")
parser.add_argument("--cookiejar", help="Chrome, Opera 34.0+ or Firefox SQLite3 cookie store file (Firefox: cookies.sqlite or Chrome: \"Safe Browsing Cookies\", Opera: Cookies")

#parser.add_argument("operation", help="extractlinksanddownload, extractimagesanddownload, savelinklist, saveimagelist")
#parser.add_argument("--filter", help="Extract urls containing this string. Seperate multiple filters with pipe char |")
#parser.add_argument("--verbosity", type=int, help="Verbosity 0=none, 1=minimal, 2=log, 3=debug")
#parser.add_argument("--usecookies", help="Use Firefox SQLite3 cookie store file cookies.sqlite in current directory.")
#parser.add_argument("--savedir", help="Directory to save downloads. Defaults to currenct directory")
#parser.add_argument("--overwrite", type=bool, help="Overwrite downloaded files if already exists. Default behavior is skip")
args = parser.parse_args()

c = CookieUtils(args.url, args.cookiejar)
print('c.cookieheader: ' + c.cookieheader)

exp = SectionExpander(args.url)
exp.TotallyExpandString()
print(exp.strs)


