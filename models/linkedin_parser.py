import http.cookiejar as cookielib
import os
import urllib
import re
import string
import time
from bs4 import BeautifulSoup
from dotenv import dotenv_values, load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from .config.filter_methods import platform_filters, testing_platform_filters
from .config.cleaning_methods import str_strip
import pandas as pd
import random
import logging
import pickle

class LinkedInParser(object):
    def __init__(self, USERNAME, PASSWORD):
        #Creating a webdriver instance to log into LinkedIn. Maybe want to use edge for universality?
        path_to_cookies = ".//credentials//cookies.pkl" #"..//dev//config//cookies.pkl"
        self.service = ChromeService(executable_path=ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service) #create a chrome instance
        self.driver.get("https://www.linkedin.com/")
        try:
            cookie_depot = pickle.load(open(path_to_cookies, "rb"))
            for cookie in cookie_depot:
                self.driver.add_cookie(cookie)
            self.driver.get("https://www.linkedin.com/feed/")
            time.sleep(2)
            cookies = True if "https://www.linkedin.com/feed/" in self.driver.current_url else False #If we get redirected, our cookies have expired.
        except Exception as e:
            cookies = False
            print(f"Error retrieving cookies, {e}")
        if cookies==False: #Refresh cookies
            self.login(USERNAME, PASSWORD)
            pickle.dump(self.driver.get_cookies(), open(path_to_cookies, "wb"))
        
        
        # for item in self.url_list:
        #     self.scrape_posting(item)
    def login(self, USERNAME, PASSWORD):

        
        self.driver.get("https://www.linkedin.com/uas/login") #opening login page
        
        time.sleep(5) #wait for page to load
        username = self.driver.find_element(By.ID, "username") #Locates username field
        print(username)
        password = self.driver.find_element(By.ID,"password") #Locates password field
        print(password)
        username.send_keys(USERNAME) #Enters username
        password.send_keys(PASSWORD) #Enters password
        # driver.find_element(By.CSS_SELECTOR, 'button.btn__primary--large from__button--floating').click()
        self.driver.find_element(By.XPATH,'//*[@id="organic-div"]/form/div[3]/button').click()
        
        
        time.sleep(3)
        #FIGURE OUT SECURITY CHECK
        while self.driver.current_url.startswith("https://www.linkedin.com/checkpoint/challenge/"):
            logging.warning("Requires Human Verification. Please Help.") #TODO implement logging elsewhere instead of printing.
            time.sleep(5)
        time.sleep(3)
        
        # self.driver.getCurrentUrl();
        ...
    def dict_clean(self, item_contents):
        #recursive dict string cleaning 
        # print(input_dict)
        # for item in input_dict.keys(): #cleaning
        # if item=='errors':
        #     return input_dict
        # item_contents = input_dict[item]
        if isinstance(item_contents, str):
            new_item_contents=str_strip(item_contents)
        elif isinstance(item_contents, list):
            new_item_contents = []
            for item in item_contents:
                new_item_contents.append(self.dict_clean(item))
        elif isinstance(item_contents, dict):
            new_item_contents = {}
            for item in item_contents.keys():
                new_item_contents.update({item:self.dict_clean(item_contents[item])})
        else:
            print("Cannot identify type for object type", type(item_contents), item_contents, sep=" --- ")
            return item_contents
            # new_item_contents=item_contents
                # new_item_contents=item_contents
        # input_dict[item]=new_item_contents
            
        return new_item_contents
    def scrape_posting(self, PostID, parsing_library=None, filter_path=None):
        '''
        Parses job listings posted on LinkedIn using BeautifulSoup and a dictionary with key:method pairs for easy data object creation.
        '''
        # filter_path= filter_path.split(".") if 
        self.driver.get(url=f'https://www.linkedin.com/jobs/view/{PostID}') #TODO if adding multithreading and async, this needs to change.
        time.sleep(2) # Maybe just rely on the implicit/explicit wait functions instead.
        page_source = self.driver.page_source
        parsing_library = "html5lib" if parsing_library==None else parsing_library
        # html_text = requests.get(PostID).text
        soup = BeautifulSoup(page_source, parsing_library)
        # TODO check if deleted 
        # soup = BeautifulSoup(html_text, parsing_library)
        listing_filters = testing_platform_filters['LinkedIn']['selenium-client']['post'] #Eventually reference the url for platform information.
        html_data = {"errors":{}, "PostID":PostID} #bucket for collected data
        for data_label in listing_filters: #loops through each data_label 
            try:
                html_data.update({data_label : listing_filters[data_label](soup)}) #applies filter to captured data and inserts the key-value pair into html_data
            except Exception as e:
                html_data.update({data_label : None}) #If error, fills in value with null
                html_data["errors"].update({data_label:e}) #
        html_data = self.dict_clean(html_data)

        return html_data
    def scrape_company_data(self, data_dict, parsing_library=None):
        # if len(data_dict)==0 #TODO Error handling
            
        company_data = {"Company_Name":data_dict["Company_Name"], "SourceID":data_dict["PostID"], 'errors':{}}
        company_url = data_dict['Company_URL']
        
        if company_url == None:
            company_data['errors'].update({"404":"Error: Listing deleted"})
            return company_data
        parsing_method_dict = testing_platform_filters['LinkedIn']['selenium-client']['company']
        

        parsing_library = "html5lib" if parsing_library==None else parsing_library
        
        for page in parsing_method_dict.keys():
            # url_extension = "" if page=="Home" else page.lower()
            page_to_scrape = company_url if page=="Home" else str(company_url)+page.lower() # Breaks when removed job listing is called.
            try:
                self.driver.get(url=page_to_scrape)
                time.sleep(2)
            except:
                print(f"Error with {page_to_scrape}")
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, parsing_library)
            
            
            
            for data_label in parsing_method_dict[page].keys():
                try:
                    company_data.update({data_label:parsing_method_dict[page][data_label](soup)})
                except Exception as e:
                    company_data.update({data_label: None})
                    company_data['errors'].update({data_label:e})
        print(company_data)
        return company_data
        
        


# <button class="btn__primary--large from__button--floating" data-litms-control-urn="login-submit" type="submit" aria-label="Sign in">Sign in</button>

'''
    OLD ATTEMPT. TODO DELETE ME
    def __init__(self, login, password):
        """ Start up... """
        self.login = login
        self.password = password

        # Simulate browser with cookies enabled
        self.cj = cookielib.MozillaCookieJar(cookie_filename)
        if os.access(cookie_filename, os.F_OK):
            self.cj.load()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPRedirectHandler(),
            urllib.request.HTTPHandler(debuglevel=0),
            urllib.request.HTTPSHandler(debuglevel=0),
            urllib.request.HTTPCookieProcessor(self.cj)
        )
        self.opener.addheaders = [
            ('User-agent', ('Mozilla/4.0 (compatible; MSIE 6.0; ''Windows NT 5.2; .NET CLR 1.1.4322)'))
        ]

        # Login
        self.loginPage()

        title = self.loadTitle()
        print(title)

        self.cj.save()
        print(self.cj)

    def loadPage(self, url, data=None):
        """
        Utility function to load HTML from URLs for us with hack to continue despite 404
        """
        # We'll print the url in case of infinite loop
        # print "Loading URL: %s" % url
        try:
            if data is not None:
                response = self.opener.open(url, data)
            else:
                response = self.opener.open(url)
            return ''.join([str(l) for l in response.readlines()])
        except Exception as e:
            # If URL doesn't load for ANY reason, try again...
            # Quick and dirty solution for 404 returns because of network problems
            # However, this could infinite loop if there's an actual problem
            return self.loadPage(url, data)

    def loadSoup(self, url, data=None):
        """
        Combine loading of URL, HTML, and parsing with BeautifulSoup
        """
        print(f"loading soup for {url}")
        html = self.loadPage(url, data)
        # print(html)
        soup = BeautifulSoup(html, "html5lib")
        # print("SOUPIFY ME",soup)
        return soup

    def loginPage(self):
        """
        Handle login. This should populate our cookie jar.
        """
        soup = self.loadSoup("https://www.linkedin.com/login/")
        csrf = soup.find_all("input", type="hidden")
        login_data = urllib.parse.urlencode({
            'session_key': self.login,
            'session_password': self.password,
            'loginCsrfParam': csrf,
        }).encode('utf8')

        contents = self.loadPage("https://www.linkedin.com/uas/login-submit", login_data)
        print("LOGIN: ", contents)
        return

    def loadTitle(self):
        soup = self.loadSoup("https://www.linkedin.com/feed/")
        return soup.find("title")
'''

if __name__=="__main__":
    configuration = dotenv_values(".env")
    parser = LinkedInParser(configuration['USERNAME'], configuration['PASSWORD'])
    PostID_list = [
        '3339972659',
        "3318210330",
        '3312249250',
        '3313305148',
        '3333564529',
        '3333558620',
    ]
    # for i in range(20):
    #     PostID_list.append(str(int(PostID_list[-1])+random.randint(-1000,1000)))
    post_cache=[]
    company_cache=[]
    for PostID in PostID_list:
        results = parser.scrape_posting(PostID, parsing_library="html5lib", filter_path="selenium-client.post")
        # post_cache.update({PostID:results})
        post_cache.append(results[0])
        company_cache.append(results[1])
        # data.update(parser.scrape_posting(data['Company_URL'], "selenium-client.post"))
        # time.sleep(5)
    # print(post_cache)
    post_df = pd.DataFrame(post_cache).set_index("PostID")
    company_df = pd.DataFrame(company_cache).set_index("Company_Name")
    post_df['error_count']=post_df['errors'].apply(len)
    print(post_df.head())
    post_df.to_csv("post_csv.csv", mode="w", encoding="utf-8", index_label="PostID")
    company_df.to_csv("company_csv.csv", mode="w", encoding="utf-8", index_label="Company_Name")