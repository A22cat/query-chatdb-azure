## テーブル定義書

- テーブルID: warehouse_mst
- テーブル名称: 倉庫マスタ


## カラム定義

| カラム名称<br>(項目名称) | カラム名<br>(項目ID) | データ型   |
|-------------------------|---------------------|------------|
| 会社ID                  | corp_id             | INT        |
| 倉庫ID                  | warehouse_id        | INT        |
| 倉庫コード              | warehouse_code      | NVARCHAR   |
| 倉庫名                  | warehouse_name      | NVARCHAR   |
| 拠点種別                | location_type       | NVARCHAR   |
| 拠点コード              | region_id           | INT        |
| 郵便番号                | postal_code         | CHAR       |
| 住所（都道府県）        | prefecture          | NVARCHAR   |
| 住所（市区町村）        | city                | NVARCHAR   |
| 電話番号                | phone_number        | NVARCHAR   |
| 稼働フラグ              | is_active           | BIT        |
| 管理者の社員ID          | wh_manager_id       | INT        | 
| 登録日時                | created_at          | DATETIME   |
| 登録者                  | created_by          | NVARCHAR   |


## インデックス・制約

- **主キー（PK）**：corp_id, warehouse_id（複合主キー）
- **ユニークキー（UK）**：warehouse_code
- **外部キー（FK）**：
    - wh_manager_id → employees_mst.employee_id

## 主な選択肢パターン

- **location_type**: 倉庫, 工場, 店舗
- **prefecture/city**: 東京都/千代田区, 大阪府/大阪市北区, 愛知県/名古屋市中区, 北海道/札幌市中央区 （他のパターンのデータあり）
