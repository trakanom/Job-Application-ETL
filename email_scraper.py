import sys
import os
import re
import csv
import urllib.request


class HTML_Scraper:
    def __init__(self, working_directory, debug=False):
        self.working_dir = working_directory
        self.read_filenames = set()
        self.scraped_htmls = set()
        self.JobID=jobID()
        self.applied_jobs = []
        self.posted_jobs = []
        self.debug=debug

    def scan_new_application(self, file_name, file_contents, debug=False):
        if debug|self.debug:
            print("~~DEBUG~~:")

        #Get Date
        date_filter=re.compile('Date: .+\(UTC\)', flags=re.DOTALL)
        date = re.search(date_filter,file_contents).group().strip("Date: ")
        

        #Get Title & Company
        prefix = "You applied for "
        m = re.compile(f"{prefix}.+\.eml",flags=re.DOTALL)
        if re.match(m, file_name):
            if debug|self.debug:
                print(f"easy way worked!")
            Subject = file_name[:-4]
            Position, Company = Subject[len(prefix):].split(" at ")
        else:
            if debug|self.debug:
                print(f"easy way failed:::{file_name}")
            try:
                p=re.compile(r"Subject: You applied for (.+)MIME", flags=re.DOTALL)
                match = re.search(p,file_contents)
                Subject = match.group().replace('\n','').strip('MIME')
                prefix = "Subject: You applied for"
                Position, Company = Subject[len(prefix):].split(" at ")
            except:
                p=re.compile(r"Subject: (.+)MIME", flags=re.DOTALL)
                match = re.search(p,file_contents)
                if debug|self.debug:
                    print("It broke. ",file_name)
                Subject = match.group().replace('\n','').replace('_'," ").strip('MIME')
                Position, Company = Subject[25:].split(" at ")

        #Get Job URL
        h=re.compile('View job: https:(\S+=?)', flags=re.DOTALL)
        j=re.compile('&jobId=\w+')
        match2 = re.search(h,file_contents)
        match3 = re.search(j, match2.group())
        stored2 = match3.group().strip('&jobId=')[2:]
        JobURL = f'https://www.linkedin.com/jobs/view/{stored2}/'
        
        if debug|self.debug:
            if m:
                print(f"SUBJECT: {Subject}")
            if match2:
                print(f"POST_ID: {stored2}")
                print(f'POST_URL: https://www.linkedin.com/jobs/view/{stored2}/')
            print(f"DATE: {date}")
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
        if debug|self.debug:
            print("DATA: ",data)
        return data

    def scan_application_viewed(self, file_name, file_contents, debug=False):
        # Definitely can consolidate all these categories into one function. Debugging first, though.
        date_filter=re.compile('Date: .+\(UTC\)', flags=re.DOTALL)
        date = re.search(date_filter,file_contents).group().strip("Date: ")
        Subject = file_name.replace("..",".")[:-4]
        prefix = "Your application for "
        m = re.compile(f"{prefix}.+\.eml",flags=re.DOTALL)
        if re.match(m, file_name):
            if debug|self.debug:
                print(f"easy way worked!")
            Position, Company = Subject[len(prefix):].split(" was viewed by ")
        data = {
            'file_name':file_name,
            'subject':Subject,
            'position': Position,
            'company': Company,
            'date_viewed': date,
        }
        return data

    def scan_application_rejected(self, file_name, file_contents, debug=False):
        # Definitely can consolidate all these categories into one function. Debugging first, though.
        date_filter=re.compile('Date: .+\(UTC\)', flags=re.DOTALL)
        date = re.search(date_filter,file_contents).group().strip("Date: ")
        Subject = file_name[:-4]
        prefix = "Your application to "
        m = re.compile(f"{prefix}.+\.eml",flags=re.DOTALL)
        if re.match(m, file_name):
            Position, Company = Subject[len(prefix):].split(" at ")
            if debug|self.debug:
                print("easy way worked! {} at {}".format(Position,Company))
        data = {
            'file_name':file_name,
            'subject':Subject,
            'position': Position,
            'company': Company,
            'date_rejected': date,
        }
        return data

    def add_new_entries(self, payload, type, debug=False):
        if debug|self.debug:
            print(payload)
        if type=="applied":
            self.applied_jobs.append(payload)
        else:
            if debug|self.debug:
                print(self.applied_jobs)
            for index, application in enumerate(self.applied_jobs):
                if debug|self.debug:
                    print("APP:",application)
                    print("app",application['company'],".")
                    print("pay",payload['company'],".")
                    print("app",application['position'],".")
                    print("pay",payload['position'],".")
                if application['company']==payload['company']:
                    if debug|self.debug:
                        print("Checks out")
                    if application['position']==payload['position']:
                        if type=="rejected":
                            self.applied_jobs[index]['date_rejected']=payload['date_rejected']
                        if type=="viewed":
                            self.applied_jobs[index]['date_viewed']=payload['date_viewed']
                        if debug|self.debug:
                            print("Checks out")
                            print(self.applied_jobs[index])
                        break
                else:
                    pass
                    if debug|self.debug:
                        print("match error")

        self.read_filenames.add(payload['file_name'])

    def update_from_local(self, data_directory=None, debug=False): 
        '''
        Searches through data_directory for newly downloaded job listings in HTML, then places the places them into database via JSON.
        '''
        data_directory = self.working_dir+"input_eml_files\\" if data_directory==None else data_directory
        #get list of all html files in directory as all_files
        #find the left outer join between all_files and set(self.read_filenames.values())
        
        file_list = set(os.listdir(data_directory))
        difference = file_list-self.read_filenames
        unread_files = list(difference)
        unread_files.sort()
        if debug|self.debug:
            print(data_directory)
            print("File List:",file_list)
            print("Read Files",self.read_filenames)
            print("Diff: !!!!!!!!!!!!!!!!!!!!!!!", (file_list-self.read_filenames))
            print("Unread: ", unread_files)
            # unread_files = [] if unread_files is None else unread_files
        
        for file in unread_files:
            eml_file = open(data_directory+file, 'r', encoding='utf-8')
            file_contents = eml_file.read()
            eml_file.close()
            
            #checks for LinkedIn template types.
            application_filter = re.compile("X-LinkedIn-Template: jobs_applicant_applied")
            viewed_filter = re.compile("X-LinkedIn-Template: email_jobs_job_application_viewed")
            rejected_filter = re.compile("X-LinkedIn-Template: email_jobs_application_rejected")
            
            #rudimentry classifier
            if re.search(application_filter,file_contents):
                scanned_info = self.scan_new_application(file,file_contents,debug)
                self.add_new_entries(scanned_info,"applied")
                if debug|self.debug:
                    print("SUCCESS: Added \"{}\" file to scanned:'{}' @ {}".format(file,scanned_info['position'], scanned_info['company']),"\n")
            elif re.search(viewed_filter,file_contents):
                scanned_info = self.scan_application_viewed(file,file_contents,debug)
                self.add_new_entries(scanned_info,"viewed")
            elif re.search(rejected_filter,file_contents):
                scanned_info = self.scan_application_rejected(file,file_contents,debug)
                self.add_new_entries(scanned_info,"rejected")
            else:
                print(f"Error: No matches ({file})")

    def export_to_file(self, export_dir=None, debug=False):
        # print(self.applied_jobs)
        applied_jobs = self.applied_jobs
        applied_keys = applied_jobs[0].keys() if len(applied_jobs)>0 else []
        export_dir=self.working_dir+'output_files' if export_dir is None else export_dir
        with open(f'{export_dir}\\job_applications.csv','w',encoding='utf-8-sig',newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, applied_keys)
            dict_writer.writeheader()
            dict_writer.writerows(applied_jobs)
            if debug|self.debug:
                print("Exported read_files.py")
        
        with open(f'{export_dir}\\read_files.py','w',encoding='utf-8-sig',newline='') as output_file:
            output_file.write("read_files={")
            for entry in self.read_filenames:
                output_file.write("\""+entry+"\",")
            output_file.write("}")
            if debug|self.debug:
                print("Exported read_files.py")

    def import_from_file(self):
        #In progress
        # from read_files import read_files
        # self.read_filenames=read_files
        # print(len(self.read_filenames))
        pass

    def download_posting_html(self, download_directory=None, debug=False):
        download_dir=self.working_dir+'output_files\\scraped_data' if download_directory is None else download_directory
        for application in self.applied_jobs:
            jobID = application['jobID']
            postURL = application['postURL']
            try:
                urllib.request.urlretrieve(postURL, f"{download_dir}\\Job_{jobID}.html")
                if debug|self.debug:
                    print(f"Success! (ID:{jobID}={postURL})")
            except:
                with open(f"{download_dir}\\Job_{jobID}.html",'w',encoding='utf-8-sig',newline='') as output_file:
                    output_file.write("Null")
                    if debug|self.debug:
                        print(f"Error 404! (ID:{jobID}={postURL}) ")

    def parse_jobs_html(self,output_filepath=None, input_directory=None,debug=False):
        input_dir=self.working_dir+"\\scraped_data" if input_directory is None else input_directory
        output_dir= (self.working_dir+"\\output_files" if output_filepath is None else output_filepath) +"\\html_data" 
        file_list = set(os.listdir(input_dir))
        unread_files = list(file_list.difference(self.scraped_htmls))
        unread_files.sort()
        data = []
        for file in unread_files:
            #TODO: Implement BS4 for parsing
            jobID = file.strip("\.html"|"Job_")
            eml_file = open(input_dir+file, 'r', encoding='utf-8')
            file_contents = eml_file.read()
            eml_file.close()
            
            #parse file_contents
            datum = {
                'JobID':jobID,
                'raw':file_contents,
            }
            if debug|self.debug:
                print(datum)
            data.append(datum)
        if debug|self.debug:
            print(f"ALL HTML DATA: {data}")
        return data

    def update_db(self):
        pass
    
    def clean_db(self,debug=False):
        host_dir="data\\output_files\\"
        working_dir=['scraped_data\\','']
        #Delete files
        for directory in working_dir:
            folder_path = host_dir+directory
            if os.path.exists(host_dir+directory):
                folder_path = host_dir+directory
                file_list=set(os.listdir(folder_path))
                if debug|self.debug:
                    print("We're in.,{}\n=,{}".format(file_path,file_list))
                for file in file_list:
                    file_path = folder_path+file
                    print(file_path)
                    if os.path.exists(file_path):
                        if debug|self.debug:
                            print("FILE FOUND!",file_path)
                        try:
                            os.remove(file_path)
                        except:
                            os.rmdir(file_path)
        #create deleted dir
        os.mkdir("data\\output_files\\scraped_data")

class jobID:
    def __init__(self):
        #starting at -1 for testing purposes.
        #eventually add reference to storage and continue count.
        self.Value = -1
    def iter(self):
        self.Value+=1
        return self.Value
    def value(self):
        return self.Value
    def next(self):
        return self.Value+1
    def prev(self):
        return self.Value-1

if __name__=='__main__':
    try:
        debug = True if 'debug' in sys.argv else False
        clean = True if 'clean' in sys.argv else False
        download = True if 'download' in sys.argv else False
    except:
        debug = False
        clean = False
        download = False
    h = HTML_Scraper('data\\', debug=debug)
    if clean==True:
        h.clean_db()
    else:
        h.update_from_local()
        h.export_to_file()
        if download:
            h.download_posting_html()
    # h.import_from_file()
    
    # # Debugging:
    # print(h.posted_jobs)
    # print(h.scan_new_application('You applied for Supply Chain Data Analyst 100% Remote Fortune 60 Co Direct Hire Salary up to $110K per annum at Confidential.eml')) #(long subject name and outputs)
    # h.scan_new_application('You applied for FULLY REMOTE- Software Engineer (Python_Django) at CyberCoders.eml',debug=True) #(symbols)
    # h.scan_new_application('You applied for Data Analyst at Fēnom Digital.eml',debug=True) #(utf-8 encoding req)
    
    # print(h.applied_jobs.values(), sep="\n")
    # "You applied for Python Developer at Comrise.eml" #(e goes missing)
    # "Your application to Python Developer at Comrise.eml"