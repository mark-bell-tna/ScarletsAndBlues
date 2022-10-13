#!/usr/bin/python3

from record_reader_classes import classificationRow, classificationRecordSet, taskActions
from annotation_comparer import annotationComparer
from sandb_data_reader import sandbDataReader
#from needleman_wunsch import needleman_wunsch
from local_align import local_align, all_alignment
from collections import OrderedDict, Counter
from multi_align import MultiAlign
from utils import add_to_dict_num, add_to_dict_list
import json


def write_to_file(subject_name, subject_id, comparer):
    
    comparer.do_annotation_alignment()
    rec_ids = comparer.get_alignment_mapping()
    MA = comparer.get_multi_alignment().multi_align
    same_rows = set([len(set(R)) for R in MA])
    rows = len(MA)
    
    task_list = ['T1','T2','T10','T11']
    
    output = {subject_name: {}}
    subject_output = output[subject_name]
    
    for i, a in enumerate(MA):
        print("Alignment:",a)
        subject_output[i] = {}
        for task in task_list:
            task_values = []
            subject_output[i][task] = {}
            for j,r in enumerate(a):
                if r > -1:
                    value = C.get_by_index(j).get_by_key(r).get_by_key(task).get_delimited()
                    task_values.append(value)
                    subject_output[i][task][j] = value
                    #print("\tTask:",task,"i:",C.get_by_index(i).get_by_key(r).get_by_key(task).get_delimited())
                else:
                    task_values.append(None)
            cnt = Counter(task_values)
            print("\tTask:",task,"Values:","|".join([str(tv) for tv in task_values]), "Counts:",cnt)
    if 1 in same_rows and len(same_rows) == 1:
        print("Matched:",rows)
    else:
        print("Unmatched:", subject_name, rows, same_rows)
        #return

    with open('../Transcriptions/' + subject_name + '.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

    #transcription_file = open("../Transcriptions/" + subject_name.replace("/","_") + ".txt", "w")
    #transcription_file.write("subject=" + str(subject_id) + "\n")

    print("Rec ids", rec_ids)
    
    #import json
    #with open("../Alignments/" + subject_name.replace("/","_") + '_align.json', 'w', encoding='utf-8') as f:
    #    json.dump(C.full_alignments, f, sort_keys=True, indent=2)
    
    #exit()

    #max_rec = -1
    #for al in C.alignments_iter([rec_ids]):
    #    #print("al:",al)
    #    this_rec = max([x[1] for x in al[0]] + [-1])
    #    if this_rec > max_rec:
    #        #transcription_file.write("\nRecord=" + str(this_rec) + "\n")
    #        max_rec = this_rec
    #    if len(al) == 0:
    #        continue
    #    CC = confidenceCalculator(PT2)
    #    if len(al[1]) == 0:
    #        continue
    #    for a in al[1]:
    #        try:
    #            CC.add_value(a.get_delimited())
    #        except:
    #            print("Error, get_delimited:", type(a), al)
        #print([C.annotation_key_index[x[0]] for x in al[0]],"\t",al[0],"\t",[x.get_delimited() for x in al[1]],"\t", next(CC.conf_iter()))
    #    try:
    #        transcription_file.write(",".join([str(x[0]) for x in al[0]]) + "|")
    #        transcription_file.write(",".join([str(C.annotation_key_index[x[0]]) for x in al[0]]) + "|")
    #        transcription_file.write(",".join([x.get_delimited() for x in al[1]]) + "\n")
    #    except:
    #        print("Error, get_delimited 2:", type(al[1]), al)
            
    #transcription_file.close()
    

if __name__ == '__main__':

    workflow = "People"

    #data_file_name = "scarlets-and-blues-classifications.csv"
    data_files = {"Meetings": "meetings-classifications.csv",
                  "People": "people-classifications.csv"}

    data_file_name = "../Data/" + data_files[workflow]

    DR = sandbDataReader()
    DR.load_data(data_file_name, workflow)

    C = annotationComparer()

    C.add_taskactions('People',   'annotations', 'create',['T20','T7'])  #, 'close':'T7', 'add':['T1','T2','T10','T11']})
    C.add_taskactions('People',   'annotations', 'close','T7')  #, 'close':'T7', 'add':['T1','T2','T10','T11']})
    C.add_taskactions('People',   'annotations', 'add',['T1','T2','T10','T11'])
    C.add_taskactions('Meetings', 'annotations', 'create',['T0','T7','T25','T14'])
    C.add_taskactions('Meetings', 'annotations', 'close',['T55','T37','T15','T14'])
    C.add_taskactions('Meetings', 'annotations', 'add',['T21','T23','T24','T20'])
    C.add_taskactions('Meetings', 'annotations', 'add',['T9','T3'])
    C.add_taskactions('Meetings', 'annotations', 'add',['T22','T6','T13','T10'])

    from calc_confidence import probabilityTree, similarityComparator, equalsComparator, missingComparator, confidenceCalculator
    PT1 = probabilityTree(similarityComparator(), {1:0.6, 2:0.3, '*': 0.1})
    PT2 = probabilityTree(equalsComparator(), {1:0.9, 0: PT1})
    PT3 = probabilityTree(missingComparator(), {1:0.7, -1:0.3, 0: PT2})

    #print("Ex1:", PT3.get_probability("jones","jones"))
    #print("Ex2:", PT3.get_probability("jones","jonesy"))
    #print("Ex3:", PT3.get_probability("jones","jonesyyy"))


    prev_subject = ""
    prev_subject_id = 0
    counter = 0
    
    #print(DR.classification_index)
    #print(DR.data_rows)
    for R in DR(3,4):
        subject_name = R[0]
        C.clear()
        subject_keys = []
        print("\nNew subject:", subject_name)
        for row_id in R[1]:
            row = DR.get_row_by_id(row_id)
            print("\t*****Id:",row_id, "Row:", row)
            classification_id = row.get_by_key("classification_id")
            subject_id = row.get_by_key("subject_ids")
            C.add_row(row)
            subject_keys.append(classification_id)
        write_to_file(subject_name, subject_id, C)

