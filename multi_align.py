#!/usr/bin/python3

from collections import OrderedDict

# Takes a set of aligned pairs of records or fields and maps the alignments into a mapping between them all
class MultiAlign:

    # The alignments are expected to be in order of length (possibly not essential but haven't tested that)
    # So the longest record goes first and sets up the virtual record (a list) to build the mapping around
    def __init__(self, record_lengths, record_alignments):

        # Assume that indices of lengths array match those of the entries in the alignments dictionary
        # Also assume ordereddict has been used as an input for alignments
        # The entries in multi_align will be lists as wide as there are records (or fields)
        # Here are two example rows to explain how the output is interpreted:
        # There are 3 records to be aligned, each record contains 4 fields
        # So record_lengths = [4,4,4]
        # Row X of multi_align = [2,2,1]; this means field 2 in record 0 and 1 and field 1 in record 2 are mapped to each other
        # Row Y of multi_align = [4,4,-1]; field 4 in records 0 and 1 are mapped, but do not map to any field in record 2
        self.multi_align = []

        self.record_lengths = record_lengths
        self.record_alignments = record_alignments  # See __main__ method below for example of expected format

        self.max_indices = [0 for i in range(len(record_lengths))]

    def add_row(self, row):
        
        print("Add row:",row)
        for i in range(len(row)):
            if row[i] > self.max_indices[i]:
                self.max_indices[i] = row[i]
        self.multi_align.append(row)

    def do_alignment(self):

        self.multi_align = []
        alignment_keys = [k for k in self.record_alignments.keys()]
        #print("MA len:", len(self.multi_align))
        #print("Record lengths:",self.record_lengths)
        #print("MultiKeys:",alignment_keys)
        #print("Alignments:", self.record_alignments)

        # The 'spine' is the multi_align variable. These two variables keep track of its length and current position
        spine_len = self.record_lengths[0]
        spine_idx = 0
    
        # Nothing to do
        if len(alignment_keys) == 0:
            return

        # Set up multi_align record (spine) using the longest record available
        # If longest record is record i, then ith entry in nth row will be n, other entries will be -1
        for i in range(spine_len):
            map_row = [-1 for s in self.record_lengths]
            map_row[alignment_keys[0]] = i
            #print("Start MA:",i,":",map_row)
            self.multi_align.append(map_row)
        #if len(self.multi_align) > 0:
        #    print("Last:",self.multi_align[-1])

        #print("MA len:", len(self.multi_align))
        # Iterating through each pair of alignments (e.g. recordset i to recordset j)
        for primary_col in alignment_keys:  # column index of primary record
            #print("Rec:",primary_col)
            column_indices = [0 for s in self.record_lengths]
            for align in self.record_alignments[primary_col]:
                #print("Match",align)
                secondary_col = align[0]  # column index of secondary (aligned with primary) record
                align_map = [(k,v) for k,v in align[1].items()]  # aligned items within each record
                spine_idx = 0
                while len(align_map) > 0:
                    this_map = align_map.pop(0)  # this is a tuple holding indexes of mapped items in the primary and secondary records
                    match_found = False
                    while not match_found: # scroll down multi_align list until value in primary or secondary columns
                                           # matches one of values in this_map tuple
                        #print("Idx",spine_idx,"ma len",len(self.multi_align),"map",this_map)
                        if spine_idx == len(self.multi_align):  # we've hit the bottom so append a new row
                            map_row = [-1 for s in self.record_lengths]
                            map_row[primary_col]= this_map[0]
                            map_row[secondary_col] = this_map[1]
                            self.multi_align.append(map_row)
                            match_found = True   # new row constructed from this mapping makes it a match
                            #print("*****Added:", map_row)
                        else:
                            #print("\t","indxs",primary_col,secondary_col,"align",self.multi_align[spine_idx],"map",this_map,"col idxs:",column_indices)

                            # keep track of column values we've skipped over
                            #print("Indexes:",spine_idx,len(self.multi_align),secondary_col, len(column_indices))
                            if column_indices[secondary_col] < self.multi_align[spine_idx][secondary_col]:
                                column_indices[secondary_col] = self.multi_align[spine_idx][secondary_col] + 1

                            # found a match in one of the columns
                            if this_map[0] == self.multi_align[spine_idx][primary_col]\
                                    or this_map[1] == self.multi_align[spine_idx][secondary_col]:
                                match_found = True
                                #print("\tMatch found",self.multi_align[spine_idx],this_map)
                            else: # keep looking for a match
                                spine_idx += 1
                                continue

                        #print("Len spine:",len(self.multi_align),"Idx",spine_idx)
                        #print("Rec width:",len(self.multi_align[spine_idx]),"primary_col",primary_col,"match",secondary_col)
                        #print("\tMap:", this_map,"This:",self.multi_align[spine_idx][primary_col],"Match:",self.multi_align[spine_idx][secondary_col])
                        #while this_map[0] > column_indices[primary_col]:
                        #    ins_row = [-1 for s in self.record_lengths]
                        #    ins_row[secondary_col] = this_map[1]
                        #    print("\tInserting primary_col col",ins_row)
                        #    self.multi_align.insert(spine_idx, ins_row)
                        #    column_indices[primary_col] += 1
                        #    spine_len += 1
                        #    spine_idx += 1

                        # If there are missing values in the secondary column then insert rows which don't map to other columns
                        # to fill in gaps. This is why we had to keep track of which numbers had been passed along the way,
                        # so they don't get duplicated
                        while this_map[1] > column_indices[secondary_col]:
                            ins_row = [-1 for s in self.record_lengths]
                            ins_row[secondary_col] = column_indices[secondary_col] #this_map[1]
                            #print("\tInserting match col",ins_row)
                            self.multi_align.insert(spine_idx, ins_row)
                            column_indices[secondary_col] += 1
                            spine_len += 1
                            spine_idx += 1

                    # set value in secondary col to item index (value in this_map[1])
                    # this will be the row where the value in the primary column matched this_map[0]
                    self.multi_align[spine_idx][secondary_col] = this_map[1]
                    column_indices[primary_col] += 1 # = this_map[0]+1
                    column_indices[secondary_col] += 1 # = max(column_indices[secondary_col],this_map[1])+1
                    #print("\tUpdated Row:",self.multi_align[spine_idx])
                    spine_idx += 1

        for ma in self.multi_align:
            self.max_indices = [max(self.max_indices[i], ma[i]+1) for i in range(len(ma))]

        if len(self.multi_align) < 6:
            print("Pre-complete:",self.multi_align)
            print("Max indices:",self.max_indices)
            print("Record lengths:",self.record_lengths)
        for i in range(len(self.max_indices)):
            while self.max_indices[i] < self.record_lengths[i]:
                self.multi_align.append([self.max_indices[i] if j == i else -1 for j in range(len(self.max_indices))])
                self.max_indices[i] += 1
        #    print("End MA:",al)

if __name__ == "__main__":

    strings = ["abcde", "abcde", "abde"]
    strings = ["abd", "abcde","abc"]
    string_lengths = [len(s) for s in strings]
    # do alignments in length order, so longest matches to others first, then next longest to remainder etc.
    alignments = OrderedDict()
    alignments[0] = [[1, {0:0,1:1,2:3}],
                     [2, {0:0,1:1}]]
    alignments[1] = [[2, {0:0,1:1,2:2}]]
    #alignments[1] = [[1, {0:0,1:1,2:2,3:3,4:4}],
    #                 [2, {0:0,1:1,3:2,4:3}]]

    print(strings)
    for al in alignments.items():
        print(al)
    M = MultiAlign(string_lengths, alignments)
    M.do_alignment()
    for ma in M.multi_align:
        print(ma)
