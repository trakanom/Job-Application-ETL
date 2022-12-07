TODO:


Features:
- Integrate email changes to main
- Add GUI to parsing process
- Add docs and requirements for the gmail oauth and 
- Browser extension for data collection/labeling


GUI:
- Create a discrete flow
- Hookup to gmail
- Log in to linkedin (or not)



Data Structures:
- Template file structure for github (with a How-To)
- Organize data into discrete tables
    - Changelog (Date changed, Change_Type, **input_values)
    - Users (User info, ID, history, skills, titles, education)
    - Application_history (JobID, UserID, Job Title, CompanyID, Location, Work_Type, Salary, Benefits, Industry, Status, **update_dates)
    - Company_Info (CompanyID, Company_Name, website, Industry, HQ Location, Locations, email_domain, )
- Data Hosting?
- efficiency: list of files + list of changelog drop duplicates keepp none. 
file for file in filter(file_list,lambda x: x[['subject','received']] not in changelog[['email_name','date_sent']]) pseudocode. Pandas set-like logic? 
~(A intercect B) = A - A intercect B


Parsing:
- Resume scanning
- LinkedIn premium data
- Add support for major recruiting sites (Indeed, Monster, etc)



Cleaning:
- Info_Tags: separate into new columns.
    - Website
    - Industry
    - Company Size
    - HQ Location
    - Founded
    - Specialties
- Salary
    - Convert Wages
    - Clean ranges
    - Store as median? Range?
- Company domain
    - Clean 
- Company Website
    - Extract domain for email flagging
        - Perhaps look at the typical domain for employee emails (Website: Contact-Us)?
    - Remove tags and clean URL for presentation (while retaining accuracy)
        - Make sure links work?
        - What if scam links?

Analysis:
- Dashboard
    - User stats
    - Response rate pivot table
