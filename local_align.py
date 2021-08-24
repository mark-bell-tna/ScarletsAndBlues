#!/usr/bin/python3

import numpy as np

# The functions Del, Ins and Sub assign scores for Deletes, Inserts and Substitutions respectively
# The scores here work well but may want to make them configurable for experimentation
def Del(x):

    return -1

def Ins(x):

    return -1

def Sub(x,y): # Could expand this to return different scores depending on x and y (i.e. if x regularly mistaken for y)

    if x == y:
        return 1
    #elif ord(x) in [30,31] or ord(y) in [30,31]:
    #    return 0
    else:
        return -3


# Takes two strings (or sequences) and builds a score matrix which is then used by other methods
# to identify an optimal alignment of the strings
def local_align(X,Y):

    m = len(X)
    n = len(Y)

    S = np.zeros((m+1,n+1))

    # Top row and left hand column set to 0
    for i in range(0,m):
        S[i,0] = 0

    for j in range(1,n+1):
        S[0,j] = 0
        # Move through char by char comparison of the strings
        # Assign score depending on whether a replacement or insert/delete of one of the chars would be most advantageous
        for i in range(1,m+1):
            S[i,j] = max(0, S[i-1,j-1]+Sub(X[i-1],Y[j-1]), S[i-1,j]+Del(X[i-1]), S[i,j-1]+Ins(Y[j-1]))

    return S

# Back traces through the matrix (parameter S) to return an optimal alignment
# Found that if one string is much longer (e.g. 3x) than other it goes wrong
# by matching individual characters of shorter string across entire length of longer on
# Use all_alignment function instead
def one_alignment(S,X,Y):

    #Sub = lambda a,b: 1 if a == b else -3
    #Del = lambda a: -1
    #Ins = lambda a: -1

    z = ["",""]
    i,j = S.shape
    # Use coordinates of highest value in matrix as starting point
    i,j = np.unravel_index(np.argmax(S, axis=None), S.shape)

    k = 0
    while k < len(X)-i:
        z[0] += X[len(X)-k-1]
        z[1] += "~"
        k += 1

    k = 0
    while k < len(Y)-j:
        z[0] += "~"
        z[1] += Y[len(Y)-k-1]
        k += 1

    while i != 0 and j != 0 and S[i,j] != 0:
        if S[i,j] == S[i-1,j-1] + Sub(X[i-1],Y[j-1]):
            z[0] += X[i-1]
            z[1] += Y[j-1]
            i,j = i-1, j-1
        elif S[i,j] == S[i-1, j] + Del(X[i-1]):
            z[0] += X[i-1]
            z[1] += "~"
            i -= 1
        else:
            z[0] += "+"
            z[1] += Y[j-1]
            j -= 1
    while i != 0:
        z[0] += X[i-1]
        z[1] += "~"
        i -= 1

    while j != 0:
        z[0] += Y[j-1]
        z[1] += "~"
        j -= 1


def all_alignment(T,A,B):

    # These need to match with local_align function above
    # Would be better to make them global parameters or functions
    #Sub = lambda a,b: 1 if a == b else -3
    #Del = lambda a: -1
    #Ins = lambda a: -1

    # Input matrix is T but S is used through rest of code so it can be replaced by a smaller matrix
    # Similar situation with strings X and Y
    S = T
    X = A
    Y = B
    #z = ["",""]
    alignment = []  # This will end as a list of tuples, each tuple mapping a char in X with one in Y, or None if there is no mapping
    while np.max(S) > 0:
        i,j = S.shape
        # Probably a better way but this finds highest value nearest to bottom right of matrix
        high_vals = (-S).argsort(axis=None)[0:10]
        high_vals[::-1].sort()
        high_vals = np.unravel_index(high_vals, S.shape)
        high_vals = [(high_vals[0][i],high_vals[1][i],S[high_vals[0][i],high_vals[1][i]]) for i in range(len(high_vals[0]))]
        max_val = max([x[2] for x in high_vals])
        high_vals = [x for x in high_vals if x[2] == max_val]
        i,j = high_vals[0][0], high_vals[0][1]

        #i,j = np.unravel_index(np.argmax(S, axis=None), S.shape) # Find coordinates of highest value
        k = 0
        # First compensate for disparity in lengths of the two strings
        # None is used to indicate there is no matching character on one side
        while k < len(X)-i:
            #z[0] += X[len(X)-k-1]
            #z[1] += "~"
            alignment.append((len(X)-k-1, None))
            k += 1

        # Do same on the Y side
        k = 0
        while k < len(Y)-j:
            #z[0] += "~"
            #z[1] += Y[len(Y)-k-1]
            alignment.append((None, len(Y)-k-1))
            k += 1

        # Start from cell i,j and work backwards finding optimal route through the matrix
        while i != 0 and j != 0 and S[i,j] != 0:
            if S[i,j] == S[i-1,j-1] + Sub(X[i-1],Y[j-1]):
                #z[0] += X[i-1]
                #z[1] += Y[j-1]
                alignment.append((i-1, j-1)) # Go diagonal
                i,j = i-1, j-1
            elif S[i,j] == S[i-1, j] + Del(X[i-1]):
                #z[0] += X[i-1]
                #z[1] += "~"
                alignment.append((i-1, None)) # Go up
                i -= 1
            else:
                #z[0] += "+"
                #z[1] += Y[j-1]
                alignment.append((None, j-1))  # Go across
                j -= 1

        # If we haven't reached the top or left of the matrix, shrink the matrix and continue
        if i > 0 and j > 0:
            S = S[0:i+1,0:j+1]
            X = X[:i]
            Y = Y[:j]
        else:
            break

    # If there are characters left at beginning of strings then add them to the alignment too
    if np.max(S) > 0:
        while i != 0:
            #z[0] += X[i-1]
            alignment.append((i-1, None))
            #z[1] += "~"
            i -= 1

        while j != 0:
            #z[0] += Y[j-1]
            #z[1] += "~"
            alignment.append((None, j-1))
            j -= 1

    alignment.reverse() # alignment comes out backwards so flip it around
    return alignment

if __name__ == "__main__":

    X = "EAWACQGKL"
    Y = "ERDAWCQPGKWY"

    #X = "ABDEFG"
    #Y = "BCEF"

    #X = "CoulthardH.G.Lieut. R.A.N.C.CrutchlyC.SirLieut Govr + SectCrichtonA.R.MissWoman ClerkCatlingD.G.MissWoman ClerkCraweA.M.MissWoman ClerkHarrisonA.C.A Res17 LancersCounterHMrs.Woman ClerkCarrington AMAMMissWoman ClerkCarneB.M.N.MissWoman ClerkCarleM.O.MissWoman ClerkConnellD.A ResRe Scots FusCavanaghJ.Somerset L.J.CastellG.C.Mrs.Woman ClerkCkarjEMrsWoman ClerkCroweMMissWoman ClerkCole-BowenM.E.MissWoman ClerkCollettM.R.MissWoman ClerkCourthorpe-MunroeDMGMrssWoman ClerkChawnerJ.1/21 FootCranefieldF.B.MissWoman ClerkClarkeM.A.MissWoman ClerkColsonE.W.MrsWoman ClerkCairnsTMrsColesE.A.MrsWomen ClerksCannoingR.G.MrsWoman ClerkChancellorF.A.MissWoman ClerkCollinsOMissWoman ClerkCrossG.MissWoman ClerkCliftonDAMissWoman ClerkCaskeE.A.MissWoman ClerkCrossH McCMissWoman ClerkCabomJOMissEx Soldr Clerk Class AClarkeJ.G.MrsTempy CookCompton-RickettJSirCasserkeyR4 Dragoon GdsCunningsJLeinster RegtChapmanAKRR Cps.CheesemanFR.A.M. Cps.CannellW.P.F.Secy's OfficeCave-Browne-CaveThos.Sir"
    #B = "CoulthardH.C.LieutR.A.N.C.CritchleyCSirLieut Govn'r SectCrichtonA.B.MissWoman ClerkCatlingD.G.MissWoman ClerkCraweA.M.MissWoman ClerkHarrisonA.C.A Res17 LancersCounterHMrs.Woman ClerkCarrington AMAMMissWoman ClerkCarneB.M.N.MissWoman ClerkCarleM.O.MissWoman ClerkConnellD.A ResRe Scots FusCavanaghJ.Somerset L.J.CastellG.C.Mrs.Woman ClerkCkarjEMrsWoman ClerkCroweMMissWoman ClerkCole-BowenM.E.MissWoman ClerkCollettM.R.MissWoman ClerkCourthorpe-MunroeDMGMrssWoman ClerkChawnerJ.1/21 FootCranefieldF.B.MissWoman ClerkClarkeM.A.MissWoman ClerkColsonE.W.MrsWoman ClerkCairnsTMrsColesE.A.MrsWomen ClerksCannoingR.G.MrsWoman ClerkChancellorF.A.MissWoman ClerkCollinsOMissWoman ClerkCrossG.MissWoman ClerkCliftonDAMissWoman ClerkCaskeE.A.MissWoman ClerkCrossH McCMissWoman ClerkCabomJOMissEx Soldr Clerk Class AClarkeJ.G.MrsTempy CookCompton-RickettJSirCasserkeyR4 Dragoon GdsCunningsJLeinster RegtChapmanAKRR Cps.CheesemanFR.A.M. Cps.CannellW.P.F.Secy's OfficeCave-Browne-CaveThos.Sir"
    #A = A #[0:300]
    #B = B[0:75]
    #Y = "CoulthardH.C.LieutR.a.n.c.CritchleyCSirLieut Govn'r Sec"

    X = "abc|def|gh ij"
    Y = "abc|def|gh j"

    print("X len:",len(X))
    print("Y len:",len(Y))
    A = local_align(X,Y)
    print(A)

    AL = all_alignment(A,X,Y)
    x = ""
    y = ""
    for t in AL:
        if t[0] is None:
            x += "-"
        else:
            x += X[t[0]]
        if t[1] is None:
            y += "-"
        else:
            y += Y[t[1]]

    print(x)
    print(y)

