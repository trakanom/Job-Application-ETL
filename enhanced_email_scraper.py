import email
from email.mime import application
import os
import re
import pandas as pd

def __init__(self):
    self.application_history=pd.DataFrame()
    self.scanned_files=pd.DataFrame()
    self.job_listings=pd.DataFrame()
    self.company_list=pd.DataFrame()
    

def match_job(self, position, company):
    '''
    Matches positon and company to a JobID
    '''
    for JobID in self.applied_jobs.keys(): #
        if self.applied_jobs[JobID][company]==company and self.applied_jobs[JobID][position]==position:
            return JobID
    #Checking entry against application history, making sure company position match, and that the application wasn't already rejected.
    #Unless we're doing this out of order? In which case maybe we should only check that this update is dissimilar from the others
    filter_df = (self.application_history['Company']==company) & (self.application_history['position']==position & (self.application_history['date_rejected']==None)
    matches = self.application_history[filter_df]
    match_count = len(matches.index)
    match match_count: #match found
        case 1:
            # Match found
            print("Match found")
        case 0:
            # None found
            print("No matches")
        case _:
            # Multiple found
            print("Uh oh, multiple applications. Match to application date!")
    # match company to CompanyID
    # {JobID: {CompanyID, Title, Role, ApplicationURL, DateApplied}}
    # lookup_val = "(Company,Title)"
    # self.YellowPages = {"(Company,Title)": JobID, CompanyID, PostURL}
    # If lookup_val in self.YellowPages:
    #   return self.YellowPages[lookup_val]["JobID"]
    # else:
    #   self.YellowPages[lookup_val]["JobID"]=self.JobID.next()
    #   return self.JobID.next()
def update_from_local(self, data_directory=None, debug=False): 
    '''
    Searches through data_directory for newly downloaded job listings in HTML, then places the places them into database via JSON.
    '''
    data_directory = self.working_dir if data_directory==None else data_directory
    #get list of all html files in directory as all_files
    #find the left outer join between all_files and set(self.read_filenames.values())
    
    file_list = set(os.listdir(data_directory))
    unread_files = list(file_list.difference(self.read_filenames)).sort()
    uncaught = []
    for file_name in unread_files:
        eml_file = open(self.working_dir+file_name, 'r', encoding='utf-8')
        file_contents = eml_file.read()
        eml_file.close()

        type_filter = re.compile(r"X-LinkedIn-Template:((\W_?)+)")
        filtered = re.search(type_filter,file_contents).group(1)
        email_type = filtered[-1] #EMAIL TYPE
        
        date_filter=re.compile('Date: .+\(UTC\)', flags=re.DOTALL)
        date = re.search(date_filter,file_contents).group().strip("Date: ") #DATE
        
        
        match email_type:
            case 'application':
                subj_filter = re.compile(r"You applied for(.+)\.eml",flags=re.DOTALL) #SUBJECT FILTER
                url_filter=re.compile(r'View job: https:(\S+&jobId=(\w+))', flags=re.DOTALL) #JOB URL FILTER
                captured = re.match(subj_filter, file_name).group(0)
                PostID = re.search(url_filter, file_contents).group(1) #LinkedIn Post ID
                
                Position, Company = captured.split(" at ") #POSITION, COMPANY
                PostURL = f'https://www.linkedin.com/jobs/view/{PostID}/' #JOB URL
                
            case 'viewed':
                subj_filter = re.compile(r"Your application for (.+)\.eml",flags=re.DOTALL)
                captured = re.match(subj_filter, file_name).group(0)
                Position, Company = captured.split(" was viewed by ")
                JobID = self.match_job(Position,Company)
            case 'rejected':
                subj_filter = re.compile(r"Your application to (.+)\.eml",flags=re.DOTALL)
                captured = re.match(subj_filter, file_name).group(0)
                Position, Company = captured.split(" at ")
                JobID = self.match_job(Position,Company)
            case 'interview_request':
                #There is no easy filter for this category.
                #Most of the interview requests come from each business instead of linkedin
                #Perhaps we can check if the emailer mentions the position/company (likely, but unstuctured)
                #Look for verbage such as 'schedule','interview', etc
                #Perhaps calendly links?
                #For now, mostly manual

                Position, Company = self.match_job(Position, Company)
            case _:
                print("Uncaught file type:",file_name)
                uncaught.append(file_name)
                
        match_entry = self.match_job(Company,Position)
        application_data = {
            'JobID': self.match(Company,Position)['JobID'],
            'PostURL': PostURL if email_type=='application' else match_entry['PostURL'], #
            'Company': Company,
            'Positition': Position,
            # 'TitleID':..., #make dim table relating title to position based on matching rate
            'application_date': date if email_type == 'application v ' else None,
            'viewed_date': date if email_type == 'viewed' else None,
            'callback_date': None,
            'interview_request_date': date if email_type == 'interview_request' else None,
            'interview_date': ...,
            'technical_interview_date': ...,
            'more_interview_dates': [],
            'rejected_date': date if email_type == 'rejected' else None,
            'offer_date': ...,
            'accepted_date': ...,
        }
        
        
        company_data = {
            "CompanyID":...,
            "CompanyName":...,
            "Title":...,
            "TitleID":...,
            
        }
        
        #rudimentry classifier
        if email_type == 'application':
            scanned_info = self.scan_new_application(file,file_contents,debug)
            self.add_new_entries(scanned_info,"applied")
            if debug:
                print("SUCCESS: Added \"{}\" file to scanned:'{}' @ {}".format(file,scanned_info['position'], scanned_info['company']),"\n")
        elif email_type == 'viewed':
            scanned_info = self.scan_application_viewed(file,file_contents,debug)
            self.add_new_entries(scanned_info,"viewed")
        elif email_type == 'rejected':
            subj_filter = re.compile(f"Your application to (.+)\.eml",flags=re.DOTALL)
            captured = re.match(subj_filter, file_name).group(0)
            self.add_new_entries(scanned_info,"rejected")
        else:
            print("Error: No matches ({file})")




def scan_new_application(self, file_name, file_contents, debug=False):
    #Get Date
    date_filter=re.compile(r'Date: .+\(UTC\)', flags=re.DOTALL) #DATE FILTER
    date = re.search(date_filter,file_contents).group().strip("Date: ") #DATE
    

    #Get Title & Company
    prefix = "You applied for " #SUBJECT PREFIX
    m = re.compile(r"\bYou applied for(.+\).eml",flags=re.DOTALL) #SUBJECT FILTER
    if re.match(m, file_name):
        if debug:
            print(f"easy way worked!")
        Subject = file_name[:-4] #SUBJECT
        Position, Company = Subject[len(prefix):].split(" at ") #POSITION, COMPANY
    else:
        if debug:
            print(f"easy way failed:::{file_name}")
        try:
            p=re.compile(r"Subject: You applied for (.+)MIME", flags=re.DOTALL)
            match = re.search(p,file_contents)
            Subject = match.group().replace('\n','').strip('MIME')
            prefix = "Subject: You applied for"
            Position, Company = Subject[len(prefix):].split(" at ") #POSITION, COMPANY
        except:
            p=re.compile(r"Subject: (.+)MIME", flags=re.DOTALL)
            match = re.search(p,file_contents)
            if debug:
                print("It broke. ",file_name)
            Subject = match.group().replace('\n','').replace('_'," ").strip('MIME')
            Position, Company = Subject[25:].split(" at ") #POSITION COMPANY

    #Get Job URL
    h=re.compile(r'View job: https:(\S+(&jobId=\w+))', flags=re.DOTALL) #JOB URL FILTER
    j=re.compile('&jobId=\w+') #JOB ID FILTER
    match2 = re.search(h,file_contents)
    match3 = re.search(j, match2.group())
    stored2 = match3.group().strip('&jobId=')[2:] #URL CLEANER
    JobURL = f'https://www.linkedin.com/jobs/view/{stored2}/' #JOB URL
    
    
    
    data = {
        'jobID':self.JobID.iter(),
        'file_name':file_name,
        'subject':Subject,
        'position': Position,
        'company': Company,
        'postURL': JobURL,
        'date_applied': date,
        'date_viewed':None,
        'date_rejected':None,
    }
    if debug:
        print("DATA: ",data)
    return data

def scan_application_viewed(self, file_name, file_contents, debug=False):
    # Definitely can consolidate all these categories into one function. Debugging first, though.
    date_filter=re.compile('Date: .+\(UTC\)', flags=re.DOTALL)
    date = re.search(date_filter,file_contents).group().strip("Date: ")
    Subject = file_name.replace("..",".")[:-4]
    prefix = "Your application for "  
    m = re.compile(f"Your application for (.+)\.eml",flags=re.DOTALL)
    re.match(m, file_name)
    Position, Company = Subject[len(prefix):].split(" was viewed by ")
    data = {
        'jobID':self.jobID.next() if email_type=='applied' else self.jobID,
        'file_name':file_name,
        'subject':Subject,
        'position': Position,
        'company': Company,
        'date_applied':date if email_type=='applied' else None,
        'date_viewed': date if email_type=='viewed' else None,
        'date_rejected': date if email_type=='rejected' else None,
    }
    return data

def scan_application_rejected(self, file_name, file_contents, debug=False):
    # Definitely can consolidate all these categories into one function. Debugging first, though.
    date_filter=re.compile('Date: .+\(UTC\)', flags=re.DOTALL)
    date = re.search(date_filter,file_contents).group().strip("Date: ")
    Subject = file_name[:-4]
    prefix = "Your application to "
    m = re.compile(f"Your application to (.+)\.eml",flags=re.DOTALL)
    if re.match(m, file_name):
        if debug:
            print(f"easy way worked!")
        Position, Company = Subject[len(prefix):].split(" at ")
    data = {
        'file_name':file_name,
        'subject':Subject,
        'position': Position,
        'company': Company,
        
    }
    return data