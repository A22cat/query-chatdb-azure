## テーブル定義書

- テーブルID: products_mst
- テーブル名称: 製品マスタ


## カラム定義

| 項目名称       | カラム名          | データ型    |
|----------------|-------------------|-------------|
| 会社ID         | corp_id           | INT         |
| 製品ID         | product_id        | INT         |
| 製品コード     | product_code      | NVARCHAR    |
| 製品名         | name              | NVARCHAR    |
| カテゴリ       | category          | NVARCHAR    |
| 価格           | price             | DECIMAL     |


- 複合主キー: corp_id, product_id
- 一意キー: product_code


## テーブルの実データ例（主要な選択肢パターンを網羅）

---

## 主な選択肢パターン

- **tax_category**: 課税, 非課税
- **open_flg_status**: 0（クローズ）, 1（オープン）, 2（再オープン）
