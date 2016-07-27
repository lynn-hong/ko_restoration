__author__ = 'Lynn'
__email__ = 'lynnn.hong@gmail.com'
__date__ = '6/10/2016'

import sys
sys.path.append('<YOUR PATH TO KOMORAN IF YOU NEED>')

import re
from datetime import datetime
from komoran.komoran import KomoranClass
from ko_restoration import util, restoration

### INPUT SETUP
data_source = "text_test"       # 'text_file' or 'text_test'
complex_verb_set = util.create_set("complex_verb.txt")
if data_source == "text_file":
    input_file = "<PATH TO YOUR INPUT TEXT FILE>"
    output_file = "<PATH TO YOUR OUTPUT TEXT FILE>"
    body_idx = "<INDEX OF YOUR TEXT BODY>"     # int
elif data_source == "text_test":
    ### to test, you just edit the line below
    txt = ["지구를 들어올린다"]     # <<<<<<< string list or string

### KOMORAN SETUP
komoran = KomoranClass(modelPath="modelsasdf")
userdic_files = ["original_userdic.txt", "noun_general_list.txt"]
userdic = "<PATH TO YOUR KOMORAN user.dic FILE>"
ko_ascii_file = open("ko_ascii_code.txt")
ko_ascii_code = ko_ascii_file.read().replace("\n", ",").split(",")
util.add_userdic(userdic_files, userdic)
print("Finish adding user dictionary...")

### READ INPUT
if data_source == "text_file":
    with open(input_file, "r") as f:
        lines = f.readlines()
elif data_source == "text_test":
    if type(txt) == str:
        lines = [txt]
    elif type(txt) == list:
        lines = txt
print("Finish setting up...start processing...")
print(datetime.now())


idx = 0
for row in lines:
    idx += 1
    #if idx == 100:     # for test
    #    break
    if idx % 10000 == 0:
        print(idx)
        print(datetime.now())
    if data_source == "text_file":       # text_file
        item = row.strip().split("\t")      # tsv format
        try:
            body = item[body_idx]
        except IndexError:
            continue
    elif data_source == "text_test":
        body = row
    body = restoration.rm_url(body)
    body = restoration.rm_specials(body)
    if body.strip() != "":
        result = komoran.analyze(body.strip())
        if len(result[0]) != 0:
            print(result)
            tokens = restoration.komoran_processing(result[0], complex_verb_set)
            if tokens == "":
                continue
            else:
                if data_source == "text_file":
                    with open(output_file, "a") as f:
                        f.write("%s\n" % "\t".join(item[:-1]+[tokens])) # if your text body is at the last index
                elif data_source == "text_test":
                    print(tokens)

print("Finish all articles...")
print(datetime.now())