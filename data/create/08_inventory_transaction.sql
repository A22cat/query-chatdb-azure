CREATE TABLE inventory_transaction (
    corp_id               INT           NOT NULL DEFAULT 0,      -- 会社ID
    inve_transaction_id   INT           NOT NULL IDENTITY(1,1),  -- 自動採番
    inventory_id          INT           NOT NULL,                -- 外部キー
    product_id            INT           NOT NULL DEFAULT 0,      -- 冗長データ
    warehouse_id          INT           NOT NULL DEFAULT 0,      -- 冗長データ
    transaction_type      NVARCHAR(20)   NOT NULL DEFAULT '調整', -- 入庫 / 出庫 / 調整
    quantity              INT           NOT NULL DEFAULT 0,      -- ±値対応
    transaction_date      DATE          NOT NULL DEFAULT GETDATE(),  -- 処理日
    handled_by            NVARCHAR(50)   NULL,                        -- 担当者
    remarks               NVARCHAR(255)  NULL,                        -- 備考・理由など
    created_at            DATETIME      NOT NULL DEFAULT GETDATE(),  -- 登録日時
    created_by            NVARCHAR(50)   NOT NULL DEFAULT 'SYSTEM',   -- 登録者

    CONSTRAINT PK_inventory_transaction PRIMARY KEY (corp_id, inve_transaction_id),
    CONSTRAINT FK_inventory_transaction_inventory FOREIGN KEY (corp_id, inventory_id)
        REFERENCES inventory_mst (corp_id, inventory_id)
);

-- 任意で追加する場合（冗長項目の正規化補助）
-- 外部キー制約（必要であれば以下も追加）
-- FOREIGN KEY (product_id) REFERENCES product_mst(product_id),
-- FOREIGN KEY (warehouse_id) REFERENCES warehouse_mst(warehouse_id);
