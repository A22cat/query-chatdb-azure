## テーブル定義書

- テーブルID: stock_transaction
- テーブル名称: 倉庫の在庫移動履歴


## カラム定義

| カラム名称<br>(項目名称) | カラム名<br>(項目ID)    | データ型   |
|-------------------------|------------------------|------------|
| 会社ID                  | corp_id                | INT        |
| 在庫移動ID              | stock_transaction_id   | INT        |
| 製品ID                  | product_id             | INT        |
| 在庫ID                  | inventory_id           | INT        |
| 倉庫ID（出庫）          | source_warehouse_id    | INT        |
| 倉庫ID（入庫）          | target_warehouse_id    | INT        |
| 移動数量                | quantity               | INT        |
| 移動日                  | transaction_date       | DATE       |
| 移動理由                | reason                 | NVARCHAR   |
| 登録日時                | created_at             | DATETIME   |
| 登録者                  | created_by             | NVARCHAR   |
| コメント                | remarks                | NVARCHAR   |


## インデックス・制約

- **主キー（PK）**：corp_id, stock_transaction_id（複合主キー）
- **外部キー（FK）**：
    - product_id → product_mst
    - inventory_id → inventory_mst
    - source_warehouse_id → warehouse_mst（NULL許可）
    - target_warehouse_id → warehouse_mst（NULL許可）

## 主な選択肢パターン

なし