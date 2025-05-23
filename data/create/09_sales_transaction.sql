CREATE TABLE sales_transaction (
    corp_id INT NOT NULL DEFAULT 0,      -- 会社ID
    sales_transaction_id INT NOT NULL IDENTITY(1,1),  -- 取引ID (自動採番、主キー)
    customer_id INT NOT NULL,  -- 顧客ID (customer_mst 外部キー)
    product_id INT NOT NULL,   -- 製品ID (product_mst 外部キー)
    transaction_date DATE NOT NULL DEFAULT GETDATE(),  -- 取引日 (現在日付)
    quantity INT NOT NULL,     -- 数量
    unit_price DECIMAL(10, 2) NOT NULL,  -- 単価
    discount_rate DECIMAL(5, 2) NULL,  -- 割引率 (NULLの場合もあり)
    tax_category NVARCHAR(10) NOT NULL DEFAULT '課税',  -- 税区分 (課税 / 非課税)
    payment_method NVARCHAR(20) NOT NULL DEFAULT '現金',  -- 支払方法 (現金 / クレカ / 電子マネー等)
    created_at DATETIME NOT NULL DEFAULT GETDATE(),  -- 登録日時 (現在日時)
    remarks NVARCHAR(255) NULL,  -- 備考

    CONSTRAINT PK_sales_transaction PRIMARY KEY (corp_id, sales_transaction_id),
    CONSTRAINT FK_sales_customer FOREIGN KEY (corp_id, customer_id)
        REFERENCES customer_mst (corp_id, customer_id),  -- 顧客ID 外部キー
     CONSTRAINT FK_sales_product FOREIGN KEY (corp_id, product_id)
        REFERENCES products_mst (corp_id, product_id)  -- 製品ID 外部キー
);
