from models.Parser import Parser
from models.Local_Database import Local_Database
import time

if __name__=='__main__':
    start = time.time() #TODO run timeit
    # DB = Local_Database(".\\dev\\data\\")
    DB = Local_Database() #TODO develop Local_Database SQL CRUD etc
    p = Parser(working_dir=".\\data\\") #TODO Instantiate/Verify file structure inside working_dir
    # DB.restore(".\\data\\output_files\\db\\")
    p.load_from_backup(directory=".\\data\\db\\", limit=40)
    # DB.update(p) #Maybe set up the DB for something like this?
    # p.update_local(".\\data\\test_input_files\\")
    p.update_local(".\\data\\input_files\\", limit=40)
    # db = p.export(directory=".\\data\\output_files\\db")
    end = time.time()
    time_to_finish = end-start
    print("Time to finish: ", time_to_finish)