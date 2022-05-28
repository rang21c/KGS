import os
import logging
import argparse
from tqdm import tqdm, trange

import numpy as np
import torch
from torch.utils.data import TensorDataset, DataLoader, SequentialSampler
from transformers import AutoModelForTokenClassification
from tokenization_kobert import KoBertTokenizer

import itertools

from postprocessor import PostProcess_Mecab

logger = logging.getLogger(__name__)

NER_path = "./model/NER"
NER_data = "./model/NER/data"
NER_preds = "./model/NER/preds"


def get_labels():
    return ['UNK', 'O', 'PS-B', 'PS-I', 'LC-B', 'LC-I', 'OG-B', 'OG-I', 'DT-B', 'DT-I', 'TI-B', 'TI-I', 'QT-B', 'QT-I']

def init_logger():
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        level=logging.INFO)


def get_device(no_cuda=False):
    device_str = "cuda"
    if not torch.cuda.is_available() or no_cuda:
        device_str = "cpu"
    return torch.device(device_str)


def load_model(model_dir, device):
    # Check whether model exists
    if not os.path.exists(model_dir):
        raise Exception("Model doesn't exists! Train first!")

    try:
        model = AutoModelForTokenClassification.from_pretrained(model_dir)
        model.to(device)
        model.eval()
        logger.info("***** Model Loaded *****")
    except:
        raise Exception("Some model files might be missing...")

    return model

def read_input_file(input_file):
    lines = []
    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            #line = delete_sign(line)
            words = line.split()
            lines.append(words)

    return lines

def convert_input(input_lines):
    lines = []
    for line in input_lines:
        line = line.strip()
        words = line.split()
        lines.append(words)

    return lines



def convert_input_file_to_tensor_dataset(lines,
                                         max_seq_len,
                                         tokenizer,
                                         pad_token_label_id,
                                         cls_token_segment_id=0,
                                         pad_token_segment_id=0,
                                         sequence_a_segment_id=0,
                                         mask_padding_with_zero=True):
    # Setting based on the current model type
    cls_token = tokenizer.cls_token
    sep_token = tokenizer.sep_token
    unk_token = tokenizer.unk_token
    pad_token_id = tokenizer.pad_token_id

    all_input_ids = []
    all_attention_mask = []
    all_token_type_ids = []
    all_slot_label_mask = []

    for words in lines:
        tokens = []
        slot_label_mask = []
        for word in words:
            word_tokens = tokenizer.tokenize(word)
            if not word_tokens:
                word_tokens = [unk_token]  # For handling the bad-encoded word
            tokens.extend(word_tokens)
            # Use the real label id for the first token of the word, and padding ids for the remaining tokens
            slot_label_mask.extend([0] + [pad_token_label_id] * (len(word_tokens) - 1))

        # Account for [CLS] and [SEP]
        special_tokens_count = 2
        if len(tokens) > max_seq_len - special_tokens_count:
            tokens = tokens[: (max_seq_len - special_tokens_count)]
            slot_label_mask = slot_label_mask[:(max_seq_len - special_tokens_count)]

        # Add [SEP] token
        tokens += [sep_token]
        token_type_ids = [sequence_a_segment_id] * len(tokens)
        slot_label_mask += [pad_token_label_id]

        # Add [CLS] token
        tokens = [cls_token] + tokens
        token_type_ids = [cls_token_segment_id] + token_type_ids
        slot_label_mask = [pad_token_label_id] + slot_label_mask

        input_ids = tokenizer.convert_tokens_to_ids(tokens)

        # The mask has 1 for real tokens and 0 for padding tokens. Only real tokens are attended to.
        attention_mask = [1 if mask_padding_with_zero else 0] * len(input_ids)

        # Zero-pad up to the sequence length.
        padding_length = max_seq_len - len(input_ids)
        input_ids = input_ids + ([pad_token_id] * padding_length)
        attention_mask = attention_mask + ([0 if mask_padding_with_zero else 1] * padding_length)
        token_type_ids = token_type_ids + ([pad_token_segment_id] * padding_length)
        slot_label_mask = slot_label_mask + ([pad_token_label_id] * padding_length)

        all_input_ids.append(input_ids)
        all_attention_mask.append(attention_mask)
        all_token_type_ids.append(token_type_ids)
        all_slot_label_mask.append(slot_label_mask)

    # Change to Tensor
    all_input_ids = torch.tensor(all_input_ids, dtype=torch.long)
    all_attention_mask = torch.tensor(all_attention_mask, dtype=torch.long)
    all_token_type_ids = torch.tensor(all_token_type_ids, dtype=torch.long)
    all_slot_label_mask = torch.tensor(all_slot_label_mask, dtype=torch.long)

    dataset = TensorDataset(all_input_ids, all_attention_mask, all_token_type_ids, all_slot_label_mask)

    return dataset

def predict(model=None, model_dir=None, lines=None, input_file_dir=None, output_file_dir=None, no_cuda=False, batch_size=64, model_type="bert", max_seq_len=100, links=None):
    # set default values
    if lines is None:
        if type(input_file_dir) is str:
            lines = read_input_file(input_file_dir)
        else:
            logger.info("No Input!")
            return [], []
    else:
        lines = convert_input(lines)
    if links is None:
        links = [i for i in range(0,len(lines))]
        print(links)
    # load model
    device = get_device(no_cuda)
    if model is None:
        if model_dir is not None:
            model = load_model(model_dir, device)
        else:
            logger.info("No Model!")
            return [], []

    # load label
    label_lst = get_labels()

    # Convert input file to TensorDataset
    pad_token_label_id = torch.nn.CrossEntropyLoss().ignore_index
    tokenizer = KoBertTokenizer.from_pretrained("monologg/kobert")
    dataset = convert_input_file_to_tensor_dataset(lines, max_seq_len, tokenizer, pad_token_label_id)

    # Predict
    sampler = SequentialSampler(dataset)
    data_loader = DataLoader(dataset, sampler=sampler, batch_size=batch_size)

    all_slot_label_mask = None
    preds = None

    for batch in tqdm(data_loader, desc="Predicting"):
        batch = tuple(t.to(device) for t in batch)
        with torch.no_grad():
            # 
            inputs = {"input_ids": batch[0],
                      "attention_mask": batch[1],
                      "labels": None}
            inputs["token_type_ids"] = batch[2]
            outputs = model(**inputs)
            logits = outputs[0]

            preds = logits.detach().cpu().numpy()
            all_slot_label_mask = batch[3].detach().cpu().numpy()

    preds = np.argmax(preds, axis=2)
    slot_label_map = {i: label for i, label in enumerate(label_lst)}
    print("slot_label_map",slot_label_map)
    preds_list = [[] for length in range(preds.shape[0])]

    for i in range(preds.shape[0]):
        for j in range(preds.shape[1]):
            if all_slot_label_mask[i, j] != pad_token_label_id:
                preds_list[i].append(slot_label_map[preds[i][j]])
    
    # Write to output file NER Result
    if output_file_dir is not None:
        with open(output_file_dir, "w", encoding="utf-8") as f:
            for words, preds in zip(lines, preds_list):
                line = ""
                for word, pred in zip(words, preds):
                    if pred == 'O':
                        line = line + word + " "
                    else:
                        line = line + "[{}:<{}>] ".format(word, pred)
                #line = PostProcess_Mecab(line.strip(),open_tag=('[',':'),close_tag=('<','>]'))
                f.write("{}\n".format(line.strip()))
    
    # Attach Entity Tag
    present = []
    entity_sentence = []

    for words, preds, link in zip(lines, preds_list, links):

        word_list = []
        entity_check = []
        ner_preds = []

        token = ""
        entity = ""
        count = 0

        # entity check
        for word, pred in zip(words, preds):

            # check : Is different label?
            if entity[:2] != pred[:2] or pred[-1] != 'I':
                word_list.append(token)
                ner_preds.append(entity)
                # previous word is not entity
                if entity == 'O':
                    entity_check.append(0)
                # check : previous word is none
                elif entity != "":
                    count = count + 1
                    entity_check.append(count)
                # update
                token = word
                entity = pred
            # same label => same entity
            else:
                # attach word
                token = token + " " + word

        # last word append
        word_list.append(token)
        ner_preds.append(entity)

        # check is entity
        if entity == 'O':
            entity_check.append(0)
        else:
            count = count + 1   # entity number
            entity_check.append(count)
        # del first blank word data
        word_list = word_list[1:]
        ner_preds = ner_preds[1:]

        print(word_list,ner_preds)
        print(entity_check)

        # make entity pair
        arr = range(1, count+1)
        pair = list(itertools.permutations(arr, 2))

        # make string
        for e1, e2 in pair:
            entity_line = ""
            e1_object = ''
            e2_object = ''

            # make string
            for word, pred, check in zip(word_list, ner_preds, entity_check):
                #entity tag attach
                if check == e1:
                    entity_line = entity_line + " " + "<e1>" + word + "</e1>"
                    e1_object = pred
                elif check == e2:
                    entity_line = entity_line + " " + "<e2>" + word + "</e2>"
                    e2_object = pred
                else:
                    entity_line = entity_line + " " + word
            present.append((e1_object, e2_object, link))
            entity_sentence.append(entity_line)

    logger.info("Prediction Done!")

    return entity_sentence, present

"""
def predict_origin(model,pred_config):
    # load model and args
    args = get_args(pred_config)
    #print(args)
    device = get_device(pred_config)
    label_lst = get_labels(pred_config)
    logger.info(args)

    # Convert input file to TensorDataset
    pad_token_label_id = torch.nn.CrossEntropyLoss().ignore_index
    tokenizer = load_tokenizer(args)
    lines = read_input_file(pred_config)
    dataset = convert_input_file_to_tensor_dataset(lines, pred_config, args, tokenizer, pad_token_label_id)

    # Predict
    sampler = SequentialSampler(dataset)
    data_loader = DataLoader(dataset, sampler=sampler, batch_size=pred_config.batch_size)

    all_slot_label_mask = None
    preds = None

    for batch in tqdm(data_loader, desc="Predicting"):
        batch = tuple(t.to(device) for t in batch)
        with torch.no_grad():
            inputs = {"input_ids": batch[0],
                      "attention_mask": batch[1],
                      "labels": None}
            if args.model_type != "distilkobert":
                inputs["token_type_ids"] = batch[2]
            outputs = model(**inputs)
            logits = outputs[0]

            if preds is None:
                preds = logits.detach().cpu().numpy()
                all_slot_label_mask = batch[3].detach().cpu().numpy()
            else:
                preds = np.append(preds, logits.detach().cpu().numpy(), axis=0)
                all_slot_label_mask = np.append(all_slot_label_mask, batch[3].detach().cpu().numpy(), axis=0)

    preds = np.argmax(preds, axis=2)
    slot_label_map = {i: label for i, label in enumerate(label_lst)}
    preds_list = [[] for _ in range(preds.shape[0])]

    # print(range(preds.shape[0]),range(preds.shape[1]))
    # print(preds)
    # print(slot_label_map)
    for i in range(preds.shape[0]):
        for j in range(preds.shape[1]):
            if all_slot_label_mask[i, j] != pad_token_label_id:
                preds_list[i].append(slot_label_map[preds[i][j]])

    # Write to output file
    with open(pred_config.output_file, "w", encoding="utf-8") as f:
        for words, preds in zip(lines, preds_list):
            line = ""
            for word, pred in zip(words, preds):
                #print(pred)
                if pred == 'O':
                    line = line + word + " "
                else:
                    line = line + "[{}:{}] ".format(word, pred)

            f.write("{}\n".format(line.strip()))
#     logger.info("Prediction Done!")
"""