import streamlit as st
import pyodbc
import pandas as pd
import openai
import os
from dotenv import load_dotenv

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

# セッションステート初期化
if "conn" not in st.session_state:
    st.session_state.conn = None
if "generated_sql" not in st.session_state:
    st.session_state.generated_sql = ""
if "query_result" not in st.session_state:
    st.session_state.query_result = None
if "summary" not in st.session_state:
    st.session_state.summary = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# セキュリティ：マスキング対象カラム
SENSITIVE_COLUMNS = ["customer_name", "created_by", "phone_number"]

# マスキング処理
def mask_sensitive_data(df, mask_columns):
    df_copy = df.copy()
    for col in mask_columns:
        if col in df_copy.columns:
            df_copy[col] = df_copy[col].astype(str).apply(lambda x: "＊＊＊" if x else x)
    return df_copy

# ページの基本設定
st.set_page_config(
    page_title="Azure生成AIChatDB",
    page_icon="🐱",
    layout="centered",
)

# タイトル
st.title("Azure生成AIチャットDB(AzureOpenAI×AzureSQLDB×AzureAISearch)")

# 1. DB接続管理
with st.container():
    op_col1, op_col2, op_col3 = st.columns([1, 2, 2])
    with op_col1:
        st.markdown("### DB操作")
    with op_col2:
        connect_clicked = st.button("DB接続テスト")
    with op_col3:
        disconnect_clicked = st.button("DB切断")

if connect_clicked:
    try:
        st.session_state.conn = pyodbc.connect(connection_string)
        st.success("接続成功！catalog_mstテーブルからデータ取得中...")
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
user_question = st.text_input("例：今月の売上トップ3の商品を教えて")

# 3. テーブルスキーマをMarkdownファイルから取得
schema_text = ""
prompts_dir = "prompts_nltosql"    #フォルダ名称
if os.path.isdir(prompts_dir):
    for filename in os.listdir(prompts_dir):
        if filename.endswith(".md"):
            with open(os.path.join(prompts_dir, filename), "r", encoding="utf-8") as f:
                schema_text += f"\n---\n# {filename}\n" + f.read() + "\n"

# 4. 自然言語 → SQL 変換（Azure OpenAI利用）
if st.button("質問を送信") and user_question:
    with st.spinner("SQLに変換中..."):
        try:
            prompt = (
                "以下はデータベースのテーブル定義やテーブル構造です。"
                f"{schema_text}\n\n"
                "この定義に基づき、次の質問に対応するSQL（データベース管理システム（DBMS）の種類はSQL Server）を出力してください。"
                "余計な解説やコードブロック（``````）は不要で、実行可能なSQLのみを返してください。"
                "DBデータを変更するDELETE文など、DROP文など(テーブル構造の変更)SQLは不可"
                "Unicode対応のため、NVARCHAR型の検索条件にはUnicode対応のためNを付けてください。"
                "質問者から特に指定がない場合は、該当データの一部の列だけでなく、行全体（すべてのカラム）を表示してください。"
                "「1つ教えて」「2個表示して」など、数を指定する表現は、データの件数（例：1件、2件）を意味しています。"
                "質問文の意図を把握し必要に応じて、他の種類や項目についても、同様に数の指定はデータの件数として扱ってください。"
                f"質問: {user_question}"
            )
            response = client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                messages=[
                    {"role": "system", "content": "あなたはSQL生成アシスタントです。"},
                    {"role": "user", "content": prompt}
                ]
            )
            st.session_state.generated_sql = response.choices[0].message.content.strip()
            st.success("SQL生成成功！")
        except Exception as e:
            st.error(f"SQL生成エラー：{e}")

# 5. バリデーション
if st.session_state.generated_sql:
    st.markdown("#### 生成されたSQL：")
    st.code(st.session_state.generated_sql, language="sql")

    if any(kw in st.session_state.generated_sql.upper() for kw in ["DELETE", "DROP", "UPDATE", "INSERT"]):
        st.warning("このSQLにはデータを変更・削除する操作が含まれています。レビューが必要です。")
    #elif "SELECT *" in st.session_state.generated_sql.upper() and "WHERE" not in st.session_state.generated_sql.upper():
    #    st.warning("WHERE句なしの全件取得は禁止されています。SQLを見直してください。")
    else:
        # 6. 承認してSQL実行
        if st.button("SQLを実行"):
            try:
                df = pd.read_sql(st.session_state.generated_sql, st.session_state.conn)
                st.session_state.query_result = df
                masked_df = mask_sensitive_data(df, SENSITIVE_COLUMNS)
                st.dataframe(masked_df)
                st.success("SQLを実行しました")
            except Exception as e:
                st.error(f"SQL実行エラー：{e}")

# 7. 要約と結果の説明を生成（Azure OpenAI利用）
if st.session_state.query_result is not None:
    if st.button("要約と結果の説明を生成"):
        with st.spinner("要約をと結果の説明を作成中..."):
            try:
                df_sample = st.session_state.query_result.head(8)
                sample_text = df_sample.to_csv(index=False)

                summarize_prompt_path = "prompts_summary/summarilze_results_prompt.md"    #フォルダ名称
                with open(summarize_prompt_path, "r", encoding="utf-8") as f:
                    summarize_prompt = f.read()

                summary_response = client.chat.completions.create(
                    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                    messages=[
                        {"role": "system", "content": "あなたはデータ要約アシスタントです。"},
                        {"role": "user", "content": f"ユーザーの質問: {user_question}"},
                        {"role": "user", "content": f"実行したSQL:\n{st.session_state.generated_sql}"},
                        {"role": "user", "content": f"CSVデータ:\n{sample_text}"},
                        {"role": "user", "content": summarize_prompt}
                    ]
                )
                st.session_state.summary = summary_response.choices[0].message.content.strip()
                st.markdown("#### 要約")
                st.write(st.session_state.summary)

                # チャット履歴に追加
                st.session_state.chat_history.append({
                    "question": user_question,
                    "generated_sql": st.session_state.generated_sql,
                    "result_sample": df_sample.to_dict(orient="records"),
                    "summary": st.session_state.summary
                })
            except Exception as e:
                st.error(f"要約と結果の説明の生成エラー：{e}")
