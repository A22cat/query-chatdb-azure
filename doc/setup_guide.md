# Qnect (キュネクト) セットアップガイド

本ガイドでは、Qnec（キュネクト）のセットアップに関する設定、ローカル環境での実行手順、および、Azure App Serviceへのデプロイ手順の概要を説明します。

## 1. 前提条件

- [Azureアカウント](https://azure.microsoft.com/ja-jp/free/)
- [Azure CLI](https://docs.microsoft.com/ja-jp/cli/azure/install-azure-cli)
- [Python 3.10 以降](https://www.python.org/downloads/)
- [Visual Studio Code](https://code.visualstudio.com/)
  - [Azure App Service 拡張機能](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-azureappservice)
  - [Python 拡張機能](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [Microsoft ODBC Driver 18 for SQL Server](https://learn.microsoft.com/ja-jp/sql/connect/odbc/download-odbc-driver-for-sql-server) (Windows/Linux/macOS)
- (サンプルデータインポート用) [Microsoft ODBC Driver 17 for SQL Server](https://learn.microsoft.com/ja-jp/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver16) (Windows/Linux/macOS)
- (サンプルデータインポート用) [Microsoft Command Line Utilities 15 for SQL Server](https://learn.microsoft.com/ja-jp/sql/tools/bcp-utility?view=sql-server-ver15&tabs=windows#windows) (bcpコマンド)


## 2. Azureリソースの準備

Azureポータルにログインし、以下のリソースを作成します。リソース名は任意ですが、後で環境変数に設定するため控えておいてください。

### a. Azure OpenAI Service

1.  Azureポータルで「Azure OpenAI」を検索し、「作成」を選択します。
2.  サブスクリプション、リソースグループ、リージョン、一意の名前を入力します。
3.  価格レベルは「Standard S0」を選択します。
4.  作成後、リソースに移動し、「モデルのデプロイ」メニューから以下の2つのモデルをデプロイします。
    -   **Chatモデル**: `gpt-4o` または `gpt-4o-mini`など
    -   **Embeddingモデル**: `text-embedding-ada-002`または `text-embedding-3-small`など
    -   **開発環境では、コストを考慮すると `gpt-4o-mini` や `text-embedding-3-small` の選択肢を検討することができます。
5.  「キーとエンドポイント」から**エンドポイント**と**キー1**をコピーします。

### b. Azure SQL Database

1.  Azureポータルで「Azure SQL」を検索し、「作成」を選択します。
2.  SQLデータベースの「作成」を選びます。
3.  リソースグループを選択し、データベース名を入力します。
4.  「サーバー」で「新規作成」を選び、サーバー名、場所、**SQL認証**(VSCodeで接続するため、「SQL と Microsoft Entra 認証の両方を使用する」または 「SQL認証」)を選択して管理者ログインとパスワードを設定し、メモします。
5.  バックアップ ストレージの冗長性：任意 (ローカル冗長バックアップ ストレージはコストを抑えることができます。)
5.  「ネットワーク」タブで、接続方法を「パブリックエンドポイント」、接続ポリシーを「既定」に設定します。
6.  「ファイアウォール規則」で「Azureサービスおよびリソースにこのサーバーへのアクセスを許可します」を「はい」に、「現在のクライアントIPアドレスを追加します」を「はい」に設定します。
7.  作成後、サーバー名、データベース名、管理者ログイン、パスワードを記録します。

### c. Azure Cosmos DB

1.  Azureポータルで「Azure Cosmos DB」を検索し、「作成」を選択します。
2.  「Azure Cosmos DB for NoSQL」の「create(作成)」を選択します。
3.  リソースグループ、アカウント名、場所などを設定します。
4.  作成後、リソースに移動し、「データエクスプローラー」から新しいデータベースとコンテナを作成します。
    「データエクスプローラー」 > 「新しいデータベース作成」(=「+New Database」)
    -   データベース名:例 `qnectdb`
5.  作成済みのデータベースの「…」ボタンを選択>「+ New Container」(=「新しいコンテナー」)を選択します。
	以下の情報を入力して「OK」で作成します。
    -   パーティションキー：例 `/chatId`
    -   Database id：Use existing：例 `qnectdb`(=データベース ID	作成したデータベースを選択（例：`qnectdb`）)
    -   コンテナー ID：例：`chat-logs`	コンテナ名。課題ごとに用途別で
    -   Indexing Mode：Automatic
    -   (途中で変更不可)パーティション キー：例 `/chatId`	IDまたは高頻度アクセスのキーにするのが一般的
    -   Dedicated Throughput(=Provision dedicated throughput for this container)：OFF（チェックしない）  
        スループットのチェック不要、すでに データベース共有スループットで作成済みのため、このチェックは外す（データベース側に任せる）
    -   ユニークキー：任意(今回はなし)
    -   Enable analytical store capability to perform near real-time analytics on your operational data, without impacting the performance of transactional workloads. 
        分析ストア機能を有効にして、トランザクション ワークロードのパフォーマンスに影響を与えることなく、運用データに対してほぼリアルタイムの分析を実行します。
    →「分析ストア機能（Analytical Store）を有効にするかどうか」の設定について、現状および目的を踏まえたおすすめは**「OFF（無効）」**です。理由：無料枠の維持・分析用途が現時点でないため。
6.  「キー」メニューから**URI**と**プライマリキー**を記録します。
    ```
    ●作成するコンテナ一覧
    - コンテナ ID：`chat-logs`、用途：質問履歴やチャット履歴、パーティションキー(任意)：`/chatId`
    ```
    #### 注意点
    - **パーティションキーは後から変更できません。最初に慎重に設計してください。**
    - **Database Throughput**  
      スループット設定画面にて「**スループットをこのコンテナーにプロビジョニングする**」のチェックは **外してください**。  
      ※チェックを入れると、そのコンテナーに対して専用スループットが割り当てられ、**個別課金の対象**になります。


### d. Azure AI Search

1.  Azureポータルで「Azure AI Search」を検索し、「作成」を選択します。
2.  リソースグループ、サービス名、場所を選択します。
3.  価格レベルは、開発・テスト用途であれば「Basic」または「Free」を選択します。（参考：今回のPoC用途にはFreeプランで充分です）
4.  作成後、リソースに移動し、「キー」メニューから**URL**と**管理者キー**をコピーします。
5.  インデックス、フィールド、ベクトルフィールドの詳細な設定方法は `azure_ai_search_setup.md` を参照してください。

### e. Azure App Service

1.  Azureポータルで「App Service」を検索し、「作成」>「Webアプリ」を選択します。
2.  サブスクリプション、リソースグループを選択します。
3.  インスタンスの詳細：
    -   名前: グローバルに一意な名前 (例: `qnect-app`)
    -   発行: `コード`
    -   ランタイム スタック: `Python 3.11` [Python(準備のセクションでインストールしたものと同じバージョンまたは一番近いバージョン)] を選択します。
    -   オペレーティング システム: `Linux` (Pythonは2025/06現在[Linux]のみサポート)
    -   地域: 地域を選択
4.  「App Service プラン」を選択または新規作成します。
5.  作成後、リソースに移動します。この時点ではデプロイは不要です。


## 3. データベースのセットアップ

### a. テーブルの作成

Azure Data StudioやSSMS、VSCodeのSQL拡張機能などを使って、作成したAzure SQL Databaseに接続します。
`data/DB/create/` フォルダ内のSQLファイルを `01_` から `10_` の順番で実行し、テーブルを作成します。

### b.(任意)(サンプルのCSVを使用する場合) CSVデータのインポート (bcpコマンド)

`bcp`コマンドラインユーティリティを使って、ローカルのCSVファイルをAzure SQL Databaseにインポートします。

1.  `data/DB/csv/` 内のCSVファイルの文字コードが`UTF-16LE`であることを確認してください。
2.  コマンドプロンプトやターミナルを開き、以下のコマンド例を参考に実行します。

```bash
# bcpコマンドの実行例 (employees_mstテーブルの場合)
# 各パラメータはご自身の環境に合わせて変更してください。

参考：
bcp [データベース名].[スキーマ名].[テーブル名] in "C:\path\to\file.csv" -w -t"," -S [サーバー名].database.windows.net -U [ユーザー名] -P [パスワード] -F 2

bcp [YourDatabaseName].[dbo].[employees_mst] in "C:\path\to\project\data\DB\csv\03_employees_mst_Results.csv" -w -C 65001 -t"," -S [YourServerName].database.windows.net -U [YourUsername] -P [YourPassword] -F 2

・-w: BOM付きUTF-16 LEが一般的に推奨
・-t ",": フィールドの区切り文字をカンマに指定します。
・-F 2: 2行目からインポートを開始します（ヘッダー行をスキップ）。
これを10個のテーブルすべてに対して実行します。
```

## 4. ローカル環境での実行
1. GitHub.com からローカルコンピューターにリポジトリをクローンします。
2. プロジェクトのルートディレクトリで、ターミナルを開きます。
3. .env.example をコピーして `.env` という名前のファイルを作成します。Azureリソースの作成時に控えた各サービスのキーとエンドポイントをすべて設定します。
必要なPythonパッケージをインストールします。

Bash
```
pip install -r requirements.txt
```

Streamlitアプリを起動します。

Bash
```
streamlit run src/main_db_chat_ai.py
```
ブラウザで http://localhost:8501 が開き、アプリケーションが表示されます。


## 5. VSCodeを使用したAzure App Serviceへのデプロイ
VSCodeのAzure拡張機能を使って、アプリケーションをデプロイします。

1. Azure ポータルでApp Service を開き、左側のメニューから 「設定」 >「環境変数」を選択し、[+追加]からアプリケーション設定にenvファイルの内容を一つずつ環境変数として追加します。
    - 名前：環境変数のキー（例：AZURE_OPENAI_ENDPOINT）
    - 値：環境変数の値 (例：https://your-resource.openai.azure.com/)
2. 左側のメニューから 「構成」(Configration) > 全般設定 を選択し、「スタートアップコマンド」に以下を設定して保存します。

```
python -m streamlit run src/main_db_chat_ai.py --server.port 8000 --server.address 0.0.0.0
```

3. 次にVSCodeで「ファイル」>「フォルダーを開く...」でプロジェクトフォルダ（query-chatdb-azure）を選択し、開きます。
4. 左のアクティビティバーからAzureアイコンを選択し、Azureアカウントにサインインします。
5. Azure拡張機能パネルに戻り、リソースの一覧からデプロイ先のApp Serviceを探します。
対象のApp ServiceはStoppedではなく通常は起動したままデプロイします。
6. 対象のApp Serviceを右クリックし、「Deploy to Web App...」を選択します。
7. 「Would you like to update your workspace configuration to run build commands on the target server?This should improve deployment performance.」の確認メッセージが表示されたら、「Yes」を選択します。「Yes」を選ぶと、今後同じワークスペースからデプロイする際に、ビルドコマンド（依存パッケージのインストールなど）がAzure側で実行されるように設定され、デプロイが効率化されます。この設定は .vscode/settings.json に保存され、プロジェクト単位で適用されます。後から変更したい場合も、ワークスペース設定で編集できます。
8. 「Are you sure you want to deploy to "<App Service名>"? This will overwrite any previous deplyment and cannot be undone.」の確認メッセージが表示されたら、「Deploy」を選択します。現在のWebアプリに新しいコードを上書いてデプロイします。
8. デプロイが完了すると通知が表示されます。その後、App ServiceのURLにアクセスして、アプリケーションが正しく動作することを確認します。