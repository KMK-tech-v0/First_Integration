# MMP Fiber Fault Reporting System - Database Setup Instructions

## 📋 Overview
This guide will help you set up the SQL Server database for the MMP Fiber Fault Reporting System using SQL Server Management Studio (SSMS).

## 🔧 Prerequisites
- SQL Server installed (SQL Server 2016 or later recommended)
- SQL Server Management Studio (SSMS)
- SQL Server authentication enabled
- Administrative access to SQL Server

## 📊 Database Schema Overview

### Tables Created:
1. **users** - User authentication and authorization
2. **materials_info** - Material master data
3. **services_info** - Service master data  
4. **fault_reports** - Main fault reporting data
5. **report_photos** - Photo attachments for reports
6. **report_materials** - Materials used in each report
7. **report_services** - Services used in each report
8. **material_inventory** - Material inventory transactions
9. **system_logs** - Audit trail and system logging

### Views Created:
1. **vw_material_inventory_summary** - Material inventory summary with current balances

### Stored Procedures Created:
1. **sp_generate_trans_num** - Generate unique transaction numbers
2. **sp_add_inventory_transaction** - Add material inventory transactions

## 🚀 Setup Steps

### Step 1: Open SQL Server Management Studio
1. Launch SQL Server Management Studio (SSMS)
2. Connect to your SQL Server instance

### Step 2: Run Database Setup Script
1. Open the `database_setup.sql` file in SSMS
2. Execute the entire script (F5 or click Execute)
3. Wait for completion - you should see success messages

### Step 3: Verify Setup
1. Open the `test_connection.sql` file in SSMS
2. Execute the script to verify everything is working
3. Check that all tables, views, and procedures are created
4. Verify sample data is inserted

### Step 4: Database Connection Details
```
Server: localhost (or your SQL Server instance)
Database: api
Username: kmk_sql
Password: kmk@161998
Authentication: SQL Server Authentication
```

## 🔐 Security Configuration

### Database User Created:
- **Login Name**: kmk_sql
- **Password**: kmk@161998
- **Database**: api
- **Permissions**: 
  - db_datareader (read access)
  - db_datawriter (write access)
  - db_ddladmin (schema modification)
  - EXECUTE on stored procedures

### Default Admin User:
- **Username**: admin
- **Password**: admin123 (should be changed in production)
- **Role**: admin

## 📈 Sample Data Included

### Materials (6 items):
- FO-001: Single Mode Fiber Optic Cable
- FO-002: Multi Mode Fiber Optic Cable  
- CN-001: SC/UPC Connector
- CN-002: LC/UPC Connector
- SP-001: Fusion Splicer Machine
- TO-001: OTDR Tester

### Services (5 items):
- SV-001: Fiber Splicing Service
- SV-002: Cable Installation
- SV-003: Network Testing
- SV-004: Fault Diagnosis
- SV-005: Site Survey

## 🔄 Backend Integration

### Connection String:
```
Server=localhost;Database=api;User Id=kmk_sql;Password=kmk@161998;TrustServerCertificate=true;
```

### For Node.js (using mssql package):
```javascript
const config = {
    server: 'localhost',
    database: 'api',
    user: 'kmk_sql',
    password: 'kmk@161998',
    options: {
        encrypt: false,
        trustServerCertificate: true
    }
};
```

### For Python (using pyodbc):
```python
import pyodbc

connection_string = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=api;"
    "UID=kmk_sql;"
    "PWD=kmk@161998;"
    "TrustServerCertificate=yes;"
)
```

### For .NET Core (using SqlConnection):
```csharp
string connectionString = "Server=localhost;Database=api;User Id=kmk_sql;Password=kmk@161998;TrustServerCertificate=true;";
```

## 📁 File Structure
```
├── database_setup.sql          # Main database setup script
├── test_connection.sql         # Connection test script
├── database_config.json        # Configuration file for backend
└── DATABASE_SETUP_INSTRUCTIONS.md  # This file
```

## ⚡ Quick Verification Checklist

After running the setup, verify:
- [ ] Database 'api' is created
- [ ] User 'kmk_sql' can connect
- [ ] All 9 tables are created
- [ ] 1 view is created
- [ ] 2 stored procedures are created
- [ ] Sample data is inserted (1 admin user, 6 materials, 5 services)
- [ ] Test connection script runs without errors

## 🔧 Troubleshooting

### Common Issues:

1. **Login Failed for 'kmk_sql'**
   - Ensure SQL Server Authentication is enabled
   - Check if the login was created successfully
   - Verify password is correct

2. **Database 'api' does not exist**
   - Re-run the database_setup.sql script
   - Check SQL Server permissions

3. **Permission Denied Errors**
   - Ensure you're running SSMS as administrator
   - Check SQL Server service is running

4. **Connection Timeout**
   - Increase connection timeout in your application
   - Check SQL Server is accepting connections

## 🎯 Next Steps

1. **Backend Development**: Use the `database_config.json` file as reference for your API development
2. **Security**: Change default passwords in production
3. **Backup**: Set up regular database backups
4. **Monitoring**: Implement database monitoring and logging
5. **Performance**: Add additional indexes based on usage patterns

## 📞 Support

If you encounter any issues:
1. Check the `test_connection.sql` results
2. Verify SQL Server error logs
3. Ensure all prerequisites are met
4. Check firewall settings if connecting remotely

---

**Database Setup Complete!** 🎉

Your MMP Fiber Fault Reporting System database is now ready for backend integration.
