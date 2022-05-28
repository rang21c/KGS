import torch
import gluonnlp as nlp
import numpy as np
from BERT_dataset import BERTDataset

def predict(model, tokenizer, vocab, predict_sentence):
    tok = nlp.data.BERTSPTokenizer(tokenizer, vocab, lower=False)
    data = [predict_sentence, '0']
    dataset_another = [data]

    device = torch.device("cuda:0")

    #parameter
    max_len = 64 # 해당 길이를 초과하는 문장은 학습X
    batch_size = 64

    another_test = BERTDataset(dataset_another, 0, 1, tok, max_len, True, False)
    test_dataloader = torch.utils.data.DataLoader(another_test, batch_size=batch_size, num_workers=5)

    model.eval()
    for batch_id, (token_ids, valid_length, segment_ids, label) in enumerate(test_dataloader):
        token_ids = token_ids.long().to(device)
        segment_ids = segment_ids.long().to(device)

        valid_length = valid_length
        label = label.long().to(device)

        out = model(token_ids, valid_length, segment_ids)

        test_eval = []
        for i in out:
            logits = i
            logits = logits.detach().cpu().numpy()

            if np.argmax(logits) == 0:
                test_eval.append("no_relation")
            elif np.argmax(logits) == 1:
                test_eval.append("org:alternate_names")
            elif np.argmax(logits) == 2:
                test_eval.append("org:dissolved")
            elif np.argmax(logits) == 3:
                test_eval.append("org:founded")
            elif np.argmax(logits) == 4:
                test_eval.append("org:founded_by")
            elif np.argmax(logits) == 5:
                test_eval.append("org:member_of")
            elif np.argmax(logits) == 6:
                test_eval.append("org:members")
            elif np.argmax(logits) == 7:
                test_eval.append("org:number_of_employees/members")
            elif np.argmax(logits) == 8:
                test_eval.append("org:place_of_headquarters")
            elif np.argmax(logits) == 9:
                test_eval.append("org:political/religious_affiliation")
            elif np.argmax(logits) == 10:
                test_eval.append("org:product")
            elif np.argmax(logits) == 11:
                test_eval.append("org:top_members/employees")
            elif np.argmax(logits) == 12:
                test_eval.append("per:alternate_names")
            elif np.argmax(logits) == 13:
                test_eval.append("per:children")
            elif np.argmax(logits) == 14:
                test_eval.append("per:colleagues")
            elif np.argmax(logits) == 15:
                test_eval.append("per:date_of_birth")
            elif np.argmax(logits) == 16:
                test_eval.append("per:date_of_death")
            elif np.argmax(logits) == 17:
                test_eval.append("per:employee_of")
            elif np.argmax(logits) == 18:
                test_eval.append("per:origin")
            elif np.argmax(logits) == 19:
                test_eval.append("per:other_family")
            elif np.argmax(logits) == 20:
                test_eval.append("per:parents")
            elif np.argmax(logits) == 21:
                test_eval.append("per:place_of_birth")
            elif np.argmax(logits) == 22:
                test_eval.append("per:place_of_death")
            elif np.argmax(logits) == 23:
                test_eval.append("per:place_of_residence")
            elif np.argmax(logits) == 24:
                test_eval.append("per:product")
            elif np.argmax(logits) == 25:
                test_eval.append("per:religion")
            elif np.argmax(logits) == 26:
                test_eval.append("per:schools_attended")
            elif np.argmax(logits) == 27:
                test_eval.append("per:siblings")
            elif np.argmax(logits) == 28:
                test_eval.append("per:spouse")
            elif np.argmax(logits) == 29:
                test_eval.append("per:title")

        print(">> 관계 " + test_eval[0])
        return test_eval[0]