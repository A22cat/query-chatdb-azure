import streamlit as st
import pyodbc
import pandas as pd
import openai
import os
import json
import re
import datetime
from dotenv import load_dotenv

# ページの基本設定
st.set_page_config(
    page_title="クエリチャットDB Azure(Qnect)",
    page_icon="🐱",
    layout="centered",
)

# .envから環境変数を読み込む
load_dotenv()

# Azure OpenAI の設定
client = openai.AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# DB接続文字列の取得
from db_config import connection_string

# マスキング設定ファイルの読み込み
#with open("../config/data_masking/masking_columns.json", "r", encoding="utf-8") as f:
#    masking_config = json.load(f)
masking_config = {}
masking_path = "../config/data_masking/masking_columns.json"
if os.path.exists(masking_path):
    with open(masking_path, "r", encoding="utf-8") as f:
        masking_config = json.load(f)

def get_mask_columns(table_name):
    return masking_config.get(table_name, [])

# 履歴保存ファイル
HISTORY_PATH = "../data/chat_history.json"

# 履歴の保存処理
def save_chat_history_to_file(new_entry):
    try:
        if os.path.exists(HISTORY_PATH):
            with open(HISTORY_PATH, "r", encoding="utf-8") as f:
                history = json.load(f)
        else:
            history = []

        # タイムスタンプを付与して追加
        timestamp = datetime.datetime.now().isoformat()
        new_entry["timestamp"] = timestamp
        history.append(new_entry)

        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"履歴の保存エラー: {e}")

# セッションステート初期化
if "conn" not in st.session_state:
    st.session_state.conn = None
if "generated_sql_ui" not in st.session_state:
    st.session_state.generated_sql_ui = ""
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
    st.session_state.generated_sql = ""
if "query_result" not in st.session_state:
    st.session_state.query_result = None
if "summary" not in st.session_state:
    st.session_state.summary = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "show_generated_sql_chat" not in st.session_state:
    st.session_state.show_generated_sql_chat = True
if "masked_query_result_chat" not in st.session_state:
    st.session_state.masked_query_result_chat = None
if "show_summary_chat_button" not in st.session_state:
    st.session_state.show_summary_chat_button = True

# マスキング処理
def mask_sensitive_data(df, mask_columns):
    df_copy = df.copy()
    for col in mask_columns:
        if col in df_copy.columns:
            df_copy[col] = df_copy[col].astype(str).apply(lambda x: "＊＊＊" if x else x)
    return df_copy

# タイトル
st.title("クエリチャットDB Azure")

# 1. DB接続管理
with st.container():
    op_col1, op_col2, op_col3 = st.columns([1, 2, 2])
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
user_question = st.text_input("例：3名の従業員を教えて")

# 3. テーブルスキーマをMarkdownファイルから取得
schema_text = ""
#フォルダ名称
prompts_dir = "prompts_nltosql"
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
            nltosql_prompt_path = "prompts_nltosql/01_natural_language_to_sql.md"
            with open(nltosql_prompt_path, "r", encoding="utf-8") as f:
                nltosql_prompt = f.read()
            
            prompt = (
                "データベース管理システム（DBMS）の種類は「SQL Server」です。"
                "SQLにはLIMIT句を使用しません"
                "次のテーブル定義に基づき、ユーザーの質問に対応するSQLを出力してください。"
                "SQLにコードブロック（``````）や解説は不要です。実行可能なSQLのみを返してください。"
                "SQL ServerでOFFSET ... FETCH NEXT ...句を使う際にORDER BY句が必須です。"
            )
            response = client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                messages=[
                    {"role": "system", "content": "あなたはSQL生成アシスタントです。"},
                    {"role": "system", "content": prompt},
                    {"role": "system", "content": f"データベースのテーブル定義やテーブル構造: {schema_text}\n\n"},
                    {"role": "system", "content": nltosql_prompt},
                    {"role": "user", "content": f"ユーザーの質問: {user_question}"}
                ]
            )

            st.session_state.generated_sql = response.choices[0].message.content.strip()
            st.success("SQL生成成功！")
        except Exception as e:
            st.error(f"SQL生成エラー：{e}")

# 5. 通常のUI側でバリデーションとSQL表示
if st.session_state.generated_sql:
    st.markdown("### 生成されたSQL：")
    st.code(st.session_state.generated_sql, language="sql")

    upper_sql = st.session_state.generated_sql.strip().upper()
    if not upper_sql.startswith("SELECT"):
        st.warning("SELECT文以外の記述やコメントが含まれているため、SQLを実行できません。")
    else:
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
                summarize_prompt_path = "prompts_summary/summarilze_results_prompt.md"
                with open(summarize_prompt_path, "r", encoding="utf-8") as f:
                    summarize_prompt = f.read()

                summary_response = client.chat.completions.create(
                    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                    messages=[
                        {"role": "system", "content": "あなたはデータ要約アシスタントです。"},
                        {"role": "user", "content": f"ユーザーの質問: {user_question}"},
                        {"role": "user", "content": f"実行したSQL:\n{st.session_state.generated_sql}"},
                        {"role": "user", "content": f"CSVデータ:\n{sample_text_csv}"},
                        {"role": "user", "content": summarize_prompt}
                    ]
                )
                ## AIからの返答をセッション(session_state.summary_ui)に保存
                st.session_state.summary_ui = summary_response.choices[0].message.content.strip()
                st.session_state.first_user_question = user_question
                st.session_state.first_sample_text_csv = sample_text_csv
                # 確認表示
                #st.write(st.session_state.first_sample_text_csv)
                #st.markdown("### ■要約")
                # AIからの返答を表示
                #st.write(st.session_state.summary_ui)

                # チャット履歴に追加
                chat_entry = {
                    "question": user_question,
                    "generated_sql": st.session_state.generated_sql,
                    "result_sample": json.loads(df_sample.to_json(orient="records")),
                    "summary_ui": st.session_state.summary_ui
                }
                st.session_state.chat_history.append(chat_entry)
                save_chat_history_to_file(chat_entry)
            except Exception as e:
                st.error(f"要約と結果の説明の生成エラー：{e}")

# 要約表示を常に維持(通常のUI側)
if st.session_state.summary_ui:
    st.markdown("### 要約")
    #AIからの返答を表示
    st.write(st.session_state.summary_ui)

# 8. チャット履歴の確認(左パネル)←1箇所に統一
with st.sidebar:
    st.markdown("### 要約と結果説明の履歴")
    show_panel = st.checkbox("表示する", value=False, key="toggle_history")
    if show_panel:
        if os.path.exists(HISTORY_PATH):
            with open(HISTORY_PATH, "r", encoding="utf-8") as f:
                try:
                    history = json.load(f)
                except json.JSONDecodeError:
                    history = []
            for item in reversed(history[-5:]):
                st.markdown(f"**日時：** {item['timestamp']}")
                st.markdown(f"**質問：** {item['question']}")
                st.markdown(f"**生成SQL：** `{item['generated_sql']}`")
                if "summary_ui" in item:
                    st.markdown(f"**要約：** {item['summary_ui']}")
                if "summary_chat" in item:
                    st.markdown(f"**要約（チャット）:** {item['summary_chat']}")
                st.markdown("---")
        else:
            st.info("履歴がまだ存在しません。")

# 履歴をプロンプトに変換する関数
def build_chat_context(history, limit=2):
    messages = []
    for h in history[-limit:]:  # 最新の2件までに絞る（Token節約）
        messages.append({"role": "user", "content": f"質問: {h.get('question', '')}"})
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
            op_col1, op_col2, op_col3 = st.columns([2, 4, 7])  # 右側に大きな空白カラム
            with op_col1:
                submitted = st.form_submit_button("送信")
            with op_col2:
                nltosqlmake_clicked = st.form_submit_button("SQL作成 (チャット用)")
            # op_col3は空白スペース用


        if submitted and user_input:
            # ユーザーのメッセージを履歴に追加
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # ローディング表示
            with st.spinner('AIが考え中...'):
                try:
                    # 履歴から過去メッセージ構築（最新2-3件）
                    history_messages = build_chat_context(st.session_state.chat_history, limit=2)
                    st.write(history_messages )#確認結果
                    
                    # 現在のユーザー入力を追加
                    current_input = {"role": "user", "content": user_input}
                    messages = history_messages + [current_input]

                    response = client.chat.completions.create(
                        model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                        messages=messages
                    )

                    ai_response = response.choices[0].message.content.strip()
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                    # 最新の質問も履歴として保持（あとで要約やSQL生成時に再利用可能）
                    st.session_state.last_user_input = user_input
                    st.session_state.last_ai_response = ai_response
                    # すぐリロードして新しい会話を表示
                    st.rerun()
                except Exception as e:
                    st.error(f"チャット応答エラー：{e}")

            '''
            with st.spinner('AIが考え中...'):
                # APIリクエスト
                response = client.chat.completions.create(
                    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                    messages=[
                        {"role": "user", "content": f"最新の質問: {user_input}"},
                        {"role": "user", "content": f"1個目の項目に入力した質問: {st.session_state.first_user_question}"},
                        {"role": "user", "content": f"実行したSQL:\n{st.session_state.generated_sql_ui}"},
                        {"role": "user", "content": f"CSVデータ:\n{st.session_state.first_sample_text_csv}"},
                    ]
                )'''

        if nltosqlmake_clicked and user_input:
            # ユーザーのメッセージを履歴に追加(チャットの上部の履歴へ)
            st.session_state.messages.append({"role": "user", "content": user_input})

            with st.spinner("チャットの質問をSQLに変換中..."):
                try:
                    #フォルダ名称
                    nltosql_prompt_path = "prompts_nltosql/01_natural_language_to_sql.md"
                    with open(nltosql_prompt_path, "r", encoding="utf-8") as f:
                        nltosql_prompt = f.read()
                    
                    prompt = (
                        "データベース管理システム（DBMS）の種類は「SQL Server」です。"
                        "SQLにはLIMIT句を使用しません"
                        "次のテーブル定義に基づき、ユーザーの質問に対応するSQLを出力してください。"
                        "SQLにコードブロック（``````）や解説は不要です。実行可能なSQLのみを返してください。"
                        "SQL ServerでOFFSET ... FETCH NEXT ...句を使う際にORDER BY句が必須です。"
                    )
                    response = client.chat.completions.create(
                        model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                        messages=[
                            {"role": "system", "content": "あなたはSQL生成アシスタントです。"},
                            {"role": "system", "content": prompt},
                            {"role": "system", "content": f"データベースのテーブル定義やテーブル構造: {schema_text}\n\n"},   
                            {"role": "system", "content": nltosql_prompt},
                            {"role": "user", "content": f"最新の質問: {user_input}"},
                        ]
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

    upper_sql = st.session_state.generated_sql_chat.strip().upper()
    if not upper_sql.startswith("SELECT"):
        st.warning("SELECT文以外の記述やコメントが含まれているため、SQLを実行できません。")
    else:
        # 6. SQL実行(SELECT文のみ)
        #if st.button("SQL実行 (チャット用)"):
        col1, col2, col3 = st.columns([3, 5, 2])
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
                df_sample = st.session_state.masked_query_result_chat.head(8)
                sample_text_csv = df_sample.to_csv(index=False)

                #フォルダ名称
                summarize_prompt_path = "prompts_summary/summarilze_results_prompt.md"
                with open(summarize_prompt_path, "r", encoding="utf-8") as f:
                    summarize_prompt = f.read()

                summary_response = client.chat.completions.create(
                    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                    messages=[
                        {"role": "system", "content": "あなたはデータ要約アシスタントです。"},
                        {"role": "user", "content": f"ユーザーの質問: {user_input}"},
                        {"role": "user", "content": f"実行したSQL:\n{st.session_state.generated_sql_chat}"},
                        {"role": "user", "content": f"CSVデータ:\n{sample_text_csv}"},
                        {"role": "user", "content": summarize_prompt}
                    ]
                )
                ## AIからの返答をセッション(session_state.summary_chat)に保存
                summary_text  = summary_response.choices[0].message.content.strip()
                st.session_state.summary_chat = summary_text
                st.session_state.first_user_question = user_question
                st.session_state.first_sample_text_csv = sample_text_csv

                # チャットに要約を上部の履歴に即時反映
                st.session_state.messages.append({"role": "assistant", "content": f"(生成したSQL) {st.session_state.generated_sql_chat}\n\n生成したSQLの要約: \n\n{summary_text}"})

                # 確認表示
                #st.write(st.session_state.first_sample_text_csv)
                # AIからの返答を表示
                #st.write(st.session_state.summary_chat)

                # チャット履歴に追加
                chat_entry = {
                    "question": st.session_state.last_user_input,
                    "generated_sql": st.session_state.generated_sql_chat,
                    "result_sample": json.loads(df_sample.to_json(orient="records")),
                    "summary_chat": st.session_state.summary_chat
                }
                st.session_state.chat_history.append(chat_entry)
                save_chat_history_to_file(chat_entry)

                st.session_state.generated_sql_chat = ""
                st.session_state.query_result_chat = None
                st.session_state.masked_query_result_chat = None
                st.session_state.summary_chat = ""
                st.session_state.show_generated_sql_chat = False
                st.session_state.show_summary_chat_button = False
                st.session_state.show_generated_sql_chat = False

                st.success("要約を生成しました")
                st.rerun()  # ← 上部の履歴に即時反映。st.rerun() を呼ぶと、それ以降のコードは一切実行されません。
            except Exception as e:
                st.error(f"要約と結果の説明の生成エラー：{e}")
