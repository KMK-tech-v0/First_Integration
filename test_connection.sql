-- =============================================
-- Database Connection Test Script
-- Run this in SSMS to verify the setup
-- =============================================

USE [api];
GO

-- Test 1: Check if all tables exist
PRINT '=== Testing Database Tables ==='
SELECT 
    TABLE_NAME as 'Table Name',
    CASE WHEN TABLE_NAME IS NOT NULL THEN 'EXISTS' ELSE 'MISSING' END as 'Status'
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_NAME;

-- Test 2: Check if views exist
PRINT ''
PRINT '=== Testing Database Views ==='
SELECT 
    TABLE_NAME as 'View Name',
    'EXISTS' as 'Status'
FROM INFORMATION_SCHEMA.VIEWS 
ORDER BY TABLE_NAME;

-- Test 3: Check if stored procedures exist
PRINT ''
PRINT '=== Testing Stored Procedures ==='
SELECT 
    ROUTINE_NAME as 'Procedure Name',
    'EXISTS' as 'Status'
FROM INFORMATION_SCHEMA.ROUTINES 
WHERE ROUTINE_TYPE = 'PROCEDURE'
ORDER BY ROUTINE_NAME;

-- Test 4: Check user permissions
PRINT ''
PRINT '=== Testing User Permissions ==='
SELECT 
    dp.name AS principal_name,
    dp.type_desc AS principal_type,
    o.name AS object_name,
    p.permission_name,
    p.state_desc AS permission_state
FROM sys.database_permissions p
LEFT JOIN sys.objects o ON p.major_id = o.object_id
LEFT JOIN sys.database_principals dp ON p.grantee_principal_id = dp.principal_id
WHERE dp.name = 'kmk_sql'
ORDER BY dp.name, o.name, p.permission_name;

-- Test 5: Verify sample data
PRINT ''
PRINT '=== Testing Sample Data ==='
SELECT 'Users' as 'Table', COUNT(*) as 'Record Count' FROM [dbo].[users]
UNION ALL
SELECT 'Materials Info', COUNT(*) FROM [dbo].[materials_info]
UNION ALL
SELECT 'Services Info', COUNT(*) FROM [dbo].[services_info];

-- Test 6: Test stored procedure
PRINT ''
PRINT '=== Testing Transaction Number Generation ==='
DECLARE @test_trans_num NVARCHAR(50);
EXEC [dbo].[sp_generate_trans_num] @trans_num = @test_trans_num OUTPUT;
PRINT 'Generated Transaction Number: ' + @test_trans_num;

-- Test 7: Test inventory view
PRINT ''
PRINT '=== Testing Material Inventory View ==='
SELECT TOP 5 
    material_code,
    material_name,
    current_balance
FROM [dbo].[vw_material_inventory_summary]
ORDER BY material_code;

PRINT ''
PRINT '=== Database Connection Test Complete ==='
PRINT 'If you see data above, your database is properly configured!'
