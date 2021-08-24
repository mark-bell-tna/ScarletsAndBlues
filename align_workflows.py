#!/usr/bin/python3

from record_reader_classes import classificationRow, classificationRecordSet, taskActions
from record_aligner_class import recordAligner
from annotation_comparer import annotationComparer
from sandb_data_reader import sandbDataReader
from needleman_wunsch import needleman_wunsch
from local_align import local_align, all_alignment
from collections import OrderedDict
from multi_align import MultiAlign
from utils import add_to_dict_num, add_to_dict_list

if __name__ == '__main__':

    workflow = "People"

    #data_file_name = "scarlets-and-blues-classifications.csv"
    data_files = {"Meetings": "meetings-classifications.csv",
                  "People": "people-classifications.csv"}

    data_file_name = data_files[workflow]

    DR = sandbDataReader()
    DR.load_data(data_file_name)

    C = annotationComparer()

    C.add_taskactions('People',   'annotations', 'create',['T20','T7'])  #, 'close':'T7', 'add':['T1','T2','T10','T11']})
    C.add_taskactions('People',   'annotations', 'close','T7')  #, 'close':'T7', 'add':['T1','T2','T10','T11']})
    C.add_taskactions('People',   'annotations', 'add',['T1','T2','T10','T11'])
    C.add_taskactions('Meetings', 'annotations', 'create',['T0','T7','T25','T14'])
    C.add_taskactions('Meetings', 'annotations', 'close',['T55','T37','T15','T14'])
    C.add_taskactions('Meetings', 'annotations', 'add',['T21','T23','T24','T20'])
    C.add_taskactions('Meetings', 'annotations', 'add',['T9','T3'])
    C.add_taskactions('Meetings', 'annotations', 'add',['T22','T6','T13','T10'])

    prev_subject = ""
    for row_id in DR.workflow_subject_iter(workflow,3,4):
        row = DR.get_row_by_id(row_id)
        subject_name = row.get_by_key("subject_name")
        classification_id = row.get_by_key("classification_id")
        print(row.items.keys())
        if subject_name != prev_subject:
            print("New subject:", subject_name)
            if prev_subject != "":
                #print("index",C.annotation_key_index)
                C.do_annotation_alignment()
                print("Rec ids",C.get_alignment_mapping())
                RMA = C.get_multi_alignment()
                RMA.do_alignment()
                print("Record and Field Alignments:")
                #if len(RMA.multi_align) > 5:
                #    continue
                for a_row in RMA.multi_align:
                    #FMA = C.get_field_alignment(a_row)
                    if 0 in C.full_alignments and 1 in C.full_alignments:
                       print("RMA:",a_row, len(C.annotations),type(C.annotations),C.annotations.keys(),C.full_alignments[0].keys(),C.full_alignments[1].keys())
                       if a_row[0] == a_row[0]:  #a_row[0] == 0 and a_row[1] == 0:
                           #print("\t",C.get_by_index(0).get_by_index(a_row[0]), C.get_by_index(1).get_by_index(a_row[1]))
                           #FMA = C.get_field_alignment(a_row)
                           #FMA.do_alignment()
                           #for f in FMA.multi_align:
                           #    print("\tFMA:",f)
                           path_list = []
                           for i in range(len(a_row)-1):
                               for j in range(i+1,len(a_row)):
                                   if a_row[i] == -1 or a_row[j] == -1:
                                       continue
                                   path_list.append([i,j,a_row[i],a_row[j]])
                           FMA2 = C.get_multi_alignment(path_list)
                           #FMA2.do_alignment()
                           for f in FMA2.multi_align:
                               print("\tFMA2:",f)
                               path_list = []
                               for i in range(len(f)-1):
                                   #print("****",C.get_by_index(i).get_by_index(a_row[i]).get_by_index(f[i]))
                                   for j in range(i+1,len(f)):
                                       if f[i] == -1 or f[j] == -1:
                                           continue
                                       path_list.append([i,j,a_row[i],a_row[j],f[i],f[j]])
                               #print("****",C.get_by_index(i+1).get_by_index(a_row[i+1]).get_by_index(f[i+1]))
                               WMA = C.get_multi_alignment(path_list)
                               for w in WMA.multi_align:
                                   print("\t\tWMA:",w)
                                   for i in range(len(w)):
                                       #print("** ** **",C.get_by_index(i).get_by_index(a_row[i]).get_by_index(f[i]).get_by_index(w[i]).get_delimited())
                                       print("** ** **",str(C.get_by_index(i).get_by_index([a_row[i],f[i],w[i]])))

                           #if len(FMA.multi_align) > 2:
                           #    exit()
                    #print("\tFMA:",FMA)
                           #records = [(i,C.get_by_index(i).get_by_index(r)) if r != -1 else (i,None) for i,r in enumerate(a_row)]
                           #print("RMA:",a_row, " **** ".join([r[1].get_delimited() for r in records if r[1] is not None]))
                           #for f in FMA2.multi_align:
                           #    fields = [C.get_by_index(i).get_by_index([a_row[i],r]) for i,r in enumerate(f) if records[i][1] is not None and r != -1]
                           #    print("\t",f, " ~~~ ".join([x.get_delimited() for x in fields]))
                #    out = ""
                #    C.do_field_alignment(a_row)
                #    for j in range(len(a_row)):
                #        if a_row[j] == -1:
                #            out += " **BLANK** "
                #        else:
                #            print(subject_keys, j)
                #            print(subject_keys[j])
                #            print(C.annotations[subject_keys[j]])
                #            out += C.annotations[subject_keys[j]].recordset[a_row[j]].get_delimited() + " *** "
                #    print(out)
                #if len(MA.multi_align) > 20:
                #    break
            subject_keys = []
            C.clear()
        C.add_row(row)
        subject_keys.append(classification_id)
        prev_subject = subject_name

