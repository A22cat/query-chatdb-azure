## テーブル定義書

- テーブルID: inventory_transaction
- テーブル名称: 在庫の入出庫履歴


## カラム定義

| カラム名称<br>(項目名称)    | カラム名<br>(項目ID)     | データ型   |
|----------------------------|-------------------------|------------|
| 会社ID                     | corp_id                 | INT        |
| 在庫トランザクションID     | inve_transaction_id     | INT        |
| 在庫ID                     | inventory_id            | INT        |
| 製品ID                     | product_id              | INT        |
| 倉庫ID                     | warehouse_id            | INT        |
| 取引種別                   | transaction_type        | NVARCHAR   |
| 数量                       | quantity                | INT        |
| 取引日                     | transaction_date        | DATE       |
| 処理者                     | handled_by              | NVARCHAR   |
| コメント                   | remarks                 | NVARCHAR   |
| 登録日時                   | created_at              | DATETIME   |
| 登録者                     | created_by              | NVARCHAR   |

---

## インデックス・制約

- **主キー（PK）**：corp_id, inve_transaction_id（複合主キー）
- **ユニークキー（UK）**：inventory_id
- **外部キー（FK）**：
    - inventory_id → inventory_mst

---

## 主な選択肢パターン

- **transaction_type**: 入庫, 出庫, 調整

