CREATE TABLE employees_mst (
    corp_id INT NOT NULL DEFAULT 0, -- 会社ID
    employee_id INT NOT NULL IDENTITY(1,1), -- 従業員ID（自動採番）
    name NVARCHAR(100) NOT NULL, -- 氏名
    department NVARCHAR(50) NOT NULL DEFAULT '営業', -- 部署（デフォルト値は'営業'）
    role NVARCHAR(50) NOT NULL DEFAULT '一般', -- 役職（デフォルト値は'一般'）
    email NVARCHAR(150) UNIQUE, -- メールアドレス（一意）
    phone_number NVARCHAR(20) NULL, -- 電話番号（NULL許可）
    hire_date DATE NOT NULL DEFAULT CONVERT(DATE, GETDATE()), -- 入社日（デフォルトは現在日付）
    status NVARCHAR(20) NOT NULL DEFAULT '在籍', -- ステータス（デフォルト値は'在籍'）
    manager_id INT NULL, -- 上司ID（自己参照外部キー）
    salary DECIMAL(10, 2) NULL DEFAULT 0, -- 月給（万単位）
    created_at DATETIME NOT NULL DEFAULT GETDATE(), -- 作成日時（デフォルトは現在日付）

    CONSTRAINT PK_employees_mst PRIMARY KEY (corp_id, employee_id), -- 複合主キー
    CONSTRAINT FK_manager FOREIGN KEY (corp_id, manager_id)
        REFERENCES employees_mst (corp_id, employee_id) -- 上司ID（自己参照外部キー）
);
