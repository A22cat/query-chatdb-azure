## テーブル定義書

- テーブルID: customer_mst
- テーブル名称: 顧客マスタ


## カラム定義

| カラム名称<br>(項目名称) | カラム名<br>(項目ID) | データ型   |
|-------------------------|---------------------|------------|
| 会社ID                  | corp_id             | INT        |
| 顧客ID                  | customer_id         | INT        |
| メールアドレス          | email               | NVARCHAR   ||
| 氏名                    | name                | NVARCHAR   ||
| 性別                    | gender              | NVARCHAR   ||
| 生年月日                | birth_date          | DATE       |
| 電話番号                | phone_number        | NVARCHAR   |
| 住所（都道府県）        | prefecture          | NVARCHAR   | 
| 住所（市区町村）        | city                | NVARCHAR   | 
| 登録日                  | registration_date   | DATE       |
| 登録者                  | created_by          | NVARCHAR   ||
| ステータス              | status              | NVARCHAR   ||



## インデックス・制約

- **主キー（PK）**：corp_id, customer_id（複合主キー）
- **ユニークキー（UK）**：email


## テーブルの実データ例（主要な選択肢パターンを網羅）


## 主な選択肢パターン

- **gender**: 男性, 女性, その他
- **status**: 有効, 無効
- **prefecture/city**: 東京都/渋谷区, 大阪府/大阪市, 北海道/札幌市, 京都府/京都市（他都道府県もデータあり）

