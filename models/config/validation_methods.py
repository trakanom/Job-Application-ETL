import pandas as pd

def company_check(df):
    '''
    Checks companies where 'update_type' is 'viewed' or 'rejected' against 'applicant' company list for mismatches and alternative naming styles.
    '''
    company_list = set(df[df['update_type']=='applicant']['company'].values)
    companies_to_match = set(df[df['update_type']!='applicant']['company'].values)
    unmatched = companies_to_match.difference(company_list)
    
    return df

validation_methods=[
    lambda x: company_check(x),
]