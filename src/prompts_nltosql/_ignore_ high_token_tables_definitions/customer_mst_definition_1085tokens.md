## テーブル定義書

- テーブルID: customer_mst
- テーブル名称: 顧客マスタ


## カラム定義

| No | PK | UK | カラム名称<br>(項目名称) | カラム名<br>(項目ID) | データ型   | 桁数 | 小数部 | NULL許可 | 初期値     | 備考                                 |
|----|----|----|-------------------------|---------------------|------------|------|--------|----------|------------|--------------------------------------|
| 1  | 1  |    | 会社ID                  | corp_id             | INT        | -    | -      | ×        | 0          | corp_id, customer_idの複合主キー     |
| 2  | 2  |    | 顧客ID                  | customer_id         | INT        | -    | -      | ×        | IDENTITY   | 自動採番                             |
| 3  |    | ○  | メールアドレス          | email               | NVARCHAR   | 100  | -      | ×        |            | 一意制約あり                          |
| 4  |    |    | 氏名                    | name                | NVARCHAR   | 100  | -      | ×        |            | フルネーム                            |
| 5  |    |    | 性別                    | gender              | NVARCHAR   | 10   | -      | ○        | NULL       | 男性 / 女性 / その他                  |
| 6  |    |    | 生年月日                | birth_date          | DATE       | -    | -      | ○        | NULL       |                                      |
| 7  |    |    | 電話番号                | phone_number        | NVARCHAR   | 20   | -      | ○        | NULL       |                                      |
| 8  |    |    | 住所（都道府県）        | prefecture          | NVARCHAR   | 50   | -      | ○        | NULL       |                                      |
| 9  |    |    | 住所（市区町村）        | city                | NVARCHAR   | 50   | -      | ○        | NULL       |                                      |
| 10 |    |    | 登録日                  | registration_date   | DATE       | -    | -      | ×        | GETDATE()  |                                      |
| 11 |    |    | 登録者                  | created_by          | NVARCHAR   | 50   | -      | ×        | SYSTEM     | APIまたはユーザー名                   |
| 12 |    |    | ステータス              | status              | NVARCHAR   | 10   | -      | ×        | '有効'     | 有効 / 無効                           |



## インデックス・制約

- **主キー（PK）**：corp_id, customer_id（複合主キー）
- **ユニークキー（UK）**：email


## テーブルの実データ例（主要な選択肢パターンを網羅）

| corp_id | customer_id | email                | name        | gender | birth_date  | phone_number   | prefecture | city   | registration_date | created_by | status |
|---------|-------------|----------------------|-------------|--------|-------------|---------------|------------|--------|-------------------|------------|--------|
| 1       | 1           | example1@example.com | 田中 太郎   | 男性   | 1990-01-01  | 090-1234-5678 | 東京都     | 渋谷区 | 2025-05-15        | SYSTEM     | 有効   |
| 1       | 2           | example2@example.com | 鈴木 花子   | 女性   | 1985-05-15  | 080-2345-6789 | 大阪府     | 大阪市 | 2025-05-15        | SYSTEM     | 有効   |
| 1       | 3           | example3@example.com | 佐藤 次郎   | 男性   | 1980-09-20  | 070-3456-7890 | 北海道     | 札幌市 | 2025-05-15        | SYSTEM     | 無効   |
| 1       | 4           | example4@example.com | 高橋 さくら | 女性   | 1992-12-10  | 090-4567-8901 | 京都府     | 京都市 | 2025-05-15        | SYSTEM     | 有効   |

---

## 主な選択肢パターン

- **gender**: 男性, 女性, その他
- **status**: 有効, 無効
- **prefecture/city**: 東京都/渋谷区, 大阪府/大阪市, 北海道/札幌市, 京都府/京都市（他都道府県もデータあり）

