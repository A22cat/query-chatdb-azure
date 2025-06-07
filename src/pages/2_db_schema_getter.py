# DBスキーマ管理と質問の例
import streamlit as st
import pyodbc
import os
from dotenv import load_dotenv
from collections import defaultdict

# --- 初期設定 ---
load_dotenv()
# DB接続文字列はメインアプリと同じものを参照
from db_config import connection_string

PROMPTS_DIR = "src/prompts_nltosql" # ユーザー指定のパス

# --- データベース操作関数 ---

@st.cache_data(ttl=600) # 10分間キャッシュ
def get_all_table_names(_conn_str):
    """データベースからすべてのテーブル名を取得する"""
    tables = []
    try:
        with pyodbc.connect(_conn_str, timeout=5) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE' ORDER BY TABLE_NAME")
            tables = [row.TABLE_NAME for row in cursor.fetchall()]
    except Exception as e:
        st.error(f"テーブル一覧の取得中にエラーが発生しました: {e}")
    return tables

def get_primary_keys(_conn_str, table_name):
    """指定されたテーブルの主キー（PK）情報を取得する"""
    pk_columns = []
    query = """
    SELECT kcu.COLUMN_NAME
    FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS AS tc
    JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS kcu
        ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME AND tc.TABLE_SCHEMA = kcu.TABLE_SCHEMA AND tc.TABLE_NAME = kcu.TABLE_NAME
    WHERE tc.CONSTRAINT_TYPE = 'PRIMARY KEY' AND tc.TABLE_NAME = ?
    ORDER BY kcu.ORDINAL_POSITION;
    """
    try:
        with pyodbc.connect(_conn_str, timeout=5) as conn:
            cursor = conn.cursor()
            cursor.execute(query, table_name)
            pk_columns = [row.COLUMN_NAME for row in cursor.fetchall()]
    except Exception as e:
        st.warning(f"テーブル `{table_name}` の主キー情報取得中にエラーが発生しました: {e}")
    return pk_columns

def get_unique_keys(_conn_str, table_name):
    """指定されたテーブルの一意キー（UK）情報を取得する（複合キー対応）"""
    unique_constraints = defaultdict(list)
    query = """
    SELECT tc.CONSTRAINT_NAME, kcu.COLUMN_NAME
    FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS AS tc
    JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS kcu
        ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME AND tc.TABLE_SCHEMA = kcu.TABLE_SCHEMA AND tc.TABLE_NAME = kcu.TABLE_NAME
    WHERE tc.CONSTRAINT_TYPE = 'UNIQUE' AND tc.TABLE_NAME = ?
    ORDER BY tc.CONSTRAINT_NAME, kcu.ORDINAL_POSITION;
    """
    try:
        with pyodbc.connect(_conn_str, timeout=5) as conn:
            cursor = conn.cursor()
            cursor.execute(query, table_name)
            for row in cursor.fetchall():
                unique_constraints[row.CONSTRAINT_NAME].append(row.COLUMN_NAME)
    except Exception as e:
        st.warning(f"テーブル `{table_name}` の一意キー情報取得中にエラーが発生しました: {e}")
    return list(unique_constraints.values())

def get_foreign_keys(_conn_str, table_name):
    """指定されたテーブルの外部キー（FK）情報を取得する (SQL Server用)"""
    fk_constraints = defaultdict(lambda: {'references_table': None, 'fk_columns': [], 'references_columns': []})
    # INFORMATION_SCHEMAより信頼性が高いシステムビューを使用
    query = """
    SELECT
        fk.name AS constraint_name,
        OBJECT_NAME(fkc.parent_object_id) AS fk_table,
        fk_col.name AS fk_column,
        OBJECT_NAME(fkc.referenced_object_id) AS referenced_table,
        ref_col.name AS referenced_column
    FROM
        sys.foreign_keys AS fk
    INNER JOIN
        sys.foreign_key_columns AS fkc ON fk.object_id = fkc.constraint_object_id
    INNER JOIN
        sys.columns AS fk_col ON fkc.parent_object_id = fk_col.object_id AND fkc.parent_column_id = fk_col.column_id
    INNER JOIN
        sys.columns AS ref_col ON fkc.referenced_object_id = ref_col.object_id AND fkc.referenced_column_id = ref_col.column_id
    WHERE
        OBJECT_NAME(fk.parent_object_id) = ?
    ORDER BY
        fk.name, fkc.constraint_column_id
    """
    try:
        with pyodbc.connect(_conn_str, timeout=5) as conn:
            cursor = conn.cursor()
            cursor.execute(query, table_name)
            for row in cursor.fetchall():
                constraint_name = row.constraint_name
                fk_constraints[constraint_name]['references_table'] = row.referenced_table
                fk_constraints[constraint_name]['fk_columns'].append(row.fk_column)
                fk_constraints[constraint_name]['references_columns'].append(row.referenced_column)
    except Exception as e:
        st.warning(f"テーブル `{table_name}` の外部キー情報取得中にエラーが発生しました: {e}")
    return list(fk_constraints.values())

# get_column_japanese_names 関数の定義
@st.cache_data(ttl=600) # 必要に応じてキャッシュデコレータを追加
def get_column_japanese_names(_conn_str, table_name):
    """指定されたテーブルの各カラムの日本語名（MS_Description）を取得する"""
    japanese_names_map = {}
    query = """
    SELECT
        c.name AS column_name,
        CAST(ep.value AS NVARCHAR(MAX)) AS japanese_name
    FROM
        sys.tables t
    INNER JOIN
        sys.columns c ON t.object_id = c.object_id
    LEFT JOIN
        sys.extended_properties ep
        ON ep.major_id = t.object_id AND ep.minor_id = c.column_id AND ep.name = 'MS_Description'
    WHERE
        t.name = ?
    ORDER BY
        c.column_id;
    """
    try:
        with pyodbc.connect(_conn_str, timeout=5) as conn:
            cursor = conn.cursor()
            cursor.execute(query, table_name)
            for row in cursor.fetchall():
                japanese_names_map[row.column_name] = row.japanese_name
    except Exception as e:
        # st.info を使用するか、エラーレベルを調整してください
        st.info(f"テーブル `{table_name}` のカラム日本語名取得情報: MS_Descriptionが存在しないか、DBアクセス権限、またはクエリに問題がある可能性があります。物理名が使用されます。(詳細: {e})")
    return japanese_names_map

@st.cache_data(ttl=600)
def get_table_schema_as_markdown(_conn_str, table_name):
    """指定されたテーブルのスキーマ（カラム一覧, PK, UK, FK, 日本語名含む, 説明列は日本語名のみ）をMarkdown形式で取得する"""
    
    japanese_names_map = get_column_japanese_names(_conn_str, table_name)
    pk_columns_phys = get_primary_keys(_conn_str, table_name)

    #all_column_names_display_list = []
    column_details_for_md_table = [] # (表示用カラム名, データ型文字列, 説明文字列)
    
    try:
        with pyodbc.connect(_conn_str, timeout=5) as conn:
            cursor = conn.cursor()
            query_cols = "SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ? ORDER BY ORDINAL_POSITION"
            cursor.execute(query_cols, table_name)
            for row in cursor.fetchall():
                physical_name = row.COLUMN_NAME
                japanese_name = japanese_names_map.get(physical_name)
                
                # Markdownテーブルの「カラム名」列に表示する名前を物理名のみにする
                display_name_for_table_cell = physical_name 
                
                data_type_str = row.DATA_TYPE
                if row.CHARACTER_MAXIMUM_LENGTH:
                    data_type_str += f"({row.CHARACTER_MAXIMUM_LENGTH})"

                # 説明文字列の構築: 日本語名のみ、または空欄
                description_str = japanese_name if japanese_name else ""
                
                column_details_for_md_table.append((display_name_for_table_cell, data_type_str, description_str))
    except Exception as e:
        st.error(f"テーブル「{table_name}」のカラム情報取得中にエラーが発生しました: {e}")
        return None

    uk_constraints = get_unique_keys(_conn_str, table_name)
    fk_constraints = get_foreign_keys(_conn_str, table_name)

    schema_md = f"### テーブル名: `{table_name}`\n\n"
    
    #- **カラム一覧の表示は重複しているため削除
    #if all_column_names_display_list:
    #    schema_md += f"- **カラム一覧**: `{', '.join(all_column_names_display_list)}`\n"

    if pk_columns_phys:
        pk_display_list = [f"{japanese_names_map.get(col, col)} ({col})" if japanese_names_map.get(col) else col for col in pk_columns_phys]
        schema_md += f"- **主キー（PK）**: `{', '.join(pk_display_list)}`\n"
    if uk_constraints:
        for uk_physical_cols in uk_constraints:
            uk_display_list = [f"{japanese_names_map.get(col, col)} ({col})" if japanese_names_map.get(col) else col for col in uk_physical_cols]
            schema_md += f"- **一意キー（UK）**: `{', '.join(uk_display_list)}`\n"
    if fk_constraints:
        for fk in fk_constraints:
            fk_display_cols = [f"{japanese_names_map.get(col, col)} ({col})" if japanese_names_map.get(col) else col for col in fk['fk_columns']]
            ref_table_physical_name = fk['references_table']
            # 参照先テーブルの日本語名マップ取得は高コストになる可能性があるため、元のコードのままとしています。
            # 必要に応じて、この部分の最適化も検討できます（例：一度取得したマップを再利用する等）。
            ref_japanese_names_map = get_column_japanese_names(_conn_str, ref_table_physical_name)
            ref_display_cols = [f"{ref_japanese_names_map.get(col, col)} ({col})" if ref_japanese_names_map.get(col) else col for col in fk['references_columns']]
            fk_cols_str = ', '.join(fk_display_cols)
            ref_cols_str = ', '.join(ref_display_cols)
            schema_md += f"- **外部キー（FK）**: `({fk_cols_str})` -> `{ref_table_physical_name}({ref_cols_str})`\n"
    
    #if all_column_names_display_list or pk_columns_phys or uk_constraints or fk_constraints:
    if pk_columns_phys or uk_constraints or fk_constraints: # 何かしらのキー情報があれば改行
        schema_md += "\n"

    schema_md += "| カラム名 | データ型 | 説明 |\n"
    schema_md += "|:---|:---|:---|\n"
    for display_col_name, data_type_str, desc_str in column_details_for_md_table:
        schema_md += f"| {display_col_name} | {data_type_str} | {desc_str} |\n"
        
    return schema_md

def save_schema_to_md(table_name, markdown_content):
    """スキーマ情報をMarkdownファイルとして保存する"""
    try:
        os.makedirs(PROMPTS_DIR, exist_ok=True)
        file_path = os.path.join(PROMPTS_DIR, f"{table_name}_table_definition.md")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        return file_path
    except Exception as e:
        st.error(f"ファイル保存中にエラーが発生しました: {e}")
        return None

# --- UIレイアウト ---
st.set_page_config(page_title="プロンプト管理", page_icon="🛠️", layout="wide")
st.title("🛠️ DBスキーマ管理と質問例")
st.caption("データベースのテーブルスキーマを管理し、自然言語での質問プロンプトの精度を向上させます。")

if 'prompt_mgmt_conn' not in st.session_state:
    st.session_state.prompt_mgmt_conn = None

with st.container(border=True):
    st.header("STEP 1: データベースに接続")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("DB接続", disabled=(st.session_state.prompt_mgmt_conn is not None)):
            try:
                conn = pyodbc.connect(connection_string, timeout=5)
                st.session_state.prompt_mgmt_conn = conn
                st.toast("DBに接続しました。")
                st.rerun()
            except Exception as e:
                st.error(f"接続エラー：{e}")
    with col2:
        if st.button("DB切断", disabled=(st.session_state.prompt_mgmt_conn is None)):
            if st.session_state.prompt_mgmt_conn:
                st.session_state.prompt_mgmt_conn.close()
                st.session_state.prompt_mgmt_conn = None
                st.toast("DB接続を切断しました。")
                st.rerun()
    if st.session_state.prompt_mgmt_conn:
        st.success("現在DBに接続中です。STEP 2に進んでください。")
    else:
        st.info("DBに接続されていません。")

with st.container(border=True):
    st.header("STEP 2: スキーマ定義ファイルを更新")
    if st.session_state.prompt_mgmt_conn:
        st.markdown("""
        データベースから最新のテーブル構造（カラム一覧、主キー、一意キー、外部キー、カラムの日本語名など）を取得し、
        自然言語での質問応答（NL-to-SQL）に使用するスキーマ定義ファイル（.md）を生成・更新します。
        カラムの日本語名は、データベースの拡張プロパティ（MS_Description）に設定されている場合、取得・表示されます。
        """)
        all_tables = get_all_table_names(connection_string)
        if not all_tables:
            st.warning("データベースからテーブルを取得できませんでした。")
        else:
            default_selection = [all_tables[0]] if all_tables else []
            selected_tables = st.multiselect(
                "スキーマを取得したいテーブルを選択してください（複数選択可）:",
                options=all_tables,
                default=default_selection # 修正: defaultを最初の1テーブルのみに変更
            )
            #    default=all_tables            )
            if st.button("選択したテーブルの定義ファイルを更新", type="primary"):
                if not selected_tables:
                    st.warning("テーブルが選択されていません。")
                else:
                    with st.spinner("スキーマ情報を取得し、ファイルを保存しています..."):
                        success_count = 0
                        error_count = 0
                        log_expander = st.expander("処理ログ", expanded=True)
                        for table in selected_tables:
                            markdown_content = get_table_schema_as_markdown(connection_string, table)
                            if markdown_content:
                                file_path = save_schema_to_md(table, markdown_content)
                                if file_path:
                                    log_expander.success(f"✅ `{table}` の定義ファイルを保存しました: `{file_path}`")
                                    success_count += 1
                                else:
                                    log_expander.error(f"❌ `{table}` のファイル保存に失敗しました。")
                                    error_count += 1
                            else:
                                error_count += 1
                        st.toast(f"処理完了： {success_count}件成功、{error_count}件失敗しました。")
    else:
        st.warning("この機能を利用するには、STEP 1でデータベースに接続してください。")

with st.expander("質問例を見る（プロンプト作成のヒント）", expanded=False):
    st.header("質問プロンプトの例")
    st.markdown("これらの例を参考に、メイン画面で自由に質問してみてください。")
    st.subheader("📊 売上・販売に関する質問")
    st.code("""
- 各製品の総売上金額を計算して
- 顧客ID「4」の今までの購入履歴を表示して。
- 最も購入額が多い優良顧客は誰？
- 直近に販売開始した製品名を3つ教えて。
- 昨年(XXXX年)と比較して、今年(XXXX年)の月別売上はどう推移している？
    """, language="markdown")
    st.subheader("📦 在庫・倉庫に関する質問")
    st.code("""
- 「東京第一倉庫」からどこの倉庫へ在庫が移動したかを教えて。
- 「東京第一倉庫」から「札幌倉庫」への在庫移動履歴を教えて。
    """, language="markdown")
    st.subheader("👤 従業員・顧客に関する質問")
    st.code("""
- 営業部に所属している従業員の一覧を見せて。
- 顧客マスタに登録されている都道府県別の顧客数を教えて。
- 最近登録された新規顧客を5名表示して。
    """, language="markdown")
    st.subheader("📘 製品・カタログに関する質問")
    st.code("""
- 各カタログに何種類の製品が掲載されているか、カタログ名と製品数を一覧で教えてください。
- カタログに掲載されている全製品の、過去1年間の総売上個数を教えてください
- カタログ名「2025年 春カタログ」に掲載されている製品のリストを教えて。
- 単価が5,000円以上の製品をすべて表示して。
- 「ボールペンセット」という製品がどのカタログに載っているか調べて。
    """, language="markdown")