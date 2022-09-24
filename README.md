# Wuxiaworld to epub
 A badly codded example of a python client for the the wuxiaworld v2 API to grab novel information and chapters to generate epubs.
The code uses Google Protocol Buffers for data serialisation with the Wuxiaworld API, undetected-chromedriver to bypass cloudflare and a Sonora inspired client (https://github.com/public/sonora) as gRPC-Web.

# Installation and Runing
 * Download or clone the package
 * you also need to have Chrome installed 
 * run `pip install -r requirements.txt`
 * edit the main.py file `__main__` to select the novels you need, each novel is identified to the last part of the corresponding url, for example https://www.wuxiaworld.com/novel/archfiend become archfiend
 * run `python main.py`