# Qnect (キュネクト) - 対話型DBクエリ支援システム

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.33-ff69b4.svg)](https://streamlit.io/)
[![Azure](https://img.shields.io/badge/Azure-Services-blue.svg)](https://azure.microsoft.com/)

**Qnect** は、Azureクラウド技術と生成AIを活用し、自然言語でのデータベース操作を可能にするチャットシステムです。専門知識がなくても、誰でも直感的にビジネスデータにアクセスし、迅速な意思決定を支援します。

## ✨ 主な機能

- **自然言語クエリ**: 「各製品の総売上金額を計算して」のような日常的な言葉でDBに質問できます。
- **SQL自動生成と実行**: Azure OpenAIが質問を解析し、安全なSQLクエリを生成してAzure SQL Databaseで実行します。
- **結果の要約と対話**: クエリ結果を平易な日本語で要約し、追加の質問にも文脈を保って応答します。
- **永続的な会話履歴**: Azure Cosmos DBに会話履歴を保存し、セッションをまたいで文脈を維持します。
- **データマスキング**: 個人情報などの機密データは自動的にマスクされ、安全なデータアクセスを実現します。

## 🚀 技術スタック

- **UI**: Streamlit
- **バックエンド/オーケストレーション**: Python, LangChain
- **AIモデル**: Azure OpenAI [gpt-4o または gpt-4o mini][text-embedding-ada-002 または text-embedding-3-small]
- **データベース**: Azure SQL Database (構造化データ), Azure Cosmos DB (会話履歴)
- **検索**: Azure AI Search (類似質問検索)
- **ホスティング**: Azure App Service

## 📂 フォルダ構成

フォルダ構成は `directory_structure.txt` を参照してください。

## 🛠️ セットアップと実行

詳細な手順は `doc/setup_guide.md` を参照してください。

### ローカルでの実行

1.  `.env` ファイルを作成し、Azureサービスの資格情報を設定します。
2.  `pip install -r requirements.txt` を実行します。
3.  `streamlit run src/main_db_chat_ai.py` を実行します。

### Azureへのデプロイ

`doc/setup_guide.md` の指示に従い、Azure App Serviceにデプロイします。

## 使い方

アプリケーションを開き、チャット入力欄にデータベースに関する質問を日本語で入力してください。AIが応答し、必要に応じてデータベースから情報を取得し要約します。
新しい会話を始めたい場合は、サイドバーの「新しい会話を始める」ボタンをクリックしてください。