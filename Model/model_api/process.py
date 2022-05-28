import sys
import os
import ast
import time
import re
#import pytz

from python_graphql_client import GraphqlClient
import asyncio # Asynchronous request

sys.path.append(os.path.realpath("../NER_RE"))
from run import main as ner_re



#from ..NER_RE.run import main

# Instantiate the client with an endpoint.
news_api = GraphqlClient("https://kgs-project.ml/news_api")
neo4j = GraphqlClient("https://kgs-project.ml/neo4j")

# Create the query string and variables required for the request.
crawling = '''mutation { 
    readNews {
        id
        content
        title
        main
        url
        uploadTime
        sub
        uniqueId
    }
}'''

graph_query = '''mutation CreateMyNodes($e1Value: String!, $e1Type: String!, $e1Url: String, $e1Main: String, $e1Sub: String, $e1Title: String, $e1UploadTime: String, $e1UniqueId: Int, $e2Value: String!, $e2Type: String!, $e2Url: String, $e2Main: String, $e2Sub: String, $e2Title: String, $e2UploadTime: String, $e2UniqueId: Int, $rel: String!) {
  insertTwoNodes(E1_value: $e1Value, E1_type: $e1Type, E1_url: $e1Url, E1_main: $e1Main, E1_sub: $e1Sub, E1_title: $e1Title, E1_uploadTime: $e1UploadTime, E1_uniqueId: $e1UniqueId, E2_value: $e2Value, E2_type: $e2Type, E2_url: $e2Url, E2_main: $e2Main, E2_sub: $e2Sub, E2_title: $e2Title, E2_uploadTime: $e2UploadTime, E2_uniqueId: $e2UniqueId, REL: $rel)
}'''

def delete_sign(sentence, change=""):
    # delete unicode sign
    result = re.sub(r'[^가-힣A-Za-z0-9\.\{\}\[\]\/?.,\)~`!\-+<>\$%\\\=\(\'\"\s\x20”’ᆞ·㎕-㏆~ＭＫｍ°]|[\_]', change, sentence)
    # except bracket
    result = re.sub(r'[\{\}\[\]\)\(]', change, result)
    # except ' "
    #result = re.sub(r'[\'\"]', change, result)

    return result

def content_to_sentence(content):
    # end sign duple
    content = re.sub(r'\. ', " .. ", content)
    content = re.sub(r'\? ', " ?? ", content)
    content = re.sub(r'! ', " !! ", content)
    # splite
    sentence = re.split(r'[\.\?!][ ]',content)
    return sentence

def PreProcess(content):
    # news content -> sentence 
    sentence = content_to_sentence(delete_sign(content," ").strip())

    return sentence


def main(model_log_hide=True):
    timer_begin = time.time()

    while True:
        data = asyncio.run(news_api.execute_async(query=crawling))
        print(data)

        real_data = data['data']['readNews']

        if real_data is None:
            time.sleep(300)
            continue
        
        if real_data['content'] is None:
            continue
        
        uptime_str = time.strftime("%Y-%m-%dT%H:%M:%S%z",time.localtime(int(real_data['uploadTime'])/1000))
        uptime_str = uptime_str[:uptime_str.find('+')+3]+':'+uptime_str[uptime_str.find('+')+3:]

        sentence = PreProcess(real_data['content'])
        #link = [ real_data['url'] ] * len(sentence)
        _main = [ real_data['main'] ] * len(sentence)
        sub = [ real_data['sub'] ] * len(sentence)
        title = [ real_data['title'] ] * len(sentence)
        url = [ real_data['url'] ] * len(sentence)
        uploadTime = [ uptime_str ] * len(sentence)
        uniqueId = [ real_data['uniqueId'] ] * len(sentence)

        for i in range(0,len(sentence)):
            print("================={}====================".format(i))
            print("sentence : ", sentence[i])
            print("main_category : ", _main[i])
            print("subcategory : ", sub[i])
            print("title : ", title[i])
            print("url : ", url[i])
            print("uploadTime : ", uploadTime[i])
            print("uniqueId : ", uniqueId[i])
            print("=======================================")
        
        print(">>>Start NER-RE===============")

        # model message hide
        if model_log_hide:
            keep_stdout, sys.stdout = sys.stdout, open("model_log.log","w")

        # model running
        model_res = ner_re(sentence, _main=_main, sub=sub, url=url, title=title, uploadTime=uploadTime, uniqueId=uniqueId)

        # stdout revert
        if model_log_hide:
            sys.stdout.close()
            sys.stdout = keep_stdout
            sys.stdout.flush()

        print(">>>End NER-RE=================")

        #print(model_res)
        
        for res in model_res:
            # execpt : no relation
            if res['re'] == 'no_relation':
                continue
            # query variable dict
            result = {
                "e1Value": res['word1'],
                "e1Type": res['ner1'],
                "e1Url": res['url'],
                "e1Main": res['main'],
                "e1Sub": res['sub'],
                "e1Title": res['title'],
                "e1UploadTime": res['uploadTime'],
                "e1UniqueId": res['uniqueId'],
                "e2Value": res['word2'],
                "e2Type": res['ner2'],
                "e2Url": res['url'],
                "e2Main": res['main'],
                "e2Sub": res['sub'],
                "e2Title": res['title'],
                "e2UploadTime": res['uploadTime'],
                "e2UniqueId": res['uniqueId'],
                "rel": res['re']
            }
            print(res)
            
            #neo4j query work
            data = asyncio.run(neo4j.execute_async(query=graph_query,variables=result))
            print(data)
            #check neo4j query error
            if 'error' in data.keys():
                print("neo4j Error Return: ", data['error'])
            else :
                print("neo4j done !")
            
        print(i)
        time.sleep(1)

    timer_end = time.time()

    print("=====================================> running time: {} second(s)".format(timer_end-timer_begin))

if __name__ == '__main__':
    main(model_log_hide=True)