import torch
import gluonnlp as nlp
import numpy as np
from torch.utils.data import Dataset, DataLoader

class BERTDataset(Dataset):
    def __init__(self, dataset, sentence_idx, label_idx, bert_tokenizer, max_len, pad, pair):
        transform = nlp.data.BERTSentenceTransform(
            bert_tokenizer, max_seq_length=max_len, pad=pad, pair=pair)

        self.sentence = [transform([i[sentence_idx]]) for i in dataset]
        self.label = [np.int32(i[label_idx]) for i in dataset]

    def __getitem__(self, i):
        return (self.sentence[i] + (self.label[i],))

    def __len__(self):
        return (len(self.label))