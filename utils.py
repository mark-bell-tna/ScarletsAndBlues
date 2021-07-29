# Utility functions for incrementing counts in dictionaries or appending to a list of values
def add_to_dict_num(D, k, v=1):
    if k in D:
        D[k] += v
    else:
        D[k] = v

def add_to_dict_list(D, k, v):
    if k in D:
        D[k].append(v)
    else:
        D[k] = [v]


