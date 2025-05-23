CREATE TABLE customer_mst (
    corp_id              INT             NOT NULL DEFAULT 0,
    customer_id          INT             NOT NULL IDENTITY(1,1),
    email                NVARCHAR(100)    NOT NULL,
    name                 NVARCHAR(100)    NOT NULL,
    gender               NVARCHAR(10)     NULL,
    birth_date           DATE            NULL,
    phone_number         NVARCHAR(20)     NULL,
    prefecture           NVARCHAR(50)     NULL,
    city                 NVARCHAR(50)     NULL,
    registration_date    DATE            NOT NULL DEFAULT GETDATE(),
    created_by           NVARCHAR(50)     NOT NULL DEFAULT 'SYSTEM',
    status               NVARCHAR(10)     NOT NULL DEFAULT '有効',

    CONSTRAINT PK_customer_mst PRIMARY KEY (corp_id, customer_id),
    CONSTRAINT UQ_customer_mst_email UNIQUE (email)
);
