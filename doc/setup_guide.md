# Qnect セットアップガイド

このガイドでは、Qnectアプリケーションをローカルで実行し、Azureにデプロイするために必要な手順を説明します。

## 1. 前提条件

- [Azureアカウント](https://azure.microsoft.com/ja-jp/free/)
- [Azure CLI](https://docs.microsoft.com/ja-jp/cli/azure/install-azure-cli)
- [Python 3.10 以降](https://www.python.org/downloads/)
- [Visual Studio Code](https://code.visualstudio.com/)
  - [Azure App Service 拡張機能](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-azureappservice)
  - [Python 拡張機能](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [Microsoft ODBC Driver 18 for SQL Server](https://learn.microsoft.com/ja-jp/sql/connect/odbc/download-odbc-driver-for-sql-server) (Windows/Linux/macOS)
- (データインポート用) [Microsoft ODBC Driver 17 for SQL Server](https://learn.microsoft.com/ja-jp/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver16) (Windows/Linux/macOS)
- (データインポート用) [Microsoft Command Line Utilities 15 for SQL Server](https://learn.microsoft.com/ja-jp/sql/tools/bcp-utility?view=sql-server-ver15&tabs=windows#windows) (bcpコマンド)

## 2. データベースのセットアップ

### a. テーブルの作成

Azure Data StudioやSSMS、VSCodeのSQL拡張機能などを使って、作成したAzure SQL Databaseに接続します。
`data/DB/create/` フォルダ内のSQLファイルを `01_` から `10_` の順番で実行し、テーブルを作成します。

### b. csvデータのインポート (bcpコマンド)

`bcp`コマンドラインユーティリティを使って、ローカルのcsvファイルをAzure SQL Databaseにインポートします。

1.  `data/DB/csv/` 内のcsvファイルの文字コードが`UTF-16LE`であることを確認してください。
2.  コマンドプロンプトやターミナルを開き、以下のコマンド例を参考に実行します。

```bash
# bcpコマンドの実行例 (employees_mstテーブルの場合)
# 各パラメータはご自身の環境に合わせて変更してください。
bcp [YourDatabaseName].[dbo].[employees_mst] in "C:\path\to\project\data\DB\csv\03_employees_mst_Results.csv" -S <your-sql-server-name>.database.windows.net -U <your-sql-admin-username> -P <your-sql-admin-password> -w -t "," -F 2

・-w: UTF-16データとして扱います。
・-t ",": フィールドの区切り文字をカンマに指定します。
・-F 2: 2行目からインポートを開始します（ヘッダー行をスキップ）。
これを10個のテーブルすべてに対して実行します。
```

## 3. Azureリソースの準備

Azureポータルにログインし、以下のリソースを作成します。リソース名は任意ですが、後で環境変数に設定するため控えておいてください。

### a. Azure OpenAI Service

1.  Azureポータルで「Azure OpenAI」を検索し、「作成」を選択します。
2.  サブスクリプション、リソースグループ、リージョン、一意の名前を入力します。
3.  価格レベルは「Standard S0」を選択します。
4.  作成後、リソースに移動し、「モデルのデプロイ」メニューから以下の2つのモデルをデプロイします。
    -   **Chatモデル**: `gpt-4o` または `gpt-4o-mini`
    -   **Embeddingモデル**: `text-embedding-ada-002`または `text-embedding-3-small`
    -   **開発環境では、コストとパフォーマンスとのバランスを考慮すると `gpt-4o-mini` や `text-embedding-3-small` の選択肢を検討することができます。
5.  「キーとエンドポイント」から**エンドポイント**と**キー1**をコピーします。

### b. Azure SQL Database

1.  Azureポータルで「Azure SQL」を検索し、「作成」を選択します。
2.  SQLデータベースの「作成」を選びます。
3.  リソースグループを選択し、データベース名を入力します。
4.  「サーバー」で「新規作成」を選び、サーバー名、場所、**SQL認証**を選択して管理者ログインとパスワードを設定します。
5.  「ネットワーク」タブで、「接続ポリシー」を「既定」のまま、「接続の暗号化」を「必須」に設定します。
6.  「ファイアウォール規則」で「Azureサービスおよびリソースにこのサーバーへのアクセスを許可します」を「はい」に、「現在のクライアントIPアドレスを追加します」を「はい」に設定します。
7.  作成後、サーバー名、データベース名、管理者ログイン、パスワードをコピーします。

### c. Azure Cosmos DB

1.  Azureポータルで「Azure Cosmos DB」を検索し、「作成」を選択します。
2.  「Azure Cosmos DB for NoSQL」の「作成」を選びます。
3.  リソースグループ、アカウント名、場所などを設定します。
4.  作成後、リソースに移動し、「データエクスプローラー」から新しいデータベースとコンテナを作成します。
    -   データベースID: `QnectDB`
    -   コンテナID: `ChatHistory`
    -   パーティションキー: `/sessionId`
5.  「キー」メニューから**URI**と**プライマリキー**をコピーします。

### d. Azure AI Search

1.  Azureポータルで「Azure AI Search」を検索し、「作成」を選択します。
2.  リソースグループ、サービス名、場所を選択します。
3.  価格レベルは、開発・テスト用途であれば「Basic」または「Free」を選択します。（PoC用途ではFreeで十分です）
4.  作成後、リソースに移動し、「キー」メニューから**URL**と**管理者キー**をコピーします。

### e. Azure App Service

1.  Azureポータルで「App Service」を検索し、「作成」>「Webアプリ」を選択します。
2.  サブスクリプション、リソースグループを選択します。
3.  インスタンスの詳細：
    -   名前: グローバルに一意な名前（例: `qnect-app`)
    -   発行: `コード`
    -   ランタイム スタック: `Python 3.11` [Python(準備のセクションでインストールしたものと同じバージョンまたは一番近いバージョン)] を選択します。
    -   オペレーティング システム: `Linux` (Pythonは2025/06現在[Linux]のみサポート)
    -   地域: 地域を選択
4.  「App Service プラン」を選択または新規作成します。
5.  作成後、リソースに移動します。この時点ではデプロイは不要です。


## 4. ローカルでの実行
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

