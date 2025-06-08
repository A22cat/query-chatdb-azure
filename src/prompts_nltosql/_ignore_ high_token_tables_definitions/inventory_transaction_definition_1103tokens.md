## テーブル定義書

- テーブルID: inventory_transaction
- テーブル名称: 在庫の入出庫履歴


## カラム定義

| No | PK | UK | カラム名称<br>(項目名称)    | カラム名<br>(項目ID)     | データ型   | 桁数 | 小数部 | NULL許可 | 初期値     | 備考                                               |
|----|----|----|----------------------------|-------------------------|------------|------|--------|----------|------------|----------------------------------------------------|
| 1  | 1  |    | 会社ID                     | corp_id                 | INT        | -    | -      | ×        | 0          | corp_id, inve_transaction_idの複合主キー           |
| 2  | 2  |    | 在庫トランザクションID     | inve_transaction_id     | INT        | -    | -      | ×        | IDENTITY   | 自動採番                                          |
| 3  |    | ○  | 在庫ID                     | inventory_id            | INT        | -    | -      | ×        |            | inventory_mst 外部キー                            |
| 4  |    |    | 製品ID                     | product_id              | INT        | -    | -      | ×        | 0          | redundancy（冗長）                                 |
| 5  |    |    | 倉庫ID                     | warehouse_id            | INT        | -    | -      | ×        | 0          | redundancy（冗長）                                 |
| 6  |    |    | 取引種別                   | transaction_type        | NVARCHAR   | 20   | -      | ×        | '調整'     | 入庫 / 出庫 / 調整                                 |
| 7  |    |    | 数量                       | quantity                | INT        | -    | -      | ×        | 0          | ±表現。出庫はマイナス、入庫はプラス                |
| 8  |    |    | 取引日                     | transaction_date        | DATE       | -    | -      | ×        | GETDATE()  |                                                    |
| 9  |    |    | 処理者                     | handled_by              | NVARCHAR   | 50   | -      | ○        | NULL       | 担当者IDまたは名前                                 |
| 10 |    |    | コメント                   | remarks                 | NVARCHAR   | 255  | -      | ○        | NULL       | 備考、理由など                                     |
| 11 |    |    | 登録日時                   | created_at              | DATETIME   | -    | -      | ×        | GETDATE()  |                                                    |
| 12 |    |    | 登録者                     | created_by              | NVARCHAR   | 50   | -      | ×        | SYSTEM     |                                                    |

---

## インデックス・制約

- **主キー（PK）**：corp_id, inve_transaction_id（複合主キー）
- **ユニークキー（UK）**：inventory_id
- **外部キー（FK）**：
    - inventory_id → inventory_mst

## テーブルの実データ例（主要な選択肢パターンを網羅）

| corp_id | inve_transaction_id | inventory_id | product_id | warehouse_id | transaction_type | quantity | transaction_date | handled_by    | remarks         | created_at              | created_by |
|---------|---------------------|--------------|------------|--------------|------------------|----------|------------------|--------------|------------------|-------------------------|------------|
| 1       | 8                  | 1            | 1          | 101          | 入庫             | 50       | 2025-05-01       | tanaka_jp    | 初回入庫         | 2025-05-15 08:08:09.167 | SYSTEM     |
| 1       | 9                  | 2            | 2          | 101          | 出庫             | -10      | 2025-05-02       | suzuki_hr    | 営業部出庫       | 2025-05-15 08:08:09.167 | SYSTEM     |
| 1       | 10                 | 3            | 3          | 102          | 調整             | -5       | 2025-05-03       | yamamoto_it  | 棚卸調整         | 2025-05-15 08:08:09.167 | SYSTEM     |
| 1       | 11                 | 4            | 4          | 102          | 入庫             | 20       | 2025-05-04       | yamada_sales | 追加発注分入庫   | 2025-05-15 08:08:09.167 | SYSTEM     |

---

## 主な選択肢パターン

- **transaction_type**: 入庫, 出庫, 調整

