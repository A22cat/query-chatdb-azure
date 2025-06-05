# テーブル構造
---

## products_mst

- 主キー（PK）：corp_id, product_id
- 一意キー（UK）：product_code

| カラム名 | データ型 |
| :-- | :-- |
| corp_id | INT |
| product_id | INT |
| product_code | NVARCHAR |
| name | NVARCHAR |
| price | DECIMAL |


---

## catalog_product_map

- PK：corp_id, cat_map_id
- FK：catalog_id → catalog_mst, product_id → product_mst

| カラム名 | データ型 |
| :-- | :-- |
| corp_id | INT |
| cat_map_id | INT |
| catalog_id | INT |
| product_id | INT |


---

## catalog_mst

- PK：corp_id, catalog_id
- UK：catalog_code

| カラム名 | データ型 |
| :-- | :-- |
| corp_id | INT |
| catalog_id | INT |
| catalog_code | NVARCHAR |
| catalog_name | NVARCHAR |


---

## inventory_mst

- PK：corp_id, inventory_id
- UK：warehouse_product_cd
- FK：warehouse_id → warehouse_mst, product_id → product_mst

| カラム名 | データ型 |
| :-- | :-- |
| corp_id | INT |
| inventory_id | INT |
| warehouse_product_cd | NVARCHAR |
| warehouse_id | INT |
| product_id | INT |
| now_stock | INT |


---

## inventory_transaction

- PK：corp_id, inve_transaction_id
- FK：inventory_id → inventory_mst

| カラム名 | データ型 |
| :-- | :-- |
| corp_id | INT |
| inve_transaction_id | INT |
| inventory_id | INT |
| quantity | INT |


---

## stock_transaction

- PK：corp_id, stock_transaction_id
- FK：product_id → product_mst, inventory_id → inventory_mst, source_warehouse_id → warehouse_mst（NULL許可）, target_warehouse_id → warehouse_mst（NULL許可）

| カラム名 | データ型 |
| :-- | :-- |
| corp_id | INT |
| stock_transaction_id | INT |
| product_id | INT |
| inventory_id | INT |
| source_warehouse_id | INT |
| target_warehouse_id | INT |
| quantity | INT |


---

## warehouse_mst

- PK：corp_id, warehouse_id
- UK：warehouse_code
- FK：wh_manager_id → employees_mst.employee_id

| カラム名 | データ型 |
| :-- | :-- |
| corp_id | INT |
| warehouse_id | INT |
| warehouse_code | NVARCHAR |
| warehouse_name | NVARCHAR |
| wh_manager_id | INT |


---

## employees_mst

- PK：corp_id, employee_id
- UK：email
- FK：manager_id → employees_mst.employee_id（自己参照）

| カラム名 | データ型 |
| :-- | :-- |
| corp_id | INT |
| employee_id | INT |
| name | NVARCHAR |
| email | NVARCHAR |
| manager_id | INT |


---

## sales_transaction

- PK：corp_id, sales_transaction_id
- FK：customer_id → customer_mst, product_id → product_mst

| カラム名 | データ型 |
| :-- | :-- |
| corp_id | INT |
| sales_transaction_id | INT |
| customer_id | INT |
| product_id | INT |


---

## customer_mst

- PK：corp_id, customer_id
- UK：email

| カラム名 | データ型 |
| :-- | :-- |
| corp_id | INT |
| customer_id | INT |
| email | NVARCHAR |
| name | NVARCHAR |


---
