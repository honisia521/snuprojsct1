import streamlit as st
import pandas as pd
from elasticsearch import Elasticsearch
import time

# Elasticsearch 클라이언트 설정
# Streamlit Cloud에서 배포 시, .streamlit/secrets.toml 파일에 설정 필요
try:
    es_host = st.secrets["ELASTICSEARCH_HOST"]
    es_user = st.secrets["ELASTICSEARCH_USER"]
    es_password = st.secrets["ELASTICSEARCH_PASSWORD"]
    client = Elasticsearch(
        es_host,
        basic_auth=(es_user, es_password)
    )
except (KeyError, FileNotFoundError):
    st.info("로컬에서 실행합니다. Elasticsearch 연결 정보를 .streamlit/secrets.toml에 설정해 주세요.")
    client = Elasticsearch("http://localhost:9200")

# 연결 확인
if not client.ping():
    st.error("Elasticsearch에 연결할 수 없습니다. 서버가 실행 중인지 확인해 주세요.")
    st.stop()

# --- 1. 앱 구성 ---
st.set_page_config(layout="wide", page_title="Elasticsearch 기반 게임 추천")

st.title("🔍 Elasticsearch 기반 게임 추천기")
st.markdown("""
<style>
    .game-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
        background-color: #f9f9f9;
    }
    .game-title {
        color: #FF4B4B;
        font-size: 1.2em;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)
st.write("원하는 키워드를 입력하여 게임을 추천받으세요!")

# --- 2. 검색 기능 ---
search_query = st.text_input("게임 이름, 장르, 설명 등으로 검색해보세요 (예: RPG, 오픈월드, 스토리)", key="search_bar")

if st.button("검색하기", key="search_button"):
    if search_query:
        with st.spinner("Elasticsearch에서 게임을 검색 중입니다..."):
            try:
                # Elasticsearch 검색 쿼리
                query_body = {
                    "query": {
                        "multi_match": {
                            "query": search_query,
                            "fields": ["게임 이름^2", "장르^1.5", "설명", "태그"], # 가중치 설정
                            "fuzziness": "AUTO", # 오타 허용
                            "operator": "or"
                        }
                    }
                }
                
                # Elasticsearch 검색 API 호출
                res = client.search(index="games", body=query_body, size=6)
                
                # 검색 결과 처리
                hits = res['hits']['hits']
                if hits:
                    st.subheader("💡 검색 결과")
                    display_cols = st.columns(2)
                    for i, hit in enumerate(hits):
                        game_info = hit['_source']
                        with display_cols[i % 2]:
                            st.markdown(f'<div class="game-card">', unsafe_allow_html=True)
                            st.markdown(f'<h3 class="game-title">{game_info["게임 이름"]}</h3>', unsafe_allow_html=True)
                            st.write(f"**장르:** {game_info['장르']}")
                            st.write(f"**난이도:** {game_info['난이도']}")
                            st.write(f"**플레이어 수:** {game_info['플레이어 수']}")
                            st.write(f"**평점:** {game_info['평점']} / 5.0")
                            st.markdown(f"**설명:** {game_info['설명']}")
                            st.markdown(f'</div>', unsafe_allow_html=True)
                else:
                    st.info("검색 결과가 없습니다. 다른 키워드로 검색해 보세요.")
            except Exception as e:
                st.error(f"검색 중 오류가 발생했습니다: {e}")
    else:
        st.warning("검색어를 입력해 주세요!")
