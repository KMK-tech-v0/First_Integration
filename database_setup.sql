-- =============================================
-- MMP Fiber Fault Reporting System Database Schema
-- SQL Server Database Setup Script
-- =============================================

-- Create Database
USE master;
GO

IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'api')
BEGIN
    CREATE DATABASE [api];
END
GO

USE [api];
GO

-- =============================================
-- 1. Users Table (Authentication & Authorization)
-- =============================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
BEGIN
    CREATE TABLE [dbo].[users] (
        [id] INT IDENTITY(1,1) PRIMARY KEY,
        [username] NVARCHAR(50) NOT NULL UNIQUE,
        [password_hash] NVARCHAR(255) NOT NULL,
        [role] NVARCHAR(20) NOT NULL DEFAULT 'user',
        [email] NVARCHAR(100) NULL,
        [full_name] NVARCHAR(100) NULL,
        [is_active] BIT NOT NULL DEFAULT 1,
        [created_at] DATETIME2 NOT NULL DEFAULT GETDATE(),
        [updated_at] DATETIME2 NOT NULL DEFAULT GETDATE(),
        [last_login] DATETIME2 NULL,
        CONSTRAINT [CK_users_role] CHECK ([role] IN ('admin', 'user', 'viewer'))
    );
    
    -- Create indexes
    CREATE INDEX [IX_users_username] ON [dbo].[users] ([username]);
    CREATE INDEX [IX_users_role] ON [dbo].[users] ([role]);
    CREATE INDEX [IX_users_is_active] ON [dbo].[users] ([is_active]);
END
GO

-- =============================================
-- 2. Materials Info Table
-- =============================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='materials_info' AND xtype='U')
BEGIN
    CREATE TABLE [dbo].[materials_info] (
        [id] INT IDENTITY(1,1) PRIMARY KEY,
        [material_code] NVARCHAR(50) NOT NULL UNIQUE,
        [material_name] NVARCHAR(200) NOT NULL,
        [material_type] NVARCHAR(100) NULL,
        [uom] NVARCHAR(20) NULL, -- Unit of Measurement
        [unit_price] DECIMAL(18,2) NULL,
        [kcn_price] DECIMAL(18,2) NULL,
        [sgg_price] DECIMAL(18,2) NULL,
        [description] NTEXT NULL,
        [is_active] BIT NOT NULL DEFAULT 1,
        [created_at] DATETIME2 NOT NULL DEFAULT GETDATE(),
        [updated_at] DATETIME2 NOT NULL DEFAULT GETDATE(),
        [created_by] INT NULL,
        [updated_by] INT NULL,
        FOREIGN KEY ([created_by]) REFERENCES [dbo].[users]([id]),
        FOREIGN KEY ([updated_by]) REFERENCES [dbo].[users]([id])
    );
    
    -- Create indexes
    CREATE INDEX [IX_materials_info_code] ON [dbo].[materials_info] ([material_code]);
    CREATE INDEX [IX_materials_info_type] ON [dbo].[materials_info] ([material_type]);
    CREATE INDEX [IX_materials_info_active] ON [dbo].[materials_info] ([is_active]);
END
GO

-- =============================================
-- 3. Services Info Table
-- =============================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='services_info' AND xtype='U')
BEGIN
    CREATE TABLE [dbo].[services_info] (
        [id] INT IDENTITY(1,1) PRIMARY KEY,
        [service_code] NVARCHAR(50) NOT NULL UNIQUE,
        [service_name] NVARCHAR(200) NOT NULL,
        [service_type] NVARCHAR(100) NULL,
        [uom] NVARCHAR(20) NULL, -- Unit of Measurement
        [unit_price] DECIMAL(18,2) NULL,
        [kcn_price] DECIMAL(18,2) NULL,
        [sgg_price] DECIMAL(18,2) NULL,
        [description] NTEXT NULL,
        [is_active] BIT NOT NULL DEFAULT 1,
        [created_at] DATETIME2 NOT NULL DEFAULT GETDATE(),
        [updated_at] DATETIME2 NOT NULL DEFAULT GETDATE(),
        [created_by] INT NULL,
        [updated_by] INT NULL,
        FOREIGN KEY ([created_by]) REFERENCES [dbo].[users]([id]),
        FOREIGN KEY ([updated_by]) REFERENCES [dbo].[users]([id])
    );
    
    -- Create indexes
    CREATE INDEX [IX_services_info_code] ON [dbo].[services_info] ([service_code]);
    CREATE INDEX [IX_services_info_type] ON [dbo].[services_info] ([service_type]);
    CREATE INDEX [IX_services_info_active] ON [dbo].[services_info] ([is_active]);
END
GO

-- =============================================
-- 4. Fault Reports Table
-- =============================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='fault_reports' AND xtype='U')
BEGIN
    CREATE TABLE [dbo].[fault_reports] (
        [id] INT IDENTITY(1,1) PRIMARY KEY,
        [trans_num] NVARCHAR(50) NOT NULL UNIQUE,
        [project_name] NVARCHAR(200) NOT NULL,
        [fault_name] NVARCHAR(200) NOT NULL,
        [circuit_id] NVARCHAR(100) NULL,
        [customer_name] NVARCHAR(200) NULL,
        [customer_address] NTEXT NULL,
        [pic] NVARCHAR(100) NULL, -- Person in Charge
        [region] NVARCHAR(50) NOT NULL,
        [township] NVARCHAR(100) NOT NULL,
        [location_lat] DECIMAL(10,8) NULL, -- GPS Latitude
        [location_long] DECIMAL(11,8) NULL, -- GPS Longitude
        [m_latitude] DECIMAL(10,8) NULL, -- Manual Latitude
        [m_longitude] DECIMAL(11,8) NULL, -- Manual Longitude
        [raised_time] DATETIME2 NOT NULL,
        [cleared_time] DATETIME2 NULL,
        [duration] AS (
            CASE 
                WHEN [cleared_time] IS NOT NULL AND [raised_time] IS NOT NULL
                THEN DATEDIFF(MINUTE, [raised_time], [cleared_time])
                ELSE NULL
            END
        ), -- Computed column for duration in minutes
        [root_cause] NTEXT NULL,
        [status] NVARCHAR(20) NOT NULL DEFAULT 'open',
        [priority] NVARCHAR(20) NOT NULL DEFAULT 'medium',
        [created_at] DATETIME2 NOT NULL DEFAULT GETDATE(),
        [updated_at] DATETIME2 NOT NULL DEFAULT GETDATE(),
        [created_by] INT NOT NULL,
        [updated_by] INT NULL,
        FOREIGN KEY ([created_by]) REFERENCES [dbo].[users]([id]),
        FOREIGN KEY ([updated_by]) REFERENCES [dbo].[users]([id]),
        CONSTRAINT [CK_fault_reports_status] CHECK ([status] IN ('open', 'in_progress', 'resolved', 'closed')),
        CONSTRAINT [CK_fault_reports_priority] CHECK ([priority] IN ('low', 'medium', 'high', 'critical'))
    );
    
    -- Create indexes
    CREATE INDEX [IX_fault_reports_trans_num] ON [dbo].[fault_reports] ([trans_num]);
    CREATE INDEX [IX_fault_reports_region] ON [dbo].[fault_reports] ([region]);
    CREATE INDEX [IX_fault_reports_status] ON [dbo].[fault_reports] ([status]);
    CREATE INDEX [IX_fault_reports_raised_time] ON [dbo].[fault_reports] ([raised_time]);
    CREATE INDEX [IX_fault_reports_created_by] ON [dbo].[fault_reports] ([created_by]);
END
GO

-- =============================================
-- 5. Report Photos Table
-- =============================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='report_photos' AND xtype='U')
BEGIN
    CREATE TABLE [dbo].[report_photos] (
        [id] INT IDENTITY(1,1) PRIMARY KEY,
        [report_id] INT NOT NULL,
        [original_name] NVARCHAR(255) NOT NULL,
        [unique_name] NVARCHAR(255) NOT NULL,
        [file_path] NVARCHAR(500) NOT NULL,
        [file_size] BIGINT NOT NULL,
        [content_type] NVARCHAR(100) NOT NULL,
        [label] NVARCHAR(200) NULL,
        [uploaded_at] DATETIME2 NOT NULL DEFAULT GETDATE(),
        [uploaded_by] INT NOT NULL,
        FOREIGN KEY ([report_id]) REFERENCES [dbo].[fault_reports]([id]) ON DELETE CASCADE,
        FOREIGN KEY ([uploaded_by]) REFERENCES [dbo].[users]([id])
    );
    
    -- Create indexes
    CREATE INDEX [IX_report_photos_report_id] ON [dbo].[report_photos] ([report_id]);
    CREATE INDEX [IX_report_photos_uploaded_by] ON [dbo].[report_photos] ([uploaded_by]);
END
GO

-- =============================================
-- 6. Report Materials Table (Materials used in reports)
-- =============================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='report_materials' AND xtype='U')
BEGIN
    CREATE TABLE [dbo].[report_materials] (
        [id] INT IDENTITY(1,1) PRIMARY KEY,
        [report_id] INT NOT NULL,
        [material_code] NVARCHAR(50) NOT NULL,
        [material_name] NVARCHAR(200) NOT NULL,
        [material_type] NVARCHAR(100) NULL,
        [uom] NVARCHAR(20) NULL,
        [material_usage] DECIMAL(18,4) NOT NULL,
        [unit_cost] DECIMAL(18,2) NULL,
        [total_cost] AS ([material_usage] * [unit_cost]), -- Computed column
        [notes] NTEXT NULL,
        [created_at] DATETIME2 NOT NULL DEFAULT GETDATE(),
        FOREIGN KEY ([report_id]) REFERENCES [dbo].[fault_reports]([id]) ON DELETE CASCADE,
        FOREIGN KEY ([material_code]) REFERENCES [dbo].[materials_info]([material_code])
    );
    
    -- Create indexes
    CREATE INDEX [IX_report_materials_report_id] ON [dbo].[report_materials] ([report_id]);
    CREATE INDEX [IX_report_materials_material_code] ON [dbo].[report_materials] ([material_code]);
END
GO

-- =============================================
-- 7. Report Services Table (Services used in reports)
-- =============================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='report_services' AND xtype='U')
BEGIN
    CREATE TABLE [dbo].[report_services] (
        [id] INT IDENTITY(1,1) PRIMARY KEY,
        [report_id] INT NOT NULL,
        [service_code] NVARCHAR(50) NOT NULL,
        [service_name] NVARCHAR(200) NOT NULL,
        [service_type] NVARCHAR(100) NULL,
        [uom] NVARCHAR(20) NULL,
        [service_usage] DECIMAL(18,4) NOT NULL,
        [unit_cost] DECIMAL(18,2) NULL,
        [total_cost] AS ([service_usage] * [unit_cost]), -- Computed column
        [notes] NTEXT NULL,
        [created_at] DATETIME2 NOT NULL DEFAULT GETDATE(),
        FOREIGN KEY ([report_id]) REFERENCES [dbo].[fault_reports]([id]) ON DELETE CASCADE,
        FOREIGN KEY ([service_code]) REFERENCES [dbo].[services_info]([service_code])
    );
    
    -- Create indexes
    CREATE INDEX [IX_report_services_report_id] ON [dbo].[report_services] ([report_id]);
    CREATE INDEX [IX_report_services_service_code] ON [dbo].[report_services] ([service_code]);
END
GO

-- =============================================
-- 8. Material Inventory Table
-- =============================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='material_inventory' AND xtype='U')
BEGIN
    CREATE TABLE [dbo].[material_inventory] (
        [id] INT IDENTITY(1,1) PRIMARY KEY,
        [material_code] NVARCHAR(50) NOT NULL,
        [transaction_type] NVARCHAR(20) NOT NULL, -- receipt, issue, return, damage, adjustment
        [transaction_ref] NVARCHAR(100) NULL, -- Reference number (PO, Job#, etc.)
        [quantity] DECIMAL(18,4) NOT NULL,
        [unit_cost] DECIMAL(18,2) NULL,
        [total_value] AS ([quantity] * [unit_cost]), -- Computed column
        [transaction_date] DATETIME2 NOT NULL DEFAULT GETDATE(),
        [notes] NTEXT NULL,
        [created_by] INT NOT NULL,
        [created_at] DATETIME2 NOT NULL DEFAULT GETDATE(),
        FOREIGN KEY ([material_code]) REFERENCES [dbo].[materials_info]([material_code]),
        FOREIGN KEY ([created_by]) REFERENCES [dbo].[users]([id]),
        CONSTRAINT [CK_material_inventory_type] CHECK ([transaction_type] IN ('receipt', 'issue', 'return', 'damage', 'adjustment'))
    );
    
    -- Create indexes
    CREATE INDEX [IX_material_inventory_material_code] ON [dbo].[material_inventory] ([material_code]);
    CREATE INDEX [IX_material_inventory_type] ON [dbo].[material_inventory] ([transaction_type]);
    CREATE INDEX [IX_material_inventory_date] ON [dbo].[material_inventory] ([transaction_date]);
    CREATE INDEX [IX_material_inventory_created_by] ON [dbo].[material_inventory] ([created_by]);
END
GO

-- =============================================
-- 9. System Logs Table (Audit Trail)
-- =============================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='system_logs' AND xtype='U')
BEGIN
    CREATE TABLE [dbo].[system_logs] (
        [id] INT IDENTITY(1,1) PRIMARY KEY,
        [user_id] INT NULL,
        [action] NVARCHAR(100) NOT NULL,
        [table_name] NVARCHAR(100) NULL,
        [record_id] INT NULL,
        [old_values] NTEXT NULL,
        [new_values] NTEXT NULL,
        [ip_address] NVARCHAR(45) NULL,
        [user_agent] NVARCHAR(500) NULL,
        [created_at] DATETIME2 NOT NULL DEFAULT GETDATE(),
        FOREIGN KEY ([user_id]) REFERENCES [dbo].[users]([id])
    );
    
    -- Create indexes
    CREATE INDEX [IX_system_logs_user_id] ON [dbo].[system_logs] ([user_id]);
    CREATE INDEX [IX_system_logs_action] ON [dbo].[system_logs] ([action]);
    CREATE INDEX [IX_system_logs_created_at] ON [dbo].[system_logs] ([created_at]);
END
GO

-- =============================================
-- 10. Create Views for Material Inventory Summary
-- =============================================
IF NOT EXISTS (SELECT * FROM sys.views WHERE name = 'vw_material_inventory_summary')
BEGIN
    EXEC('
    CREATE VIEW [dbo].[vw_material_inventory_summary] AS
    SELECT 
        mi.material_code,
        mi.material_name,
        mi.material_type,
        mi.uom,
        ISNULL(SUM(CASE WHEN inv.transaction_type = ''receipt'' THEN inv.quantity ELSE 0 END), 0) as total_receipts,
        ISNULL(SUM(CASE WHEN inv.transaction_type = ''issue'' THEN inv.quantity ELSE 0 END), 0) as total_issues,
        ISNULL(SUM(CASE WHEN inv.transaction_type = ''return'' THEN inv.quantity ELSE 0 END), 0) as total_returns,
        ISNULL(SUM(CASE WHEN inv.transaction_type = ''damage'' THEN inv.quantity ELSE 0 END), 0) as total_damages,
        ISNULL(SUM(CASE WHEN inv.transaction_type = ''adjustment'' THEN inv.quantity ELSE 0 END), 0) as total_adjustments,
        ISNULL(SUM(
            CASE 
                WHEN inv.transaction_type IN (''receipt'', ''return'') THEN inv.quantity
                WHEN inv.transaction_type IN (''issue'', ''damage'') THEN -inv.quantity
                WHEN inv.transaction_type = ''adjustment'' THEN inv.quantity
                ELSE 0
            END
        ), 0) as current_balance,
        MAX(inv.transaction_date) as last_transaction_date
    FROM [dbo].[materials_info] mi
    LEFT JOIN [dbo].[material_inventory] inv ON mi.material_code = inv.material_code
    WHERE mi.is_active = 1
    GROUP BY mi.material_code, mi.material_name, mi.material_type, mi.uom
    ')
END
GO

-- =============================================
-- 11. Create Stored Procedures
-- =============================================

-- Procedure to generate transaction numbers
IF EXISTS (SELECT * FROM sys.objects WHERE type = 'P' AND name = 'sp_generate_trans_num')
    DROP PROCEDURE [dbo].[sp_generate_trans_num];
GO

CREATE PROCEDURE [dbo].[sp_generate_trans_num]
    @prefix NVARCHAR(10) = 'RPT',
    @trans_num NVARCHAR(50) OUTPUT
AS
BEGIN
    DECLARE @year NVARCHAR(4) = YEAR(GETDATE())
    DECLARE @month NVARCHAR(2) = FORMAT(GETDATE(), 'MM')
    DECLARE @sequence INT
    
    -- Get next sequence number for current month
    SELECT @sequence = ISNULL(MAX(CAST(RIGHT(trans_num, 4) AS INT)), 0) + 1
    FROM [dbo].[fault_reports]
    WHERE trans_num LIKE @prefix + @year + @month + '%'
    
    SET @trans_num = @prefix + @year + @month + FORMAT(@sequence, '0000')
END
GO

-- Procedure to add material inventory transaction
IF EXISTS (SELECT * FROM sys.objects WHERE type = 'P' AND name = 'sp_add_inventory_transaction')
    DROP PROCEDURE [dbo].[sp_add_inventory_transaction];
GO

CREATE PROCEDURE [dbo].[sp_add_inventory_transaction]
    @material_code NVARCHAR(50),
    @transaction_type NVARCHAR(20),
    @quantity DECIMAL(18,4),
    @unit_cost DECIMAL(18,2) = NULL,
    @transaction_ref NVARCHAR(100) = NULL,
    @notes NTEXT = NULL,
    @created_by INT
AS
BEGIN
    BEGIN TRY
        -- Validate material exists
        IF NOT EXISTS (SELECT 1 FROM [dbo].[materials_info] WHERE material_code = @material_code AND is_active = 1)
        BEGIN
            RAISERROR('Material code does not exist or is inactive', 16, 1)
            RETURN
        END
        
        -- Insert transaction
        INSERT INTO [dbo].[material_inventory] 
        (material_code, transaction_type, transaction_ref, quantity, unit_cost, notes, created_by)
        VALUES 
        (@material_code, @transaction_type, @transaction_ref, @quantity, @unit_cost, @notes, @created_by)
        
        -- Log the action
        INSERT INTO [dbo].[system_logs] (user_id, action, table_name, record_id, new_values)
        VALUES (@created_by, 'INSERT', 'material_inventory', SCOPE_IDENTITY(), 
                'Material: ' + @material_code + ', Type: ' + @transaction_type + ', Qty: ' + CAST(@quantity AS NVARCHAR))
                
    END TRY
    BEGIN CATCH
        THROW
    END CATCH
END
GO

-- =============================================
-- 12. Insert Default Data
-- =============================================

-- Insert default admin user (password hash for 'admin123' - should be properly hashed in production)
IF NOT EXISTS (SELECT 1 FROM [dbo].[users] WHERE username = 'admin')
BEGIN
    INSERT INTO [dbo].[users] (username, password_hash, role, full_name, email)
    VALUES ('admin', '$2b$12$LQv3c1yqBwWVHGkGH2Yk6OeTQGP0YC8LjRzMmjLQEj9N7CfUIz.V6', 'admin', 'System Administrator', 'admin@mmp.com');
END
GO

-- Insert sample materials
IF NOT EXISTS (SELECT 1 FROM [dbo].[materials_info] WHERE material_code = 'FO-001')
BEGIN
    INSERT INTO [dbo].[materials_info] (material_code, material_name, material_type, uom, unit_price, created_by)
    VALUES 
    ('FO-001', 'Single Mode Fiber Optic Cable', 'Cable', 'Meter', 15.50, 1),
    ('FO-002', 'Multi Mode Fiber Optic Cable', 'Cable', 'Meter', 12.75, 1),
    ('CN-001', 'SC/UPC Connector', 'Connector', 'Piece', 5.25, 1),
    ('CN-002', 'LC/UPC Connector', 'Connector', 'Piece', 6.80, 1),
    ('SP-001', 'Fusion Splicer Machine', 'Equipment', 'Unit', 15000.00, 1),
    ('TO-001', 'OTDR Tester', 'Tool', 'Unit', 8500.00, 1);
END
GO

-- Insert sample services
IF NOT EXISTS (SELECT 1 FROM [dbo].[services_info] WHERE service_code = 'SV-001')
BEGIN
    INSERT INTO [dbo].[services_info] (service_code, service_name, service_type, uom, unit_price, created_by)
    VALUES 
    ('SV-001', 'Fiber Splicing Service', 'Installation', 'Joint', 25.00, 1),
    ('SV-002', 'Cable Installation', 'Installation', 'Meter', 8.50, 1),
    ('SV-003', 'Network Testing', 'Testing', 'Hour', 75.00, 1),
    ('SV-004', 'Fault Diagnosis', 'Maintenance', 'Hour', 85.00, 1),
    ('SV-005', 'Site Survey', 'Planning', 'Site', 150.00, 1);
END
GO

-- =============================================
-- 13. Create Database User for API Access
-- =============================================
USE master;
GO

-- Create login if it doesn't exist
IF NOT EXISTS (SELECT name FROM sys.server_principals WHERE name = 'kmk_sql')
BEGIN
    CREATE LOGIN [kmk_sql] WITH PASSWORD = 'kmk@161998';
END
GO

USE [api];
GO

-- Create user if it doesn't exist
IF NOT EXISTS (SELECT name FROM sys.database_principals WHERE name = 'kmk_sql')
BEGIN
    CREATE USER [kmk_sql] FOR LOGIN [kmk_sql];
END
GO

-- Grant permissions
ALTER ROLE [db_datareader] ADD MEMBER [kmk_sql];
ALTER ROLE [db_datawriter] ADD MEMBER [kmk_sql];
ALTER ROLE [db_ddladmin] ADD MEMBER [kmk_sql];
GO

-- Grant execute permissions on stored procedures
GRANT EXECUTE ON [dbo].[sp_generate_trans_num] TO [kmk_sql];
GRANT EXECUTE ON [dbo].[sp_add_inventory_transaction] TO [kmk_sql];
GO

-- =============================================
-- 14. Final Setup Complete Message
-- =============================================
PRINT '=================================================='
PRINT 'MMP Fiber Fault Reporting System Database Setup Complete!'
PRINT '=================================================='
PRINT 'Database: api'
PRINT 'User: kmk_sql'
PRINT 'Tables Created: 9'
PRINT 'Views Created: 1'
PRINT 'Stored Procedures Created: 2'
PRINT 'Sample Data Inserted: Yes'
PRINT '=================================================='
PRINT 'You can now connect your application using:'
PRINT 'Server: localhost'
PRINT 'Database: api'
PRINT 'Username: kmk_sql'
PRINT 'Password: kmk@161998'
PRINT 'Authentication: SQL Server Authentication'
PRINT '=================================================='
GO
