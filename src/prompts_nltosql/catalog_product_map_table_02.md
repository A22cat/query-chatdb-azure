## テーブル定義書

- テーブルID: catalog_product_map
- テーブル名称: カタログ商品マッピング


## カラム定義

| カラム名称<br>(項目名称) | カラム名<br>(項目ID)   | データ型   |
|-------------------------|-----------------------|------------|
| 会社ID                  | corp_id               | INT        |
| カタログマッピングID    | cat_map_id            | INT        | 
| カタログID              | catalog_id            | INT        |
| 製品ID                  | product_id            | INT        |
| 表示順                  | display_order         | INT        |
| ページ番号              | page_number           | INT        |
| 強調フラグ              | highlight_flag        | BIT        |
| 割引率                  | discount_rate         | DECIMAL    |
| 掲載開始日              | start_date            | DATE       |
| 掲載終了日              | end_date              | DATE       |
| 登録者                  | created_by            | NVARCHAR   |
| 登録日時                | created_at            | DATETIME   |


## インデックス・制約

- **主キー（PK）**：corp_id, cat_map_id（複合主キー）
- **外部キー（FK）**：
    - catalog_id → catalog_mst
    - product_id → product_mst

---

## 主な選択肢パターン

- **highlight_flag**: 0（通常）, 1（強調）