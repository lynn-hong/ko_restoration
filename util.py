__author__ = 'Lynn'
__email__ = 'lynnn.hong@gmail.com'
__date__ = '6/9/2016'

def add_userdic(file_list, userdic_file):
    add_list = list()
    for f in file_list:
        with open(f, "r") as fi:
            for word in fi.readlines():
                if f.startswith("original"):
                    # word \t tag
                    items = word.strip().split("\t")
                    add_list.append("%s\t%s" % (items[0], items[1]))
                else:
                    add_list.append("%s\t%s" % (word.strip(), "NNP"))
    with open(userdic_file, "w") as f:
        f.write("\n".join(add_list))

def create_dic(inputFile):
    return_dic = dict()
    with open(inputFile, "r") as f:
        for line in f.readlines():
            items = line.strip().split("\t")
            return_dic[items[0]] =  items[1]
    return return_dic

def create_set(inputFile):
    return_list = list()
    with open(inputFile, "r") as f:
        for line in f.readlines():
            return_list.append(line.strip())
    return set(return_list)
