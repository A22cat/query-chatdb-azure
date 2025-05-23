CREATE TABLE products_mst (
    corp_id                INT             NOT NULL DEFAULT 0,             -- 会社ID
    product_id             INT             NOT NULL IDENTITY(1,1),          -- 製品ID（自動採番）
    product_code           NVARCHAR(20)     NOT NULL,                         -- 製品コード（UK）
    name                   NVARCHAR(100)    NOT NULL,                         -- 製品名
    category               NVARCHAR(50)     NOT NULL DEFAULT 'その他',       -- カテゴリ（初期値：その他）
    price                  DECIMAL(10,2)   NOT NULL DEFAULT 0.00,           -- 税抜価格
    tax_category           NVARCHAR(10)     NOT NULL DEFAULT '課税',         -- 税区分
    supplier_name          NVARCHAR(100)    NULL,                             -- 仕入先名
    release_date           DATE            NULL,                             -- 発売日
    open_flg_status        NVARCHAR(20)     NOT NULL DEFAULT '0',            -- オープンフラグ（0：クローズ、1：オープン、2：再オープン）
    open_datetime          DATETIME        NULL,                             -- OPEN日時
    close_datetime         DATETIME        NULL,                             -- CLOSE日時
    reopen_datetime        DATETIME        NULL,                             -- 再OPEN日時
    description            NVARCHAR(200)   NULL,                             -- 製品説明
    created_at             INT             NOT NULL DEFAULT 0,              -- 登録ユーザーID
    input_user_id          DATETIME        NOT NULL DEFAULT GETDATE(),      -- 登録日時
    input_datetime         INT             NULL,                             -- 最終更新ユーザーID
    lastupdate_datetime    DATETIME        NULL,                             -- 最終更新日時
    rec_status             NUMERIC(5,0)    NOT NULL DEFAULT 0,              -- 状態フラグ

    -- 主キー：複合主キー（corp_id, product_id）
    CONSTRAINT PK_products_mst PRIMARY KEY (corp_id, product_id),

    -- 一意制約（製品コード）
    CONSTRAINT UQ_products_mst_product_code UNIQUE (product_code)
);
