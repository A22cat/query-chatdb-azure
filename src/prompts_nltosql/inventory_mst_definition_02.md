## テーブル定義書

- テーブルID: inventory_mst
- テーブル名称: 在庫マスタ


## カラム定義

| カラム名称<br>(項目名称) | カラム名<br>(項目ID) | データ型   |
|-------------------------|---------------------|------------|
| 会社ID                  | corp_id             | INT        |
| 在庫ID                  | inventory_id        | INT        |
| 倉庫コード＋製品        | warehouse_product_cd| NVARCHAR   |
| 倉庫ID                  | warehouse_id        | INT        |
| 製品ID                  | product_id          | INT        |
| 棚番号                  | shelf_no            | NVARCHAR   |
| 在庫数                  | now_stock           | INT        |
| 安全在庫数              | safety_stock_qty    | INT        |
| 最大在庫数              | max_stock_qty       | INT        |
| 発注点                  | reorder_point       | INT        |
| 登録日時                | created_at          | DATETIME   |
| 登録者                  | created_by          | NVARCHAR   |
| ステータス              | status              | NVARCHAR   |


## インデックス・制約

- 主キー（PK）：corp_id, inventory_id（複合主キー）
- ユニークキー（UK）：warehouse_product_cd
- 外部キー（FK）：
    - warehouse_id → warehouse_mst
    - product_id → product_mst


## inventory_mst テーブルの実データ例（主要な選択肢パターンを網羅）

---

## 主な選択肢パターン

- **status**: 有効, 無効