# 履歴検索
import streamlit as st
import os
from dotenv import load_dotenv
import openai
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.cosmos import CosmosClient


# --- UIレイアウト ---
st.set_page_config(page_title="クエリチャットDB Azure(Qnect)(キュネクト)", page_icon="🔗", layout="wide")
st.title("🔎 履歴検索")
st.caption("チャットの履歴から、キーワードと意味（ベクトル）の両方で類似したやり取りを検索します。")

# --- 初期設定とクライアントの準備 ---
load_dotenv()

# Streamlitのキャッシュ機能を使って、リソースを効率的に管理
@st.cache_resource
def get_openai_client():
    return openai.AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )

@st.cache_resource
def get_search_client():
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    key = os.getenv("AZURE_SEARCH_KEY")
    index_name = os.getenv("AZURE_SEARCH_INDEX_NAME", "chat-history-index")
    if endpoint and key:
        return SearchClient(endpoint=endpoint, index_name=index_name, credential=AzureKeyCredential(key))
    return None

@st.cache_resource
def get_cosmos_container():
    endpoint = os.getenv("AZURE_COSMOS_ENDPOINT")
    key = os.getenv("AZURE_COSMOS_KEY")
    db_name = os.getenv("AZURE_COSMOS_DATABASE")
    container_name = os.getenv("AZURE_COSMOS_CONTAINER")
    if not all([endpoint, key, db_name, container_name]):
        return None
    try:
        client = CosmosClient(endpoint, key)
        db = client.get_database_client(db_name)
        container = db.get_container_client(container_name)
        return container
    except Exception:
        return None

# --- ヘルパー関数 ---
def generate_openai_embedding(text, client):
    if not text: return None
    try:
        response = client.embeddings.create(input=text, model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"))
        return response.data[0].embedding
    except Exception as e:
        st.error(f"Embedding生成エラー: {e}")
        return None

def search_ai_search(query_text, search_client, openai_client, top_n=3): #Azure AI Search (ハイブリッド検索)の結果件数n=XのときX件。3件表示。
    if not search_client or not query_text: return []
    try:
        embedding = generate_openai_embedding(query_text, openai_client)
        vector_queries = [VectorizedQuery(vector=embedding, k_nearest_neighbors=top_n, fields="summary_vector")] if embedding else None
        results = search_client.search(
            search_text=query_text,
            vector_queries=vector_queries,
            select=["id", "question", "summary", "timestamp"],
            top=top_n
        )
        return [result for result in results]
    except Exception as e:
        st.error(f"AI Search 検索エラー: {e}")
        return []

def search_cosmos_db(query_text, container):
    if not container or not query_text: return []
    try:
        query = "SELECT * FROM c WHERE CONTAINS(LOWER(c.question), @query) OR CONTAINS(LOWER(c.summary), @query) OR CONTAINS(LOWER(c.summary_chat), @query)"
        params = [{"name": "@query", "value": query_text.lower()}]
        items = list(container.query_items(query=query, parameters=params, enable_cross_partition_query=True))
        return items
    except Exception as e:
        st.error(f"Cosmos DB検索エラー: {e}")
        return []

# クライアントの取得
openai_client = get_openai_client()
search_client = get_search_client()
cosmos_container = get_cosmos_container()

if not all([openai_client, search_client, cosmos_container]):
    st.warning("必要な設定（Azure OpenAI, AI Search, Cosmos DB）が環境変数に正しく設定されているか確認してください。")
else:
    search_query = st.text_input("検索キーワードを入力してください:", placeholder="例：従業員の売上について")
    if st.button("検索実行", type="primary"):
        if search_query:
            with st.spinner("履歴を検索中..."):
                st.markdown("### Azure AI Search (ハイブリッド検索) の結果")
                ai_search_results = search_ai_search(search_query, search_client, openai_client)
                if ai_search_results:
                    for result in ai_search_results:
                        with st.container(border=True):
                            st.markdown(f"**質問:** {result.get('question', 'N/A')}")
                            st.markdown(f"**要約:** {result.get('summary', 'N/A')}")
                            score = result.get('@search.score')
                            st.caption(f"関連スコア: {score:.4f} | タイムスタンプ: {result.get('timestamp')}" if score else f"タイムスタンプ: {result.get('timestamp')}")
                else:
                    st.info("Azure AI Search で一致する履歴は見つかりませんでした。")

                st.divider()

                st.markdown("### Cosmos DB (キーワード検索) の結果")
                cosmos_results = search_cosmos_db(search_query, cosmos_container)
                if cosmos_results:
                    for item in cosmos_results[:3]: # [:3]検索結果は最大3件。最大3件までのループ。
                        with st.container(border=True):
                            st.markdown(f"**質問:** {item.get('question', 'N/A')}")
                            summary = item.get('summary_ui') or item.get('summary_chat')
                            if summary: st.markdown(f"**要約:** {summary}")
                            if item.get('generated_sql'): st.code(item.get('generated_sql'), language='sql')
                            st.caption(f"タイムスタンプ: {item.get('timestamp')}")
                else:
                    st.info("Cosmos DB で一致する履歴は見つかりませんでした。")
        else:
            st.warning("検索キーワードを入力してください。")