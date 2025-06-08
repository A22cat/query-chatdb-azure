## テーブル定義書

- テーブルID: warehouse_mst
- テーブル名称: 倉庫マスタ


## カラム定義

| No | PK | UK | カラム名称<br>(項目名称) | カラム名<br>(項目ID) | データ型   | 桁数 | 小数部 | NULL許可 | 初期値     | 備考                                  |
|----|----|----|-------------------------|---------------------|------------|------|--------|----------|------------|---------------------------------------|
| 1  | 1  |    | 会社ID                  | corp_id             | INT        | -    | -      | ×        | 0          | corp_id, warehouse_idの複合主キー     |
| 2  | 2  |    | 倉庫ID                  | warehouse_id        | INT        | -    | -      | ×        | IDENTITY   | 自動採番                              |
| 3  |    | ○  | 倉庫コード              | warehouse_code      | NVARCHAR   | 20   | -      | ×        |            | 一意制約あり                           |
| 4  |    |    | 倉庫名                  | warehouse_name      | NVARCHAR   | 100  | -      | ×        |            |                                       |
| 5  |    |    | 拠点種別                | location_type       | NVARCHAR   | 30   | -      | ×        | '倉庫'     | 倉庫 / 店舗 / 工場など                 |
| 6  |    |    | 拠点コード              | region_id           | INT        | -    | -      | ×        | 0          |                                       |
| 7  |    |    | 郵便番号                | postal_code         | CHAR       | 8    | -      | ○        | NULL       |                                       |
| 8  |    |    | 住所（都道府県）        | prefecture          | NVARCHAR   | 50   | -      | ○        | NULL       |                                       |
| 9  |    |    | 住所（市区町村）        | city                | NVARCHAR   | 50   | -      | ○        | NULL       |                                       |
| 10 |    |    | 電話番号                | phone_number        | NVARCHAR   | 20   | -      | ○        | NULL       |                                       |
| 11 |    |    | 稼働フラグ              | is_active           | BIT        | -    | -      | ×        | 1          | 0:無効, 1:有効                        |
| 12 |    |    | 管理者の社員ID          | wh_manager_id       | INT        | -    | -      | ○        | NULL       | employees_mst 外部キー                |
| 13 |    |    | 登録日時                | created_at          | DATETIME   | -    | -      | ×        | GETDATE()  |                                       |
| 14 |    |    | 登録者                  | created_by          | NVARCHAR   | 50   | -      | ×        | SYSTEM     | APIまたはユーザー名                   |


## インデックス・制約

- **主キー（PK）**：corp_id, warehouse_id（複合主キー）
- **ユニークキー（UK）**：warehouse_code
- **外部キー（FK）**：
    - wh_manager_id → employees_mst.employee_id


## テーブルの実データ例（主要な選択肢パターンを網羅）

| corp_id | warehouse_id | warehouse_code | warehouse_name | location_type | region_id | postal_code | prefecture | city         | phone_number    | is_active | wh_manager_id | created_at              | created_by |
|---------|--------------|---------------|---------------|--------------|-----------|-------------|------------|--------------|-----------------|-----------|---------------|-------------------------|------------|
| 1       | 1            | WH001         | 東京第一倉庫  | 倉庫         | 1         | 1000001     | 東京都     | 千代田区     | 03-1234-5678    | 1         | 2             | 2025-05-15 06:27:56.403 | SYSTEM     |
| 1       | 2            | WH002         | 大阪工場      | 工場         | 2         | 5300001     | 大阪府     | 大阪市北区   | 06-2345-6789    | 1         | 2             | 2025-05-15 06:27:56.403 | SYSTEM     |
| 1       | 3            | WH003         | 名古屋中央店  | 店舗         | 3         | 4600001     | 愛知県     | 名古屋市中区 | 052-3456-7890   | 1         | 2             | 2025-05-15 06:27:56.403 | SYSTEM     |
| 1       | 4            | WH004         | 札幌倉庫      | 倉庫         | 4         | 0600001     | 北海道     | 札幌市中央区 | 011-1111-2222   | 1         | 3             | 2025-05-15 06:27:56.403 | admin      |

---

## 主な選択肢パターン

- **location_type**: 倉庫, 工場, 店舗
- **prefecture/city**: 東京都/千代田区, 大阪府/大阪市北区, 愛知県/名古屋市中区, 北海道/札幌市中央区 （他のパターンのデータあり）
