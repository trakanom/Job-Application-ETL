# from .models.config.schema import tables
import pandas as pd
class Local_Database:
    def __init__(self, tables=None):
        '''
        tables: dict()
        format: 
        tables = {
            'table_name' : {
                'columns' : {col_0_name:col_0_type}, #required
                'data' : [{key0:{col0':'val0', ... }}], #optional
                'metadata' : { } #optional
            }
        }
        '''
        
        #tables should be a dict of the format:
        #{table_name : 
        self.table_meta = {}
        self.tables = {}
        if tables != None:
            self.new_db(tables)
    def load_db(self):
        ...
    
    
    def new_db(self, init_dict):
        for table in init_dict.keys():
            self.add_table(table, init_dict[table]['columns'])
            # if table['data']:
    def add_table(self,name,columns):
        self.tables[name]=pd.DataFrame(columns=columns)
        self.table_meta.update({name:{'columns':columns}})
    def update_db(self, df, new_entries):
        ...
    
    def query(self, QUERY):
        # lol, dangerous.
        return "Just kidding, it's not done yet."
