# メイン画面
import streamlit as st
import pyodbc
import pandas as pd
import openai
import os
import json
import re
import datetime
import uuid

from dotenv import load_dotenv

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.models import VectorizedQuery
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    HnswAlgorithmConfiguration, # HNSWアルゴリズム用
    VectorSearchProfile
#    SemanticConfiguration, # セマンティック検索用 (オプション)
#    SemanticPrioritizedFields,
#    SemanticField
)
import tiktoken # トークン数計算用ライブラリ

# ページの基本設定
st.set_page_config(
    page_title="クエリチャットDB Azure(Qnect)(キュネクト)",
    page_icon="🔗",
    layout="wide",
)

# タイトルと説明
st.title("🔗 Qnect (キュネクト)")
st.caption("Azure OpenAIとAzure AI Searchを活用した対話型DBクエリ支援システム")

# .envから環境変数を読み込む
load_dotenv()

# Azure OpenAI の設定
client = openai.AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# Azure AI Search の設定
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
AZURE_SEARCH_INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME", "chat-history-index")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")


# DB接続文字列の取得
from db_config import connection_string

# マスキング設定ファイルの読み込み
#with open("config/data_masking/masking_columns.json", "r", encoding="utf-8") as f:
#    masking_config = json.load(f)
masking_config = {}
masking_path = "config/data_masking/masking_columns.json"
if os.path.exists(masking_path):
    with open(masking_path, "r", encoding="utf-8") as f:
        masking_config = json.load(f)

def get_mask_columns(table_name):
    return masking_config.get(table_name, [])

# 履歴保存ファイル
HISTORY_PATH = "data/chat_history.json"

# --- トークン数制限のためのヘルパー関数 ---
def trim_messages_to_token_limit(messages, max_tokens=10000, model_name="gpt-4o-mini"):
    """指定されたトークン数上限を超えないようにメッセージをトリミングする"""
    try:
        enc = tiktoken.encoding_for_model(model_name)
    except KeyError:
        # モデル名が見つからない場合はデフォルトのエンコーディングを使用 (例: gpt-4)
        enc = tiktoken.get_encoding("cl100k_base")

    total_tokens = 0
    trimmed_messages = []
    # messages は [ {"role": "system", "content": "..."}, {"role": "user", "content": "..."} ] の形式を想定
    # 最新のメッセージを優先するため、逆順で処理し、上限を超えたら停止
    for message in reversed(messages):
        # "content" が None の場合や存在しない場合を考慮
        content_to_encode = message.get("content", "") if message.get("content") is not None else ""
        if not isinstance(content_to_encode, str): # contentが文字列でない場合のフォールバック
            content_to_encode = str(content_to_encode)

        tokens_in_message = len(enc.encode(content_to_encode))
        
        # システムメッセージは常に含める場合や、特定のメッセージタイプを優先するロジックも検討可能
        # ここでは単純にトークン数で判断
        if total_tokens + tokens_in_message <= max_tokens:
            trimmed_messages.insert(0, message) # 先頭に追加して元の順序を維持
            total_tokens += tokens_in_message
        else:
            # トークン上限を超えたので、これ以上古いメッセージは追加しない
            # 重要：システムメッセージが先頭にある場合、それがトリムされる可能性を考慮する必要がある。
            # この実装では最新のメッセージから優先的に保持する。
            # システムメッセージを常に保持したい場合は、別途ロジックを追加する。
            # 例: システムメッセージを最初に `trimmed_messages` に追加し、残りのトークンで他のメッセージを処理する。
            # ただし、今回は与えられたシンプルなトリミング関数例[1]に従う。
            break
    # st.info(f"元のメッセージ数: {len(messages)}, トリム後のメッセージ数: {len(trimmed_messages)}, 合計トークン数: {total_tokens}")
    return trimmed_messages

# Azure AI Search 関連の関数
def get_search_client():
    if AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_KEY:
        return SearchClient(endpoint=AZURE_SEARCH_ENDPOINT,
                            index_name=AZURE_SEARCH_INDEX_NAME,
                            credential=AzureKeyCredential(AZURE_SEARCH_KEY))
    return None

def get_search_index_client():
    if AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_KEY:
        return SearchIndexClient(endpoint=AZURE_SEARCH_ENDPOINT,
                                 credential=AzureKeyCredential(AZURE_SEARCH_KEY))
    return None

def generate_openai_embedding(text):
    if not text or not AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME:
        return None
    try:
        response = client.embeddings.create(
            input=text,
            model=AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME
        )
        return response.data[0].embedding
    except Exception as e:
        st.error(f"Embedding生成エラー: {e}")
        st.warning("`AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME` の設定が正しいか確認してください。")
        return None

def create_search_index_if_not_exists():
    if not AZURE_SEARCH_ENDPOINT or not AZURE_SEARCH_KEY or not AZURE_SEARCH_INDEX_NAME:
        st.warning("Azure AI Search の設定が不足しているため、インデックス作成をスキップします。")
        return

    index_client = get_search_index_client()
    if not index_client:
        return

    try:
        index_client.get_index(AZURE_SEARCH_INDEX_NAME)
        # st.info(f"検索インデックス '{AZURE_SEARCH_INDEX_NAME}' は既に存在します。")
    except Exception:
        st.info(f"検索インデックス '{AZURE_SEARCH_INDEX_NAME}' が存在しないため、新規作成します。")
        # インデックスのフィールドを定義
        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True, sortable=True, filterable=True, facetable=True),
            SearchableField(name="question", type=SearchFieldDataType.String, sortable=True, filterable=True),
            SearchableField(name="generated_sql", type=SearchFieldDataType.String, filterable=True),
            SearchableField(name="summary", type=SearchFieldDataType.String),
            SearchField(name="summary_vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                        searchable=True, vector_search_dimensions=1536, vector_search_profile_name="my-hnsw-profile"), # text-embedding-ada-002、text-embedding-3-smallは1536次元
            SimpleField(name="timestamp", type=SearchFieldDataType.DateTimeOffset, sortable=True, filterable=True)
        ]

        # ベクトル検索プロファイル (HNSWアルゴリズムを使用)
        vector_search = VectorSearch(
            profiles=[VectorSearchProfile(name="my-hnsw-profile", algorithm_configuration_name="my-hnsw-config")],
            algorithms=[HnswAlgorithmConfiguration(name="my-hnsw-config")]
        )
        
        # セマンティック検索の設定 (オプション、ランキング向上に寄与)
        # semantic_config = SemanticConfiguration(
        #     name="my-semantic-config",
        #     prioritized_fields=SemanticPrioritizedFields(
        #         title_field=None,
        #         content_fields=[SemanticField(field_name="summary")]
        #     )
        # )
        index = SearchIndex(
            name=AZURE_SEARCH_INDEX_NAME,
            fields=fields,
            vector_search=vector_search,
            # semantic_search = semantic_config # セマンティック検索を有効にする場合
        )
        try:
            index_client.create_index(index)
            st.success(f"検索インデックス '{AZURE_SEARCH_INDEX_NAME}' を作成しました。")
        except Exception as e:
            st.error(f"検索インデックスの作成エラー: {e}")

# アプリ起動時にインデックス存在確認・作成
create_search_index_if_not_exists()


def upload_document_to_search(doc_data):
    search_client = get_search_client()
    if not search_client or not doc_data:
        return

    try:
        search_client.upload_documents(documents=[doc_data])
        # st.info(f"ドキュメント ID {doc_data['id']} を検索インデックスにアップロードしました。")
    except Exception as e:
        st.error(f"検索インデックスへのドキュメントアップロードエラー: {e}")


def search_chat_history(query_text, top_n=3):
    search_client = get_search_client()
    if not search_client or not query_text:
        return []

    try:
        query_embedding = generate_openai_embedding(query_text)
        if not query_embedding:
            st.warning("クエリのEmbedding生成に失敗したため、ベクトル検索は行えません。キーワード検索のみ行います。")
            vector_queries = None
        else:
            vector_queries = [VectorizedQuery(vector=query_embedding, k_nearest_neighbors=top_n, fields="summary_vector")]

        results = search_client.search(
            search_text=query_text, # キーワード検索用
            vector_queries=vector_queries, # ベクトル検索用
            select=["id", "question", "summary", "timestamp"], # 取得するフィールド
            top=top_n
        )
        
        return [result for result in results]
    except Exception as e:
        st.error(f"チャット履歴の検索エラー: {e}")
        return []

# Cosmos DB 保存用関数
from azure.cosmos import CosmosClient, PartitionKey

COSMOS_ENDPOINT = os.getenv("AZURE_COSMOS_ENDPOINT")
COSMOS_KEY = os.getenv("AZURE_COSMOS_KEY")
COSMOS_DB_NAME = os.getenv("AZURE_COSMOS_DATABASE")
COSMOS_CONTAINER_NAME = os.getenv("AZURE_COSMOS_CONTAINER")

def get_cosmos_container():
    try:
        client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
        db = client.create_database_if_not_exists(id=COSMOS_DB_NAME)
        container = db.create_container_if_not_exists(
            id=COSMOS_CONTAINER_NAME,
            partition_key=PartitionKey(path="/id"),
            offer_throughput=400
        )
        return container
    except Exception as e:
        st.error(f"Cosmos DB接続エラー：{e}")
        return None

def save_to_cosmos(new_entry):
    try:
        container = get_cosmos_container()
        if container:
            # new_entryにidがなければ作成
            if "id" not in new_entry:
                new_entry["id"] = str(uuid.uuid4())
            container.create_item(body=new_entry)
            st.success("Cosmos DBにチャット履歴を保存しました。")
    except Exception as e:
        st.error(f"Cosmos DB保存エラー：{e}")


def save_chat_history_to_file(new_entry):
    # ... (既存のJSONファイルへの保存処理) ...
    try:
        if os.path.exists(HISTORY_PATH):
            with open(HISTORY_PATH, "r", encoding="utf-8") as f:
                history = json.load(f)
        else:
            history = []

        # タイムスタンプにUTCタイムゾーンを付与して追加
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        new_entry["timestamp"] = timestamp
        history.append(new_entry)

        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"履歴の保存エラー: {e}")

    # Azure AI Search にもアップロード
    if AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_KEY:
        doc_id = str(uuid.uuid4())
        summary_text = new_entry.get("summary_ui") or new_entry.get("summary_chat", "") # summary_ui または summary_chat を使う
        
        search_doc = {
            "id": doc_id,
            "question": new_entry.get("question", ""),
            "generated_sql": new_entry.get("generated_sql", ""),
            "summary": summary_text,
            # new_entryから正しい形式のタイムスタンプを使用
            "timestamp": new_entry.get("timestamp")
        }
        if summary_text:
            embedding = generate_openai_embedding(summary_text)
            if embedding:
                search_doc["summary_vector"] = embedding
        
        upload_document_to_search(search_doc)


# 新しい会話を始めるための関数
def start_new_conversation():
    """
    新しい会話を開始するために、セッション情報をクリアします。
    通常UIとチャットUIの入力・出力をすべてリセットし、
    AIが過去の対話履歴を引き継がないようにします。
    """
    # 1. 過去のQ&Aの流れがAIに引き継がれないように、AIに渡すコンテキスト履歴をクリア
    st.session_state.chat_history = []
    
    # 2. 画面に表示するチャットメッセージ履歴をクリア
    st.session_state.messages = []

    # 3. 通常UIとチャットUIで生成・保持される各種情報をクリアするためのキーリスト
    keys_to_clear = [
        # 通常UI関連のキー
        "user_question",            # 最初の質問入力
        "generated_sql",            # 通常UIで生成されたSQL
        "query_result_ui",          # 通常UIのSQL実行結果(DataFrame)
        "masked_query_result_ui",   # マスキングされた実行結果
        "summary_ui",               # 通常UIで生成された要約
        "first_user_question",      # 要約後に保持される最初の質問
        "first_sample_text_csv",    # 要約後に保持される最初の結果サンプル

        # チャットUI関連のキー
        "generated_sql_chat",       # チャットで生成されたSQL
        "query_result_chat",        # チャットのSQL実行結果(DataFrame)
        "masked_query_result_chat", # マスキングされた実行結果
        "summary_chat",             # チャットで生成された要約
        "last_user_input",          # チャットの最後のユーザー入力
        "last_ai_response",         # チャットの最後のAI応答
        "first_sample_text_csv_chat",# チャットの要約で使われた結果サンプル

        # UIの表示状態を制御するフラグ
        "show_generated_sql",
        "show_summary_button",
        "show_chat_button",
        "show_generated_sql_chat",
        "show_summary_chat_button"
    ]

    # 4. st.session_stateにキーが存在すれば安全に削除
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

    # 5. ユーザーにクリアされたことを通知
    st.toast("新しい会話を開始しました。入力と出力がクリアされました。", icon="🧹")

    # 6. 画面を即時更新して変更を反映
    # st.rerun()はスクリプトを最初から再実行します。
    # しかし「ボタンのon_clickなどのコールバック関数内」で st.rerun() を呼ぶと、
    # そのコールバックの実行が終わった後にすでにStreamlitが自動的に再実行を行うため、明示的なst.rerun()は無効（no-op）になります。
    #st.rerun() #Calling st.rerun() within a callback is a no-op.


# --- セッションステート初期化 ---
if "conn" not in st.session_state:
    st.session_state.conn = None
if "generated_sql" not in st.session_state:
    st.session_state.generated_sql = ""
if "query_result_ui" not in st.session_state:
    st.session_state.query_result_ui = None
if "summary_ui" not in st.session_state:
    st.session_state.summary_ui = ""
if "generated_sql_chat" not in st.session_state:
    st.session_state.generated_sql_chat = ""
if "query_result_chat" not in st.session_state:
    st.session_state.query_result_chat = None
if "summary_chat" not in st.session_state:
    st.session_state.summary_chat = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- マスキング処理 ---
def mask_sensitive_data(df, mask_columns):
    df_copy = df.copy()
    for col in mask_columns:
        if col in df_copy.columns:
            df_copy[col] = df_copy[col].astype(str).apply(lambda x: "＊＊＊" if x else x)
    return df_copy


# 1. DB接続管理
with st.container():
    op_col1, op_col2, op_col3 = st.columns([1, 1, 6])
    with op_col1:
        st.markdown("### DB操作")
    with op_col2:
        connect_clicked = st.button("DB接続！")
    with op_col3:
        disconnect_clicked = st.button("DB切断")

if connect_clicked:
    try:
        st.session_state.conn = pyodbc.connect(connection_string)
        st.success("接続成功！catalog_mstテーブルからデータを取得しました。")
        query = "SELECT TOP 2 * FROM catalog_mst;"
        df = pd.read_sql(query, st.session_state.conn)
        st.dataframe(df)
    except Exception as e:
        st.error(f"接続エラー：{e}")
elif disconnect_clicked:
    try:
        if st.session_state.conn:
            st.session_state.conn.close()
            st.session_state.conn = None
            st.success("DB接続を切断しました。")
        else:
            st.info("すでに切断されています。")
    except Exception as e:
        st.error(f"切断時エラー：{e}")

# 2. 自然言語で質問入力
st.markdown("### 質問を入力")
#st.text_inputの初期値（第2引数）をst.session_state.get("user_question", "")にして、クリア時にst.session_state["user_question"] = ""とする。
user_question = st.text_input("例：営業部に所属している従業員の一覧を見せて。",value=st.session_state.get("user_question", ""), key="user_question")

# 3. テーブルスキーマをMarkdownファイルから取得
schema_text = ""
#フォルダ名称
prompts_dir = "src/prompts_nltosql"
if os.path.isdir(prompts_dir):
    #このos.listdir はサブフォルダの中身を探索しない
    for filename in os.listdir(prompts_dir):
        if filename.endswith(".md"):
            with open(os.path.join(prompts_dir, filename), "r", encoding="utf-8") as f:
                schema_text += f"\n---\n# {filename}\n" + f.read() + "\n"

# 4. 通常のUI側で自然言語 → SQL 変換（Azure OpenAI利用）
if st.button("SQL作成") and user_question:
    with st.spinner("SQLに変換中..."):
        try:
            #フォルダ名称
            nltosql_prompt_path = "src/prompts_nltosql/nltosql/01_natural_language_to_sql.md"
            if not os.path.exists(nltosql_prompt_path):
                st.warning(f"プロンプトファイルが見つかりません: {nltosql_prompt_path}")
            else:
                with open(nltosql_prompt_path, "r", encoding="utf-8") as f:
                    nltosql_prompt = f.read()

                prompt = (
                    "データベース管理システム（DBMS）の種類は「SQL Server」です。"
                    "SQLにコードブロックは不要です。「```sql」や「```」は不要です。SQLに解説は不要です。実行可能なSQLのみを返してください。"
                    "SQLにはLIMIT句を使用しません"
                    "次のテーブル定義に基づき、ユーザーの質問に対応するSQLを出力してください。"
                )

                messages_for_sql=[
                    {"role": "system", "content": "あなたはSQL生成アシスタントです。"},
                    {"role": "system", "content": prompt},
                    {"role": "system", "content": f"データベースのテーブル定義やテーブル構造: {schema_text}\n\n"},
                    {"role": "system", "content": nltosql_prompt},
                    {"role": "user", "content": f"ユーザーの質問: {user_question}"}
                ]
                # 送信前にトークン数を制限
                trimmed_messages_for_sql = trim_messages_to_token_limit(messages_for_sql, max_tokens=10000, model_name="gpt-4o-mini")

                response = client.chat.completions.create(
                    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                    messages=trimmed_messages_for_sql,
                    max_tokens=500 # 受信するトークン数の上限
                )

                st.session_state.generated_sql = response.choices[0].message.content.strip()
                st.success("SQL生成成功！")
        except Exception as e:
            st.error(f"SQL生成エラー：{e}")

# 5. 通常のUI側でバリデーションとSQL表示
if st.session_state.generated_sql:
    st.markdown("### 生成されたSQL：")
    st.code(st.session_state.generated_sql, language="sql")

    #upper_sql = st.session_state.generated_sql.strip().upper()
    #if not upper_sql.startswith("SELECT"):
    #    st.warning("SELECT文以外の記述やコメントが含まれているため、SQLを実行できません。")
    #else:

    # 6. SQL実行(SELECT文のみ)
    if st.button("SQL実行"):
        try:
            df = pd.read_sql(st.session_state.generated_sql, st.session_state.conn)
            st.session_state.query_result_ui = df

            #対象テーブル名を取得してマスキング適用
            match = re.search(r'FROM\s+([a-zA-Z0-9_]+)', st.session_state.generated_sql, re.IGNORECASE)
            table_name = match.group(1) if match else ""
            mask_columns = get_mask_columns(table_name)
            masked_df = mask_sensitive_data(df, mask_columns)
            st.session_state.masked_query_result_ui = masked_df
            #st.dataframe(masked_df)
            st.success("SQLを実行しました")
        except Exception as e:
            st.error(f"SQL実行エラー：{e}")

# SQL実行結果を常に表示(通常のUI側)
if st.session_state.query_result_ui is not None:
    st.markdown("### SQL実行結果")
    st.dataframe(st.session_state.masked_query_result_ui)

# 7. 要約と結果の説明(通常のUI側)
if st.session_state.query_result_ui is not None:
    if st.button("要約と結果の説明") and st.session_state.query_result_ui is not None:
        with st.spinner("要約と結果の説明を作成中..."):
            try:
                df_sample = st.session_state.masked_query_result_ui.head(8)
                sample_text_csv = df_sample.to_csv(index=False)

                #フォルダ名称
                summarize_prompt_path = "src/prompts_summary/summarilze_results_prompt.md"
                with open(summarize_prompt_path, "r", encoding="utf-8") as f:
                    summarize_prompt = f.read()
                messages_for_summary=[
                    {"role": "system", "content": "あなたはデータ要約アシスタントです。"},
                    {"role": "user", "content": f"ユーザーの質問: {user_question}"},
                    {"role": "user", "content": f"実行したSQL:\n{st.session_state.generated_sql}"},
                    {"role": "user", "content": f"CSVデータ:\n{sample_text_csv}"},
                    {"role": "user", "content": summarize_prompt}
                ]
                # 送信前にトークン数を制限
                trimmed_messages_for_summary = trim_messages_to_token_limit(messages_for_summary, max_tokens=10000, model_name="gpt-4o-mini")

                summary_response = client.chat.completions.create(
                    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                    messages=trimmed_messages_for_summary,
                    max_tokens=50
                )
                ## AIからの返答をセッション(session_state.summary_ui)に保存
                st.session_state.summary_ui = summary_response.choices[0].message.content.strip()
                st.session_state.first_user_question = user_question  # このuser_questionもSQL作成時のもの
                st.session_state.first_sample_text_csv = sample_text_csv
                # 確認表示
                #st.write(st.session_state.first_sample_text_csv)
                #st.markdown("### ■要約")
                # AIからの返答を表示
                #st.write(st.session_state.summary_ui)

                # チャット履歴に追加(通常のUI側)
                chat_entry = {
                    "question": user_question,  # SQL作成時の質問
                    "generated_sql": st.session_state.generated_sql,
                    "result_sample": json.loads(st.session_state.query_result_ui.head(8).to_json(orient="records")),
                    #"result_sample": json.loads(df_sample.to_json(orient="records")),
                    "summary_ui": st.session_state.summary_ui
                }
                st.session_state.chat_history.append(chat_entry)
                save_chat_history_to_file(chat_entry) # 内部でAISearchに保存
                save_to_cosmos(chat_entry)# 内部でCosmosDBに保存
            except Exception as e:
                st.error(f"要約と結果の説明の生成エラー：{e}")

# 要約表示を常に維持(通常のUI側)
if st.session_state.summary_ui:
    st.markdown("### 要約")
    #AIからの返答を表示
    st.write(st.session_state.summary_ui)

# 8. チャット履歴の確認(左パネル)
with st.sidebar:
    st.markdown("### 会話操作")
    # on_clickに設定した関数内で st.rerun() を呼ぶため、ボタンが押された後の st.rerun() は不要です。
    st.button('新しい会話を始める', on_click=start_new_conversation, key="new_conversation_btn")

    st.markdown("---") # 区切り線

    st.markdown("### 要約と結果説明、送信の履歴")
    show_panel = st.checkbox("表示する", value=False, key="toggle_history")
    if show_panel:
        if os.path.exists(HISTORY_PATH):
            with open(HISTORY_PATH, "r", encoding="utf-8") as f:
                try:
                    history = json.load(f) # ローカルファイルからの履歴
                except json.JSONDecodeError:
                    history = []
                for item in reversed(history[-5:]): #表示するのはファイルからの履歴（最大5件）
                    st.markdown(f"**日時：** {item.get('timestamp', '')}")
                    st.markdown(f"**質問：** {item.get('question', '')}")
                    st.markdown(f"**生成SQL：** `{item.get('generated_sql', '')}`")
                    if "summary_ui" in item:
                        st.markdown(f"**要約：** {item['summary_ui']}")
                    if "summary_chat" in item:
                        st.markdown(f"**要約（チャット）:** {item['summary_chat']}")
                st.markdown("---")
        else:
            st.info("履歴がまだ存在しません。")

# 履歴をプロンプトに変換する関数
def build_chat_context(history, limit=2):  # 最新の2件or3件までに絞る（Token節約）
    messages = []
    for h in history[-limit:]:  # 最新の2件or3件までに絞る（Token節約）
        messages.append({"role": "user", "content": f"質問: {h.get('question', '')}"})
        if h.get('generated_sql'): # SQLがある場合のみ追加
            messages.append({"role": "user", "content": f"生成SQL:\n{h.get('generated_sql', '')}"})
        if "summary_ui" in h:
            messages.append({"role": "assistant", "content": f"要約: {h['summary_ui']}"})
        elif "summary_chat" in h:
            messages.append({"role": "assistant", "content": f"要約（チャット）: {h['summary_chat']}"})
    return messages

# 9. チャットのUI側、対話型インターフェイス（要約後に入力受付）
if st.session_state.summary_ui:
    st.markdown("### チャット形式で質問")
    # チャット履歴をセッションで管理
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # チャット履歴を表示（まず履歴だけ上に表示）
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"**あなた:** {msg['content']}")
        else:
            st.markdown(f"**AI:** {msg['content']}")

    # --- ここから下に入力欄とボタンを表示 ---
    st.divider()  # 仕切り線（オプション）


    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_area("続けて質問を入力してください:", height=100)
        with st.container():
            op_col1, op_col2, op_col3 = st.columns([1, 5, 8])  # 右側に大きな空白カラム
            with op_col1:
                submitted = st.form_submit_button("送信")
            with op_col2:
                nltosqlmake_clicked = st.form_submit_button("SQL作成 (チャット用)")
            # op_col3は空白スペース用


        if submitted and user_input:
            # ユーザーのメッセージを履歴に追加
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # ローディング表示
            with st.spinner('AIが考え中... (検索と応答)'):
                try:
                    # Azure AI Searchから関連情報を取得
                    retrieved_search_context_str = ""
                    if AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_KEY:
                        search_results = search_chat_history(user_input, top_n=2) # 上位2件を取得
                        if search_results:
                            retrieved_search_context_str += "【関連する過去のやり取り】:\n"
                            for result in search_results:
                                retrieved_search_context_str += f"- 質問: {result.get('question', 'N/A')}\n  要約: {result.get('summary', 'N/A')}\n"
                            retrieved_search_context_str += "\n---\n"
                    # 履歴から過去メッセージ構築（最新2件）
                    #history_messages = build_chat_context(st.session_state.chat_history, limit=2)   # 最新の2件or3件までに絞る（Token節約）
                    #st.write(history_messages )#確認結果
                    # 履歴から過去メッセージ構築（最新2件） + AI Search結果 + 現在のユーザー入力
                    history_messages_for_chat = build_chat_context(st.session_state.chat_history, limit=2)
                    constructed_messages_for_chat = []
                    # 既存のチャット履歴（画面表示用）もコンテキストに含める場合
                    # constructed_messages_for_chat.extend(st.session_state.messages[-3:]) # 最新のチャット数件

                    # 過去のDB操作履歴
                    constructed_messages_for_chat.extend(history_messages_for_chat)
                    
                    # Azure AI Search から取得したコンテキスト
                    if retrieved_search_context_str:
                         constructed_messages_for_chat.append({"role": "system", "content": retrieved_search_context_str})
                    

                    # 現在のユーザー入力を追加
                    #current_input = {"role": "user", "content": user_input}
                    #messages = history_messages + [current_input]
                    constructed_messages_for_chat.append({"role": "user", "content": user_input})

                    # 送信前にトークン数を制限
                    trimmed_messages_for_chat_response = trim_messages_to_token_limit(constructed_messages_for_chat, max_tokens=10000, model_name="gpt-4o-mini")

                    #response = client.chat.completions.create(
                    #    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                    #    messages=messages
                    #
                    response = client.chat.completions.create(
                        model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"), # GPT-4o miniを指定
                        messages=trimmed_messages_for_chat_response,
                        max_tokens=500
                    )

                    ai_response = response.choices[0].message.content.strip()
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                    # 最新の質問も履歴として保持（あとで要約やSQL生成時に再利用可能）
                    st.session_state.last_user_input = user_input
                    st.session_state.last_ai_response = ai_response
                    # チャットのやり取りも検索対象として保存する場合 
                    # この時点ではSQLやDBからの結果がないため、質問とAIの一般的な応答を保存する形になる
                    # もし、このAI応答が「要約」に類するものであれば、保存する価値がある

                    current_chat_entry_for_search = {
                         "question": user_input,
                        "summary_chat": ai_response, # "summary_chat" としてAIの応答を保存
                        # チャットのやり取り保存時もUTCタイムゾーン付きのタイムスタンプを使用
                        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
                    }
                    save_chat_history_to_file(current_chat_entry_for_search)  # AISearchに保存
                    save_to_cosmos(current_chat_entry_for_search) # CosmosDBに保存
                    # すぐリロードして新しい会話を表示
                    st.rerun()
                except Exception as e:
                    st.error(f"チャット応答エラー（検索含む）：{e}")

        if nltosqlmake_clicked and user_input:
            # ユーザーのメッセージを履歴に追加(チャットの上部の履歴へ)
            st.session_state.messages.append({"role": "user", "content": user_input})

            with st.spinner("チャットの質問をSQLに変換中..."):
                try:
                    #フォルダ名称
                    nltosql_prompt_path = "src/prompts_nltosql/nltosql/01_natural_language_to_sql.md"
                    if not os.path.exists(nltosql_prompt_path):
                        st.warning(f"プロンプトファイルが見つかりません: {nltosql_prompt_path}")
                    else:
                        with open(nltosql_prompt_path, "r", encoding="utf-8") as f:
                            nltosql_prompt_content_chat = f.read()

                        system_prompt_sql_chat = (
                            "データベース管理システム（DBMS）の種類は「SQL Server」です。"
                            "SQLにコードブロックは不要です。「```sql」や「```」は不要です。SQLに解説は不要です。実行可能なSQLのみを返してください。"
                            "SQLにはLIMIT句を使用しません"
                            "次のテーブル定義に基づき、ユーザーの質問に対応するSQLを出力してください。"
                        )

                        messages_for_chat_sql = [
                            {"role": "system", "content": "あなたはSQL生成アシスタントです。"},
                            {"role": "system", "content": system_prompt_sql_chat},
                            {"role": "system", "content": f"データベースのテーブル定義やテーブル構造: {schema_text}\n\n"},
                            {"role": "system", "content": nltosql_prompt_content_chat},
                            {"role": "user", "content": f"最新の質問: {user_input}"},
                        ]
                        
                        # チャット履歴からのコンテキストも追加する場合 (例: 直前の会話)
                        # chat_context_messages = st.session_state.messages[-3:] # 最新3件（ユーザー入力、AI応答、ユーザー入力）
                        # messages_for_chat_sql = chat_context_messages + messages_for_chat_sql

                        # 送信前にトークン数を制限
                        trimmed_messages_for_chat_sql = trim_messages_to_token_limit(messages_for_chat_sql, max_tokens=10000, model_name="gpt-4o-mini")

                        response = client.chat.completions.create(
                            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"), # GPT-4o miniを指定
                            messages=trimmed_messages_for_chat_sql,
                            max_tokens=500
                        )

                        # AIからの返答を履歴に追加
                        ai_sql = response.choices[0].message.content.strip()
                        st.session_state.generated_sql_chat = ai_sql
                        #st.write(st.session_state.generated_sql_chat )
                        st.success("SQL生成成功！")
                        #チャットの上部の履歴へ
                        st.session_state.messages.append({"role": "assistant", "content": f"(生成SQL) {ai_sql}"})
                        st.session_state.last_user_input = user_input
                        #st.write(st.session_state.last_user_input )
                        # すぐリロードして新しい会話を表示
                        st.rerun()
                except Exception as e:
                    st.error(f"SQL生成エラー：{e}")

# 10. チャットのUI側のバリデーションとSQL表示
if st.session_state.generated_sql_chat:
    st.markdown("### 生成されたSQL：")
    st.code(st.session_state.generated_sql_chat, language="sql")

    #upper_sql = st.session_state.generated_sql_chat.strip().upper()
    #if not upper_sql.startswith("SELECT"):
    #    st.warning("SELECT文以外の記述やコメントが含まれているため、SQLを実行できません。")
    #else:

    # 6. SQL実行(SELECT文のみ)
    #if st.button("SQL実行 (チャット用)"):
    col1, col2, col3 = st.columns([3, 5, 8])
    with col1:
        exec_clicked = st.button("SQL実行 (チャット用)")
    with col2:
        cancel_clicked = st.button("戻る (SQL実行しない)")
    # op_col3は空白スペース用


    if exec_clicked:
        try:
            df = pd.read_sql(st.session_state.generated_sql_chat, st.session_state.conn)
            st.session_state.query_result_chat = df

            #対象テーブル名を取得してマスキング適用
            match = re.search(r'FROM\s+([a-zA-Z0-9_]+)', st.session_state.generated_sql_chat, re.IGNORECASE)
            table_name = match.group(1) if match else ""
            mask_columns = get_mask_columns(table_name)

            masked_df = mask_sensitive_data(df, mask_columns)
            st.session_state.masked_query_result_chat = masked_df
            #st.dataframe(masked_df)
            
            # 表示用にCSV形式に変換（先頭5行などに制限可）
            df_preview = st.session_state.masked_query_result_chat.head(5)  # 必要に応じて制限
            result_text = df_preview.to_markdown(index=False)  # Markdownで表形式
            #チャットの上部の履歴へ
            st.session_state.messages.append({"role": "assistant", "content": f"SQL実行結果（上位5件）:\n```\n{result_text}\n```"})
            # 通常のUIにも表示（任意）
            #st.markdown("### SQL実行結果(チャット)")
            #st.dataframe(st.session_state.masked_query_result_chat)
            st.success("SQLを実行しました")
            st.rerun()  # 上部の履歴に即座に反映させるために必要
        except Exception as e:
            st.error(f"SQL実行エラー：{e}")
    
    # SQL実行結果を常に表示(通常のUI側)
    if st.session_state.query_result_chat is not None:
        st.markdown("### SQL実行結果(チャット)")
        st.dataframe(st.session_state.masked_query_result_chat)

    if cancel_clicked:
        st.session_state.generated_sql_chat = ""
        st.session_state.query_result_chat = None
        st.session_state.masked_query_result_chat = None
        st.session_state.summary_chat = ""
        st.session_state.show_generated_sql_chat = False
        st.session_state.show_summary_chat_button = False
        st.rerun()



# 11. 要約と結果の説明(チャットのUI側)
if st.session_state.query_result_chat is not None:
    if st.button("要約と結果の説明 (チャット用)"):
        with st.spinner("チャットの要約と結果の説明を作成中..."):
            try:
                df_sample_chat = st.session_state.masked_query_result_chat.head(8)
                sample_text_csv_chat = df_sample_chat.to_csv(index=False)

                #フォルダ名称
                summarize_prompt_path = "src/prompts_summary/summarilze_results_prompt.md"
                with open(summarize_prompt_path, "r", encoding="utf-8") as f:
                    summarize_prompt_content_chat = f.read()

                messages_for_chat_summary=[
                    {"role": "system", "content": "あなたはデータ要約アシスタントです。"},
                    {"role": "user", "content": f"ユーザーの質問: {st.session_state.last_user_input}"}, # 直前のチャット入力
                    #{"role": "user", "content": f"ユーザーの質問: {user_input}"},
                    {"role": "user", "content": f"実行したSQL:\n{st.session_state.generated_sql_chat}"},
                    {"role": "user", "content": f"CSVデータ:\n{sample_text_csv_chat}"},
                    {"role": "user", "content": summarize_prompt_content_chat}
                ]

                # 送信前にトークン数を制限
                trimmed_messages_for_chat_summary = trim_messages_to_token_limit(messages_for_chat_summary, max_tokens=10000, model_name="gpt-4o-mini")

                summary_response_chat = client.chat.completions.create(
                    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"), # GPT-4o miniを指定
                    messages=trimmed_messages_for_chat_summary,
                    max_tokens=500
                )

                ## AIからの返答をセッション(session_state.summary_chat)に保存
                summary_text  = summary_response_chat.choices[0].message.content.strip()
                st.session_state.summary_chat = summary_text
                st.session_state.first_user_question = user_question
                st.session_state.first_sample_text_csv_chat = sample_text_csv_chat

                # チャットに要約を上部の履歴に即時反映
                st.session_state.messages.append({"role": "assistant", "content": f"(生成したSQL) {st.session_state.generated_sql_chat}\n\n生成したSQLの要約: \n\n{st.session_state.summary_chat}"})

                # 確認表示
                #st.write(st.session_state.first_sample_text_csv_chat)
                # AIからの返答を表示
                #st.write(st.session_state.summary_chat)

                # ファイルとCosmosDBへの保存用)
                chat_entry_summary = {
                    "question": st.session_state.last_user_input,
                    "generated_sql": st.session_state.generated_sql_chat,
                    "result_sample": json.loads(df_sample_chat.to_json(orient="records")),
                    "summary_chat": st.session_state.summary_chat, # summary_chat として保存
                    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
                }
                st.session_state.chat_history.append(chat_entry_summary)
                save_chat_history_to_file(chat_entry_summary) # 内部でAISearchに保存
                save_to_cosmos(chat_entry_summary) # CosmosDBに保存

                st.session_state.generated_sql_chat = ""
                st.session_state.query_result_chat = None
                st.session_state.masked_query_result_chat = None
                st.session_state.summary_chat = ""
                st.session_state.show_generated_sql_chat = False
                st.session_state.show_summary_chat_button = False

                st.success("要約を生成しました")
                st.rerun()  # 上部の履歴に即時反映。st.rerun() を呼ぶと、それ以降のコードは一切実行されません。
            except Exception as e:
                st.error(f"要約と結果の説明の生成エラー：{e}")
