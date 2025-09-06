import streamlit as st
import pandas as pd
from elasticsearch import Elasticsearch
import time

# --- 1. Elasticsearch 연결 ---
# Streamlit Cloud 배포 시 secrets.toml에서 정보를 가져오고,
# 로컬 실행 시 localhost로 연결을 시도합니다.
try:
    if st.secrets["ELASTICSEARCH_HOST"]:
        client = Elasticsearch(
            st.secrets["ELASTICSEARCH_HOST"],
            basic_auth=(st.secrets["ELASTICSEARCH_USER"], st.secrets["ELASTICSEARCH_PASSWORD"])
        )
        is_local = False
    else:
        # secrets.toml에 키는 있지만 값이 비어있을 경우
        client = Elasticsearch("http://localhost:9200")
        is_local = True
except (KeyError, FileNotFoundError):
    # secrets.toml 파일 자체가 없을 경우
    client = Elasticsearch("http://localhost:9200")
    is_local = True

# 연결 상태 확인
if not client.ping():
    st.error("Elasticsearch에 연결할 수 없습니다. 서버가 실행 중인지 확인해 주세요.")
    if is_local:
        st.warning("로컬에서 실행하려면 Elasticsearch를 먼저 실행해야 합니다.")
    st.stop()

# --- 2. 앱 구성 ---
st.set_page_config(layout="wide", page_title="Elasticsearch 기반 게임 추천")
st.title("🔍 Elasticsearch 기반 게임 추천기")
st.write("원하는 키워드를 입력하여 게임을 추천받으세요!")

# --- 3. 검색 기능 ---
search_query = st.text_input("게임 이름, 장르, 설명 등으로 검색해보세요", key="search_bar")

if st.button("검색하기", key="search_button"):
    if search_query:
        with st.spinner("Elasticsearch에서 게임을 검색 중입니다..."):
            try:
                # Elasticsearch 검색 쿼리 (multi_match를 사용해 여러 필드에서 검색)
                query_body = {
                    "query": {
                        "multi_match": {
                            "query": search_query,
                            "fields": ["게임 이름^2", "장르^1.5", "설명", "태그"],
                            "fuzziness": "AUTO",
                            "operator": "or"
                        }
                    }
                }
                
                res = client.search(index="games", body=query_body, size=6)
                
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
