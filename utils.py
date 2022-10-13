import string

# Utility functions for incrementing counts in dictionaries or appending to a list of values
def add_to_dict_num(D, k, v=1):
    if isinstance(k, list):
        path = k
    else:
        path = [k]
    this_d = D
    for k in path[:-1]:
        #print(k)
        if k in this_d:
            this_d = this_d[k]
        else:
            this_d[k] = {}
            this_d = this_d[k]
    k = path[-1]
    if k in this_d:
        this_d[k] += v
    else:
        this_d[k] = v
    #print(D)

def add_to_dict_list(D, k, v):
    if k in D:
        D[k].append(v)
    else:
        D[k] = [v]

def truncate_float(F, places=3):

    power_ten = 10 ** places
    return int(F * power_ten) / power_ten

class TextForm:

    def __init__(self, text, case_sensitive=True):

        self.text = text
        if case_sensitive:
            self.set_text_form(text)
        else:
            self.set_text_form(text.lower())

    def strip_punc(self):
        
        return self.text.translate(str.maketrans('', '', string.punctuation)).strip().replace(" ","")
        
    def set_text_form(self, text):

        self.text_form = []
        self.text = text

        for c in text:
            ord_c = ord(c)

            if 48 <= ord_c <= 57:
                this_form = '9'
            elif 65 <= ord_c <= 90:
                this_form = 'A'
            elif 97 <= ord_c <= 122:
                this_form = 'a'
            else:
                this_form = c

            if len(self.text_form) == 0:
                self.text_form.append([this_form,1])
                continue
            last_form = self.text_form[-1]
            if last_form[0] == this_form[0]:
                last_form[1] += 1
            else:
                self.text_form.append([this_form, 1])


    def __repr__(self):

        return self.text_form

    def __str__(self):

        return self.get_form_regex()

    def get_form_list(self):

        return self.text_form

    def get_form_regex(self, multi=None):

        out_form = ""

        for f in self.text_form:
            out_form += f[0]

            if f[1] > 1:
                if multi is None:
                    out_form +=  "{" + str(f[1]) + "}"
                else:
                    out_form += "{" + multi + "}"

        return out_form
    