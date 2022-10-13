#!/usr/bin/python3

import os
import json
from utils import TextForm, add_to_dict_num, truncate_float
from operator import itemgetter
from collections import Counter, ChainMap
import networkx as nx

def normalise_dict(D):
    
    factor=1.0/sum(D.values())
    for k in D:
        D[k] = D[k]*factor


trans_dir = "../Transcriptions/5x5/"
trans_files = os.listdir(trans_dir)

acronyms = dict([a,1] for a in ['A.','A.A.','A.A.A.','A.A.A.A.'])  # force preference of these formats
acronyms[''] = 0   # force suppression of blank values
#normalise_dict(acronyms)

format_dict = {}

TF = TextForm("")
all_transcription_values = {}
row_count = 0
task_count = 0
total_values = 0
for tf in trans_files:
    
    with open(trans_dir + tf, 'r', encoding='utf-8') as f:
        trans_data = json.load(f)
        key = tf[:-5]
        trans_data = trans_data[key]
        
        for row in trans_data.keys():  # Each row of data, e.g. person in list
            row_count += 1
            all_transcription_values[row_count] = {}
            for task in trans_data[row].keys(): # Each task in the row, e.g. T1
                task_count += 1
                if task not in format_dict:
                    format_dict[task] = {}
                    
                transcription_values = {'fuzzy_format':[], 'full_format':[], 'value':[], 'stripped_value':[]}
                for value in trans_data[row][task].values():    # Value entered by each transcriber
                    total_values += 1
                    value = value.replace(chr(0), '')
                    TF.set_text_form(value)
                    transcription_values['fuzzy_format'].append(TF.get_form_regex(multi="*"))
                    transcription_values['full_format'].append(TF.get_form_regex())
                    transcription_values['stripped_value'].append(TF.strip_punc().lower())
                    transcription_values['value'].append(value)
                    add_to_dict_num(format_dict[task], transcription_values['fuzzy_format'][-1])
                #print(transcription_values)
                all_transcription_values[row_count][task] = transcription_values

TFC = {}
for task in format_dict.keys():
    #print(task, formats)
    normalise_dict(format_dict[task])
    format_dict[task] = ChainMap(acronyms, format_dict[task])
    #TFC[task] = sum([v for v in formats.values()])



format_mismatches = {}  # replace with DiGraph eventually 
value_mismatches = {}
format_counts = {}
DG = nx.DiGraph()

print("Rows:", row_count)
print("Tasks:", task_count)
print("Values:", total_values)
#print(all_transcription_values.keys())
row_count = 0
task_count = 0
total_values = 0

debug_counts = [0,0]

for row, data in all_transcription_values.items():
    row_count += 1
    for task, values in data.items():
        task_count += 1
        V = values # to save typing
        fuzzy_count = Counter(V['fuzzy_format'])
        full_count = Counter(V['full_format'])
        stripped_count = Counter(V['stripped_value'])
        value_count = Counter(V['value'])
        top_value = value_count.most_common(1)
        top_stripped_value = stripped_count.most_common(1)
        if top_stripped_value[0][1] == 1:
            print("Task:", task, "There is no majority value", top_stripped_value)
            continue
        #if top_stripped_value[0][0] == '':
        #    print("Task:", task, "Top value is blank", top_stripped_value)
        #    continue
        #stripped_matches = [i for i, x in enumerate(V['stripped_value']) if x == top_stripped_value[0][0]]
        L = len(V['value'])
        V['prob'] = []
        
        for i,v in enumerate(V['value']):
            total_values += 1
            p = 1.0
            p *= 0.1 ** (L-stripped_count[V['stripped_value'][i]])
            if format_dict[task][V['fuzzy_format'][i]] == 0:
                p = 0
            #if top_stripped_value[0][0] == 'WWHC':
            #    print("*********",v,L, stripped_count[V['stripped_value'][i]],v,stripped_count,
            #            0.1 ** (L-stripped_count[V['stripped_value'][i]]),format_dict[task][V['fuzzy_format'][i]])
            #p *= format_dict[task][V['fuzzy_format'][i]]
            V['prob'].append(p)
        #print(task, "V:", V)
        sorted_probs = sorted([(i,p) for i,p in enumerate(V['prob'])], key=itemgetter(1), reverse=True)
        hi_index = sorted_probs[0][0]
        chosen_value = V['stripped_value'][hi_index]
        
        for i,v in enumerate(V['value']):
            #total_values += 1
            if V['stripped_value'][i] == chosen_value:
                V['prob'][i] *= format_dict[task][V['fuzzy_format'][i]]
            else:
                V['prob'][i] = 0
            #if top_stripped_value[0][0] == 'WWHC':
            #    print("*********",v,L, stripped_count[V['stripped_value'][i]],v,stripped_count,
            #            0.1 ** (L-stripped_count[V['stripped_value'][i]]),format_dict[task][V['fuzzy_format'][i]])
            #p *= format_dict[task][V['fuzzy_format'][i]]
            #V['prob'].append(p)
        sorted_probs = sorted([(i,p) for i,p in enumerate(V['prob'])], key=itemgetter(1), reverse=True)
        hi_index = sorted_probs[0][0]
        chosen_form = V['fuzzy_format'][hi_index]
        #if chosen_form == 'Aa{*}':
        #    for z,x in enumerate(V['fuzzy_format']):
        #        if len(x) == 0 and V['stripped_value'][z] != chosen_value:
        #            print(chosen_value, "format:",V['fuzzy_format'][z], "value:",V['value'][z], "stripped:",V['stripped_value'][z], "same:",V['stripped_value'][z] == chosen_value)
        #            print("V:",V)
        add_to_dict_num(format_counts, chosen_form)
        #if chosen_form not in format_mismatches:
        #    #print("Chosen:", chosen_form)
        #    format_mismatches[chosen_form] = {}
        #    #DG.add_node(chosen_form)
        #if chosen_form not in value_mismatches:
        #    value_mismatches[chosen_form] = {}
        value_len = len(V['value'])
        value_mismatch_count = len([x for x in V['stripped_value'] if x != chosen_value])
        format_mismatch_count = len([x for x in V['fuzzy_format'] if x != chosen_form])
        for i in range(value_len):
            #if value_len != 5:
            #    print("******VL:", value_len, "V:", V['value'])
            if V['stripped_value'][i] != chosen_value:
                add_to_dict_num(value_mismatches, [task, chosen_form, V['fuzzy_format'][i]], 1/value_len)
            if V['fuzzy_format'][i] != chosen_form:
                add_to_dict_num(format_mismatches, [task, chosen_form, V['fuzzy_format'][i]], 1/value_len)
                if chosen_form == "a{*}":
                    printed = False
                    if V['fuzzy_format'][i] == '':
                        debug_counts[0] += 1
                        if V['stripped_value'][i] != chosen_value:
                            debug_counts[1] += 1
                        if not printed:
                            print("V:", V)
                            print("P:", sorted_probs)
                            printed = True
                        print("\t",V['stripped_value'][i] != chosen_value, "\t", i, hi_index, chosen_value, "Value:", chosen_value, "NotValue:", V['value'][i], "Stripped:", V['stripped_value'][i])
                        
                #if not DG.has_node(f):
                #    DG.add_node(f)
                #if DG.has_edge(chosen_form, f):
                #    DG[chosen_form][f]['weight'] += 1
                #else:
                #    DG.add_edge(chosen_form, f, weight=1)
                #if chosen_form == 'A.A.A.':
                #    print("Diff length",f,chosen_form,V)
                
#print(format_counts)

task_keys = set().union(format_mismatches.keys(), value_mismatches.keys())
#print(format_mismatches.keys())
#print(value_mismatches.keys())
print(task_keys)
#exit()

for task in task_keys:
    results_file = open("patterns_of_difference_" + task + ".txt", "w")
    fm_dict = format_mismatches[task]
    vl_dict = value_mismatches[task]
    format_keys = set().union(fm_dict.keys(), vl_dict.keys())
    print("*****************",task,"*******************\n")
    for k in format_keys:
        fm_total = 0
        vl_total = 0
        #print(k,":", format_counts[k])
        #if len(k) == 0:
        #    print("Blank:", ord(k))
        results_file.write(k.replace("\n","\\n") + ":" + str(format_counts[k]) + "\n")
        if k in fm_dict:
            fm_keys = fm_dict[k].keys()
        else:
            fm_keys = {}.keys()
        if k in vl_dict:
            vl_keys = vl_dict[k].keys()
        else:
            vl_keys = {}.keys()
        mismatch_keys = set().union(fm_keys, vl_keys)
        for mk in mismatch_keys:
            #print("\t",mk)
            if mk in fm_keys:
                counts = str(truncate_float(fm_dict[k][mk]/format_counts[k],5))
                fm_total += truncate_float(fm_dict[k][mk]/format_counts[k],5)
            else:
                counts = "0"
            if mk in vl_keys:
                counts += ", " + str(truncate_float(vl_dict[k][mk]/format_counts[k],5))
                vl_total += truncate_float(vl_dict[k][mk]/format_counts[k],5)
            else:
                counts += ", 0"
            #print("\t",mk.replace("\n","\\n"), ":",counts)
            #if len(mk) == 0:
            #    print("Blank:", ord(mk))
            results_file.write("\t" + mk.replace("\n","\\n") + ":" + counts + "\n")
        results_file.write("\tTotal:" + str(truncate_float(fm_total)) + "," + str(truncate_float(vl_total)) + "\n")
    results_file.close()

print("Rows:", row_count)
print("Tasks:", task_count)
print("Values:", total_values)
print("Debug:", debug_counts)
#nx.write_gexf(DG, 'format_graph.gexf')        
        
# TODO: Next - compare each different string, using strip_punc function to remove punctuation
# Weight each variant according to format likelihood and both exact and stripped versions
# Choose most likely
# Then count format variations by other variants
                    
#for task, formats in format_dict.items():        
#    print(task)
#    sorted_formats = sorted([(k,v) for k,v in formats.items()], key=itemgetter(1), reverse=True)
#    print("\tcount:", len(sorted_formats),"formats:",sorted_formats[0:10])
#    print("\t**********************")
