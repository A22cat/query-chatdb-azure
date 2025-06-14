## テーマ：生成AIを活用したデータベースとのチャットシステムの構築

## 1. ソリューション概要

- **ソリューション名**：QueryChatDbAzure(対話型DBクエリ支援システム)
- **プロダクト名**：Qnect(キュネクト)  
→ Query(クエリー) + Connection(接続) の略語。

Azureクラウド技術と生成AIを活用し、自然言語でのデータベース操作を可能にするチャットシステムです。このシステムの最大の特長は、ITスキルがなくても誰でもビジネスデータにアクセスでき、迅速な意思決定や業務改善を実現できる点です。ユーザーが自然言語で質問すると、Azure OpenAIがその内容を解析し、適切なSQL文を自動生成してAzure SQL Databaseから業務データを取得し、その結果を分かりやすく説明します。これにより、専門知識がなくても直感的にデータ活用が可能となります。


## 2. 解決したい課題

企業内の業務データベースは膨大な情報を有していますが、専門知識がないと、その情報を十分に引き出して活用することが困難です。その結果、必要なデータを迅速に取得できない、日常的な意思決定や問い合わせ対応のたびにIT部門へ依頼が発生するなど、業務のタイムロスが生じてしまいます。こうした状況を改善し、誰もが簡単に業務データへアクセスできる環境の実現が求められています。


## 3. 主な機能

- 自然言語からのクエリ生成・実行(SQL自動生成)
- クエリ結果の要約・分析
- データアクセス・変更を防ぐためのセキュリティ機能
- 会話レスポンス内の機密情報のマスキング
- 対話履歴を基にした文脈保持
- ユーザーによるクエリ修正指示への柔軟な対応
- DBからDBスキーマ(テーブル構造)を取得してAzure OpenAIに提示可能
- 埋込用ベクトル生成＋類似検索(Azure OpenAI Embedding + Azure AI Search ベクトルインデックス)
- キーワード検索(完全一致)(Azure Cosmos DB)
- Azure OpenAIへの1回あたりの送信Token数と受信Token数を制御
- 「新しい会話を始める」ボタンで、過去の文脈を保持せずに対話可能


## 4. 使用技術(Tech Stack)
- Azure OpenAI (Chat用モデル)[gpt-4o または gpt-4o mini]
- Azure SQL Database
- Python
- Streamlit (UI)
- Azure OpenAI (Embedding用モデル)[text-embedding-ada-002 または text-embedding-3-small]
- Azure AI Search
- Azure Cosmos DB
- Azure App Service


## 5. スケーラビリティ設計
- 本システムでは、Azure SQL Database の情報スキーマを参照し、テーブル構造の変化に応じて動的にテーブル定義を取得・反映可能とする設計を採用しています。これによりスキーマ変更にも柔軟に対応し、運用時の拡張性と保守性を両立しています。
- Azure OpenAIへの1回あたりの送信Token数と受信Token数を制御し、大規模DBに対応(機能搭載)
- Azure OpenAIのChatモデル（gpt-4、gpt-4oなど）の応答品質と処理性能を比較検証でき、トークン制限や処理速度に応じて動的にモデルを選択可能な構成を設計しています。今後のAPIアップデートにも柔軟に対応できる拡張性を備えています。
- 本システムは、Azureのサービス（Azure OpenAI, Azure SQL Database, Azure AI Search, Azure Cosmos DB, Azure App Service）を採用しています。これらのサービスはアクセス数やデータ量の増加に応じてシームレスにスケールアップ/ダウンが可能です。これにより、初期はスモールスタートし、ビジネスの成長に合わせて柔軟かつコスト効率よくシステムを拡張していくことができます。


<br>■今後のスケーラビリティ向上策<br>

- 今後は、テーブル数の増加やスキーマ構成が複雑になった場合にも効率的に対応できるよう、LangChain を使用してユーザークエリから関連するテーブルを事前に推定し、必要なスキーマ情報のみを抽出する仕組みを導入予定です。これにより、不要な情報の送信を抑えつつ、該当テーブルの詳細情報を適切に送信し、高精度なSQLクエリの生成を実現する機能拡充を計画しています。
- ユーザーごとのアクセス権限設定
- テーブル構造のキャッシュ保存と更新頻度制御
- チャット履歴のストレージ保存と分析機能


## 6. システム構成

architecture_diagram_Qnect.pdf


## 7. 想定されるユースケースと効果

| ユースケース                 | 効果                                                              |
|-----------------------------|-------------------------------------------------------------------|
| 営業担当者の在庫確認         | 顧客からの問い合わせに対し、チャット形式で数秒で販売データや在庫状況を確認。時間短縮と顧客対応力を向上。      |
| 商品データの傾向分析         | ノーコードで売れ筋商品や顧客情報を把握。データに基づくマーケティング施策を迅速に立案可能。                    |
| 経営者の意思決定支援         | 複数データベースを横断した要約情報を自然言語で瞬時に取得。膨大な分析時間を削減し、迅速かつ的確な経営判断を支援 |



## 8. 拡張構想

- DBスキーマの詳細な情報を活用し、Token数を最適化する。
- パフォーマンスの高いクエリを生成するため、取り扱うデータ範囲を制限する。
- 会話の流れの中で、適切にコンテキストとメモリを引き渡す。
- SQLAlchemyなどのORMを利用し、テーブルメタデータに基づくルールベースのバリデーションを実施する。



## 9. GitHubリポジトリのURL

- メインリポジトリ：
https://github.com/A22cat

- 本課題実装のリポジトリ：
https://github.com/A22cat/query-chatdb-azure
