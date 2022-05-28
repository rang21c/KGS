from konlpy.tag import Mecab
import re

mecab = Mecab()

def delete_sign(sentence, change=""):
    # delete unicode sign
    result = re.sub(r'[^가-힣A-Za-z0-9\.\{\}\[\]\/?\.,\)~`!\-+<>\$%\\\=\(\'\"\s\x20”’ᆞ·㎕-㏆~ＭＫｍ°]|[\_]', change, sentence)
    # except bracket
    result = re.sub(r'[\{\}\[\]\)\(]', "", result)
    # except ' "
    result = re.sub(r'[!’\.,\'\"]', "", result)

    return result

def PostProcess_Mecab(original_sentence, open_tag=('<','>'), close_tag=('</','>')):
    open_start, open_end = open_tag
    close_start, close_end = close_tag

    original = mecab.pos(original_sentence)
    #print("original : ",original)

    josa = ['JKS', 'JKC', 'JKG', 'JKO', 'JKB', 'JKV', 'JKQ', 'JX', 'JC']
    verbs = ['VV', 'VA', 'VX', 'VCP', 'VCN']
    eomal = ['EP', 'EF', 'EC', 'ETN', 'ETM'] # eomal eomi

    detach_pos = josa + verbs + eomal

    check_postag = []
    change_seq = []
    
    flag = 0
    start = 0
    end = 0
    out = 0

    debug_original = []
    temp = []

    pos_label = []
    # check tag content and close tag
    for index, (value, label) in enumerate(original):
        # check open tag
        if value==open_start:
            flag = 1
        elif value==open_end and flag == 1:
            flag = 2
            start = index + 1
        # check close tag
        elif value==close_start:
            flag = 3
            end = index - 1
        elif value==close_end and flag == 3:
            flag = 0
            out = index + 1
            #
            check_postag.append(pos_label)
            change_seq.append((start, end, out))
            debug_original.append(temp)
            pos_label = []
            temp = []
        #check entity inside
        elif flag == 2:
            pos_label.append(label)
            temp.append(original[index])
            
    answer_sentence = original_sentence

    for i, (s, e, o) in enumerate(change_seq):
        print ("original:",debug_original,"check:",check_postag[i])

        no_name_str=""
        end_tag_str=""
        nn_len = 0

        # count not name entity
        for ind, label in enumerate(reversed(check_postag[i])):
            if not label in detach_pos:
                nn_len = ind
                break

        # if only name entity
        if nn_len == 0:
            continue
        # get josa string
        for value, pos in original[e-nn_len+1:e+1]:
            no_name_str = no_name_str + value
        # get close tag string
        for value, pos in original[e+1:o]:
            end_tag_str = end_tag_str + value

        print("str :  ",no_name_str)
        print("tag :  ",end_tag_str)

        # switching place string and close tag
        origin_str = no_name_str + end_tag_str
        result_str = end_tag_str + no_name_str

        print("change:  ",origin_str,"  ==>  ",result_str)

        # replace string
        answer_sentence = answer_sentence.replace(origin_str,result_str)

    return answer_sentence