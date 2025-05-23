CREATE TABLE catalog_product_map (
    corp_id INT  NOT NULL DEFAULT 0,           -- 会社ID
    cat_map_id INT IDENTITY(1,1),  -- カタログマッピングID（自動採番）

    catalog_id INT NOT NULL,                  -- カタログID（外部キー）
    product_id INT NOT NULL,                  -- 製品ID（外部キー）

    display_order INT NULL,                   -- 表示順
    page_number INT NULL,                     -- ページ番号
    highlight_flag BIT NOT NULL DEFAULT 0,    -- 強調フラグ（0: 通常, 1: 強調）
    discount_rate DECIMAL(5,2) NULL,          -- 割引率（例: 10.00 ＝10%）

    start_date DATE NULL,                     -- 掲載開始日
    end_date DATE NULL,                       -- 掲載終了日

    created_by NVARCHAR(50) NOT NULL DEFAULT 'SYSTEM',  -- 登録者
    created_at DATETIME NOT NULL DEFAULT GETDATE(),    -- 登録日時

    -- 主キー：複合主キー（corp_id, product_id）
    CONSTRAINT PK_catalog_product_map PRIMARY KEY (corp_id, cat_map_id),

    -- 外部キー制約（corp_id + catalog_id に変更）
    CONSTRAINT fk_catalog FOREIGN KEY (corp_id, catalog_id)
    REFERENCES catalog_mst (corp_id, catalog_id),

    CONSTRAINT fk_product FOREIGN KEY (corp_id, product_id)
    REFERENCES products_mst (corp_id, product_id)
);
