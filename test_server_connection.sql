-- =============================================
-- SQL Server Instance Connection Test
-- Server: DESKTOP-17P73P0\SQLEXPRESS
-- =============================================

-- Test 1: Check SQL Server Version and Instance
SELECT 
    @@SERVERNAME as 'Server Name',
    @@VERSION as 'SQL Server Version',
    SERVERPROPERTY('ProductVersion') as 'Product Version',
    SERVERPROPERTY('ProductLevel') as 'Product Level',
    SERVERPROPERTY('Edition') as 'Edition';

-- Test 2: Check if database exists
SELECT 
    name as 'Database Name',
    database_id,
    create_date,
    collation_name
FROM sys.databases 
WHERE name = 'api';

-- Test 3: Check login exists
SELECT 
    name as 'Login Name',
    type_desc,
    is_disabled,
    create_date
FROM sys.server_principals 
WHERE name = 'kmk_sql';

-- Test 4: If database exists, test connection
IF EXISTS (SELECT 1 FROM sys.databases WHERE name = 'api')
BEGIN
    PRINT 'Database "api" exists. Testing connection...'
    
    USE [api];
    
    -- Test user permissions in database
    SELECT 
        dp.name AS 'Principal Name',
        dp.type_desc AS 'Principal Type',
        r.name AS 'Role Name'
    FROM sys.database_principals dp
    LEFT JOIN sys.database_role_members rm ON dp.principal_id = rm.member_principal_id
    LEFT JOIN sys.database_principals r ON rm.role_principal_id = r.principal_id
    WHERE dp.name = 'kmk_sql';
    
    -- Test table count
    SELECT COUNT(*) as 'Total Tables' FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE';
    
    PRINT 'Connection test successful!'
END
ELSE
BEGIN
    PRINT 'Database "api" does not exist. Please run database_setup.sql first.'
END

-- Test 5: Check SQL Server Authentication mode
SELECT 
    CASE SERVERPROPERTY('IsIntegratedSecurityOnly')
        WHEN 1 THEN 'Windows Authentication Only'
        WHEN 0 THEN 'Mixed Mode (Windows and SQL Server Authentication)'
    END as 'Authentication Mode';

PRINT '=============================================='
PRINT 'Server Instance: DESKTOP-17P73P0\SQLEXPRESS'
PRINT 'Expected Database: api'
PRINT 'Expected User: kmk_sql'
PRINT 'Authentication: SQL Server Authentication'
PRINT '=============================================='
