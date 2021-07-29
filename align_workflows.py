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
        if subject_name != prev_subject:
            print("New subject:", subject_name)
            if prev_subject != "":
                C.do_annotation_alignment()
                print("Rec ids",C.get_alignment_mapping())
                RMA = C.get_multi_alignment()
                RMA.do_alignment()
                print("Record and Field Alignments:")
                for a_row in RMA.multi_align:
                    FMA = C.get_field_alignment(a_row)
                    records = [(i,C.annotations[C.annotation_key_index[i]].get_by_index(r)) if r != -1 else (i,None) for i,r in enumerate(a_row)]
                    print("RMA:",a_row, " **** ".join([r[1].get_delimited() for r in records if r[1] is not None]))
                    for f in FMA:
                        fields = [records[i][1].get_by_index(r) for i,r in enumerate(f) if records[i][1] is not None and r != -1]
                        print("\t",f, " ~~~ ".join(fields)) #[x.get_delimited() for x in fields]))
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

