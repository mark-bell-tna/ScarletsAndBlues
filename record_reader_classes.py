#!/usr/bin/python3

import json
from collections import OrderedDict
#from needleman_wunsch import needleman_wunsch

###################################################################################################
# A set of container classes for Scarlets and Blues data
# The classificationObject is the basic type which comprises an Ordered Dictionary and a key index
# to lookup entries by the order the were entered.
# The class also includes methods to add new items and retrieve by key or index position
#
# classificationRow, classificationRecord and classificationRecordSet are all types of classificationObject
#
# A Row represents an entry in the export csv where the data is loaded from
# A Record consists of a set of values entered by a transcriber in response to task questions
#          e.g. T0='enter surname', T1='enter initials'
# In this case T0 and T1 are a series of tasks which group together to form one record
# The record may represent a row in a table, or an item within some meeting minutes
# A RecordSet is a collection of Record objects. This may represent all of the rows in a table,
# or all of the items on the meeting agenda.
#
# A taskActions object contains a set of tasks with actions assigned to each one.
# A transcription workflow (e.g. People) consists of a defined set of tasks. Some task ids (e.g. T0) will signify
# the beginning of a larger task, others signify the capture of data, and others the end of the main task.
# These roles are represented in a taskActions object as 'create', 'add' and 'close', respectively
# The classificationRecordset object uses actions to group together task answers into Records
# 
###################################################################################################

import re
from nvm import pmemobj

class Ditto:

    def __init__(self):

        self.value = '-do-'

    def is_ditto(self, text):
        assert not re.search(r'[-_]+d[do][-_]+d+[do][-_]+', text), "Double -do- style ditto"
        assert not re.search(r'""', text), 'Double " style ditto' #Maybe should treat this as finger-stutter and collapse to one ditto
        return re.fullmatch(r'(?:^|\s)("|[-_~]+d+[do][-_~]+)(?:\s|$)', text) is not None

    def update(self, value):

        self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)

class classificationObject: #(pmemobj.PersistentObject):

    delimiter = chr(32)

    def __init__(self, parent = None, predecessor = None):

        self.items = OrderedDict()  # Maintains entry order when iterated over
        self.key_index = []         # Despite maintaining order, OrderedDict does not have a method for looking up the ith item
        #self.delimiter = chr(32)    # Used by get_delimited method, this should be overridden by each subclass so each has a unique delimiter
        self.parent = parent
        self.predecessor = predecessor
        self.has_dittos = False

    def add(self, value, key = None):  # Add a new entry to the object

        if key is None:
            key = len(self.items)
        if isinstance(value, str):
            if len(value) == 0:
                value = chr(0)  # This is needed for aligning empty strings/values
        self.items[key] = value
        self.key_index.append(key)

    def get_last_added(self):
        if len(self.key_index) == 0:
            return None
        return self.get_by_index(len(self.key_index)-1)

    def get_by_key(self, key):  # Lookup a known key

        return self.items[key]

    def get_by_index(self, index):  # Lookup the Nth item

        if isinstance(index, list):
            if len(index) == 1:
                if index[0] == -1:
                    return ""
                if index[0] not in self.key_index:
                    return self.items
                return self.items[self.key_index[index[0]]]
            else:
                if isinstance(self.items[self.key_index[index[0]]], classificationObject):
                    return self.items[self.key_index[index[0]]].get_by_index(index[1:])
                else:
                    print(self.items[self.key_index[index[0]]],"not CO")
        else:
            if index == -1:
                return ""
            if index not in self.key_index:
                return self.items
            return self.items[self.key_index[index]]

    def __str__(self):
        return str(self.items)

    def __repr__(self):
        return str(self)

    def get_delimited(self):  # Turn object into a delimited string; could potentially be called by the __str__ method

        delim_entry = ""
        for r in self.items.values():
            delim_entry += self.delimiter
            if r is None:
                delim_entry += ""
            elif isinstance(r, classificationObject):  # This is why delimiters should be unique to subclass, so
                                                       # records, fields, words are delimited differently
                delim_entry += r.get_delimited()
            else:
                delim_entry += str(r)

        return delim_entry[1:]  # first character will be a delimiter so remove it

# A classificationRow represents a row of the csv export from Zooniverse
class classificationRow(classificationObject):

    # Fields expected in the Zooniverse export csv plus subject_name which is extracted from another field
    #__field_lookup = {'classification_id':0, 'user_name':1, 'user_id':2, 'user_ip':3, 'workflow_id':4, 'workflow_name':5,
    #                  'workflow_version':6, 'created_at':7, 'gold_standard':8, 'expert':9, 'metadata':10, 'annotations':11,
    #                  'subject_data':12, 'subject_ids':13, 'subject_name':14}
    #__field_list = ['classification_id', 'user_name', 'user_id', 'user_ip', 'workflow_id', 'workflow_name',
    #                  'workflow_version', 'created_at', 'gold_standard', 'expert', 'metadata', 'annotations',
    #                  'subject_data', 'subject_ids', 'subject_name']

    __field_list = ['classification_id', 'workflow_id', 'workflow_name',
                      'workflow_version', 'created_at', 'gold_standard', 'expert', 'annotations',
                      'subject_data', 'subject_ids', 'user_name']


    #def __init__(self):

    #    super().__init__()

    def add_row(self, row):  # Expecting an already split row in a list

        for i,fld in enumerate(row):
            try:
                j_fld = json.loads(fld)  # If the contents of the field are json this will be successful and j_fld will be a dictionary
            except:  # if they're just a string there will be an exception
                j_fld = fld
            self.add(j_fld, self.__field_list[i])

        subject_id   = self.get_by_key('subject_ids')
        subject_data = self.get_by_key('subject_data')

        # Ideally the subject_id would be used but this changes when images are reloaded
        # so name is more consistent, although the case varies for how Name is named.
        
        subject = ""

        if 'name' in subject_data[str(subject_id)]:
            subject = subject_data[str(subject_id)]['name']
        if 'Name' in subject_data[str(subject_id)]:
            subject = subject_data[str(subject_id)]['Name']
        if 'image' in subject_data[str(subject_id)]:
            subject = subject_data[str(subject_id)]['image']
        subject = subject.replace(" ","/")
        #print("Subject:", subject, "Id:", subject_id)
        self.add(subject, 'subject_name')


# A classificationRecordSet is expected to be multiple entries on a page
# For example a list of names in the People workflow
class classificationRecordSet(classificationObject):

    delimiter = chr(30)

    #def __init__(self, parent=None, predecessor=None):

    #    super().__init__(parent, predecessor)
    #    self.delimiter = chr(30) # This will be the delimiter between records with a RecordSet

    def set_actions(self, actions): # Actions are used to group tasks to make a record (i.e. fields within a record - surname etc.)
        
        self.actions = actions

    def add_annotation(self, annotation):

        R = None

        # an annotation contains all of the tasks performed by a transcriber for a workflow on a subject (page of document)
        # By following the task order for a specific group of tasks we can build a Record
        # Each Record is then added to the RecordSet
        ann_queue = []  # use a queue because of nested tasks in lists (see below)
        record_id = 0
        prev_record = None
        for ann in annotation: # each annotation is a dictionary containing a task and a value
            ann_queue.append(ann)
            while len(ann_queue) > 0:
                this_ann = ann_queue.pop(0)
                #print(this_ann)
                if isinstance(this_ann['value'], list): # some tasks consist of sub-tasks which are held in a list
                                                        # This will convert a list into multiple entries in the queue
                    for v in this_ann['value']:
                        if 'task' in v:  # Things in lists are not always tasks
                            ann_queue.append(v)

                if this_ann['task'] == 'T20' and this_ann['value'] == 'No':
                    print("No names found")
                    return False
                if this_ann['task'] in self.actions:  # only interested in certain tasks
                    actions = self.actions[this_ann['task']]
                    if 'close' in actions or 'create' in actions:
                        if R is not None:
                            self.add(R) # Add current record to the recordset
                            #print("Record is:", R.get_field_tasks())
                            prev_record = self.get_last_added()
                    if 'create' in actions:
                        R = classificationRecord(self, prev_record)  # Create a new record
                    if 'add' in actions:
                        if R is None:
                            R = classificationRecord(self, prev_record)
                            # There is a data error in the current version of the export which means that
                            # the first task of a group is not always coming through.
                            # Ideally this would be the 'create' task and would also provide a label
                            # for the type of record.
                            #print("********** Warning: expected create action missing:",this_ann['task'])
                        R.add(this_ann['value'], this_ann['task'])  # Add field value to the current record
                        if R.has_dittos:
                            self.has_dittos = True

        return True

# A classificationRecord object represents a single entry in a RecordSet (e.g. a row in a list of people)
# Each item added will represent a field in the Record
class classificationRecord(classificationObject):

    delimiter = chr(31)

    #def __init__(self, parent=None, predecessor=None):

    #    super().__init__(parent, predecessor)
    #    self.delimiter = chr(31)

    def add(self, value, key=None):

        predecessor = self.get_last_added()
        field = classificationField(self, predecessor)
        field.add(value)
        if field.has_dittos:
            self.has_dittos = True
        super().add(field, key)

    def get_field_tasks(self):

        return [k for k in self.items.keys()]

class classificationField(classificationObject):


    def add(self, value, key=None):

        tokens = value.split(self.delimiter)
        prev_token = None
        for tk in tokens:
            CW = classificationWord(tk, self, prev_token)
            if CW.has_dittos:
                self.has_dittos = True
            super().add(CW)
            if CW.has_dittos:
                if self.parent is not None:
                    if self.parent.predecessor is not None:
                        parent_index = len(self.parent.items)
                        this_index = len(self.items)-1
                        #print("idx",parent_index,this_index,"parent",self.parent.get_delimited(),"pred",self.parent.predecessor.get_delimited())
                        predecessor_field = self.parent.predecessor.get_by_index(parent_index)
                        key = CW.key_index[0]
                        if isinstance(predecessor_field,classificationObject):
                            self.items = predecessor_field.items
                            self.key_index = predecessor_field.key_index
                            #print(self.get_delimited(),"updated", self.parent.get_delimited())

            prev_token = CW

class classificationWord(classificationObject):

    delimiter = chr(0)
    ditto_test = Ditto()

    def __init__(self, token=None, parent=None, predecessor=None):

        super().__init__(parent, predecessor)
        #self.delimiter = chr(0)

        if token is not None:
            self.add(token)
        
    def add(self, value, key=None):

        if self.ditto_test.is_ditto(value):
            super().add(Ditto())
            self.has_dittos = True
            return

        for c in value.split(self.delimiter):
            super().add(c)

            # If you were to implement objects down to Token level this is how it would work
            # There are advantages to this for individual character comparisons
            # However, before doing that the alignment code would need to change has it has
            # character positions at the field level rather than word
            #tokens = list(c)
            #for t in tokens:
            #    CT = classificationToken()
            #    CT.add(t)
            #    super().add(CT)

class classificationToken(classificationObject):

    delimiter = chr(0)


# taskActions are used to identify recordssets, records and fields through the tasks in a workflow
# Example code for loading is in the align_workflows.py file
# Usage to filter workflow is in the classificationRecordSet class above
class taskActions:

    def __init__(self):

        self.actions = {}

    def add(self, action_name, workflows):

        if isinstance(workflows, str): # Allows single item workflow to be passed as a string
            workflows = [workflows]

        for w in workflows:
            if w not in self.actions:
                self.actions[w] = []
            self.actions[w].append(action_name)
            
    def __repr__(self):
        
        return str(self.actions)


if __name__ == "__main__":

    D = Ditto()
    print(D.is_ditto("vair"),"vair")
    print(D.is_ditto('"'),'"')
    print(D.is_ditto("~do~"),"~do~")
    print(D.is_ditto("-ddd-"), "-ddd-")
    print(D.is_ditto("-DDD-"), "-DDD-")
