## テーブル定義書

- テーブルID: stock_transaction
- テーブル名称: 倉庫の在庫移動履歴


## カラム定義

| No | PK | UK | カラム名称<br>(項目名称) | カラム名<br>(項目ID)    | データ型   | 桁数 | 小数部 | NULL許可 | 初期値     | 備考                                  |
|----|----|----|-------------------------|------------------------|------------|------|--------|----------|------------|---------------------------------------|
| 1  | 1  |    | 会社ID                  | corp_id                | INT        | -    | -      | ×        | 0          | corp_id, stock_transaction_idの複合主キー |
| 2  | 2  |    | 在庫移動ID              | stock_transaction_id   | INT        | -    | -      | ×        | IDENTITY   | 自動採番                              |
| 3  |    |    | 製品ID                  | product_id             | INT        | -    | -      | ×        |            | product_mst 外部キー                   |
| 4  |    |    | 在庫ID                  | inventory_id           | INT        | -    | -      | ×        |            | inventory_mst 外部キー                 |
| 5  |    |    | 倉庫ID（出庫）          | source_warehouse_id    | INT        | -    | -      | ○        | NULL       | 出庫元 倉庫                            |
| 6  |    |    | 倉庫ID（入庫）          | target_warehouse_id    | INT        | -    | -      | ○        | NULL       | 入庫先 倉庫                            |
| 7  |    |    | 移動数量                | quantity               | INT        | -    | -      | ×        |            |                                       |
| 8  |    |    | 移動日                  | transaction_date       | DATE       | -    | -      | ×        |            |                                       |
| 9  |    |    | 移動理由                | reason                 | NVARCHAR   | 50   | -      | ○        | NULL       | 補充 / 移動 / 調整など                 |
| 10 |    |    | 登録日時                | created_at             | DATETIME   | -    | -      | ×        | GETDATE()  |                                       |
| 11 |    |    | 登録者                  | created_by             | NVARCHAR   | 50   | -      | ×        | SYSTEM     |                                       |
| 12 |    |    | コメント                | remarks                | NVARCHAR   | 255  | -      | ○        | NULL       | 備考                                  |


## インデックス・制約

- **主キー（PK）**：corp_id, stock_transaction_id（複合主キー）
- **外部キー（FK）**：
    - product_id → product_mst
    - inventory_id → inventory_mst
    - source_warehouse_id → warehouse_mst（NULL許可）
    - target_warehouse_id → warehouse_mst（NULL許可）


## stock_transaction テーブルの実データ例（主要な選択肢パターンを網羅）

| corp_id | stock_transaction_id | product_id | inventory_id | source_warehouse_id | target_warehouse_id | quantity | transaction_date | reason | created_at              | created_by | remarks      |
|---------|---------------------|------------|--------------|---------------------|---------------------|----------|------------------|--------|-------------------------|------------|--------------|
| 1       | 1                   | 1          | 1            | 1                   | 1                   | 20       | 2025-05-01       | 補充   | 2025-05-17 22:01:16.973 | SYSTEM     | 定期補充     |
| 1       | 2                   | 2          | 2            | 2                   | 2                   | 15       | 2025-05-02       | 移動   | 2025-05-17 22:01:16.973 | admin      | 倉庫再配置   |
| 1       | 3                   | 3          | 3            | 3                   | 3                   | 10       | 2025-05-03       | 調整   | 2025-05-17 22:01:16.973 | SYSTEM     | 在庫調整     |
| 1       | 4                   | 4          | 4            | 4                   | 4                   | 18       | 2025-05-04       | 補充   | 2025-05-17 22:01:16.973 | SYSTEM     | 増補         |

---

## 主な選択肢パターン

なし