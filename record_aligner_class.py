#!/usr/bin/python3

from local_align import local_align, all_alignment

class recordAligner:

    def __init__(self, delimiters = [30,31,32], case_sensitive = False):

        self.delimiters = delimiters
        self.case_sensitive = case_sensitive

    def align(self, recordA, recordB):

        #NW = needleman_wunsch(recordA, recordB)
        LA = local_align(recordA, recordB)
        NW = all_alignment(LA, recordA, recordB)
        #print("A:",recordA[0:50])
#        #print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        #print("B:",recordB[0:50])
        print("NW:",NW[0:50])

        self.alignments = {}
        p1 = 0
        p2 = 0
        l1 = len(recordA)
        l2 = len(recordB)
        f1 = [0,0,0,-1]
        f2 = [0,0,0,-1]
        n_pos = 0
        d1 = True
        d2 = True

        while p1 < l1 and p2 < l2:
            c1 = NW[n_pos][0]
            ord1 = None
            ord2 = None
            if c1 is not None:
                p1 += 1
                ord1 = ord(recordA[c1])
                d1 = True
                if ord1 == self.delimiters[0]:
                    f1[0] += 1
                    f1[1] = 0
                    f1[2] = 0
                    f1[3] = -1
                elif ord1 == self.delimiters[1]:
                    f1[1] += 1
                    f1[2] = 0
                    f1[3] = -1
                elif ord1 == self.delimiters[2]:
                    f1[2] += 1
                    d1 = False
                    f1[3] += 1
                else:
                    d1 = False
                    f1[3] += 1

            c2 = NW[n_pos][1]
            if c2 is not None:
                p2 += 1
                ord2 = ord(recordB[c2])
                d2 = True
                if ord2 == self.delimiters[0]:
                    f2[0] += 1
                    f2[1] = 0
                    f2[2] = 0
                    f2[3] = -1
                elif ord2 == self.delimiters[1]:
                    f2[1] += 1
                    f2[2] = 0
                    f2[3] = -1
                elif ord2 == self.delimiters[2]:
                    f2[2] += 1
                    d2 = False
                    f2[3] += 1
                else:
                    d2 = False
                    f2[3] += 1

            #print("C1:",c1,"Ord1:",ord1,"C2:",c2,"Ord2:",ord2,"n_pos:",n_pos,"F1:",f1,"F2:",f2,"D1:",d1,"D2:",d2)
            if c1 is not None and not d1 and c2 is not None and not d2 and chr(ord1).lower() == chr(ord2).lower():
                #print("In loop, C1:",c1,"Ord1:",ord1,"C2:",c2,"Ord2:",ord2,"n_pos:",n_pos,"F1:",f1,"F2:",f2)
                D = self.alignments
                for i in range(len(f1)-1):
                    if f1[i] not in D:
                        D[f1[i]] = {}
                    if f2[i] not in D[f1[i]]:
                        D[f1[i]][f2[i]] = {}
                    D = D[f1[i]][f2[i]]
                D[f1[-1]] = f2[-1]
            n_pos += 1

        #print("Final:",self.alignments)

if __name__ == "__main__":

    A = "abc|def|ghi"
    B = "abc|def|ghi"
    RA = recordAligner(delimiters = [ord('|'), ord('^'), 32])
    RA.align(A,B)
    print("A:",A,"B:",B)
    print(RA.alignments)

    A = "abc|def|ghi"
    B = "abc|de^f|ghi"
    RA = recordAligner(delimiters = [ord('|'), ord('^'), 32])
    RA.align(A,B)
    print("A:",A,"B:",B)
    print(RA.alignments)

    A = "abc|def|gh ij"
    B = "abc|def|gh j"
    RA = recordAligner(delimiters = [ord('|'), ord('^'), 32])
    RA.align(A,B)
    print("A:",A,"B:",B)
    print(RA.alignments)
