## テーブル定義書

- テーブルID: catalog_mst
- テーブル名称: 製品カタログマスタ


## カラム定義

| No | PK | UK | カラム名称       | カラム名        | データ型    | 桁数 | 小数部 | NULL許可 | 初期値         | 備考                          |
|----|----|----|------------------|------------------|-------------|------|--------|----------|----------------|-------------------------------|
| 1  | 1  |    | 会社ID           | corp_id          | INT         | -    | -      | ×        | 0              | corp_id, catalog_id の複合主キー |
| 2  | 2  |    | カタログID       | catalog_id       | INT         | -    | -      | ×        | IDENTITY(1,1)  | 自動採番                      |
| 3  |    | ○  | カタログコード   | catalog_code     | NVARCHAR    | 20   | -      | ×        |                | 一意コード                    |
| 4  |    |    | カタログ名       | catalog_name     | NVARCHAR    | 100  | -      | ×        |                |                               |
| 5  |    |    | カテゴリ         | category         | NVARCHAR    | 50   | -      | ×        | '一般'         | 一般 / 季節 / 限定           |
| 6  |    |    | シーズン         | season           | NVARCHAR    | 30   | -      | ○        | NULL           | 春 / 夏 / 秋 / 冬             |



- 複合主キー: corp_id, catalog_id
- 一意キー: catalog_code