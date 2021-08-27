#!/usr/bin/python3

import csv
import json
from record_reader_classes import classificationRecordSet, taskActions
from record_aligner_class import recordAligner
from needleman_wunsch import needleman_wunsch
from collections import OrderedDict
from multi_align import MultiAlign
from utils import add_to_dict_num, add_to_dict_list

gap_char = "~"

# Accepts multiple annotations of a subject from the same workflow and uses an alignment function
# to compare the transcriptions by record and field
class annotationComparer:

    def __init__(self):
       
        self._init_variables()
        self.task_actions = {}
        self.aligner = recordAligner()

    def _init_variables(self): # used by both __init__ and clear

        self.annotations = OrderedDict()
        self.annotation_key_index = [] # it is better for later code to use the index rather than the unique id
        self.workflows = set() # simple way to check that only one workflow is involved
        self.subjects = set()  # check that only one subject is involved
        self.record_lengths = []
        self.annotation_texts = []

    def get_by_index(self, index):

        return self.annotations[self.annotation_key_index[index]]

    # Set up the workflow tasks to be extracted from each annotation
    def add_taskactions(self, workflow, field, action, tasks):

        if workflow not in self.task_actions:
            self.task_actions[workflow] = {}
        if field not in self.task_actions[workflow]:
            self.task_actions[workflow][field] = taskActions()
        task_list = []
        if isinstance(tasks, str): # allow for single task or list of tasks as parameter
            task_list.append(str)
        elif isinstance(tasks, list):
            task_list = tasks
        self.task_actions[workflow][field].add(action, task_list)

    def add_row(self, classification_row):

        workflow_name = classification_row.get_by_key('workflow_name')
        self.workflows.add(workflow_name)
        assert len(self.workflows) <= 1, "Can only compare records from the same workflow"  # this will raise an error which isn't caught
        assert len(self.subjects) <= 1, "Can only compare records of the same subject"
        annotation = classification_row.get_by_key('annotations')
        RS = classificationRecordSet(parent=self)
        RS.set_actions(self.task_actions[workflow_name]['annotations'].actions)
        RS.add_annotation(annotation)
        if RS.has_dittos:
            print("****************************HAS DITTOS************************")
        user_name = classification_row.get_by_key('user_name')
        classification_id = classification_row.get_by_key('classification_id')  # this is a unique identifier for the row
        self.annotations[classification_id] = RS
        self.annotation_key_index.append(classification_id)  # for looking up by order of entry elsewhere
        self.annotation_texts.append(RS.get_delimited()) # will be used for alignment step
        self.record_lengths.append(len(RS.items))  # length is number of records or fields not total length of text

    def clear(self): # reset for new set of records to compare

        self._init_variables()

    # pairwise alignment of annotations
    # Start at longest and compare to others in length order, then second longest compared to remainder, etc. (only expecting 2 or 3 annotations)
    def do_annotation_alignment(self):

        keys = [k for k in self.annotations.keys()]
        #print("RL:",self.record_lengths)
        #return

        # sort the annotations in order of number of records
        self.sorted_texts = sorted(range(len(self.record_lengths)), key=lambda k: self.record_lengths[k], reverse=True)
        self.sorted_texts = [i for i in range(len(self.record_lengths))]

        print("Texts:",len(self.annotation_texts),"Order:",self.sorted_texts)

        #for s in self.sorted_texts:
        #    print("~~~~~~~~~~~~~~~~~~~~")
        #    print("id:",s,"Text:",self.annotation_texts[s])
        #print("************************************************************************")

        #record_alignments = {}
        self.full_alignments = {}  # container for nested recordset, record, field, word and character alignments
                                   # The expectation is that a record will generally map to one other,
                                   # a field to one other field, and so on
                                   # So traversing through this dictionary will be efficient
                                   # {0 : {1 : {2 : {3 : {4: {5 : {6:7, 8:9}}}}}}}
                                   # for annotations A and B
                                   # this means - record 0 of A aligns with record 1 of B
                                   #              with field 2 of A[0] aligning with field 3 of B[1]
                                   #              and word 4 of A[0][2] aligns with word 5 of B[1][3]
                                   #              with characters 6 and 8 of A[0][2][4] mapping to
                                   #                   characters 7 and 9 of B[1][3][5]

        # pairwise comparisons of annotations in length order
        # compares and stored results in one direction only so important to keep consistent ordering through process
        # hence sorted_texts variable (which could do with better name perhaps)
        for i in range(len(self.sorted_texts)-1):
            id_i = self.sorted_texts[i]   # index of annotation with ith longest entry
            if id_i not in self.full_alignments:
                self.full_alignments[id_i] = {}
            this_alignment =  self.full_alignments[id_i]
            for j in range(i+1,len(self.sorted_texts)):
                id_j = self.sorted_texts[j]
                # Use alignment algorithm to find optimal character by character alignment of annotations
                self.aligner.align(self.annotation_texts[id_i], self.annotation_texts[id_j])
                this_alignment[id_j] = self.aligner.alignments

        #print("RA:",record_alignments)
        #print("Lengths:",self.record_lengths)
        #M = MultiAlign(record_lengths,record_alignments,self.sorted_texts)
        #M.do_alignment()
        #return M

    # Extract the first set of keys and the keys of their immediate children after following path through the alignment dictionary
    # To get a mapping of, for example, the fields of two records (which are specified in the path parameter)
    def get_alignment_mapping(self, path = []):

        this_dict = self.full_alignments
        for p in path:
            if p in this_dict:
                if isinstance(this_dict[p], dict):
                    this_dict = this_dict[p]
                else:
                    break
            else:
                return []
        mapping = []
        #print("\tparameter:",path,"this_dict:", this_dict.keys())
        for k1, v in this_dict.items():
            if isinstance(v,dict):
                for k2 in v.keys():
                    mapping.append([k1,k2])
            else:
                mapping.append([k1,v])
        return mapping

    # Intention was for this to be a generic function to be used at each stage in the recordset, record, field, word hierarchy
    # but it effectively just finds the mappings at the recordset level. Needs some thought to make it work as intended.
    def get_multi_alignment(self, path_list = [[]]):

        record_alignments = {}  # This maps each annotation to its alignments between records which each other annotation
                                # Example {0 : [[1, {0:0,1:1}], [2, {0:0,1:1}]]}
                                # Annotation 0 aligns perfectly to both annotations 1 and 2 on records 0 and 1
        max_map_length = 0
        for path in path_list:
            mappings = self.get_alignment_mapping(path)
            #max_map_length = max(max_map_length, len(mappings))
            #print("\tpath:",path,"\tmappings:",mappings)
            for m in mappings:
                if len(path) == 0:
                    record_mapping = self.get_alignment_mapping(path + m)
                    r_id_1 = m[0]
                    r_id_2 = m[1]
                else:
                    record_mapping = [m]
                    r_id_1 = path[0]
                    r_id_2 = path[1]
                #print(m,"Record map:",record_mapping,"Ids:",r_id_1,r_id_2)
                if r_id_1 not in record_alignments:
                    record_alignments[r_id_1] = []

                new_alignments = [r_id_2, {}]
                for a,b in record_mapping:
                    if a not in new_alignments[1]: # deals with one to many mappings but not in a good way TODO
                        new_alignments[1][a] = b
                record_alignments[r_id_1].append(new_alignments)
                #print("\tAdded alignment:",r_id_1,"map:",new_alignments)

        # Turn pairwise alignments into multi alignment. In example above result will be:
        #[[0 0 0]
        # [1 1 1]]
        #M = MultiAlign([self.record_lengths[i] for i in self.sorted_texts],record_alignments)
        #M = MultiAlign([i for i in range(len(self.annotation_key_index))],record_alignments)
        #M = MultiAlign(self.record_lengths, record_alignments)
        M = MultiAlign([0 for i in range(len(self.annotation_key_index))], record_alignments)
        #print("**Alignments:",record_alignments)
        M.do_alignment()
        #print("MA-1:",M.multi_align[-1])
        M.multi_align.sort(key=lambda x: (min([i for i in x if i > -1]), max(x)))
        #print("MA-1:",M.multi_align[-1],type(M.multi_align))

        return M

    # Performs the same task as above but at field level
    # Main difference is in extracting the field lengths from the records. A little redesign would reduce repeated code
    def get_field_alignment(self,  mappings):

        ordered_mappings = [mappings[i] for i in self.sorted_texts]
        field_alignments = {}
        #print("Sorted order",self.sorted_texts, "Map2:", ordered_mappings,"Orig:",mappings)
        # Can only get field length for the records which have been aligned
        field_lengths = [len(self.annotations[self.annotation_key_index[self.sorted_texts[i]]].
                         get_by_index(ordered_mappings[i]).items) if ordered_mappings[i] > -1 else 0 for i in range(len(self.sorted_texts))]

        for i in range(len(ordered_mappings)-1):
            if ordered_mappings[i] == -1:
                continue
            for j in range(i+1,len(ordered_mappings)):
                if ordered_mappings[j] == -1:
                    continue
                if self.sorted_texts[i] not in field_alignments:
                    field_alignments[self.sorted_texts[i]] = []
                new_alignments = [self.sorted_texts[j], {}]
                path = [self.sorted_texts[i], self.sorted_texts[j]]
                #print("Path:",path, "Map:",[ordered_mappings[i], ordered_mappings[j]])
                field_mappings = self.get_alignment_mapping(path + [ordered_mappings[i], ordered_mappings[j]])
                for f in field_mappings:
                    if f[0] not in new_alignments[1]:
                        new_alignments[1][f[0]] = f[1]
                field_alignments[self.sorted_texts[i]].append(new_alignments)
                print("\tAdded alignment:",self.sorted_texts[i],"map:",new_alignments)

        #print("\tField lengths:",field_lengths,"Alignments:",field_alignments)
        M = MultiAlign(field_lengths,field_alignments)
        M.do_alignment()

        return M #.multi_align


    def alignments_iter(self, rec_ids, depth=2):

        max_p_len = depth*2
        p_queue = rec_ids

        while len(p_queue) > 0:
            this_rec = p_queue.pop(0)
            path_list = this_rec
            #parent = this_rec[1]
            MA = self.get_multi_alignment(path_list)
            for a_row in MA.multi_align:
                #print("p:",path_list[0])
                #a_queue.append([a_row, (int(len(path_list[0])/2)-1),counter,parent])
                #print("\t" * (int(len(path_list[0])/2)-1),"row:",a_row)
                new_path = []
                printed = set()
                output_paths = []
                output_text = []
                for i,p in enumerate(path_list):
                    if a_row[p[0]] > -1 and a_row[p[1]] > -1 and len(p) <= max_p_len:
                        new_path.append(p + [a_row[p[0]], a_row[p[1]]])
                    if len(p) > max_p_len and a_row[p[0]] > -1 and a_row[p[1]] > -1:
                        #print("P:",p,"Keys:", self.annotation_key_index)
                        if p[0] not in printed:
                            if p[0] > -1 and p[1] > -1:
                                this_path = [x for i,x in enumerate(p[2:]) if i % 2 == 0] + [a_row[p[0]]]
                                this_text = self.get_by_index(p[0]).get_by_index(this_path)
                                #print("P0",p[0], "Text type",type(this_text),id(this_text),"Text",this_text,"P:",p,a_row[p[0]])
                                printed.add(p[0])
                                output_paths.append([p[0]] + this_path)
                                output_text.append(this_text)
                                #yield this_text
                        if p[1] not in printed:
                            if p[0] > -1 and p[1] > -1:
                                this_path = [x for i,x in enumerate(p[2:]) if i % 2 == 1] + [a_row[p[1]]]
                                this_text = self.get_by_index(p[1]).get_by_index(this_path)
                                #print("P1",p[1], "Text type",type(this_text),id(this_text),"Text",this_text,"P:",p,a_row[p[1]])
                                printed.add(p[1])
                                output_paths.append([p[1]] + this_path)
                                output_text.append(this_text)
                                #yield this_text
                yield [output_paths, output_text]

                #p_queue.append([new_path, counter])
                if len(new_path) > 0:
                    for al in self.alignments_iter([new_path], depth):
                        yield al

