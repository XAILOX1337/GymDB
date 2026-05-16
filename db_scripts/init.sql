-- ============================================================================
-- DATABASE: Sports Club Information System
-- DBMS: Microsoft SQL Server 2019/2022
-- ============================================================================
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'GymDB')
BEGIN
    CREATE DATABASE GymDB;
END
GO
USE GymDB;
GO

-- ============================================================================
-- 1. POSITIONS 
-- ============================================================================
IF OBJECT_ID('dbo.Positions', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Positions (
        PositionID INT IDENTITY(1,1) NOT NULL,
        Title NVARCHAR(100) NOT NULL,
        AccessLevel INT NOT NULL DEFAULT 1,
        CONSTRAINT PK_Positions PRIMARY KEY (PositionID),
        CONSTRAINT CHK_Positions_AccessLevel CHECK (AccessLevel >= 1 AND AccessLevel <= 5),
        CONSTRAINT UQ_Positions_Title UNIQUE (Title)
    );
END
GO

-- ============================================================================
-- 2. EMPLOYEES
-- ============================================================================
IF OBJECT_ID('dbo.Employees', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Employees (
        EmployeeID INT IDENTITY(1,1) NOT NULL,
        PositionID INT NOT NULL,
        LastName NVARCHAR(100) NOT NULL,
        FirstName NVARCHAR(100) NOT NULL,
        MiddleName NVARCHAR(100) NULL,
        Login NVARCHAR(50) NOT NULL,
        PasswordHash VARBINARY(64) NOT NULL,
        Phone NVARCHAR(20) NOT NULL,
        DeletedAt DATETIME NULL,
        CONSTRAINT PK_Employees PRIMARY KEY (EmployeeID),
        CONSTRAINT FK_Employees_Positions FOREIGN KEY (PositionID) REFERENCES dbo.Positions(PositionID) ON DELETE NO ACTION,
        CONSTRAINT UQ_Employees_Login UNIQUE (Login),
        CONSTRAINT UQ_Employees_Phone UNIQUE (Phone)
    );
END
GO

-- ============================================================================
-- 3. CLIENTS
-- ============================================================================
IF OBJECT_ID('dbo.Clients', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Clients (
        ClientID INT IDENTITY(1,1) NOT NULL,
        LastName NVARCHAR(100) NOT NULL,
        FirstName NVARCHAR(100) NOT NULL,
        MiddleName NVARCHAR(100) NULL,
        BirthDate DATE NOT NULL,
        Phone NVARCHAR(20) NOT NULL,
        Email NVARCHAR(100) NULL,
        PassportData NVARCHAR(50) NOT NULL,
        DeletedAt DATETIME NULL,
        CONSTRAINT PK_Clients PRIMARY KEY (ClientID),
        CONSTRAINT CHK_Clients_BirthDate CHECK (BirthDate < GETDATE()),
        CONSTRAINT UQ_Clients_Phone UNIQUE (Phone),
        CONSTRAINT UQ_Clients_Passport UNIQUE (PassportData)
    );
END
GO

-- ============================================================================
-- 4. SUBSCRIPTION TYPES (Reference table - subscription options)
-- ============================================================================
IF OBJECT_ID('dbo.SubscriptionTypes', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.SubscriptionTypes (
        SubscriptionTypeID INT IDENTITY(1,1) NOT NULL,
        Title NVARCHAR(100) NOT NULL,
        DurationDays INT NOT NULL,
        Price DECIMAL(10,2) NOT NULL,
        CONSTRAINT PK_SubscriptionTypes PRIMARY KEY (SubscriptionTypeID),
        CONSTRAINT CHK_SubscriptionTypes_Duration CHECK (DurationDays > 0),
        CONSTRAINT CHK_SubscriptionTypes_Price CHECK (Price >= 0),
        CONSTRAINT UQ_SubscriptionTypes_Title UNIQUE (Title)
    );
END
GO

-- ============================================================================
-- 5. PAYMENTS
-- ============================================================================
IF OBJECT_ID('dbo.Payments', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Payments (
        PaymentID INT IDENTITY(1,1) NOT NULL,
        Amount DECIMAL(10,2) NOT NULL,
        PaymentDate DATETIME NOT NULL DEFAULT GETDATE(),
        PaymentType NVARCHAR(50) NOT NULL DEFAULT 'Cash',
        Status NVARCHAR(20) NOT NULL DEFAULT 'Completed',
        CONSTRAINT PK_Payments PRIMARY KEY (PaymentID),
        CONSTRAINT CHK_Payments_Amount CHECK (Amount >= 0),
        CONSTRAINT CHK_Payments_Type CHECK (PaymentType IN ('Cash', 'Cashless', 'Card', 'Online')),
        CONSTRAINT CHK_Payments_Status CHECK (Status IN ('Completed', 'Pending', 'Cancelled'))
    );
END
GO

-- ============================================================================
-- 6. HALLS
-- ============================================================================
IF OBJECT_ID('dbo.Halls', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Halls (
        HallID INT IDENTITY(1,1) NOT NULL,
        Title NVARCHAR(100) NOT NULL,
        Capacity INT NOT NULL,
        Description NVARCHAR(500) NULL,
        CONSTRAINT PK_Halls PRIMARY KEY (HallID),
        CONSTRAINT CHK_Halls_Capacity CHECK (Capacity > 0),
        CONSTRAINT UQ_Halls_Title UNIQUE (Title)
    );
END
GO

-- ============================================================================
-- 7. CONTRACTS
-- ============================================================================
IF OBJECT_ID('dbo.Contracts', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Contracts (
        ContractID INT IDENTITY(1,1) NOT NULL,
        ClientID INT NOT NULL,
        SubscriptionTypeID INT NOT NULL,
        EmployeeID INT NOT NULL,
        PaymentID INT NOT NULL,
        StartDate DATE NOT NULL,
        EndDate DATE NOT NULL,
        Status NVARCHAR(20) NOT NULL DEFAULT 'Active',
        CONSTRAINT PK_Contracts PRIMARY KEY (ContractID),
        CONSTRAINT FK_Contracts_Client FOREIGN KEY (ClientID) REFERENCES dbo.Clients(ClientID) ON DELETE NO ACTION,
        CONSTRAINT FK_Contracts_SubscriptionType FOREIGN KEY (SubscriptionTypeID) REFERENCES dbo.SubscriptionTypes(SubscriptionTypeID) ON DELETE NO ACTION,
        CONSTRAINT FK_Contracts_Employee FOREIGN KEY (EmployeeID) REFERENCES dbo.Employees(EmployeeID) ON DELETE NO ACTION,
        CONSTRAINT FK_Contracts_Payment FOREIGN KEY (PaymentID) REFERENCES dbo.Payments(PaymentID) ON DELETE NO ACTION,
        CONSTRAINT CHK_Contracts_Dates CHECK (EndDate >= StartDate),
        CONSTRAINT CHK_Contracts_Status CHECK (Status IN ('Active', 'Completed', 'Terminated', 'Suspended'))
    );
END
GO

-- ============================================================================
-- 8. INDIVIDUAL TRAINING SCHEDULE
-- ============================================================================
IF OBJECT_ID('dbo.TrainingSchedule', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.TrainingSchedule (
        TrainingID INT IDENTITY(1,1) NOT NULL,
        ClientID INT NOT NULL,
        EmployeeID INT NOT NULL,
        HallID INT NOT NULL,
        PaymentID INT NOT NULL,
        TrainingDateTime DATETIME NOT NULL,
        TrainingName NVARCHAR(100) NOT NULL,
        Status NVARCHAR(20) NOT NULL DEFAULT 'Scheduled',
        CONSTRAINT PK_TrainingSchedule PRIMARY KEY (TrainingID),
        CONSTRAINT FK_TrainingSchedule_Client FOREIGN KEY (ClientID) REFERENCES dbo.Clients(ClientID) ON DELETE NO ACTION,
        CONSTRAINT FK_TrainingSchedule_Employee FOREIGN KEY (EmployeeID) REFERENCES dbo.Employees(EmployeeID) ON DELETE NO ACTION,
        CONSTRAINT FK_TrainingSchedule_Hall FOREIGN KEY (HallID) REFERENCES dbo.Halls(HallID) ON DELETE NO ACTION,
        CONSTRAINT FK_TrainingSchedule_Payment FOREIGN KEY (PaymentID) REFERENCES dbo.Payments(PaymentID) ON DELETE NO ACTION,
        CONSTRAINT CHK_TrainingSchedule_Date CHECK (TrainingDateTime > GETDATE() OR Status IN ('Completed', 'Cancelled')),
        CONSTRAINT CHK_TrainingSchedule_Status CHECK (Status IN ('Scheduled', 'Completed', 'Cancelled', 'Rescheduled'))
    );
END
GO

-- ============================================================================
-- 9. EQUIPMENT
-- ============================================================================
IF OBJECT_ID('dbo.Equipment', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Equipment (
        EquipmentID INT IDENTITY(1,1) NOT NULL,
        Title NVARCHAR(100) NOT NULL,
        Type NVARCHAR(50) NOT NULL,
        Status NVARCHAR(20) NOT NULL DEFAULT 'InUse',
        PurchaseDate DATE NULL,
        Description NVARCHAR(500) NULL,
        CONSTRAINT PK_Equipment PRIMARY KEY (EquipmentID),
        CONSTRAINT CHK_Equipment_Type CHECK (Type IN ('Machine', 'SportsEquipment', 'Furniture', 'Other')),
        CONSTRAINT CHK_Equipment_Status CHECK (Status IN ('InUse', 'UnderRepair', 'WrittenOff', 'InStock'))
    );
END
GO

-- ============================================================================
-- 10. SYSTEM LOG (logging)
-- ============================================================================
IF OBJECT_ID('dbo.SystemLog', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.SystemLog (
        LogID BIGINT IDENTITY(1,1) NOT NULL,
        EmployeeID INT NOT NULL,
        OperationTime DATETIME NOT NULL DEFAULT GETDATE(),
        OperationType NVARCHAR(50) NOT NULL,
        TableName NVARCHAR(100) NOT NULL,
        RecordID INT NOT NULL,
        Description NVARCHAR(500) NULL,
        CONSTRAINT PK_SystemLog PRIMARY KEY (LogID),
        CONSTRAINT FK_SystemLog_Employee FOREIGN KEY (EmployeeID) REFERENCES dbo.Employees(EmployeeID) ON DELETE NO ACTION,
        CONSTRAINT CHK_SystemLog_Type CHECK (OperationType IN ('INSERT', 'UPDATE', 'DELETE', 'SELECT', 'LOGIN', 'LOGOUT'))
    );
END
GO

-- ============================================================================
-- 11. VISITS (Client visit log)
-- ============================================================================
IF OBJECT_ID('dbo.Visits', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Visits (
        VisitID BIGINT IDENTITY(1,1) NOT NULL,
        ContractID INT NOT NULL,
        ClientID INT NOT NULL,
        CheckInTime DATETIME NOT NULL DEFAULT GETDATE(),
        CheckOutTime DATETIME NULL,
        CONSTRAINT PK_Visits PRIMARY KEY (VisitID),
        CONSTRAINT FK_Visits_Contract FOREIGN KEY (ContractID) REFERENCES dbo.Contracts(ContractID) ON DELETE NO ACTION,
        CONSTRAINT FK_Visits_Client FOREIGN KEY (ClientID) REFERENCES dbo.Clients(ClientID) ON DELETE NO ACTION
    );
END
GO

-- ============================================================================
-- INDEXES 
-- ============================================================================
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Clients_Phone' AND object_id = OBJECT_ID('dbo.Clients'))
    CREATE NONCLUSTERED INDEX IX_Clients_Phone ON dbo.Clients(Phone);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Clients_Passport' AND object_id = OBJECT_ID('dbo.Clients'))
    CREATE NONCLUSTERED INDEX IX_Clients_Passport ON dbo.Clients(PassportData);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Employees_Login' AND object_id = OBJECT_ID('dbo.Employees'))
    CREATE NONCLUSTERED INDEX IX_Employees_Login ON dbo.Employees(Login);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Clients_DeletedAt' AND object_id = OBJECT_ID('dbo.Clients'))
    CREATE NONCLUSTERED INDEX IX_Clients_DeletedAt ON dbo.Clients(DeletedAt) WHERE DeletedAt IS NOT NULL;

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Employees_DeletedAt' AND object_id = OBJECT_ID('dbo.Employees'))
    CREATE NONCLUSTERED INDEX IX_Employees_DeletedAt ON dbo.Employees(DeletedAt) WHERE DeletedAt IS NOT NULL;

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Contracts_ClientStatus' AND object_id = OBJECT_ID('dbo.Contracts'))
    CREATE NONCLUSTERED INDEX IX_Contracts_ClientStatus ON dbo.Contracts(ClientID, Status);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Contracts_Dates' AND object_id = OBJECT_ID('dbo.Contracts'))
    CREATE NONCLUSTERED INDEX IX_Contracts_Dates ON dbo.Contracts(StartDate, EndDate);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_TrainingSchedule_ClientDate' AND object_id = OBJECT_ID('dbo.TrainingSchedule'))
    CREATE NONCLUSTERED INDEX IX_TrainingSchedule_ClientDate ON dbo.TrainingSchedule(ClientID, TrainingDateTime);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_SystemLog_OperationTime' AND object_id = OBJECT_ID('dbo.SystemLog'))
    CREATE NONCLUSTERED INDEX IX_SystemLog_OperationTime ON dbo.SystemLog(OperationTime);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Visits_ClientCheckIn' AND object_id = OBJECT_ID('dbo.Visits'))
    CREATE NONCLUSTERED INDEX IX_Visits_ClientCheckIn ON dbo.Visits(ClientID, CheckInTime);
GO

-- ============================================================================
-- TRIGGERS
-- ============================================================================
-- Trigger: prevent employee deletion (soft delete)
IF OBJECT_ID('trg_Employees_PreventDelete', 'TR') IS NOT NULL
    DROP TRIGGER trg_Employees_PreventDelete;
GO
CREATE TRIGGER trg_Employees_PreventDelete
ON dbo.Employees
INSTEAD OF DELETE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE e SET DeletedAt = GETDATE()
    FROM dbo.Employees e INNER JOIN deleted d ON e.EmployeeID = d.EmployeeID
    WHERE e.DeletedAt IS NULL;

    INSERT INTO dbo.SystemLog (EmployeeID, OperationType, TableName, RecordID, Description)
    SELECT d.EmployeeID, 'DELETE', 'Employees', d.EmployeeID,
           'Soft delete employee: ' + d.LastName + ' ' + d.FirstName
    FROM deleted d;
END
GO

-- Trigger: prevent client deletion (soft delete)
IF OBJECT_ID('trg_Clients_PreventDelete', 'TR') IS NOT NULL DROP TRIGGER trg_Clients_PreventDelete;
GO
CREATE TRIGGER trg_Clients_PreventDelete
ON dbo.Clients
INSTEAD OF DELETE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE c SET DeletedAt = GETDATE()
    FROM dbo.Clients c INNER JOIN deleted d ON c.ClientID = d.ClientID
    WHERE c.DeletedAt IS NULL;
END
GO

-- Trigger: log changes in Contracts table
IF OBJECT_ID('trg_Contracts_Audit', 'TR') IS NOT NULL
    DROP TRIGGER trg_Contracts_Audit;
GO
CREATE TRIGGER trg_Contracts_Audit
ON dbo.Contracts
FOR INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;

    IF EXISTS (SELECT 1 FROM inserted) AND NOT EXISTS (SELECT 1 FROM deleted)
        INSERT INTO dbo.SystemLog (EmployeeID, OperationType, TableName, RecordID, Description)
        SELECT i.EmployeeID, 'INSERT', 'Contracts', i.ContractID, 'New contract created'
        FROM inserted i;

    IF EXISTS (SELECT 1 FROM inserted) AND EXISTS (SELECT 1 FROM deleted)
        INSERT INTO dbo.SystemLog (EmployeeID, OperationType, TableName, RecordID, Description)
        SELECT i.EmployeeID, 'UPDATE', 'Contracts', i.ContractID, 'Contract updated'
        FROM inserted i;

    IF EXISTS (SELECT 1 FROM deleted) AND NOT EXISTS (SELECT 1 FROM inserted)
        INSERT INTO dbo.SystemLog (EmployeeID, OperationType, TableName, RecordID, Description)
        SELECT d.EmployeeID, 'DELETE', 'Contracts', d.ContractID, 'Contract deleted'
        FROM deleted d;
END
GO

-- Trigger: log changes in Clients table
IF OBJECT_ID('trg_Clients_Audit', 'TR') IS NOT NULL DROP TRIGGER trg_Clients_Audit;
GO
CREATE TRIGGER trg_Clients_Audit
ON dbo.Clients
FOR UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @CurrentUserID INT = 1;
    IF UPDATE(LastName) OR UPDATE(FirstName) OR UPDATE(MiddleName) OR UPDATE(Phone) OR UPDATE(Email)
        INSERT INTO dbo.SystemLog (EmployeeID, OperationType, TableName, RecordID, Description)
        SELECT @CurrentUserID, 'UPDATE', 'Clients', i.ClientID, 'Client data updated' FROM inserted i;
END
GO

-- ============================================================================
-- VIEWS
-- ============================================================================
IF OBJECT_ID('vw_ActiveContracts', 'V') IS NOT NULL DROP VIEW vw_ActiveContracts;
GO
CREATE VIEW vw_ActiveContracts AS
SELECT
    c.ContractID,
    cl.LastName + ' ' + cl.FirstName + ' ' + ISNULL(cl.MiddleName, '') AS ClientFullName,
    cl.Phone AS ClientPhone,
    st.Title AS SubscriptionType,
    c.StartDate,
    c.EndDate,
    c.Status AS ContractStatus,
    p.Amount,
    e.LastName + ' ' + e.FirstName AS EmployeeFullName
FROM dbo.Contracts c
JOIN dbo.Clients cl ON c.ClientID = cl.ClientID
JOIN dbo.SubscriptionTypes st ON c.SubscriptionTypeID = st.SubscriptionTypeID
JOIN dbo.Payments p ON c.PaymentID = p.PaymentID
JOIN dbo.Employees e ON c.EmployeeID = e.EmployeeID
WHERE c.Status = 'Active' AND cl.DeletedAt IS NULL;
GO

IF OBJECT_ID('vw_TrainingSchedule', 'V') IS NOT NULL DROP VIEW vw_TrainingSchedule;
GO
CREATE VIEW vw_TrainingSchedule AS
SELECT
    ts.TrainingID,
    cl.LastName + ' ' + cl.FirstName AS ClientFullName,
    cl.Phone AS ClientPhone,
    ts.TrainingName,
    ts.TrainingDateTime,
    h.Title AS Hall,
    e.LastName + ' ' + e.FirstName AS TrainerFullName,
    ts.Status
FROM dbo.TrainingSchedule ts
JOIN dbo.Clients cl ON ts.ClientID = cl.ClientID
JOIN dbo.Halls h ON ts.HallID = h.HallID
JOIN dbo.Employees e ON ts.EmployeeID = e.EmployeeID
WHERE cl.DeletedAt IS NULL;
GO

IF OBJECT_ID('vw_VisitLog', 'V') IS NOT NULL DROP VIEW vw_VisitLog;
GO
CREATE VIEW vw_VisitLog AS
SELECT
    v.VisitID,
    cl.LastName + ' ' + cl.FirstName AS ClientFullName,
    v.CheckInTime,
    v.CheckOutTime,
    DATEDIFF(MINUTE, v.CheckInTime, ISNULL(v.CheckOutTime, GETDATE())) AS DurationMinutes,
    v.ContractID
FROM dbo.Visits v
JOIN dbo.Clients cl ON v.ClientID = cl.ClientID
JOIN dbo.Contracts c ON v.ContractID = c.ContractID
WHERE cl.DeletedAt IS NULL;
GO

-- ============================================================================
-- STORED PROCEDURES 
-- ============================================================================
IF OBJECT_ID('sp_RegisterClient', 'P') IS NOT NULL DROP PROCEDURE sp_RegisterClient;
GO
CREATE PROCEDURE sp_RegisterClient
    @LastName NVARCHAR(100),
    @FirstName NVARCHAR(100),
    @MiddleName NVARCHAR(100) = NULL,
    @BirthDate DATE,
    @Phone NVARCHAR(20),
    @Email NVARCHAR(100) = NULL,
    @PassportData NVARCHAR(50),
    @EmployeeID INT
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        BEGIN TRANSACTION;
        
        IF EXISTS (SELECT 1 FROM dbo.Clients WHERE Phone = @Phone AND DeletedAt IS NULL)
            THROW 50001, 'Client with this phone already exists', 16;
            
        IF EXISTS (SELECT 1 FROM dbo.Clients WHERE PassportData = @PassportData AND DeletedAt IS NULL)
            THROW 50002, 'Client with this passport data already exists', 16;
            
        IF @BirthDate >= GETDATE() OR @BirthDate < DATEADD(YEAR, -120, GETDATE())
            THROW 50003, 'Invalid birth date', 16;
            
        INSERT INTO dbo.Clients (LastName, FirstName, MiddleName, BirthDate, Phone, Email, PassportData)
        VALUES (@LastName, @FirstName, @MiddleName, @BirthDate, @Phone, @Email, @PassportData);
        
        DECLARE @NewID INT = SCOPE_IDENTITY();
        
        INSERT INTO dbo.SystemLog (EmployeeID, OperationType, TableName, RecordID, Description)
        VALUES (@EmployeeID, 'INSERT', 'Clients', @NewID, 'New client registered');
        
        COMMIT TRANSACTION;
        SELECT @NewID AS ClientID;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END
GO

IF OBJECT_ID('sp_CreateContract', 'P') IS NOT NULL DROP PROCEDURE sp_CreateContract;
GO
CREATE PROCEDURE sp_CreateContract
    @ClientID INT,
    @SubscriptionTypeID INT,
    @EmployeeID INT,
    @Amount DECIMAL(10,2),
    @PaymentType NVARCHAR(50) = 'Cash',
    @StartDate DATE = NULL
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        BEGIN TRANSACTION;
        
        IF NOT EXISTS (SELECT 1 FROM dbo.Clients WHERE ClientID = @ClientID AND DeletedAt IS NULL)
            THROW 50004, 'Client not found', 16;
            
        IF @Amount < 0 THROW 50005, 'Payment amount cannot be negative', 16;
            
        DECLARE @DurationDays INT, @Price DECIMAL(10,2);
        SELECT @DurationDays = DurationDays, @Price = Price FROM dbo.SubscriptionTypes WHERE SubscriptionTypeID = @SubscriptionTypeID;
        IF @DurationDays IS NULL THROW 50006, 'Subscription type not found', 16;
        
        IF @StartDate IS NULL SET @StartDate = CAST(GETDATE() AS DATE);
        DECLARE @EndDate DATE = DATEADD(DAY, @DurationDays, @StartDate);
        
        INSERT INTO dbo.Payments (Amount, PaymentType) VALUES (@Amount, @PaymentType);
        DECLARE @PaymentID INT = SCOPE_IDENTITY();
        
        INSERT INTO dbo.Contracts (ClientID, SubscriptionTypeID, EmployeeID, PaymentID, StartDate, EndDate)
        VALUES (@ClientID, @SubscriptionTypeID, @EmployeeID, @PaymentID, @StartDate, @EndDate);
        
        DECLARE @ContractID INT = SCOPE_IDENTITY();
        
        INSERT INTO dbo.SystemLog (EmployeeID, OperationType, TableName, RecordID, Description)
        VALUES (@EmployeeID, 'INSERT', 'Contracts', @ContractID, 'New contract created');
        
        COMMIT TRANSACTION;
        SELECT @ContractID AS ContractID;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END
GO

IF OBJECT_ID('sp_ScheduleTraining', 'P') IS NOT NULL DROP PROCEDURE sp_ScheduleTraining;
GO
CREATE PROCEDURE sp_ScheduleTraining
    @ClientID INT,
    @EmployeeID INT,
    @HallID INT,
    @TrainingName NVARCHAR(100),
    @TrainingDateTime DATETIME,
    @Amount DECIMAL(10,2) = 0,
    @LogEmployeeID INT
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        BEGIN TRANSACTION;
        
        IF NOT EXISTS (SELECT 1 FROM dbo.Clients WHERE ClientID = @ClientID AND DeletedAt IS NULL)
            THROW 50004, 'Client not found', 16;
        IF NOT EXISTS (SELECT 1 FROM dbo.Halls WHERE HallID = @HallID)
            THROW 50007, 'Hall not found', 16;
            
        DECLARE @PaymentID INT;
        INSERT INTO dbo.Payments (Amount, PaymentType, Status) VALUES (@Amount, 'Cash', 'Completed');
        SET @PaymentID = SCOPE_IDENTITY();
        
        INSERT INTO dbo.TrainingSchedule (ClientID, EmployeeID, HallID, PaymentID, TrainingDateTime, TrainingName)
        VALUES (@ClientID, @EmployeeID, @HallID, @PaymentID, @TrainingDateTime, @TrainingName);
        
        DECLARE @TrainingID INT = SCOPE_IDENTITY();
        
        INSERT INTO dbo.SystemLog (EmployeeID, OperationType, TableName, RecordID, Description)
        VALUES (@LogEmployeeID, 'INSERT', 'TrainingSchedule', @TrainingID, 'Client scheduled for training');
        
        COMMIT TRANSACTION;
        SELECT @TrainingID AS TrainingID;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END
GO

-- ============================================================================
-- INITIAL DATA
-- ============================================================================
IF NOT EXISTS (SELECT 1 FROM dbo.Positions)
    INSERT INTO dbo.Positions (Title, AccessLevel) VALUES
    ('Administrator', 5), ('Manager', 4), ('Trainer', 3), ('Receptionist', 2), ('Cleaner', 1);

IF NOT EXISTS (SELECT 1 FROM dbo.SubscriptionTypes)
    INSERT INTO dbo.SubscriptionTypes (Title, DurationDays, Price) VALUES
    ('1 Month', 30, 3500.00), ('3 Months', 90, 9000.00), ('6 Months', 180, 16000.00), ('1 Year', 365, 28000.00), ('Unlimited (Year)', 365, 45000.00);

IF NOT EXISTS (SELECT 1 FROM dbo.Halls)
    INSERT INTO dbo.Halls (Title, Capacity, Description) VALUES
    ('Gym Hall', 50, 'Main hall with exercise machines'), ('Cardio Zone', 30, 'Area with cardio equipment'), ('Group Programs Hall', 40, 'Hall for group classes'), ('Swimming Pool', 20, '25-meter pool'), ('SPA Zone', 15, 'Relaxation and recovery area');

IF NOT EXISTS (SELECT 1 FROM dbo.Equipment)
    INSERT INTO dbo.Equipment (Title, Type, Status) VALUES
    ('Treadmill #1', 'Machine', 'InUse'), ('Treadmill #2', 'Machine', 'InUse'), ('Elliptical #1', 'Machine', 'InUse'), ('Exercise Bike #1', 'Machine', 'UnderRepair'), ('Dumbbells 5kg', 'SportsEquipment', 'InUse'), ('Dumbbells 10kg', 'SportsEquipment', 'InUse'), ('Barbell', 'SportsEquipment', 'InUse'), ('Bench Press', 'SportsEquipment', 'InUse');
GO

-- ============================================================================
-- COMPLETION
-- ============================================================================
PRINT 'SportClubDB database initialized successfully!';
GO