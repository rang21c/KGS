# KGS(Knowledge Graph Search)
광운대학교 제 6회 산학연계 SW프로젝트(2021-2022) - 한화시스템

- 팀명 : 외않되
- 프로젝트명 : 인공지능 자연어 처리 기반 지식그래프 검색 기술 개발
- 배포 링크 : [KGS-PROJECT](http://kgs-project.ml/)

## 시스템 구조도
![구조도](https://user-images.githubusercontent.com/33370179/170817504-2615caef-e9ea-4da6-8bf6-06b1ccb4147f.svg)

## 모듈 설명
### Data Source

네이버 뉴스 기사를 실시간으로 크롤링해 MySQL DB에 저장하는 모듈

파이썬 파일은 Ubuntu crontab 위에서 동작, DB 삽입 API 서버는 Nginx 위에서 동작, 프로세스 매니저는 pm2를 이용

---
### Model

NER, RE 모델 모두 KoBERT 를 Finetuning 하여 사용
- 개체명 인식 모델(NER)
  - Input : 문장
  - Output : 개체명 태그가 달린 문장

- 관계 추출 모델(RE)
  - Input : e1, e2 태그가 달린 문장
  - Output : 두 엔티티 사이의 관계

---
### Backend

모델에서 받은 두 엔티티의 메타 정보, 관계를 이용해 Neo4j GraphDB에 지식그래프를 구성, Frontend에 API를 제공 하는 모듈

GraphDB 삽입 API 서버는 Nginx 위에서 동작, 프로세스 매니저는 pm2를 이용

---
### Frontend

Neo4j GraphDB에 있는 정보를 이용해 웹 페이지에 지식그래프를 시각화 하고 검색 할 수 있게 하는 모듈

React.js 를 사용하며, D3.js 를 이용해 지식그래프 시각화

---

## 지식그래프 검색 시스템
![image](https://user-images.githubusercontent.com/33370179/174234908-0ac81186-502c-417b-a1f8-7905e8244cba.png)



## 팀원 소개
### 팀장 류화랑(rang21c) [github](https://github.com/rang21c)
- Model
  - NER Tag 쌍 추출
  - NER Model 후처리(조사 분리)
- Backend
  - Neo4j GraphDB API 설계 및 코딩 
- Frontend
  - React.js 사용 D3.js 시각화

<br/>

### 팀원 강성운(clover7kso) [github](https://github.com/clover7kso)
- Data Source
  - 뉴스 데이터 크롤링
  - 뉴스 데이터 API 설계 및 코딩
- Model
  - NER Model Fine-tuning 및 전처리
- Backend
  - Neo4j GraphDB API 설계 및 코딩 
- Frontend
  - React.js 사용 D3.js 시각화

<br/>

### 팀원 조정우(JEONGWOO-C) [github](https://github.com/JEONGWOO-C)
- Data Source
  - 뉴스 데이터 크롤링
  - 뉴스 데이터 API 설계 및 코딩
- Model
  - NER Model Fine-tuning 및 전처리
  - NER Tag 쌍 추출
  - RE Model Fine-tuning 및 전처리

<br/>

### 팀원 임경택(Izar111) [github](https://github.com/Izar111)
- Model
  - NER Model Fine-tuning 및 전처리
  - NER Tag 쌍 추출
  - NER, RE Model 연동

<br/>

### 팀원 이민석(lllminsuk) [github](https://github.com/lllminsuk)
- Data Source
  - 뉴스 데이터 크롤링
- Model
  - NER Tag 쌍 추출
  - NER Model 후처리(조사 분리)
  - RE Model Fine-tuning 및 전처리


<br/>
