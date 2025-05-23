CREATE TABLE inventory_mst (
    corp_id INT NOT NULL DEFAULT 0,
    inventory_id INT IDENTITY(1,1) NOT NULL,
    warehouse_product_cd NVARCHAR(40) NOT NULL UNIQUE,
    warehouse_id INT NOT NULL,
    product_id INT NOT NULL,
    shelf_no NVARCHAR(10) NULL,
    now_stock INT NOT NULL DEFAULT 0,
    safety_stock_qty INT NOT NULL DEFAULT 0,
    max_stock_qty INT NOT NULL DEFAULT 1000,
    reorder_point INT NOT NULL DEFAULT 50,
    created_at DATETIME NOT NULL DEFAULT GETDATE(),
    created_by NVARCHAR(50) NOT NULL DEFAULT 'SYSTEM',
    status NVARCHAR(10) NOT NULL DEFAULT '有効',

    CONSTRAINT PK_inventory_mst PRIMARY KEY (corp_id, inventory_id),

    -- 外部キー制約（必要に応じて有効化）
    -- CONSTRAINT FK_inventory_mst_warehouse FOREIGN KEY (warehouse_id) REFERENCES warehouse_mst(warehouse_id),
    -- CONSTRAINT FK_inventory_mst_product FOREIGN KEY (product_id) REFERENCES products_mst(product_id)
);
