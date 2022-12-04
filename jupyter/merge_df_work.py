'''
Trying to fix a mismatch between company names used in different update_type emails.
'''


rejected_companies = set(rejected['company'].str.strip(".").unique())
viewed_companies = set(viewed['company'].str.strip(".").unique())
applied_companies = set(merged_companies['Company_Name'].unique())
update_companies = rejected_companies.union(viewed_companies)
update_companies = viewed_companies.union(rejected_companies)
update_companies.difference(applied_companies)
company_comparison = merged_companies[['Company_Name','Company_Name_original']]
# company_comparison = merged_companies[merged_companies[[['Company_Name','Company_Name_original']].isin(update_companies.difference(applied_companies))]]
rename_dict = {}
for index, entry in company_comparison.iterrows():
    if entry.hasnans:
        continue
    companies = [entry['Company_Name'], entry['Company_Name_original']]
    # print(companies)
    
    smaller, larger = min(companies).title().strip("."), max(companies).title().strip(".")
    if smaller in larger and not smaller==larger:
        print("{} <= {}".format(smaller, larger))
        rename_dict.update({companies[1]:companies[0]})
        
rejected_companies['company'].replace(rename_dict)
viewed_companies['company'].replace(rename_dict)

pre_application_history = pd.merge(applicants, new_viewed[['PostID','date']], how="left", on="PostID", suffixes=["_applied", "_viewed"])
pre_application_history = pd.merge(applicants, new_viewed[['company','position','date']], how="left", on=['company', 'position'], suffixes=["", "_viewed"])
pre_application_history = pd.merge(pre_application_history, new_rejected[['company','position','date']], how="left", on=['company', 'position'], suffixes=["", "_rejected"])
col_names = pre_application_history.columns
# ['Unnamed: 0','errors','Post_Body']
application_history_columns = ['PostID', 'position', 'company', 'Company_Name', 'Location', 'Workplace_Type', 'Premium-Salary', 'Premium-Skills', 'Premium-Skills_Possessed', 'date_applied', 'date_viewed', 'date_rejected', 'Closed']

application_history = pre_application_history[application_history_columns]