## テーブル定義書

- テーブルID: catalog_mst
- テーブル名称: 製品カタログマスタ


## カラム定義

| カラム名称       | カラム名        | データ型    | 
|------------------|------------------|-------------|
| 会社ID           | corp_id          | INT         |
| カタログID       | catalog_id       | INT         |
| カタログコード   | catalog_code     | NVARCHAR    |
| カタログ名       | catalog_name     | NVARCHAR    |
| カテゴリ         | category         | NVARCHAR    |
| シーズン         | season           | NVARCHAR    |
| 発行日           | publish_date     | DATE        |
| 有効期限         | expire_date      | DATE        |
| ステータス       | status           | NVARCHAR    |
| 言語             | language         | NVARCHAR    |
| 地域             | region           | NVARCHAR    |
| 登録者           | created_by       | NVARCHAR    |
| 登録日時         | created_at       | DATETIME    |


- 複合主キー: corp_id, catalog_id
- 一意キー: catalog_code
---

## データの選択肢の種類

- **category**: 季節, 一般, 限定
- **season**: 春, 夏, 秋, 冬, NULL
- **language**: 日本語, 英語
- **region**: 関東, 関西, 全国, 海外, 北海道, 東北, 中部 （その他の選択肢あり）
- **status**: 有効, 無効
