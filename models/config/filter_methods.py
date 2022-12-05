import re
import pandas as pd
from bs4 import BeautifulSoup
from .cleaning_methods import decode_mime_stuff, str_strip
from .CONSTS import DATE_FORMAT
import datetime as dt



'''
Contains all the parsing methods for email and website scraping.


'''



platform_filters = {
    'LinkedIn': {
        'match' : lambda x : re.search(x,re.compile(r"X-LinkedIn-Template: (\D+_?)_")), 
        'scan' : {
            'date'        : lambda x : dt.datetime.strptime(re.search(re.compile('Date: \D{3}, (.+ \+0000 \(UTC\))', flags = re.DOTALL),x).group(1),'%d %b %Y %H:%M:%S %z (%Z)').strftime(DATE_FORMAT), #standard to gmail format; gets datetime of email sent
            'update_type' : lambda x : re.search(r"X-LinkedIn-Template: (\D+_?)_", x).group(1).split("_")[-1], #type of email update
            # 'title' : lambda x : re.search(x,r''), #title of job posting
            # 'company' : lambda x : re.search(x,r''), #company name
        },
        'applicant' : {
            'jobID'    : lambda x : re.search( r'View job: https:(\S+&jobId=3D(\w+))' , x, flags = re.DOTALL ).group(2), #grabs url string for job posting; used to scrape post for listing information. Only if application type
            'url'      : lambda x : 'https://www.linkedin.com/jobs/view/{}/'.format( re.search( r'View job: https:(\S+&jobId=3D(\w+))' , x, flags = re.DOTALL ).group(2) ), #grabs url string for job posting; used to scrape post for listing information. Only if application type
            'title'    : lambda x : re.search(re.compile(r"Subject: (You applied for (.+))MIME", flags=re.DOTALL), x.replace("_"," ").replace("=?UTF-8?Q?","").replace("?=","")).group(1), #TODO fix all these replacements and strips to be a text cleaning operation or something.
            'position' : lambda x : re.search(re.compile(r"Subject: (You applied for (.+))MIME", flags=re.DOTALL), x.replace("_"," ").replace("=?UTF-8?Q?","").replace("?=","")).group(2).split(" at ")[0],
            'company'  : lambda x : re.search(re.compile(r"Subject: (You applied for (.+))MIME", flags=re.DOTALL), x.replace("_"," ").replace("=?UTF-8?Q?","").replace("?=","")).group(2).split(" at ")[1],
        },
        'viewed' : {
            'title'    : lambda x : re.search(re.compile(r"Subject: (Your application for (.+))MIME", flags=re.DOTALL), x.replace("_"," ").replace("=?UTF-8?Q?","").replace("?=","")).group(1),
            'position' : lambda x : re.search(re.compile(r"Subject: (Your application for (.+))MIME", flags=re.DOTALL), x.replace("_"," ").replace("=?UTF-8?Q?","").replace("?=","")).group(2).split(" was viewed by ")[0],
            'company'  : lambda x : re.search(re.compile(r"Subject: (Your application for (.+))MIME", flags=re.DOTALL), x.replace("_"," ").replace("=?UTF-8?Q?","").replace("?=","")).group(2).split(" was viewed by ")[1]
        },
        'rejected' : {
            'title'    : lambda x : re.search(re.compile(r"Subject: (Your application to (.+))MIME", flags=re.DOTALL), x.replace("_"," ").replace("=?UTF-8?Q?","").replace("?=","")).group(1),
            'position' : lambda x : re.search(re.compile(r"Subject: (Your application to (.+))MIME", flags=re.DOTALL), x.replace("_"," ").replace("=?UTF-8?Q?","").replace("?=","")).group(2).split(" at ")[0],
            'company'  : lambda x : re.search(re.compile(r"Subject: (Your application to (.+))MIME", flags=re.DOTALL), x.replace("_"," ").replace("=?UTF-8?Q?","").replace("?=","")).group(2).split(" at ")[1],
        },
        'html' : {
            "Company_URL"       : lambda x: x.find("a",{"data-tracking-control-name" :"public_jobs_topcard-org-name"})['href'].split("?")[0],
            "Position_Tags"     : lambda x: [result.text.strip() for result in x.find_all("span",class_="description__job-criteria-text description__job-criteria-text--criteria")],
            # "Top_Position_Tags" :lambda x: [result.text.strip() for result in x.find_all("li",class_="jobs-unified-top-card__job-insight")],
            "Posted_Time"       : lambda x: x.find("span", class_="posted-time-ago__text topcard__flavor--metadata").text.strip(),
            "Location"          : lambda x: x.find("span", class_="topcard__flavor topcard__flavor--bullet").text.strip(),
            "Number_Applicants" : lambda x: x.find("span", class_="num-applicants__caption topcard__flavor--metadata topcard__flavor--bullet").text.replace(" applicants","").strip(),
            "Recruiter_Profile" : lambda x: x.find("a", class_="message-the-recruiter__cta"),
            "Post_Body"         : lambda x: x.find("div", class_="show-more-less-html__markup show-more-less-html__markup--clamp-after-5").text.strip(),
        }, # <-- LIKE THIS
        
    },
    # 'ZipRecruiter' : {
    #     'classifier' : lambda x : re.compile(r''),
    #     'date_filter' : lambda x : re.compile(r''),
    #     'url_filter' : lambda x : re.compile(r''),
    #     'type_filter' : lambda x : re.compile(r''),
    # },
    # 'Other' : {
    #     'classifier' : lambda x : re.compile(r''),
    #     'date_filter' : lambda x : re.compile(r''),
    #     'url_filter' : lambda x : re.compile(r''),
    #     'type_filter' : lambda x : re.compile(r''),
    # }
}




def get_employee_distribution(url):
    # URL: https://www.linkedin.com/company/{company_name}/insights/
    # Requires LinkedIn Premium
    # Charts:
        # Total employee count - Time Series (Line)
        # Employee distribution and headcount growth by function - Pie Chart with slicer
        # New Hires - Time Series (Column)
        # Notable company alumni - Senior Execs
        # Total job openings - Categorical (Donut)
    # Targeting "div", class_="org-premium-container premium-accent-bar artdeco-card"
    # These are the graphs 
    ...




    
testing_platform_filters = {
    'LinkedIn': {

        'eml': {
            'match' : lambda x : re.search(x,re.compile(r"X-LinkedIn-Template: (\D+_?)_")), 
            'scan' : {
                'date'        : lambda x : dt.datetime.strptime(re.search(re.compile('Date: \D{3}, (.+ \+0000 \(UTC\))', flags = re.DOTALL),x).group(1),'%d %b %Y %H:%M:%S %z (%Z)').strftime(DATE_FORMAT), #standard to gmail format; gets datetime of email sent
                'update_type' : lambda x : re.search(r"X-LinkedIn-Template: (\D+_?)_", x).group(1).split("_")[-1], #type of email update
                # 'title' : lambda x : re.search(x,r''), #title of job posting
                # 'company' : lambda x : re.search(x,r''), #company name
            },
            'applicant' : {
                'PostID'   : lambda x : re.search( r'View job: https:(\S+&jobId=3D(\w+))' , x, flags = re.DOTALL ).group(2), #grabs linked-in PostID for 
                'url'      : lambda x : 'https://www.linkedin.com/jobs/view/{}/'.format( re.search( r'View job: https:(\S+&jobId=3D(\w+))' , x, flags = re.DOTALL ).group(2) ), #grabs url string for job posting; used to scrape post for listing information. Only if application type
                'title'    : lambda x : decode_mime_stuff(re.search(re.compile(r"Subject: ((\=\?UTF-8\?Q\?)?You[\s_]applied[\s_]for[\s_](.+))MIME", flags=re.DOTALL), x).group(1)), #TODO fix all these replacements and strips to be a text cleaning operation or something.
                'position' : lambda x : decode_mime_stuff(re.search(re.compile(r"Subject: ((\=\?UTF-8\?Q\?)?You[\s_]applied[\s_]for[\s_](.+))MIME", flags=re.DOTALL), x).group(1)).split(" at ")[0],
                'company'  : lambda x : decode_mime_stuff(re.search(re.compile(r"Subject: ((\=\?UTF-8\?Q\?)?You[\s_]applied[\s_]for[\s_](.+))MIME", flags=re.DOTALL), x).group(1)).split(" at ")[1],
            },
            'viewed' : {
                'PostID'   : lambda x : re.search(re.compile(r'jobPostingId%3D(\d{10})%26pivotType%3Dsim', flags = re.DOTALL),x).group(1),
                'title'    : lambda x : decode_mime_stuff(re.search(re.compile(r"Subject: ((\=\?UTF-8\?Q\?)?Your[\s_]application[\s_]for[\s_](.+))MIME", flags=re.DOTALL), x).group(1)),
                'position' : lambda x : decode_mime_stuff(re.search(re.compile(r"Subject: ((\=\?UTF-8\?Q\?)?Your[\s_]application[\s_]for[\s_](.+))MIME", flags=re.DOTALL), x).group(1)).split(" was viewed by ")[0],
                'company'  : lambda x : decode_mime_stuff(re.search(re.compile(r"Subject: ((\=\?UTF-8\?Q\?)?Your[\s_]application[\s_]for[\s_](.+))MIME", flags=re.DOTALL), x).group(1)).split(" was viewed by ")[1]
                
            },
            'rejected' : {
                'original_date_applied' : lambda x: dt.datetime.strptime(re.search(re.compile(r"Applied on (\w{3,9} \d{1,3}, \d{4})"),x).group(1),'%B %d, %Y').strftime(DATE_FORMAT),
                'title'    : lambda x : decode_mime_stuff(re.search(re.compile(r"Subject: ((\=\?UTF-8\?Q\?)?Your[\s_]application[\s_]to[\s_](.+))MIME", flags=re.DOTALL), x).group(1)),
                'position' : lambda x : decode_mime_stuff(re.search(re.compile(r"Subject: ((\=\?UTF-8\?Q\?)?Your[\s_]application[\s_]to[\s_](.+))MIME", flags=re.DOTALL), x).group(1)).split(" at ")[0],
                'company'  : lambda x : decode_mime_stuff(re.search(re.compile(r"Subject: ((\=\?UTF-8\?Q\?)?Your[\s_]application[\s_]to[\s_](.+))MIME", flags=re.DOTALL), x).group(1)).split(" at ")[1],
            },
        }, 
        'email': {
            'match' : lambda x : "X-LinkedIn-Template" in x['headers'].keys(),
            'scan' : {
                'date'        : lambda x : lambda x : dt.datetime.strptime(re.sub(r"\s\(\w{3}\)","", x['headers']['Received'].split(';')[1].split(",")[1].strip()), '%d %b %Y %H:%M:%S %z').strftime(DATE_FORMAT), #standard to gmail format; gets datetime of email sent
                'update_type' : lambda x : re.search(r'jobs?_appli\w{4,6}_([a-z]+)', x['headers']['X-LinkedIn-Template']).group(1), #type of email update
                'subject'     : lambda x : decode_mime_stuff(x['headers']['Subject']).replace(",","").replace(".","").replace("&", "and").split(":")[0],
                # 'title' : lambda x : re.search(x,r''), #title of job posting
                # 'company' : lambda x : re.search(x,r''), #company name
            },
            'applicant' : {
                'PostID'   : lambda x : re.search(r"(\d{10})",x['body'].find("a", href=re.compile(r"https://www.linkedin.com/comm/jobs/view/"))['href']).group(1),
                'url'      : lambda x : 'https://www.linkedin.com/jobs/view/{}/'.format(re.search(r"(\d{10})",x['body'].find("a", href=re.compile(r"https://www.linkedin.com/comm/jobs/view/"))['href']).group(1)),
                'position' : lambda x : x['subject'].split(" at ")[0],
                'company'  : lambda x : x['subject'].split(" at ")[1],
            },
            'viewed' : {
                'PostID'   : lambda x : re.search(re.compile(r'jobPostingId%3D(\d{10})%26pivotType%3Dsim', flags = re.DOTALL), x['body']).group(1),
                'position' : lambda x : x['subject'].split(" was viewed by ")[0],
                'company'  : lambda x : x['subject'].split(" was viewed by ")[0],
            },
            'rejected' : {
                'original_date_applied' : lambda x: dt.datetime.strptime(re.search(re.compile(r"Applied on (\w{3,9} \d{1,3}, \d{4})"),x['body']).group(1),'%B %d, %Y').strftime(DATE_FORMAT),
                'position' : lambda x : x['subject'].split(" at ")[0],
                'company'  : lambda x : x['subject'].split(" at ")[1],
            },

        },
        'html' : {
            "Company_URL"       : lambda x: x.find("a",{"data-tracking-control-name" :"public_jobs_topcard-org-name"})['href'].split("?")[0], #//*[@id="ember25
            "Position_Tags"     : lambda x: [str_strip(result) for result in x.find_all("span",class_="description__job-criteria-text description__job-criteria-text--criteria")],
            # "Top_Position_Tags" :lambda x: [result.text.strip() for result in x.find_all("li",class_="jobs-unified-top-card__job-insight")],
            "Posted_Time"       : lambda x: str_strip(x.find("span", class_="posted-time-ago__text topcard__flavor--metadata").text),
            "Location"          : lambda x: str_strip(x.find("span", class_="topcard__flavor topcard__flavor--bullet").text),
            "Number_Applicants" : lambda x: int(str_strip(x.find("span", class_="num-applicants__caption topcard__flavor--metadata topcard__flavor--bullet").text.replace(" applicants",""))),
            "Recruiter_Profile" : lambda x: x.find("a", class_="message-the-recruiter__cta"),
            "Post_Body"         : lambda x: x.find("div", class_="show-more-less-html__markup show-more-less-html__markup--clamp-after-5").text,
            "Premium-Skills"    : lambda x: [str_strip(result.p.text) for result in x.findall("li", class_="jobs-premium-applicant-insights__list-skill-item")],
            "Premium-Number_Applicants": lambda x: x.find("span", class_="jobs-premium-applicant-insights__list-num t-18 t-bold pr2").text.strip(),
            "Premium-Salary"    : lambda x: x.find("a", class_="app-aware-link ", href="#SALARY").text.strip(),
            "Workplace_Type"    : lambda x: x.find("span", class_="jobs-unified-top-card__workplace-type").text.strip(),
            
            
        },
        'selenium-client': {
            "post" : { #Change all of these for selenium
                "Date_Scanned"      : dt.datetime.now(),
                "Company_Name"      : lambda x: x.find("span", class_="jobs-unified-top-card__company-name").a.text,
                "Company_URL"       : lambda x: "https://www.linkedin.com" + x.find("span", class_="jobs-unified-top-card__company-name").a['href'].replace("life/", ""), #/html/body/div[6]/div[3]/div/div[1]/div[1]/div/div[1]/div/div/div[1]/div[1]/span[1]/span[1]/a ////// '//*[@id="ember25"]'
                "Number_Applicants" : lambda x: int(x.find("span", class_=re.compile(r"^jobs-unified-top-card__applicant-count")).text.replace(" applicants","").strip()),
                "Workplace_Type"    : lambda x: str_strip(x.find("span", class_="jobs-unified-top-card__workplace-type").text),
                "Top_Card_Contents" : lambda x: str_strip(x.find("div", class_="p5").text),#" · ".join(x.find("div", class_="p5").find_all("text")).split(" · "),
                "Position_Tags"     :  lambda x: " · ".join([" ".join([str_strip(element) for element in result.span.find_all(text=True)]) for result in x.find_all("li", class_="jobs-unified-top-card__job-insight")]).split(" · "), #" . ".join([" · ".join(content.find_all("text")) for content in x.find_all("li", class_="jobs-unified-top-card__job-insight")]).split(" · "),
                # "Posted_Time"       :  ...,
                # "Location"          :  ...,
                "Premium_Other_Applicant_Info" :  lambda x: [str_strip(" ".join([element.text for element in content.find_all("span")])).replace(" a ","").split(r" % have") for content in x.find_all("li", class_="jobs-premium-applicant-insights__list-item")],
                # "Recruiter_Profile" :  ...,
                "Post_Body"         :  lambda x: [content for content in x.find("article", class_="jobs-description__container").div.div.span],
                "Premium-Skills"    :  lambda x: [str_strip(skill.p.text) for skill in x.find_all("li", class_="jobs-premium-applicant-insights__list-skill-item")],
                "Premium-Skills_Possessed": lambda x: x.find("div", class_="jobs-details-premium-insight jobs-details-premium-insight--row top-skills").p.span.text.replace(" most common skills","").split(" out of the ")[0],
                # "Premium-Number_Applicants":  ...,
                "Premium-Salary"    : lambda x: " · ".join([str_strip(x.find("div", id="SALARY").find("div", class_="mt4").p.text), str_strip(x.find("div", class_="jobs-salary-main-rail-card__salary-label-container").p.text)]).split(" · "),
                "Closed"            : lambda x: True if x.find("span", class_="artdeco-inline-feedback__message").text else False,
            },
            "company" : {
                "Home": {
                    "Ticker_Symbol": lambda x: x.find("div", class_="org-stockquote-info__content-left").span.text,
                    "Follower_Count": lambda x: x.find(string=re.compile("\d followers")),#x.find_all("div", class_="org-top-card-summary-info-list__info-item", text=re.compile(r"\d\sfollowers"))
                },
                "About": {
                    "Company_Website" : lambda x: x.find("a", class_="ember-view org-top-card-primary-actions__action", href=True)['href'],
                    "Overview" : lambda x: x.find("section", class_="artdeco-card p5 mb4").p.text,
                    "Info_Tags" : lambda x: [text for text in [str_strip(item) for item in x.find("dl", class_="overflow-hidden").find_all(text=True)] if text!=''], #includes labels and info. Needs postprocessing.
                    # "Phone":...,
                    # "Headquarters":...,
                    # "Year_Founded":...,
                    # "Specialties":...,
                    "Locations": lambda x: x.find("g", class_="highcharts-markers highcharts-series-1").find_all("path"), #Geographic data. I don't know how to parse this yet.
                },
                # "Insights": { #these are graphs! Cool! Probably need functions instead of lambdas.
                #     "Count_timeseries":...,
                #     "Employee_Distribution_proportions":...,
                #     "New_Hires_timeseries":...,
                #     "Openings_By_Dept":...,
                    
                # },
                # "Jobs": {},
            }
            
        },
    },
} #TODO REMOVE ME WHEN WORKING ON OTHER FILTERS
'''    /html/body/div[6]/div[3]/div/div[1]/div[1]/div/div[2]/article/div/div[1]/span/p[1]


#li class="jobs-unified-top-card__job-insight"
li[1]/span/a/text() #$115,000/yr - $120,000/yr
li[1]/span/text()   # "· Full-time · Mid-Senior leve"
li[2]/span/text()   #1,001-5,000 employees · Pharmaceutical Manufacturing
'''
    # 'ZipRecruiter' : {
    #     'classifier' : lambda x : re.compile(r''),
    #     'date_filter' : lambda x : re.compile(r''),
    #     'url_filter' : lambda x : re.compile(r''),
    #     'type_filter' : lambda x : re.compile(r''),
    # },
    # 'Other' : {
    #     'classifier' : lambda x : re.compile(r''),
    #     'date_filter' : lambda x : re.compile(r''),
    #     'url_filter' : lambda x : re.compile(r''),
    #     'type_filter' : lambda x : re.compile(r''),
    # },
# } TODO UNCOMMENT THIS



DATE_FORMAT = '%Y-%m-%d %H:%M:%S %Z'

DEFAULT_FILTER = testing_platform_filters

def get_filter_set(filter_path, filter_library=None):
    '''
    Slices the filter method dictionaries 
    "Platform.parsing_typelabel:method
    
    '''
    if filter_library is None:
        filter_library=DEFAULT_FILTER
    
    # parsing_methods = self.default_filter_dict
    parsing_methods = filter_library
    for slicer in filter_path.split("."):
        try:
            parsing_methods = parsing_methods[slicer]
        except Exception as e:
            
            break
    return parsing_methods