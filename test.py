# from selenium import webdriver
# import requests

# driver = webdriver.Firefox()

# s = requests.Session()

# driver.get("https://www.wuxiaworld.com/")
# selenium_user_agent = driver.execute_script("return navigator.userAgent;")
# selenium_cookies=";".join(list(map(lambda x:f" {x['name']} = {x['value']} ",driver.get_cookies())))

# selenium_user_agent = driver.execute_script("return navigator.userAgent;")
# s.headers.update({"user-agent": selenium_user_agent})
# for cookie in driver.get_cookies():
#     s.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])

# response = s.get("https://www.wuxiaworld.com/")
# print(response)

# import cloudscraper

# scraper = cloudscraper.create_scraper( debug=True,delay=10,browser={
#         'browser': 'firefox',
#         'platform': 'windows',
#         'mobile': False
#     })  # returns a CloudScraper instance
# # Or: scraper = cloudscraper.CloudScraper()  # CloudScraper inherits from requests.Session
# print(scraper.get("https://www.wuxiaworld.com/").text) 



import undetected_chromedriver as uc

if __name__ == '__main__':
	driver = uc.Chrome()
	driver.get('https://api2.wuxiaworld.com')
	response = driver.request('POST', 'url', data={"x": "y"})
