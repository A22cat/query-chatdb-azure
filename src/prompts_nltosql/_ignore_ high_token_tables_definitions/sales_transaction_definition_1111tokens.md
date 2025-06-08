## テーブル定義書

- テーブルID: sales_transaction
- テーブル名称: 販売取引


## カラム定義


| No | PK | UK | カラム名称<br>(項目名称) | カラム名<br>(項目ID)      | データ型   | 桁数 | 小数部 | NULL許可 | 初期値     | 備考                                  |
|----|----|----|-------------------------|--------------------------|------------|------|--------|----------|------------|---------------------------------------|
| 1  | 1  |    | 会社ID                  | corp_id                  | INT        | -    | -      | ×        | 0          | corp_id, sales_transaction_idの複合主キー |
| 2  | 2  |    | 取引ID                  | sales_transaction_id     | INT        | -    | -      | ×        | IDENTITY   | 自動採番                              |
| 3  |    |    | 顧客ID                  | customer_id              | INT        | -    | -      | ×        |            | customer_mst 外部キー                  |
| 4  |    |    | 製品ID                  | product_id               | INT        | -    | -      | ×        |            | product_mst 外部キー                   |
| 5  |    |    | 取引日                  | transaction_date         | DATE       | -    | -      | ×        | GETDATE()  |                                       |
| 6  |    |    | 数量                    | quantity                 | INT        | -    | -      | ×        |            |                                       |
| 7  |    |    | 単価                    | unit_price               | DECIMAL    | 10   | 2      | ×        |            |                                       |
| 8  |    |    | 割引率                  | discount_rate            | DECIMAL    | 5    | 2      | ○        | NULL       | 割引がない場合はNULL                   |
| 9  |    |    | 税区分                  | tax_category             | NVARCHAR   | 10   | -      | ×        | '課税'     | 課税 / 非課税                          |
| 10 |    |    | 支払方法                | payment_method           | NVARCHAR   | 20   | -      | ×        | '現金'     | 現金 / クレカ / 電子マネーなど         |
| 11 |    |    | 登録日時                | created_at               | DATETIME   | -    | -      | ×        | GETDATE()  |                                       |
| 12 |    |    | 備考                    | remarks                  | NVARCHAR   | 255  | -      | ○        | NULL       | メモ                                   |


## インデックス・制約

- **主キー（PK）**：corp_id, sales_transaction_id（複合主キー）
- **外部キー（FK）**：
    - customer_id → customer_mst
    - product_id → product_mst


## sales_transaction テーブルの実データ例（主要な選択肢パターンを網羅）

| corp_id | sales_transaction_id | customer_id | product_id | transaction_date | quantity | unit_price | discount_rate | tax_category | payment_method   | created_at              | remarks     |
|---------|---------------------|-------------|------------|------------------|----------|------------|---------------|--------------|------------------|-------------------------|-------------|
| 1       | 9                   | 1           | 1          | 2025-05-01       | 3        | 1500.00    | NULL          | 課税         | 現金             | 2025-05-01 10:00:00.000 | 通常購入    |
| 1       | 10                  | 2           | 3          | 2025-05-02       | 2        | 2200.00    | 5.00          | 課税         | クレジットカード | 2025-05-02 11:30:00.000 | 割引適用    |
| 1       | 11                  | 3           | 5          | 2025-05-03       | 4        | 800.00     | NULL          | 非課税       | 電子マネー       | 2025-05-03 12:00:00.000 | まとめ買い  |
| 1       | 12                  | 4           | 7          | 2025-05-04       | 1        | 3000.00    | 10.00         | 課税         | 現金             | 2025-05-04 13:00:00.000 | キャンペーン|

---

## 主な選択肢パターン

- **tax_category**: 課税, 非課税
- **payment_method**: 現金, クレジットカード, 電子マネー
