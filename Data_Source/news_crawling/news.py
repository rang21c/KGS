# -*- coding: utf-8 -*-
from cgitb import text
from email import header
from enum import unique
from pickle import NONE
from urllib.request import Request, urlopen
import requests
import re
import pandas as pd
from bs4 import BeautifulSoup
import time
import kss
from datetime import datetime, timedelta
from python_graphql_client import GraphqlClient

client = GraphqlClient(endpoint="http://localhost:5000")

# Init 단발성 이벤트 필요할때만
# 대분류 URL
# 대분류 URL > 소분류 URL
# 대분류 URL > 소분류 URL > 뉴스기사 URL
# 대분류 URL > 소분류 URL > 뉴스기사 URL > 각 뉴스정보
BASE_URL = "https://news.naver.com"
IS_INIT = False
MAIN_CATEGORY = ["정치", "경제", "사회", "생활/문화", "IT/과학"]
SUB_CATEGORY = ["청와대", "국회/정당", "북한", "행정", "국방/외교", "정치일반", "금융", "증권", "산업/재계",
                "중기/벤처", "부동산", "글로벌 경제", "생활경제", "경제 일반", "사건사고", "교육", "노동",
                "언론", "환경", "인권/복지", "식품/의류", "지역", "인물", "사회 일반", "건강정보", "자동차/시승기", 
                "도로/교통", "여행/레저", "음식/막집", "패션/뷰티", "공연/전시", "책", "종교", "생활문화 일반", 
                "모바일", "인터넷/SNS", "통신/뉴미디어", "IT 일반", "보안/해킹", "컴퓨터", "게임/리뷰", "과학 일반"]
NEWS_COMPANY = ["연합뉴스", "매일경제", "조선일보", "MBC", "스포츠조선",
                "머니투데이", "SBS", "한겨레", "KBS", "동아일보", "파이낸셜뉴스", "중앙일보", "YTN", "JTBC", "아시아경제", "헤럴드경제", "이데일리"]
NEWS_URL = []
NEWS = []

checkNews = """
    query Query ($uniqueId: String!){
        checkNews(uniqueId: $uniqueId)
    }
"""

deleteAll = """
    mutation Mutation {
        deleteAll
    }
"""

insertNews = """
    mutation Mutation($uniqueId: String!, $url: String!, $urlOrigin: String!, $title: String!, $content: String!, $uploadTime: String!, $main: String!, $sub: String!) {
        insertNews(uniqueId: $uniqueId, url: $url, urlOrigin: $urlOrigin, title: $title, content: $content, uploadTime: $uploadTime, main: $main, sub: $sub)
    }
"""

# 과정 함수 1
# 메인카테고리의 URL을 불러오는 부분
def getMainCategoryUrl():
    RESULT = []  # Return할 함수 결과

    # 기본 Html Request
    reqUrl = Request(BASE_URL, headers={"User-Agent": "Mozilla/5.0"})
    html = urlopen(reqUrl)
    soup = BeautifulSoup(html, "html.parser")

    # 필요한 데이터 영역 필터
    soup = soup.find("ul", class_="Nlnb_menu_list")
    soup = soup.findAll("a")

    # 데이터 추출
    for i in soup:
        url = i["href"] if i["href"] != None else None

        if i.text.strip() in MAIN_CATEGORY:
            RESULT.append([i.text.strip(), url])  # 결과추가

    return RESULT

# 과정 함수 2
# 서브카테고리의 URL을 불러오는 부분
def getSubCategoryUrl(mainCategoryURL):
    RESULT = []  # Return할 함수 결과

    for main in mainCategoryURL:

        # 기본 Html Request
        reqUrl = Request(main[1],
                         headers={"User-Agent": "Mozilla/5.0"})
        html = urlopen(reqUrl)
        soup = BeautifulSoup(html, "html.parser")

        # 필요한 데이터 영역 필터
        soup = soup.find("ul", class_="nav")
        soup = soup.find_all("a")

        # 데이터 추출
        for i in soup:
            url = i["href"] if i["href"] != None else None

            if i.text.strip() in SUB_CATEGORY:
                # print([main[0], i.text.strip(), BASE_URL+url])
                RESULT.append([main[0], i.text.strip(), BASE_URL+url])  # 결과추가
    return RESULT

def getNewsUrl(subCategoryURL):
    for sub in subCategoryURL:
        isInserted = False
        for page_num in range(1, 15):
            # 기본 Html Request
            reqUrl = Request(sub[2]+'&page='+str(page_num),
                                headers={"User-Agent": "Mozilla/5.0"})
            html = urlopen(reqUrl)
            soup = BeautifulSoup(html, "html.parser")

            # 필요한 데이터 영역 필터
            newsData = soup.select('.type06_headline li dl')
            for news in newsData:
                # 각 뉴스 URL 필터
                newsUrl = news.a.get('href')
                # 각 뉴스별 ID 필터
                uniqueId = newsUrl[newsUrl.rfind('/') + 1: newsUrl.rfind("?sid")]
                variables = { "uniqueId": uniqueId }

                # 중복 뉴스 확인
                checkResponse = client.execute(query=checkNews, variables = variables)
                print(checkResponse)
                if checkResponse['data']['checkNews'] == True:
                    isInserted = True
                    break
                
                # 뉴스 신문사 필터
                if news.find("span", class_="writing").text.strip() in NEWS_COMPANY:
                    newsContent = getNewsContent(newsUrl, sub[0], sub[1])
                    insertResponse = client.execute(
                        query=insertNews, variables=newsContent)
                    print(insertResponse)
                    print("--------")
            if isInserted == True:
                break

            newsData = soup.select('.type06 li dl')
            for news in newsData:
                 # 각 뉴스 URL 필터
                newsUrl = news.a.get('href')
                # 각 뉴스별 ID 필터
                uniqueId = newsUrl[newsUrl.rfind('/') + 1: newsUrl.rfind("?sid")]
                variables = { "uniqueId": uniqueId }

                # 중복 뉴스 확인
                checkResponse = client.execute(query=checkNews, variables = variables)
                print(checkResponse)
                if checkResponse['data']['checkNews'] == True:
                    break
                
                # 뉴스 신문사 필터
                if news.find("span", class_="writing").text.strip() in NEWS_COMPANY:
                    newsContent = getNewsContent(newsUrl, sub[0], sub[1])
                    insertResponse = client.execute(
                        query=insertNews, variables=newsContent)
                    print(insertResponse)
                    print("--------")
            if isInserted == True:
                break
                
    return

def contentPreprocess(data):
    # 뉴스 요약 삭제하기
    data = re.sub('<strong.*?>.*?</strong>', '', str(data))
    # HTML tag 삭제하기
    data = re.sub('(<([^>]+)>)', '', str(data))
    # 개행문자, 탭, 백슬래시 제거하기
    data = data.replace("\n", "").replace("\t", "").replace('\\', '')

    split_result=[]
    for sent in kss.split_sentences(data):
        split_result.append(sent)
    result=''

    for i in split_result:
        if clean_text(i):
            result = result + ' ' + i

    return result.strip()

def clean_text(text):
    if re.search('([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', text):     # 이메일 지우기
        return False
    if re.search('(http|ftp|https)://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', text):    # URL 제거
        return False
    if re.search('[0-9-]+\.[0-9-]+\.[0-9-.]+', text):    # 날짜 지우기
        return False
    if re.search('\(.+=.+\)', text):  # (@@=@@) 지우기 ex) (서울=연합뉴스)
        return False
    if re.search('\[.+\]', text):  # [@@@@] 지우기 ex) [파이낸셜뉴스]
        return False
    if re.search('=|Δ|&lt;|&gt;|ⓒ|☎|▲|▶|△|▷', text):   # 특수문자 지우기
        return False
    return text[0]!='/' # 첫 문장이 /로 시작하는 문장 지우기

def getNewsContent(newsURL, main, sub):
    uniqueId = ""
    uploadTime = ""
    urlOrigin = ""
    title = ""
    content = ""

    uniqueId = newsURL[newsURL.rfind('/') + 1: newsURL.rfind("?sid")]
    # 필요한 데이터 영역 필터
    # 기본 Html Request
    reqUrl = Request(newsURL,
                     headers={"User-Agent": "Mozilla/5.0"})
    html = urlopen(reqUrl)
    soup = BeautifulSoup(html, "html.parser")
    print(newsURL)

    if soup.find("h2", class_="end_tit") != None :
        title = soup.find("h2", class_="end_tit").text.strip()
        
        Time = soup.find("span", class_="author").find('em').text.strip()
        if Time.find('오전') == -1:
            Time = Time.replace(u'오후', "") + ' pm'
        else:
            Time = Time.replace(u'오전', "") + ' am'
        uploadTime = datetime.strptime(Time, '%Y.%m.%d.  %I:%M %p')
        uploadTime = uploadTime.strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            urlOrigin = soup.find("a", class_="btn_news_origin")
            urlOrigin = urlOrigin["href"] if urlOrigin["href"] != None else None
        except:
            urlOrigin = ""

        content = soup.find("div", id="articeBody")
        #ex : https://entertain.naver.com/read?oid=469&aid=0000673736

    elif soup.find("div", class_="media_end_head_title").find("h2", class_="media_end_head_headline") != None :
        title = soup.find("h2", class_="media_end_head_headline").text.strip()
        
        uploadTime = soup.find("span", class_="media_end_head_info_datestamp_time")[
            'data-date-time']
            
        try:
            urlOrigin = soup.find("a", class_="media_end_head_origin_link")
            urlOrigin = urlOrigin["href"] if urlOrigin["href"] != None else None
        except:
            urlOrigin = ""

        content = soup.find("div", id="dic_area")
        #ex : https://n.news.naver.com/mnews/article/658/0000008985?sid=102

    elif soup.find("h4", class_="title") != None:
        title = soup.find("h4", class_="title").text.strip()

        Time = soup.find("div", class_="info").find('span').text.strip().strip("기사입력 ")
        if Time.find('오전') == -1:
            Time = Time.replace(u'오후', "") + ' pm'
        else:
            Time = Time.replace(u'오전', "") + ' am'
        uploadTime = datetime.strptime(Time, '%Y.%m.%d.  %I:%M %p')
        uploadTime = uploadTime.strftime('%Y-%m-%d %H:%M:%S')

        try:
            urlOrigin = soup.find("a", class_="press_link")
            urlOrigin = urlOrigin["href"] if urlOrigin["href"] != None else None
        except:
            urlOrigin = ""
        
        content = soup.find("div", id="newsEndContents")
        #ex : https://sports.naver.com/news?oid=001&aid=0013191035


    if content != type(None):
        #뉴스 본문 전처리
        content = contentPreprocess(content)
    print("uniqueId : " + uniqueId+"\nurl : " + newsURL+"\nurlOrigin : " + urlOrigin+"\ntitle : "+title+"\ncontent : " + content[0:10]+"\nuploadtime : "+uploadTime+"\nmain : "+main+"\nsub : "+sub+"\n")
    return {
        "uniqueId": uniqueId,
        "url": newsURL,
        "urlOrigin": urlOrigin,
        "title": title,
        "content": content,
        "uploadTime": uploadTime,
        "main": main,
        "sub": sub}

def initAll(subCategoryURL):
    deleteResponse = client.execute(query=deleteAll)
    print(deleteResponse)
    for category in subCategoryURL:
        # 기본 Html Request
        reqUrl = Request(category[2],
                         headers={"User-Agent": "Mozilla/5.0"})
        html = urlopen(reqUrl)
        soup = BeautifulSoup(html, "html.parser")

        # 필요한 데이터 영역 필터
        soup = soup.find("ul", class_="type06_headline")
        soup = soup.find("a")
        newsUrl = soup["href"] if soup["href"] != None else None
        newsContent = getNewsContent(newsUrl, category[0], category[1])
        insertResponse = client.execute(
            query=insertNews, variables=newsContent)
        print(insertResponse)
        print("--------")

    return True
    # 단계1 : DB의 모든데이터를 지움
    # 단계2 : 각 SUB_CATEGORY 별 NEWS 한개씩만 추가

if __name__ == "__main__":
    # mainCategoryURL [0]:MAIN CATEGORY, [1]:MAIN_URL
    mainCategoryURL = getMainCategoryUrl()

    # subCategoryURL [0]:MAIN CATEGORY [1]:SUB CATEGORY, [2]:SUB_URL
    subCategoryURL = getSubCategoryUrl(mainCategoryURL)
    print(subCategoryURL)

    # Flush Buffer
    if(IS_INIT):
        initAll(subCategoryURL)

    getNewsUrl(subCategoryURL)