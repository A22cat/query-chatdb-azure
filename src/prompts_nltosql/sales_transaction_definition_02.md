## テーブル定義書

- テーブルID: sales_transaction
- テーブル名称: 販売取引


## カラム定義


| カラム名称<br>(項目名称) | カラム名<br>(項目ID)      | データ型   |
|-------------------------|--------------------------|------------|
| 会社ID                  | corp_id                  | INT        |
| 取引ID                  | sales_transaction_id     | INT        |
| 顧客ID                  | customer_id              | INT        |
| 製品ID                  | product_id               | INT        |
| 取引日                  | transaction_date         | DATE       |
| 数量                    | quantity                 | INT        |
| 単価                    | unit_price               | DECIMAL    |
| 割引率                  | discount_rate            | DECIMAL    |
| 税区分                  | tax_category             | NVARCHAR   |
| 支払方法                | payment_method           | NVARCHAR   |
| 登録日時                | created_at               | DATETIME   |
| 備考                    | remarks                  | NVARCHAR   |


## インデックス・制約

- **主キー（PK）**：corp_id, sales_transaction_id（複合主キー）
- **外部キー（FK）**：
    - customer_id → customer_mst
    - product_id → product_mst

## 主な選択肢パターン

- **tax_category**: 課税, 非課税
- **payment_method**: 現金, クレジットカード, 電子マネー
