#!/usr/bin/python3

from utils import add_to_dict_num
from math import log10
from jellyfish import levenshtein_distance
from operator import itemgetter

class comparator:

    def __init__(self):

        None

    def compare(self, A, B):

        return A == B

class probabilityTree:

    def __init__(self, function, probability_lookup):

        self.tree = probability_lookup
        self.function = function

    def get_probability(self, A, B):

        #print(self.function, A, B)
        comparison = self.function.compare(A, B)
        if comparison in self.tree:
            value = self.tree[comparison]
        else:
            value = self.tree['*']

        if isinstance(value, probabilityTree):
            return value.get_probability(A,B)
        else:
            return value


class equalsComparator(comparator):  # Kind of unnecessary but it has a Ronseal name

    def __init__(self):

        super().__init__()

class missingComparator(comparator):

    def __init__(self):

        super().__init__()

    def compare(self, A, B):

        if len(A) > 0 and len(B) == 0:
            return 1
        elif len(B) > 0 and len(A) == 0:
            return -1
        else:
            return 0

class similarityComparator(comparator):

    def __init__(self):

        super().__init__()

    def compare(self, A, B):

        return levenshtein_distance(A,B)

class confidenceCalculator:

    def __init__(self, probability_tree):

        self.values = {}
        self.probability_tree = probability_tree
        self.value_count = 0
        self.calculated = False

    def add_value(self, value):

        add_to_dict_num(self.values, value)
        self.value_count += 1

    def calc(self):

        keys = [k for k in self.values.keys()]
        all_probabilities = []
        probability_sum = 0

        for i in range(len(keys)):
            total_probability = 1

            for j in range(len(keys)):

                probability = self.probability_tree.get_probability(keys[i], keys[j])
                total_probability *= probability ** self.values[keys[j]]

            if len(keys) == 1:
                probability_sum += (1-probability) ** self.values[keys[j]]
            all_probabilities.append([keys[i],total_probability])
            probability_sum += total_probability
            print(keys[i],i,probability_sum,total_probability)

        self.calculated_probabilities = sorted([p for p in all_probabilities], key=itemgetter(1), reverse=True)
        for cp in self.calculated_probabilities:
            cp.append(int(log10(cp[1]/(probability_sum-cp[1]))*10))

        self.calculated = True


    def conf_iter(self):

        if not self.calculated:
            self.calc()

        for cp in self.calculated_probabilities:
            yield cp



if __name__ == '__main__':


    PT1 = probabilityTree(similarityComparator(), {1:0.6, 2:0.3, '*': 0.1})
    PT2 = probabilityTree(equalsComparator(), {1:0.9, 0: PT1})
    PT3 = probabilityTree(missingComparator(), {1:0.7, -1:0.7, 0: PT2})

    print("Ex1:", PT3.get_probability("jones","jones"))
    print("Ex2:", PT3.get_probability("jones","jonesy"))
    print("Ex3:", PT3.get_probability("jones","jonesyyy"))
    print("Ex4:", PT3.get_probability("","jonesyyy"))

    CC = confidenceCalculator(PT3)
    CC.add_value("jones")
    CC.add_value("jones")
    CC.add_value("jones")
    
    for c in CC.conf_iter():
        print(c)
