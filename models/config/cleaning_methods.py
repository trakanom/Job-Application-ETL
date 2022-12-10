import pandas as pd
import re
from .CONSTS import DATE_FORMAT
import email


def decode_mime_stuff(s, verbose=None):
    if verbose:
        print(s)
    s=s.replace("\n","").strip()
    if "=?" in s:
        # print(s)
        results =  u''.join(
            word.decode(encoding or 'utf8') if isinstance(word, bytes) else word
            for word, encoding in email.header.decode_header(s))
    else:
        results = s
    # results = " ".join(results.split(" ")[3:])
    if verbose:
        print("DECODE RESULTS: ",results)
    return results

def str_strip(s, verbose=None):
    if verbose:
        print("1'",s,"'",sep="")
    s = re.sub(r'\n','', s)
    s = re.sub(r'\s+', ' ', s)
    # s = re.sub(r'\s+%\s+?', " ", s)
    s = s.strip().strip()
    if verbose:
        print("2'",s,"'",sep="")
    # new_string = " ".join([word.strip() for word in s.split(" ")])
    return s



def create_new_columns(df):
    new_df=pd.DataFrame()
    new_df['date_applied']=df[df['type'=='applied']['date']] #fix this syntax, lol
    new_df['date_viewed']=df[df['type'=='viewed']['date']] 
    new_df['date_rejected']=df[df['type'=='rejected']['date']] 
    modified_df = pd.concat(df, new_df)
    return modified_df

def merge_df(self,df1,df2, cache): #TODO refactor for current paradigm
        # df['new'] = np.where((df1['Company'],df2['Company']) & (df['Title'] <= df['Title']), df['Column1'], None)
        columns = cache['applicant'].keys()
        df1 = pd.DataFrame(cache['applicant'])['company'].unique()
        updated_companies = []
        updates = cache.keys().remove('applicant')
        for update_type in updates:
            updated_companies.append(list(pd.DataFrame(cache[update_type])['company']))
        df2 = pd.DataFrame(update_companies).unique()
        
        
        
        
        
        
        
        
        
        
        uniques = df1.Company.unique()
    
        print("UNIQUE: \n",uniques)
        matches = {}
        no_matches = []
        #tries its best to match. Might be unnecessary processing. Should attempt merge on viable entries then go back for the missed ones.
        for index,row in df2.iterrows():
            matching_company = row['Company']
            for df_company in uniques:
                companies = [matching_company,df_company]
                if min(companies).title() in max(companies).title(): #without lower, fully caps names don't match.
                    # print(companies)
                    matches[matching_company]=df_company
                    break
            if matching_company not in matches.keys():
                no_matches.append(matching_company)
        
        print(matches)
        df2.replace(matches, inplace=True)
        print(df2)
        grouped_by = ['Company','Title']
        app_history = df1.merge(df2, how='left', on=grouped_by)
        newgroups = app_history.groupby(grouped_by)
        print("APP HISTORY!\n",app_history)
        print(newgroups.head())
        # uniques = df1.Company.unique()

def fix_unicode(df):
    '''
    replaces UTF-8 encoded unicode characters that look like "=FF" with a replacement string.
    '''
    #TODO efficiency improvements?
    cleaned_df=pd.DataFrame()
    cols_to_clean = [column for column in df.columns if df[column].dtype=='string']
    
    match_pattern = re.compile(r'(=[A-F0-9]{2})')
    replacement_func = lambda y: y.group(0).lower().replace("=",r"_replace_me_lol_")+" " #TODO find out how to replace character with its unicode equivalent
    clean_func = lambda entry: re.sub(match_pattern, replacement_func, entry)
    
    
    for col in df.columns:
        if df[col].dtype=='string':
            #TODO fix this spaghetti
            #Update: Maybe did?
            cleaned_df[col]=df[[col]].applymap(clean_func, na_action='ignore')
        else:
            cleaned_df[col]=df[[col]]
    return cleaned_df

def fix_dtypes(df):
    modified_df = df.convert_dtypes()
    modified_df['date']=pd.to_datetime(modified_df['date'],format=DATE_FORMAT) #TODO Fix this
    modified_df['update_type']=modified_df['update_type'].astype('category')
    
    # data_types = {
    #     'date':'datetime',
    #     'update_type':'category',
        
        
    # }
    
    
    return modified_df

def cache_to_df(cache):
    # df = pd.DataFrame()
    # for category in ['applicant', 'viewed', 'rejected']:
    #     new_df = pd.DataFrame(cache[category])
    #     new_df[f'date_{category}']=new_df['date']
    # df['date_applied']=df[]
    #FROM WHIMSICAL:
    applied_df = pd.DataFrame(cache['applicant'])
    applied_df['date_applied']=applied_df['date']
    # applied_df['update_type']=[applied_df['update_type']]
    columns = list(applied_df.columns.values)
    # columns.remove('date')
    # columns.remove('update_type')
    for category in ['viewed', 'rejected']:
        merging_df = pd.DataFrame(cache[category])
        merging_df['company'].replace(".","").replace(",","").str.strip()
        right_suffix = f'_{category}'
        merging_df[f'date_{category}']=merging_df['date']
        columns.append("date"+right_suffix)
        applied_df = pd.merge(applied_df, merging_df, how='left', on=['company', 'position'], suffixes=["","_dupe"]) #TODO ERROR DROPPING UNMATCHED COMPANY DATA. CLEAN COMPANY DATA FIRST
        # applied_df['update_type']
    modified_df = applied_df[columns]
    return modified_df


cleaning_methods = [
    # lambda x: x.applymap(decode_mime_stuff, na_action="ignore"),
    # lambda x: clean_companies(x),
    # lambda x: fix_dtypes(x),
    lambda x: cache_to_df(x),

    


    # lambda x: x.convert_dtypes(),
    # lambda x: fix_unicode(x),
    # lambda x: create_new_columns(x),
    
]