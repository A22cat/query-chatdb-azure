CREATE TABLE warehouse_mst (
    corp_id             INT NOT NULL DEFAULT 0,
    warehouse_id        INT NOT NULL IDENTITY(1,1),
    warehouse_code      NVARCHAR(20) NOT NULL UNIQUE,
    warehouse_name      NVARCHAR(100) NOT NULL,
    location_type       NVARCHAR(30) NOT NULL DEFAULT '倉庫', -- 倉庫 / 店舗 / 工場
    region_id           INT NOT NULL DEFAULT 0,
    postal_code         CHAR(8) NULL,
    prefecture          NVARCHAR(50) NULL,
    city                NVARCHAR(50) NULL,
    phone_number        NVARCHAR(20) NULL,
    is_active           BIT NOT NULL DEFAULT 1, -- 0: 無効, 1: 有効
    wh_manager_id          INT NULL, -- 管理者の社員ID
    created_at          DATETIME NOT NULL DEFAULT GETDATE(),
    created_by          NVARCHAR(50) NOT NULL DEFAULT 'SYSTEM',
    
    CONSTRAINT PK_warehouse_mst PRIMARY KEY (corp_id, warehouse_id)
);
