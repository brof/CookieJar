# CookieJar

A collection of python classes I'm writing in order to learn Python. It consists of some classes to help with spidering tasks. 

Stuff it can do:
- Accessing password protected web pages using read-only access to your browser cookie store. (Although probably better to create a copy of your cookie file to the script directory rather thatn use the live cookie file)
- Expanding urls like http://example.com/thread.php?page={0-150,15} (will expand to a list of 16 urls page=0 to page=150 
where page increments by 15 each time.). 
- There is also a class to allow you to extract hyper links base on a string filter, or image urls.
- A file download class is also included.


#Requires Python 3.5+
