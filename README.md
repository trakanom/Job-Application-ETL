# Job Application ETL
Job application statistics and archival.
Data from Gmail, LinkedIn to .csv, SQL   

Extracts data from job application related emails with Gmail API and OAuth, 
Reads user email via Gmail Oauth and API services,

Web scrapes job application posts and associated companies' pages from LinkedIn
Loads cleaned data into SQL database for data analysis and ML applications.

Included:
- Gmail OAuth & API integration
- Selenium and BeautifulSoup powered web scraping of LinkedIn
- Export to csv
- Read local email files.

In-Development:
- Docs
- GUI Support
- Additional feature extraction and cleaning with pandas
- Export to SQL
- PowerBI Dashboard 

Requires google credential json

Next Steps:
- Retrieval of all LinkedIn Premium data available for companies and positions applied to.
- Multi-platform support (Untapped, Ziprecruiter, etc)
- Identification of non-template emails (BoW, NLP)
- Data Validation
- Performance improvements

Stretch Goals:
- Gmail add-on for easier manual dataset aggregation 
- Causal ML, A/B Testing to correlate resume features with outreach metrics
- Personalized ATS-optimized resume generation









