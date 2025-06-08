## テーブル定義書

- テーブルID: inventory_mst
- テーブル名称: 在庫マスタ


## カラム定義

| No | PK | UK | カラム名称<br>(項目名称) | カラム名<br>(項目ID) | データ型   | 桁数 | 小数部 | NULL許可 | 初期値      | 備考                                    |
|----|----|----|-------------------------|---------------------|------------|------|--------|----------|-------------|-----------------------------------------|
| 1  | 1  |    | 会社ID                  | corp_id             | INT        | -    | -      | ×        | 0           | corp_id, inventory_idの複合主キー        |
| 2  | 2  |    | 在庫ID                  | inventory_id        | INT        | -    | -      | ×        | IDENTITY     | 自動採番                                 |
| 3  |    | ○  | 倉庫コード＋製品        | warehouse_product_cd| NVARCHAR   | 40   | -      | ×        |             | 倉庫＋製品の一意キー                     |
| 4  |    |    | 倉庫ID                  | warehouse_id        | INT        | -    | -      | ×        |             | warehouse_mst 外部キー                   |
| 5  |    |    | 製品ID                  | product_id          | INT        | -    | -      | ×        |             | product_mst 外部キー                     |
| 6  |    |    | 棚番号                  | shelf_no            | NVARCHAR   | 10   | -      | ○        | NULL        | 倉庫内の配置                             |
| 7  |    |    | 在庫数                  | now_stock           | INT        | -    | -      | ×        | 0           | 現在の在庫数                             |
| 8  |    |    | 安全在庫数              | safety_stock_qty    | INT        | -    | -      | ×        | 0           | 最低必要在庫数                           |
| 9  |    |    | 最大在庫数              | max_stock_qty       | INT        | -    | -      | ×        | 1000        | 最大保管量                               |
| 10 |    |    | 発注点                  | reorder_point       | INT        | -    | -      | ×        | 50          | 補充基準点                               |
| 11 |    |    | 登録日時                | created_at          | DATETIME   | -    | -      | ×        | GETDATE()   |                                         |
| 12 |    |    | 登録者                  | created_by          | NVARCHAR   | 50   | -      | ×        | SYSTEM      | APIまたはユーザー名                      |
| 13 |    |    | ステータス              | status              | NVARCHAR   | 10   | -      | ×        | '有効'      | 有効 / 無効                              |


## インデックス・制約

- 主キー（PK）：corp_id, inventory_id（複合主キー）
- ユニークキー（UK）：warehouse_product_cd
- 外部キー（FK）：
    - warehouse_id → warehouse_mst
    - product_id → product_mst


## inventory_mst テーブルの実データ例（主要な選択肢パターンを網羅）

| corp_id | inventory_id | warehouse_product_cd | warehouse_id | product_id | shelf_no | now_stock | safety_stock_qty | max_stock_qty | reorder_point | created_at              | created_by | status |
|---------|--------------|---------------------|--------------|------------|----------|-----------|------------------|--------------|--------------|-------------------------|------------|--------|
| 1       | 1            | WH01-P001           | 101          | 1001       | A-01     | 150       | 30               | 500          | 80           | 2025-05-15 06:29:35.393 | SYSTEM     | 有効   |
| 1       | 3            | WH02-P001           | 202          | 1001       | B-01     | 200       | 50               | 600          | 100          | 2025-05-15 06:29:35.393 | SYSTEM     | 有効   |
| 1       | 4            | WH02-P003           | 202          | 1003       | NULL     | 0         | 10               | 200          | 30           | 2025-05-15 06:29:35.393 | SYSTEM     | 無効   |
| 1       | 6            | WH01-P003           | 101          | 1003       | A-03     | 120       | 40               | 450          | 70           | 2025-05-15 08:01:23.243 | SYSTEM     | 有効   |

---

## 主な選択肢パターン

- **status**: 有効, 無効