## 버전
version 3.11.5(버전 준수)

## 설치 
환경변수 셋팅 후 터미널에서 python 입력 시 아래랑 비슷하게 떠야함.

```shell
Python 3.11.5 (tags/v3.11.5:cce6ba9, Aug 24 2023, 14:38:34) [MSC v.1936 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>>
```

## 실행방법
1. 터미널에서 `pip instapll -r ./requirements.txt`
2. 라이브러리 설치 완료되면
3. `python ./main.py` 실행

## commit / push
초기 셋팅 말고 작업 중에 pip install하여 다른 라이브러리를 설치했을 경우 작업 완료 후 `pip freeze > requirements.txt` 실행하여 라이브러리 목록 추출 후 해당 목록 반영하여 push 부탁.... (requirements 변경될 경우 기존 파일 `_x`로 버전 명시)



## 데이터베이스 query 작성 Guide

### 다량의 데이터를 삽입하는 테이블의 중복 체크

1. SELECT 후 중복 체크하는 과정 없이 INSERT문에서 DB가 자체적으로 중복 방지하는 postgresql 함수 사용
: ON CONFLICT DO NOTHING

    * 단, UNIQUE 제약 조건은 기본적으로 NULL 값을 동일한 값으로 간주
    따라서 Null 값 허용 X or 무조건 값이 들어가는 컬럼에 한에서 적용할 것
    
    해당되는 테이블     track_tb        (album_id, track_name)
                    album_type_tb   (album_id, release_id, type_category)
                    
                    album_release_code  (code)
                    genre_code          (code)
                    

    * 또한, 
    컬럼들의 조합이 pk 가 되는 경우 unique 제약조건 없이 자동 적용
    
    해당되는 테이블     artist_genre_tb (artist_id, genre_id)
                    artist_track_tb (artist_id, track_id)
                    artist_album_tb (artist_id, album_id)


2. SELECT 조회 후 INSERT

    해당되는 테이블     artist_tb       (mbid, artist_name)
                    album_tb        (title, release_date_origin)


API or 관련 트랜젝션이 많을 경우 select 조회 후 Insert
그 외 데이터의 양이 많을 경우, ON CONFLICT DO NOTHING 함수 사용함


# 데이터 적재 실행 방법

```sh
# 1.TOP 아티스트 데이터 적재
python main.py --mode top_artists --limit 50

# 2. 국가별 데이터 적재
python main.py --mode country --country "Korea" --limit 50
## 장르별로 적재
python main.py --mode country --country Korea --genre kpop --limit 50
## limit 없을 경우, 전체 데이터 적재
python main.py --mode country --country Korea --genre kpop

# 3. 아티스트 데이터 적재
## 아티스트명으로 적재
python main.py --mode artist --name "BTS"
## MBID로 적재
python main.py --mode artist --mbid "b6b21b0c-a706-4b46-a929-bd4d21b06cad"

# 4. 특정 아티스트의 앨범/트랙 데이터 적재
python main.py --mode album --mbid "b6b21b0c-a706-4b46-a929-bd4d21b06cad"

# 5. 아티스트명으로 다수 아티스트 데이터 적재
python main.py --mode artist --names "BTS,IU,Red Velvet,New Jeans"

```