from .config.filter_methods import platform_filters, testing_platform_filters
from .config.cleaning_methods import cleaning_methods, decode_mime_stuff
from .config.validation_methods import validation_methods
from .linkedin_parser import LinkedInParser
from .Local_Database import Local_Database
import os, re, time, csv
import pandas as pd
import numpy as np
from .email_parser import Listener
import requests
from bs4 import BeautifulSoup
from dotenv import dotenv_values

class Parser:
    def __init__(self, working_dir=None, filter_methods=None, cleaning_methods=None):
        self.working_dir = "data\\" if working_dir is None else working_dir
        self.filters = filter_methods
        # self.DB=Local_Database(schema_tables)
        self.read_email_subjects = set()
        configuration = dotenv_values(".env")
        self.parser = LinkedInParser(configuration['USERNAME'], configuration['PASSWORD'])
    def load_from_backup_csv(self, directory=None, limit=None):
        '''
        Syncs from (local) db.
        params:
            directory  str()    file path to load backup data from. Default is "{working_dir}\data\export\DB"
        
        ''' 
        
        target_dir = directory if directory is not None else self.working_dir+"exported_files\\"
        try:
            file_list = os.listdir(target_dir)
        except FileNotFoundError:
            return "File not Found"
        file_filter = lambda x: True if "_df.csv" in x else False
        filtered_list = filter(file_filter, file_list)
        self.db = {}
        if limit is not None and isinstance(limit,int): #makes testing easier.
            filtered_list=filtered_list[:limit]
        
        for df_csv in filtered_list:
            label = df_csv.replace("_df.csv", "")
            path = target_dir+df_csv
            imported_df = pd.read_csv(path)
            self.db.update({label:imported_df})
            print(f"Imported {label} from {path}.\nContents:", self.db[label].head(), sep="\n", end="\n-------------------------------------------------------------------------------------------------------")
    def update_local_from_eml(self, input_dir = None, limit=None):
        '''
        Control function. 
        Scans an input directory and loads parsed data to the database.
        Load -> Classify/Scan -> Parse -> Clean -> Transform -> Load -> Export
        '''
        input_dir = self.working_dir+'input_files\\' if input_dir==None else input_dir
        file_list = os.listdir(input_dir)
        cached_data = {'companies':[]}
        if limit is not None and isinstance(limit,int): #makes testing easier
            file_list=file_list[:min(limit,len(file_list)-1)] #slices the list to size 
        for file_name in file_list:
            #TODO Needs error handling
            file_path = input_dir+file_name
            print("file path:",file_path)
            file_data = self.scan_file(file_path) #classify the application
            print("file data:",file_data)
            results = self.add_features(file_data) if file_data['update_type']=="applicant" else file_data #scrape html and add data to set
            application_data = results[0] if len(results)==2 else results
            company_data = results[1] if len(results)==2 else None
            print("application data", application_data)
            # cleaned_data = self.clean_data(application_data) #cleans the data and separates data into the correct buckets
            # print("cleaned data", cleaned_data)
            if True or application_data['valid']==True: #TODO Get rid of this tautology.
                if application_data['update_type'] in cached_data.keys():
                    cached_data[application_data['update_type']].append(application_data)
                    if company_data!= None:
                        cached_data['companies'].append(company_data)
                else: # 
                    cached_data[application_data['update_type']]=[application_data]
                    if company_data!= None:
                        cached_data['companies'].append(company_data)
            else:
                print(f"Data validation error for {file_path}: {application_data['valid']}")
        # df = pd.DataFrame(cached_data['applicant'])
        db = self.merge_df(cached_data)
        self.export(db)
        # cleaned_df = self.clean_data(db)
        # print(cleaned_df)
        # # post_df, company_df = self.parse_companies(cleaned_df) #TODO MAKE THIS STEP BEFORE cached_data IS UTILIZED.
        # validated_data = self.validate_data(cached_data) #removes null values and duplicates before database insertion
        # self.DB.update_db(validated_data)
        
    def scan_file(self,file_path):   
        file = open(file_path, 'r', encoding = 'utf-8')
        file_contents = file.read() 
        file.close()
        
        data = {}
        # self.parse_emails("All",input_dir=file)
        platform_filters=testing_platform_filters
        for platform in platform_filters.keys():
            # if platform_filters[platform]['match'](file_contents):
            # try:
            features = {feature:platform_filters[platform]['eml']['scan'][feature](file_contents) for feature in platform_filters[platform]['eml']['scan']}
            print("Features: ", features)
            data.update(features)
            print("Data: ", data)
            # except Exception as e: #maybe look for a specific failure of match?
            #     print('The error is',e)
            #     continue
            if data['update_type'] in platform_filters[platform]['eml'].keys():
                more_features = {feature:platform_filters[platform]['eml'][data['update_type']][feature](file_contents) for feature in platform_filters[platform]['eml'][data['update_type']].keys()}
                data.update(more_features)
                # break
            # else:
                # continue
        return data
    def parse_companies(self, PostID,application_df=None):

        # PostID_list = [
        #     '3339972659',
        #     "3318210330",
        #     '3312249250',
        #     '3313305148',
        #     '3333564529', 
        #     '3333558620',
        # ]
        # PostID_list = application_df['PostID'].values
        # # for i in range(20):
        # #     PostID_list.append(str(int(PostID_list[-1])+random.randint(-1000,1000)))
        # cached_data=[]
        # cached_data=[]
        # for PostID in PostID_list:
        post_data = self.parser.scrape_posting(PostID, parsing_library="html5lib", filter_path="selenium-client.post")
            # cached_data.update({PostID:results})
            # cached_data.append(results[0])
            # cached_data.append(results[1])
            # data.update(parser.scrape_posting(data['Company_URL'], "selenium-client.post"))
            # time.sleep(5)
        # print(cached_data)
        # post_df = pd.DataFrame(cached_data).set_index("PostID")
        # company_df = pd.DataFrame(cached_data).set_index("Company_Name")
        # post_df['error_count']=post_df['errors'].apply(len)
        # print(post_df.head())
        time.sleep(1)
        # post_df.to_csv("post_csv.csv", mode="w", encoding="utf-8", index_label="PostID")
        # company_df.to_csv("company_csv.csv", mode="w", encoding="utf-8", index_label="Company_Name")
        # return post_df,company_df
        return post_data
        ...
    def add_features(self, input_data):
        '''create new columns from available data and utilizes the scrape_html helper function to parse job posting's html for more info'''
        #
        #scrapes html
        data = input_data
        print(data)
        parsed_features = self.scrape_html(input_data['url'])
        post_data = self.parser.scrape_posting(input_data['PostID'], parsing_library="html5lib", filter_path="selenium-client.post")
        company_data = self.parser.scrape_company_data(post_data)
        
        data.update(parsed_features)
        data.update(post_data)
        return [data, company_data]
    
    def scrape_html(self, URL, parsing_library=None):
        '''
        Parses job listings posted on LinkedIn using BeautifulSoup and a dictionary with key:method pairs for easy data object creation.
        '''
        parsing_library = "html5lib" if parsing_library==None else parsing_library
        html_text = requests.get(URL).text
        soup = BeautifulSoup(html_text, parsing_library)
        listing_filters = platform_filters['LinkedIn']['html'] #Eventually reference the url for platform information.
        html_data = {"errors":{}} #bucket for collected data
        for data_label in listing_filters: #loops through each data_label 
            try:
                html_data.update({data_label : listing_filters[data_label](soup)}) #applies filter to captured data and inserts the key-value pair into html_data
            except Exception as e:
                html_data.update({data_label : None}) #If error, fills in value with null
                html_data["errors"].update({data_label:e}) #
        return html_data
        # data = {key : listing_filters[key](soup) for key in listing_filters}
    def clean_data(self, input_df):
        '''cleans the data and separates data into the correct buckets'''
        df = input_df
        for method in cleaning_methods:
            df=method(df)
        return df
    def get_email(self, credPath):
        Listener.getEmails(credpath=credPath)
    def validate_data(self, df):
        modified_df = df
        for method in validation_methods:
            modified_df=method(df)
        
        return modified_df
    def parse_emails(self, source, cred_path=None, input_dir=None):
        source = source.upper()
        scanned_subjects_titles = []
        if source=="LOCAL" or source=="ALL":
            input_dir = self.working_dir + "input_files\\" if input_dir is None else input_dir
            raw_file_list = set(file_name.strip(".eml") for file_name in os.listdir(input_dir))
            filtered_file_list = list(raw_file_list.difference(self.read_email_subjects))
            for file_name in filtered_file_list:
                file_path = input_dir + file_name + ".eml"
                with open(file_path, 'r', encoding = 'utf-8') as file: 
                    pass
        if source=="GMAIL" or source=="ALL":
            cred_path = "models\\credentials.json" if cred_path is None else cred_path
    def merge_df(self, cached_data):
        # post_df = pd.DataFrame(cached_data).set_index("PostID")
        # company_df = pd.DataFrame(cached_data).set_index("Company_Name")
        db = {}
        # COPY THIS BUT IN MORE LINES # [pd.DataFrame(cached_data[item]).to_csv(f"{item}_df.csv", mode="w", encoding="utf-8") for item in cached_data.keys()]
        for item in cached_data.keys():
            db[item]=pd.DataFrame(cached_data[item])
            try:
                db[item]['error_count']=db[item]['errors'].apply(len)
            except:
                pass
            print(db[item].head())
        # post_df = pd.DataFrame(item)
        # post_df['error_count']=post_df['errors'].apply(len)
        # print(post_df.head())
        # time.sleep(5)
        # post_df.to_csv("post_csv.csv", mode="w", encoding="utf-8", index_label="PostID")
        # company_df.to_csv("company_csv.csv", mode="w", encoding="utf-8", index_label="Company_Name")
        return db
    def export(self, db=None, directory=None):
        db = self.db if db==None else db
        for item in db:
            print(f"{item} DB", db[item])
            target_dir = directory if directory is not None else self.working_dir+"db\\"
            file_path = target_dir+item
            db[item].to_csv(f"{file_path}_df.csv", mode="w", encoding="utf-8")
    def import_db(self,directory=None):
        target_dir = directory if directory is not None else self.working_dir+"exported_files\\"
        file_list = os.listdir(target_dir)
        file_filter = lambda x: True if "_df.csv" in x else False
        filtered_list = filter(file_filter, file_list)
        self.db = {}
        for df_csv in filtered_list:
            label = df_csv.replace("_df.csv", "")
            path = target_dir+df_csv
            imported_df = pd.read_csv(path)
            self.db.update({label:imported_df})
            print(f"\nImported {label} from {path}.\nContents:", self.db[label].head(), sep="\n", end="\n-----------------------------------------------------------------------------------------------------------------------------------------------------------\r\n")
            
        
if __name__=='__main__':
    # p = Parser(working_dir="data\\")
    # p.load_from_backup_csv("data\\output_files\\")
    # p.update_local_from_eml("data\\input\\")
    # p.get_email(credPath="\\dev\\config\\credentials.json")
    start = time.now()
    db = Local_Database()
    p = Parser(working_dir="data\\")
    p.load_from_backup_csv("data\\output_files\\")
    p.update_local_from_eml("data\\input_files\\")
    end = time.now()
    time_to_finish = end-start
    print(time_to_finish)
    # # p.get_email(credPath="\\dev\\config\\credentials.json")