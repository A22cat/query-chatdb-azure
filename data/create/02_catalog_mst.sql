CREATE TABLE catalog_mst (
    corp_id            INT                     NOT NULL DEFAULT 0,
    catalog_id         INT                     NOT NULL IDENTITY(1,1),
    catalog_code       NVARCHAR(20)             NOT NULL,
    catalog_name       NVARCHAR(100)            NOT NULL,
    category           NVARCHAR(50)             NOT NULL DEFAULT '一般',           -- 一般 / 季節 / 限定
    season             NVARCHAR(30)             NULL,                              -- 春 / 夏 / 秋 / 冬
    publish_date       DATE                    NOT NULL,
    expire_date        DATE                    NULL,
    status             NVARCHAR(20)             NOT NULL DEFAULT '有効',           -- 有効 / 無効
    language           NVARCHAR(20)             NOT NULL DEFAULT '日本語',         -- 日本語 / 英語 / その他
    region             NVARCHAR(50)             NULL,                              -- 関東 / 関西 / 海外
    created_by         NVARCHAR(50)             NOT NULL DEFAULT 'SYSTEM',         -- APIまたはユーザー名
    created_at         DATETIME                NOT NULL DEFAULT GETDATE(),

    CONSTRAINT PK_catalog_mst PRIMARY KEY (corp_id, catalog_id),
    CONSTRAINT UQ_catalog_code UNIQUE (catalog_code)
);
