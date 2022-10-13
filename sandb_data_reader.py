#!/usr/bin/python3

import csv
import json
from utils import add_to_dict_num, add_to_dict_list
from record_reader_classes import classificationRow

from nvm import pmemobj
# TODO: Make this optional, so code works whether or not nvm is installed
#       Needs conditional statements to optionally load the data from file or persistent memory
#       For now it will require nvm, so keep away from main branch in Github

class sandbDataReader:   #(pmemobj.PersistentObject):

    def __init__(self):

        self.data_rows = []  #self._p_mm.new(pmemobj.PersistentList) #[]
        self.user_index = {}  #self._p_mm.new(pmemobj.PersistentDict) #{}
        self.workflow_subject_index = {}  #self._p_mm.new(pmemobj.PersistentDict) # {}
        self.classification_index = {}
        self.iter_min = 1
        self.iter_max = 999

    def load_data(self, data_file_name, workflow, version=None, after_date = None):

        # TODO: Add a date filter to only process latest transcriptions
        
        self.workflow = workflow
        self.workflow_subject_index[workflow] = {}  # This can be phased out since only loading a single workflow

        if after_date is None:
            date_limit = '1/1/2021'
        else:
            date_limit = after_date

        self.data_file_name = data_file_name
        file_handle = open(data_file_name, 'r')
        csv_reader = csv.reader(file_handle)
        read_headings = True

        for row in csv_reader:
            if read_headings:
                read_headings = False
                continue
            if row[0][0] == "#":   # commented out row
                continue
            R = classificationRow()
            R.add_row(row)
            if R.get_by_key('workflow_name') != workflow:
                continue
            if version is not None:
                if R.get_by_key('workflow_version') != version:
                    continue
            self.data_rows.append(R)
            row_id = len(self.data_rows)-1
            user = R.get_by_key('user_name')
            classification_id = R.get_by_key('classification_id')
            add_to_dict_list(self.user_index, user, row_id)
            add_to_dict_num(self.classification_index, classification_id, row_id)
            task = R.get_by_key('workflow_name')
            subject_name = R.get_by_key('subject_name')

            #if task not in self.workflow_subject_index:
            #    self.workflow_subject_index[task] = {}
            task_dict = self.workflow_subject_index[task]
            add_to_dict_list(task_dict, subject_name, row_id)
            
        print(self.workflow_subject_index)


    def workflow_subject_iter(self, workflow, min_count=1,max_count=100):
        
        #print(workflow, min_count, max_count)
        subject_index = self.workflow_subject_index[workflow]
        for k,v in subject_index.items():
            #print("\t",k, len(v))
            if min_count <= len(v) <= max_count:
                #print("Aaaa")
                for row_id in v:
                    #print("\tId:",row_id)
                    yield row_id
                    
    def get_row_by_classification(self, classification_id):
        
        if classification_id in self.classification_index:
            return self.get_row_by_id(self.classification_index[classification_id])
        return None

    def get_row_by_id(self, row_id):

        return self.data_rows[row_id]
        
    def __call__(self, iter_min=1, iter_max=999):
        
        self.iter_min = iter_min
        self.iter_max = iter_max
        
        return self
        
    def __iter__(self):
        
        subject_index = self.workflow_subject_index[self.workflow]
        for k,v in subject_index.items():
            if self.iter_min <= len(v) <= self.iter_max:
                #print("Aaaa")
                yield [k,v]
        


if __name__ == '__main__':
    
    workflow = "People"

    #data_file_name = "scarlets-and-blues-classifications.csv"
    data_files = {"Meetings": "meetings-classifications.csv",
                  "People": "../Data/people-classifications.csv"}

    data_file_name = data_files[workflow]

    DR = sandbDataReader()
    DR.load_data(data_file_name, workflow)
    
    print(DR.get_row_by_classification(345776257).get_delimited())
    
    # TODO: Implement POP
    
    #pop = pmemobj.PersistentObjectPool('person-classifications.pmemobj', flag='c')

    # Create an instance of our AppRoot class as the object pool root.
    #if pop.root is None:
    #    pop.root = pop.new(sandbDataReader)
        
    
    #DR = sandbDataReader()
    #DR = pop.root
    #DR.load_data('../Data/people-classifications.csv')
    
    #for row_id in DR.workflow_subject_iter('People', 5, 5):
    #    print(row_id)
