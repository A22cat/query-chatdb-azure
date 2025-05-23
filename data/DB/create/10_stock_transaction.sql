CREATE TABLE stock_transaction (
    corp_id INT NOT NULL DEFAULT 0,  -- 会社ID
    stock_transaction_id INT IDENTITY(1,1) NOT NULL,  -- 在庫移動ID（自動採番）
    product_id INT NOT NULL,  -- 製品ID（外部キー）
    inventory_id INT NOT NULL,
    source_warehouse_id INT NULL,  -- 出庫元倉庫ID
    target_warehouse_id INT NULL,  -- 入庫先倉庫ID
    quantity INT NOT NULL,  -- 移動数量
    transaction_date DATE NOT NULL,  -- 移動日
    reason NVARCHAR(50) NULL,  -- 移動理由（補充 / 移動 / 調整など）
    created_at DATETIME NOT NULL DEFAULT GETDATE(),  -- 登録日時
    created_by NVARCHAR(50) NOT NULL DEFAULT 'SYSTEM',  -- 登録者
    remarks NVARCHAR(255) NULL,  -- 備考

    -- 主キー（複合）
    CONSTRAINT PK_stock_transaction PRIMARY KEY (corp_id, stock_transaction_id),

    -- 外部キー制約（製品ID）
    CONSTRAINT FK_stock_transaction_product FOREIGN KEY (corp_id, product_id) REFERENCES products_mst(corp_id, product_id),


    -- 外部キー制約（在庫ID）
    CONSTRAINT FK_stock_transaction_inventory FOREIGN KEY (corp_id, inventory_id) REFERENCES inventory_mst(corp_id, inventory_id)
);
