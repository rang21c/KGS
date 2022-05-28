import argparse
import logging
import os
import re
import unicodedata
import pandas as pd
from pathlib import Path
from typing import List, Optional

import torch
from torch.utils.data import TensorDataset
import csv

train_path = "./origin_klue/klue-ner-v1.1_train.tsv"
test_path = "./origin_klue/klue-ner-v1.1_dev.tsv"

def TSV_dataset(file_name):
    file_path = Path(file_name)
    raw_text = file_path.read_text().strip()
    raw_docs = re.split(r"\n\t?\n", raw_text)

    original_guid = []
    original_sentence = []
    original_tokens = []
    original_labels = []

    dataset = []

    for doc in raw_docs:
        sentence = ""

        token_list = []
        label_list = []
        arg_list = []
        prev = ""
        bracket = False

        for line in doc.split("\n"):
            if line[:2] == "##":
                guid = line.split("\t")[0].replace('## ', "")
                continue
            token, tag = line.split("\t")

            if token == ')':
                bracket = False
                continue

            if token == '(' or bracket == True:
                bracket = True
                continue

            if len(re.findall(u'[ㄱ-ㅎㅏ-ㅣ]', "" + token)) > 0:
                continue

            if len(re.findall(u'[^가-힣A-Za-z0-9\.\{\}\[\]\/?.,\)~`!\-+<>\$%\\\=\(\'\"\s\x20”’ᆞ·]|[\_]', "" + token)) > 0:
                continue

            sentence += token
            # if token == " ":
            #  continue
            if tag[0] != 'O':
                tag = tag + "-" + tag[0]
                tag = tag[2:]
            # if token == "." or token == "!" or token == "?":
            #  arg_list.append({"token":' ',"label":"O"})

            # -- 체크
            if prev == '-' and token == '-':
                arg_list.pop()
                token_list.pop()
                label_list.pop()
                prev = '^'
                continue
            if prev == '^' and token == '-':
                continue

            # 한글. 체크
            # if len(re.findall(u'[,가-힣ㄱ-ㅎ]', prev))>0:
            #  if len(re.findall(u'[\.!\?~]', ""+token))>0:
            #   arg_list.append({"token":' ',"label":"O"})
            # print(prev+token)
            # .한글 체크
            #    if len(re.findall(u'[\.!\?~]', prev)):
            #     if len(re.findall(u'[,가-힣ㄱ-ㅎ]', ""+token))>0:
            #      arg_list.append({"token":' ',"label":"O"})
            # prev = ""+token

            # list append
            token_list.append(token)
            label_list.append(tag)
            arg_list.append({"token": token, "label": tag})
        arg_list.append({"token": ' ', "label": "O"})

        original_guid.append(guid)
        original_sentence.append(sentence)
        original_tokens.append(token_list)
        original_labels.append(label_list)
        dataset.append({"sentence": sentence, "guid": guid, "args": arg_list})



    return dataset




def get_labels():
    return ["O",
            "B-PS","I-PS",
            "B-LC","I-LC",
            "B-OG","I-OG",
            "B-DT","I-DT",
            "B-TI","I-TI",
            "B-QT","I-QT"]

def setting(dataset):
    label_list = get_labels()

    input_tokens = []
    input_labels = []

    for data in dataset:
      tokens = ""
      labels = ""
      for arg in data["args"]:
        tokens += arg["token"] + " "
        labels += arg["label"] + " "
      input_tokens+=[tokens[:-3]]
      input_labels+=[labels[:-3]]
    print(input_tokens, input_labels)
    return list(zip(input_tokens, input_labels));



#regular func

def regulation(token_train):
    token_train = list(token_train)
    for i in range(0,len(token_train)):
      token_train[i] = list(token_train[i])

    # . 연속(2개이상) -> ...
    pattern3 = "”" # -> "
    pattern4 = "[’`]" # -> '
    pattern5 = "\d·\d|\dᆞ\d" # -> .
    pattern6 = "[ᆞ·+]" # -> ,
    pattern7 = "~+" # -> ~
    pattern8 = "!+" # -> !
    pattern9 = "\?+" # -> ?
    pattern10 = "\.{2,}" # -> ?
    pattern11 = ",+" # -> ,
    pattern12 = "~ {2,}" # -> ~
    r3 = re.compile(pattern3)
    r4 = re.compile(pattern4)
    r5 = re.compile(pattern5)
    r6 = re.compile(pattern6)
    r7 = re.compile(pattern7)
    r8 = re.compile(pattern8)
    r9 = re.compile(pattern9)
    r10 = re.compile(pattern10)
    r11 = re.compile(pattern11)
    r12 = re.compile(pattern12)


    for t in token_train:
      if r9.search(t[0]) is not None:
        print(r9.search(t[0]))


    for t in token_train:
      t[0]=re.sub(pattern3,'\"',t[0])
      t[0]=re.sub(pattern4,'\'',t[0])
      if r5.search(t[0]) is not None:
        t[0]=re.sub('[ᆞ·]','/',t[0])
      t[0]=re.sub(pattern6,',',t[0])
      t[0]=re.sub(pattern7,'~',t[0])
      t[0]=re.sub(pattern8,'!',t[0])
      t[0]=re.sub(pattern9,'?',t[0])
      t[0]=re.sub(pattern10,'...',t[0])
      t[0]=re.sub(pattern11,',',t[0])
      t[0]=re.sub(pattern12,'~',t[0])




    for t in range(len(token_train)-1,-1,-1):
      sentence, label = token_train[t]
      if "-0-" in sentence:
        del token_train[t]
      elif "-o-" in sentence:
        del token_train[t]
      elif "-O-" in sentence:
        del token_train[t]
      elif "- -" in sentence:
        del token_train[t]
      elif "><" in sentence:
        del token_train[t]
      elif "-.-" in sentence:
        del token_train[t]
      elif "-,-" in sentence:
        del token_train[t]
      elif ">" in sentence:
        del token_train[t]
      elif "<" in sentence:
        del token_train[t]

    pattern = "[\;:|\)*`^\_+<>@\#$\\\(]"
    r = re.compile(pattern)

    return token_train


def TSV_Write(ds_list,file_name):
    with open(file_name+'.tsv', 'w', encoding='utf-8', newline='') as f:
      tw = csv.writer(f, delimiter='\t')
      for sentence, labels in ds_list:
          tw.writerow([sentence,labels])



def main(path):
    dataset = TSV_dataset(path)
    token_train = setting(dataset)

    #token_train = regulation(token_train)
    #TSV_Write(token_train,filename)
    return token_train