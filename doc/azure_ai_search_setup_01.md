## Azure AI Searchのインデックスとフィールドの設定

1.  Azureポータルで「Azure AI Search」を検索し、「AI Search」を選択します。
2.  作成したサービス名(＝名前)を選択します。
3.  左メニューから「インデックス」を選択し、インデックスを作成 (例：`chat-history-index`)します。
4.  作成したインデックス (例：`chat-history-index`)を選択し、フィールド(タブ)の「+フィールドの追加」を選択します。
5.  右側のサイドバーのインデックスフィールドの設定画面で次に必要なフィールド名（`id`, `question`, `generated_sql`, `summary`, `timestamp`）を設定します。
6.  「保存」ボタンを選択します。

**Azure AI Search インデックス名**：`chat-history-index`

| フィールド名       | 種類 (Data Type)          | 取得可能<br>(Retrievable) | フィルター<br>可能<br>(Filterable) | 並べ替え<br>可能<br>(Sortable) | Facetable      | 検索可能<br>(Searchable) | 検索可能の<br>“アナライザー”         | その他               | 備考                  |
|--------------------|----------------------------|-----------------------------|------------------------------------|-------------------------------|----------------|---------------------------|--------------------------------------|----------------------|----------------------|
| id                 | Edm.String                 | 〇                          | 〇                                 | 〇                            | 〇              | ✕                         |                                      |                      |               |
| question           | Edm.String                 | 〇                          | 〇                                 | 〇                            | ✕ (任意)        | 〇                         | 日本語-Microsoft                    |                      |              |
| generated_sql      | Edm.String                 | 〇                          | 〇                                 | 〇 (任意)                     | ✕ (任意)        | 〇 (任意)                 | Standard-Lucene（デフォルト）       |                      |               |
| summary            | Edm.String                 | 〇                          | 〇 (任意)                          | 〇 (任意)                     | ✕ (任意)        | 〇                         | 日本語-Microsoft                    |                      |              |
| timestamp          | Edm.DateTimeOffset         | 〇                          | 〇                                 | 〇                            | ✕ (任意)        | ー                         |                                      |                      |              |
| summary_vector     | Collection(Edm.Single)     | 〇                          | ー                                 | ー                            | ー              | 〇                         |                                      | ディメンション：1536 | ※1でベクトルプロファイルの設定を確認 |

## ※1：ベクトルフィールド（`summary_vector`）に「リスト形式の数値配列」を設定し、ベクトルプロファイルを構成する詳細な手順。

- フィールド名：`summary_vector`
- 種類：`Collection(Edm.Single)`

## ▼ベクトルフィールドの作成手順
1.  Azureポータルで「Azure AI Search」を検索し、「AI Search」を選択します。
2.  左メニューから作成した「インデックス」(例：`chat-history-index`)を選択します。
3.  フィールド(タブ)の追加画面で、以下の設定を行います。


### ▼ベクトルフィールド設定例

| 項目                     | 設定値例／説明                                                                 |
|--------------------------|------------------------------------------------------------------------------|
| フィールド名             | `summary_vector`                                                             |
| 種類                     | `Collection(Edm.Single)`                                                     |
| 取得可能                 | `true`（検索結果で取得できるようにする）                                      |
| 検索可能                 | `true`（ベクトル検索対象とする）                                              |
| フィルター可能           | `false`（ベクトルフィールドは不可）                                           |
| 並べ替え可能             | `false`（ベクトルフィールドは不可）                                           |
| ファセット可能           | `false`（ベクトルフィールドは不可）                                           |
| ディメンション           | `1536`（例: OpenAIの `text-embedding-ada-002` や `text-embedding-3-small` の次元数）は1536 |
| ベクトル(検索)プロファイル | 後述の「ベクトル(検索)プロファイル」で作成した名称（例: `my-vector-profile`）      |


### ▼ベクトル検索プロファイルの設定方法
4. 右サイドバーのインデックスフィールド画面でベクトル検索プロファイルの「作成」ボタンを選択
5. ベクトルプロファイルの名前：`my-vector-profile-01`（例: my-vector-profile、vector-profile-1748932868930）を設定
6. 「新しいベクターアルゴリズムの作成」を選択
7. ベクトルアルゴリズム画面で次の項目を設定

```
例:アルゴリズムのパラメータを設定（デフォルト値でも可）
ベクトルアルゴリズム
アルゴリズム名:`hnsw-01` (例：hnsw-1、vector-config-1748933060962）
種類: hnsw

Kindパラメーター
- m(双方向リンク数(m)): 4
- efConstruction: 400
- efSearch: 500
- metric(類似性メトリック): cosine
```

8.アルゴリズムを選択：hnsw-01（例: HNSW）
9.プロファイルを保存
10.「保存」ボタンを選択。


ベクトル化：ベクトル化の設定なし()
圧縮：圧縮構成の設定は必須ではありませんが、大規模な運用を視野に入れる場合は設定を強く推奨します。

### ▼ベクトルフィールドの構成例（JSON形式）
json
{
  "name": "summary_vector",
  "type": "Collection(Edm.Single)",
  "searchable": true,
  "retrievable": true,
  "filterable": false,
  "sortable": false,
  "facetable": false,
  "dimensions": 1536,
  "vectorSearchProfile": "my-vector-profile-01"
}

### ▼ベクトル検索プロファイルの構成例（JSON形式）
json
"vectorSearch": {
  "algorithms": [
    {
      "name": "hnsw-01",
      "kind": "hnsw",
      "hnswParameters": {
        "m": 4,
        "efConstruction": 400,
        "efSearch": 500,
        "metric": "cosine"
      }
    }
  ],
  "profiles": [
    {
      "name": "my-vector-profile-01",
      "algorithm": "hnsw-1"
    }
  ]
}

### ▼6. まとめ
この構成で、summary_vector フィールドに「リスト形式の数値配列（例: [0.1, -0.2, 0.3, ...]）」をアップロードできるようになります。