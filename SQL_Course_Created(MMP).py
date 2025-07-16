import os

# The HTML content for your  SQL course, now with definitions,
# a  quote, and expanded SQL functions (Window Functions, Advanced Joins, JSON Handling).
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=0.9">
    <title> SQL Course by Kaung Myat Kyaw</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <!-- Prism.js for syntax highlighting -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css" rel="stylesheet" />
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f3f4f6;
            color: #374151;
            line-height: 1.6;
        }
        .container {
            max-width: 960px;
            margin: 2rem auto;
            padding: 2rem;
            background-color: #ffffff;
            border-radius: 0.75rem;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }
        .sql-section {
            margin-bottom: 2.5rem;
            padding: 1.5rem;
            background-color: #f9fafb;
            border-radius: 0.625rem;
            border: 1px solid #e5e7eb;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .sql-section h2 {
            margin-bottom: 1.5rem;
            color: #1f2937;
            font-size: 1.875rem; /* text-3xl */
            font-weight: 700; /* font-bold */
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        .sql-query-block {
            margin-bottom: 1.5rem;
            background-color: #ffffff;
            border: 1px solid #d1d5db;
            border-radius: 0.5rem;
            overflow: hidden;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }
        .sql-query-block h3 {
            background-color: #edf2f7;
            padding: 0.75rem 1rem;
            font-size: 1.125rem; /* text-lg */
            font-weight: 600; /* font-semibold */
            color: #374151;
            border-bottom: 1px solid #d1d5db;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .sql-query-container {
            position: relative;
            padding: 1rem;
        }
        .sql-query-container pre {
            background-color: #1f2937; /* Dark background for code */
            color: #e5e7eb; /* Light text for code */
            padding: 1rem;
            border-radius: 0.375rem;
            overflow-x: auto;
            font-size: 0.9rem;
            line-height: 1.4;
            position: relative; /* Needed for copy button positioning */
        }
        .sql-query-container pre code {
            display: block; /* Ensures code block wraps properly */
            white-space: pre-wrap; /* Wrap long lines */
            word-break: break-all; /* Break words if needed */
        }
        .result-output {
            background-color: #f3f4f6;
            padding: 1rem;
            border-top: 1px dashed #d1d5db;
            margin-top: 1rem;
            border-radius: 0.375rem;
            overflow-x: auto;
        }
        .result-output table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.875rem;
            margin-top: 0.5rem;
        }
        .result-output th, .result-output td {
            border: 1px solid #d1d5db;
            padding: 0.6rem 0.8rem;
            text-align: left;
        }
        .result-output th {
            background-color: #e5e7eb;
            color: #4b5563;
            font-weight: 600;
        }
        .result-output tr:nth-child(even) {
            background-color: #edf2f7;
        }
        .result-output tr:hover {
            background-color: #e2e8f0;
        }

        .btn {
            padding: 0.6rem 1.2rem;
            border-radius: 0.5rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }
        .btn-primary {
            background-color: #4f46e5; /* indigo-600 */
            color: #ffffff;
            border: none;
        }
        .btn-primary:hover {
            background-color: #4338ca; /* indigo-700 */
        }
        .btn-secondary {
            background-color: #6b7280; /* gray-500 */
            color: #ffffff;
            border: none;
        }
        .btn-secondary:hover {
            background-color: #4b5563; /* gray-700 */
        }
        .btn-copy {
            background-color: #10b981; /* emerald-500 */
            color: #ffffff;
            border: none;
        }
        .btn-copy:hover {
            background-color: #059669; /* emerald-600 */
        }
        .copy-message {
            margin-left: 0.75rem;
            font-size: 0.875rem;
            color: #10b981;
            opacity: 0;
            transition: opacity 0.3s ease-in-out;
            display: flex;
            align-items: center;
            gap: 0.25rem;
        }
        .copy-message.show {
            opacity: 1;
        }
        .toggle-container {
            display: flex;
            gap: 0.75rem;
            margin-top: 1rem;
        }

        /* Venn Diagram Styling */
        .venn-diagram-container {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 2rem;
            margin: 2rem 0;
            flex-wrap: wrap; /* Allow wrapping on small screens */
        }
        .venn-diagram {
            width: 150px;
            height: 100px;
            position: relative;
        }
        .circle {
            position: absolute;
            width: 100px;
            height: 100px;
            border-radius: 50%;
            border: 2px solid #374151; /* gray-700 */
            box-sizing: border-box;
            opacity: 0.6;
        }
        .circle-A {
            left: 0;
            background-color: #60a5fa; /* blue-400 */
        }
        .circle-B {
            right: 0;
            background-color: #fca5a5; /* red-300 */
        }
        .intersection {
            position: absolute;
            width: 100px;
            height: 100px;
            border-radius: 50%;
            left: 25px; /* Center of intersection for overlapping circles */
            background-color: transparent;
        }
        .venn-label {
            position: absolute;
            font-weight: bold;
            color: #1f2937;
            font-size: 0.9rem;
        }
        .label-A { left: 10px; top: -20px; }
        .label-B { right: 10px; top: -20px; }
        .label-intersection { left: 60px; top: 40px; } /* For inner text */

        /* Specific highlights for join types */
        .inner-highlight .intersection {
            background-color: #10b981; /* emerald-500 */
            opacity: 0.8;
            border: 2px solid #059669;
        }
        .left-highlight .circle-A {
            background-color: #10b981; /* emerald-500 */
            opacity: 0.8;
            border: 2px solid #059669;
        }
        .left-highlight .intersection {
            background-color: #10b981; /* emerald-500 */
            opacity: 0.8;
            border: 2px solid #059669;
        }
        .right-highlight .circle-B {
            background-color: #10b981; /* emerald-500 */
            opacity: 0.8;
            border: 2px solid #059669;
        }
        .right-highlight .intersection {
            background-color: #10b981; /* emerald-500 */
            opacity: 0.8;
            border: 2px solid #059669;
        }
        .full-highlight .circle-A,
        .full-highlight .circle-B {
            background-color: #10b981; /* emerald-500 */
            opacity: 0.8;
            border: 2px solid #059669;
        }
        .full-highlight .intersection {
            background-color: #10b981; /* emerald-500 */
            opacity: 0.8;
            border: 2px solid #059669;
        }

        @media (max-width: 768px) {
            .container {
                margin: 1rem auto;
                padding: 1rem;
            }
            .sql-section {
                padding: 1rem;
            }
            .sql-section h2 {
                font-size: 1.5rem;
                margin-bottom: 1rem;
            }
            .sql-query-block h3 {
                font-size: 1rem;
                padding: 0.6rem 0.8rem;
            }
            .btn {
                padding: 0.5rem 1rem;
                font-size: 0.875rem;
            }
            .toggle-container {
                flex-direction: column;
                gap: 0.5rem;
            }
        }

 /* Popup Styles */
        .popup-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.7);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.3s ease-in-out, visibility 0.3s ease-in-out;
            backdrop-filter: blur(4px);
        }
        .popup-overlay.show {
            opacity: 1;
            visibility: visible;
        }
        .popup-content {
            background-color: #fff;
            padding: 2.5rem;
            border-radius: 1rem;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
            text-align: center;
            max-width: 90%;
            width: 480px;
            position: relative;
            transform: scale(0.8
            ) translateY(20px);
            transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            border: 1px solid rgba(79, 70, 229, 0.2);
        }
        .popup-overlay.show .popup-content {
            transform: scale(1) translateY(0);
        }
        .popup-content h3 {
            font-size: 1.75rem;
            font-weight: 700;
            color: #1f2937;
            margin-bottom: 1.25rem;
        }
        .popup-content p {
            font-size: 1rem;
            line-height: 1.6;
            color: #4b5563;
            margin-bottom: 1.5rem;
            max-height: 200px;
            overflow-y: auto;
            text-align: left;
            padding-right: 0.5rem;
        }
        .popup-content a {
            color: #4f46e5;
            text-decoration: none;
            font-weight: 600;
            transition: color 0.2s;
        }
        .popup-content a:hover {
            color: #4338ca;
            text-decoration: underline;
        }
        .popup-close {
            position: absolute;
            top: 1rem;
            right: 1rem;
            background: #f3f4f6;
            border: none;
            border-radius: 50%;
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.25rem;
            cursor: pointer;
            color: #6b7280;
            transition: all 0.2s ease;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .popup-close:hover {
            background: #e5e7eb;
            color: #1f2937;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
.profile-photo {
            width: 150px;
            height: 150px;
            border-radius: 50%;
            object-fit: cover;
            margin: 0 auto 1.5rem;
            border: none;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            background-color: #e0e7ff; /* Fallback background if image fails to load */
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2.5rem;
            font-weight: bold;
            color: #4f46e5;
        }
        .skills-list {
            list-style: none;
            padding: 0;
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 0.5rem;
            margin-top: 1rem;
        }
        .skills-list li {
            background-color: #e0e7ff; /* indigo-100 */
            color: #4338ca; /* indigo-700 */
            padding: 0.3rem 0.7rem;
            border-radius: 0.375rem;
            font-size: 0.875rem;
            font-weight: 500;
        }
    </style>
</head>
<body>
    <div class="container rounded-xl">
        <!-- Header Section -->
        <header class="text-center mb-8 pb-4 border-b border-gray-200">
            <h1 class="text-4xl font-bold text-blue-600 mb-2"> SQL Course</h1>
            <p class="text-xl text-gray-600 mb-1">Interactive Learning Module</p>
            <div class="mt-4 text-gray-500 text-sm">
                <p><strong>Instructor:</strong> Kaung Myat Kyaw | <strong>Role:</strong> Data Analyst</p>
                <p><strong>Contact:</strong> Ph - 09446844590 | Email - kaungmyatkyaw446844590@gmail.com</p>
                <p class="flex items-center justify-center gap-2">
                    <!-- LinkedIn Icon -->
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-linkedin">
                        <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/>
                        <rect width="4" height="12" x="2" y="9"/>
                        <circle cx="4" cy="4" r="2"/>
                    </svg>
                    <strong>LinkedIn:</strong> <a href="https://www.linkedin.com/in/kaung-myat-kyaw-96705231a/" target="_blank" rel="noopener noreferrer">linkedin.com/in/kaung-myat-kyaw-96705231a/</a>
                </p>
            </div>
        </header>

        <!-- Course Introduction -->
        <section class="mb-8 p-6 bg-blue-50 border border-blue-200 rounded-lg">
            <h2 class="text-2xl font-semibold text-blue-800 mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-book-open-text">
                    <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
                    <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h6z"/>
                    <path d="M10 12H8"/>
                    <path d="M16 12h-2"/>
                    <path d="M14 16h-4"/>
                </svg>
                Welcome to Your SQL Journey!
            </h2>
            <p class="text-gray-700 leading-relaxed">
                This course is meticulously designed to help you master SQL through hands-on examples.
                Each section presents a key SQL concept with a practical query and its corresponding result.
                Click the "Show Result" button to reveal the output, and use the "Copy Query" button to easily replicate and experiment in your own environment.
                Let's explore the power of data together!
            </p>
        </section>

        <!-- New Section: Data Definitions and Importance -->
        <section class="sql-section">
            <h2>
                <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-info">
                    <circle cx="12" cy="12" r="10"/>
                    <path d="M12 16v-4"/>
                    <path d="M12 8h.01"/>
                </svg>
                Fundamental Data Concepts
            </h2>
            <p class="text-gray-700 mb-4">Understanding these core terms is crucial for anyone working with data and databases.</p>

            <div class="mb-6">
                <h3 class="text-lg font-semibold text-gray-700 mb-2">Data</h3>
                <p class="text-gray-600">
                    Data refers to raw, unorganized facts, figures, or information, such as numbers, text, images, or sounds, that can be processed and analyzed to derive meaning or knowledge. In its raw form, data may seem random or unrelated, but when organized and interpreted, it becomes the foundation for decision-making and understanding.
                </p>
            </div>

            <div class="mb-6">
                <h3 class="text-lg font-semibold text-gray-700 mb-2">Database</h3>
                <p class="text-gray-600">
                    A database is a structured collection of organized information or data, typically stored electronically in a computer system. It is designed to efficiently store, retrieve, and manage large amounts of data, allowing for easy access and manipulation by various applications and users. Databases are fundamental for managing information in almost all modern businesses and organizations.
                </p>
            </div>

            <div class="mb-6">
                <h3 class="text-lg font-semibold text-gray-700 mb-2">DBMS (Database Management System)</h3>
                <p class="text-gray-600">
                    A DBMS (Database Management System) is a software system that allows users to define, create, maintain, and control access to a database. It acts as an interface between the user or applications and the database, providing functionalities for data storage, retrieval, security, integrity, and concurrency control. Examples include MySQL, PostgreSQL, Oracle Database, and Microsoft SQL Server.
                </p>
            </div>

            <div class="mb-6">
                <h3 class="text-lg font-semibold text-gray-700 mb-2">RDBMS (Relational Database Management System)</h3>
                <p class="text-gray-600">
                    An RDBMS (Relational Database Management System) is a specific type of DBMS that organizes data into one or more tables (or "relations") of rows and columns. Each table has a unique key, and rows in different tables can be related to each other using foreign keys. This relational model, introduced by E.F. Codd, emphasizes data integrity, consistency, and the use of Structured Query Language (SQL) for data manipulation.
                </p>
            </div>

            <div class="mt-6 p-4 bg-gray-100 border border-gray-300 rounded-md">
                <h3 class="text-lg font-semibold text-gray-700 mb-2">Professional Quote on Data Importance:</h3>
                <p class="text-gray-700 italic">
                    "Data is a precious thing and will last longer than the systems themselves."
                </p>
                <p class="text-right text-gray-500 font-medium">— Tim Berners-Lee, Inventor of the World Wide Web</p>
            </div>
        </section>

        <!-- Dataset Setup Section -->
        <section class="sql-section">
            <h2>
                <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-database">
                    <ellipse cx="12" cy="5" rx="9" ry="3"/>
                    <path d="M3 5V19A9 3 0 0 0 21 19V5"/>
                    <path d="M3 12A9 3 0 0 0 21 12"/>
                </svg>
                Dataset Setup
            </h2>
            <p class="text-gray-700 mb-4">
                Before we dive into queries, let's establish our training dataset. Below are the SQL statements to create and populate the `Departments`, `Employees`, and `Salaries` tables. You can copy and run these in your SQL environment (e.g., MySQL, PostgreSQL, SQL Server) to follow along.
            </p>

            <div class="sql-query-block">
                <h3>SQL Data Definition & Insertion</h3>
                <div class="sql-query-container">
                    <pre class="language-sql"><code>-- 📚 SQL Training Dataset & Exercises for MMP

-- =============== DROP EXISTING TABLES ===============
DROP TABLE IF EXISTS Salaries;
DROP TABLE IF EXISTS Employees;
DROP TABLE IF EXISTS Departments;

-- =============== TABLE: Departments ===============
CREATE TABLE Departments (
    DepartmentID INT PRIMARY KEY,
    DepartmentName VARCHAR(100)
);

INSERT INTO Departments VALUES
(101, 'IT'),
(102, 'Finance'),
(103, 'HR'),
(104, 'Marketing');

-- =============== TABLE: Employees ===============
CREATE TABLE Employees (
    EmpID INT PRIMARY KEY,
    FullName VARCHAR(100),
    Gender CHAR(1),
    DepartmentID INT,
    Position VARCHAR(50),
    HireDate DATE,
    City VARCHAR(50)
);

INSERT INTO Employees VALUES
(1, 'Alice Johnson', 'F', 101, 'Developer', '2018-01-10', 'Yangon'),
(2, 'Bob Smith', 'M', 102, 'Accountant', '2019-03-15', 'Mandalay'),
(3, 'Carol White', 'F', 101, 'QA Engineer', '2020-07-22', 'Yangon'),
(4, 'David Lee', 'M', 103, 'HR Officer', '2021-10-01', 'Naypyidaw'),
(5, 'Eve Parker', 'F', 102, 'Financial Analyst', '2017-04-11', 'Yangon'),
(6, 'Frank Murphy', 'M', 104, 'Marketing Lead', '2016-12-05', 'Mandalay'),
(7, 'Grace Liu', 'F', 103, 'HR Assistant', '2022-02-01', 'Taunggyi'),
(8, 'Henry Chan', 'M', 101, 'Sys Admin', '2020-05-20', 'Mandalay');

-- =============== TABLE: Salaries ===============
CREATE TABLE Salaries (
    EmpID INT,
    SalaryMonth VARCHAR(10),
    Year INT,
    BaseSalary DECIMAL(10, 2),
    Bonus DECIMAL(10, 2)
);

INSERT INTO Salaries VALUES
(1, 'JAN', 2023, 5000, 200),
(1, 'FEB', 2023, 5000, 100),
(2, 'JAN', 2023, 4800, 0),
(2, 'FEB', 2023, 4800, 300),
(3, 'JAN', 2023, 4700, 150),
(3, 'FEB', 2023, 4700, 200),
(4, 'JAN', 2023, 4600, 100),
(5, 'JAN', 2023, 4900, 0),
(5, 'FEB', 2023, 4900, 50),
(6, 'JAN', 2023, 5100, 300),
(7, 'JAN', 2023, 4500, 100),
(7, 'FEB', 2023, 4500, 0),
(8, 'JAN', 2023, 5200, 150),
(8, 'FEB', 2023, 5200, 180);
</code></pre>
                    <div class="toggle-container">
                        <button class="btn btn-copy" onclick="copyCode(this)">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-copy">
                                <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>
                                <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
                            </svg>
                            Copy All Setup Code
                        </button>
                        <span class="copy-message">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-check">
                                <path d="M20 6 9 17l-5-5"/>
                            </svg>
                            Copied!
                        </span>
                    </div>
                </div>
            </div>
        </section>

        <!-- SELECT, WHERE, LIKE Section -->
        <section class="sql-section">
            <h2>
                <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-filter">
                    <path d="M22 3H2l8 12.46V19l4 2v-5.54L22 3z"/>
                </svg>
                SELECT, WHERE, and LIKE
            </h2>
            <p class="text-gray-700 mb-4">
                These clauses are fundamental for retrieving specific data based on conditions.
            </p>

            <div class="sql-query-block">
                <h3>Query: Select Female Employees with 'a' in their Name</h3>
                <div class="sql-query-container">
                    <pre class="language-sql"><code>SELECT * FROM Employees WHERE Gender = 'F' AND FullName LIKE '%a%';</code></pre>
                    <div class="toggle-container">
                        <button class="btn btn-primary toggle-result">Show Result</button>
                        <button class="btn btn-copy" onclick="copyCode(this)">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-copy">
                                <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>
                                <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
                            </svg>
                            Copy Query
                        </button>
                        <span class="copy-message">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-check">
                                <path d="M20 6 9 17l-5-5"/>
                            </svg>
                            Copied!
                        </span>
                    </div>
                    <div class="result-output" style="display:none;">
                        <table class="result-table">
                            <thead>
                                <tr>
                                    <th>EmpID</th>
                                    <th>FullName</th>
                                    <th>Gender</th>
                                    <th>DepartmentID</th>
                                    <th>Position</th>
                                    <th>HireDate</th>
                                    <th>City</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr><td>1</td><td>Alice Johnson</td><td>F</td><td>101</td><td>Developer</td><td>2018-01-10</td><td>Yangon</td></tr>
                                <tr><td>3</td><td>Carol White</td><td>F</td><td>101</td><td>QA Engineer</td><td>2020-07-22</td><td>Yangon</td></tr>
                                <tr><td>5</td><td>Eve Parker</td><td>F</td><td>102</td><td>Financial Analyst</td><td>2017-04-11</td><td>Yangon</td></tr>
                                <tr><td>7</td><td>Grace Liu</td><td>F</td><td>103</td><td>HR Assistant</td><td>2022-02-01</td><td>Taunggyi</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </section>

        <!-- Aggregation Functions Section -->
        <section class="sql-section">
            <h2>
                <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-calculator">
                    <rect width="16" height="20" x="4" y="2" rx="2"/>
                    <path d="M8 6h8"/>
                    <path d="M8 10h8"/>
                    <path d="M8 14h8"/>
                    <path d="M8 18h8"/>
                </svg>
                Aggregation Functions
            </h2>
            <p class="text-gray-700 mb-4">
                Aggregate functions perform calculations on a set of rows and return a single value.
            </p>

            <div class="sql-query-block">
                <h3>Query: Total Bonus for January</h3>
                <div class="sql-query-container">
                    <pre class="language-sql"><code>SELECT SUM(Bonus) AS TotalBonus FROM Salaries WHERE SalaryMonth = 'JAN';</code></pre>
                    <div class="toggle-container">
                        <button class="btn btn-primary toggle-result">Show Result</button>
                        <button class="btn btn-copy" onclick="copyCode(this)">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-copy">
                                <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>
                                <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
                            </svg>
                            Copy Query
                        </button>
                        <span class="copy-message">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-check">
                                <path d="M20 6 9 17l-5-5"/>
                            </svg>
                            Copied!
                        </span>
                    </div>
                    <div class="result-output" style="display:none;">
                        <table class="result-table">
                            <thead>
                                <tr><th>TotalBonus</th></tr>
                            </thead>
                            <tbody>
                                <tr><td>1000.00</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </section>

        <!-- GROUP BY with HAVING Section -->
        <section class="sql-section">
            <h2>
                <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-list-collapse">
                    <path d="M11 10H3"/>
                    <path d="M18 6H3"/>
                    <path d="M21 14H3"/>
                    <path d="M14 18H3"/>
                    <path d="M20 10V8l-2 2"/>
                </svg>
                GROUP BY and HAVING
            </h2>
            <p class="text-gray-700 mb-4">
                `GROUP BY` groups rows that have the same values into summary rows. `HAVING` filters these groups based on aggregate conditions.
            </p>

            <div class="sql-query-block">
                <h3>Query: Departments with More Than One Employee</h3>
                <div class="sql-query-container">
                    <pre class="language-sql"><code>SELECT DepartmentID, COUNT(*) AS TotalEmployees
FROM Employees
GROUP BY DepartmentID
HAVING COUNT(*) > 1;</code></pre>
                    <div class="toggle-container">
                        <button class="btn btn-primary toggle-result">Show Result</button>
                        <button class="btn btn-copy" onclick="copyCode(this)">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-copy">
                                <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>
                                <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
                            </svg>
                            Copy Query
                        </button>
                        <span class="copy-message">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-check">
                                <path d="M20 6 9 17l-5-5"/>
                            </svg>
                            Copied!
                        </span>
                    </div>
                    <div class="result-output" style="display:none;">
                        <table class="result-table">
                            <thead>
                                <tr>
                                    <th>DepartmentID</th>
                                    <th>TotalEmployees</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr><td>101</td><td>3</td></tr>
                                <tr><td>102</td><td>2</td></tr>
                                <tr><td>103</td><td>2</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </section>

        <!-- JOIN Types Section -->
        <section class="sql-section">
            <h2>
                <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-link">
                    <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07L9.54 3.54a5 5 0 0 0-7.07 7.07l1.41-1.41"/>
                    <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.41-1.41"/>
                </svg>
                JOIN Types
            </h2>
            <p class="text-gray-700 mb-4">
                SQL JOINs are used to combine rows from two or more tables based on a related column between them.
            </p>

            <!-- Inner Join -->
            <div class="sql-query-block">
                <h3>INNER JOIN: Only Matching Records</h3>
                <div class="venn-diagram-container">
                    <div class="venn-diagram inner-highlight">
                        <div class="circle circle-A"></div>
                        <div class="circle circle-B" style="left: 50px;"></div>
                        <div class="venn-label label-A">Table A</div>
                        <div class="venn-label label-B" style="right: 10px;">Table B</div>
                        <div class="intersection"></div>
                    </div>
                </div>
                <div class="sql-query-container">
                    <pre class="language-sql"><code>SELECT e.FullName, d.DepartmentName
FROM Employees e
INNER JOIN Departments d ON e.DepartmentID = d.DepartmentID;</code></pre>
                    <div class="toggle-container">
                        <button class="btn btn-primary toggle-result">Show Result</button>
                        <button class="btn btn-copy" onclick="copyCode(this)">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-copy">
                                <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>
                                <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
                            </svg>
                            Copy Query
                        </button>
                        <span class="copy-message">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-check">
                                <path d="M20 6 9 17l-5-5"/>
                            </svg>
                            Copied!
                        </span>
                    </div>
                    <div class="result-output" style="display:none;">
                        <table class="result-table">
                            <thead>
                                <tr>
                                    <th>FullName</th>
                                    <th>DepartmentName</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr><td>Alice Johnson</td><td>IT</td></tr>
                                <tr><td>Bob Smith</td><td>Finance</td></tr>
                                <tr><td>Carol White</td><td>IT</td></tr>
                                <tr><td>David Lee</td><td>HR</td></tr>
                                <tr><td>Eve Parker</td><td>Finance</td></tr>
                                <tr><td>Frank Murphy</td><td>Marketing</td></tr>
                                <tr><td>Grace Liu</td><td>HR</td></tr>
                                <tr><td>Henry Chan</td><td>IT</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- LEFT JOIN -->
            <div class="sql-query-block">
                <h3>LEFT JOIN: All from Left Table, Matched from Right</h3>
                <div class="venn-diagram-container">
                    <div class="venn-diagram left-highlight">
                        <div class="circle circle-A"></div>
                        <div class="circle circle-B" style="left: 50px;"></div>
                        <div class="venn-label label-A">Table A</div>
                        <div class="venn-label label-B" style="right: 10px;">Table B</div>
                        <div class="intersection"></div>
                    </div>
                </div>
                <div class="sql-query-container">
                    <pre class="language-sql"><code>SELECT e.FullName, d.DepartmentName
FROM Employees e
LEFT JOIN Departments d ON e.DepartmentID = d.DepartmentID;</code></pre>
                    <div class="toggle-container">
                        <button class="btn btn-primary toggle-result">Show Result</button>
                        <button class="btn btn-copy" onclick="copyCode(this)">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-copy">
                                <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>
                                <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
                            </svg>
                            Copy Query
                        </button>
                        <span class="copy-message">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-check">
                                <path d="M20 6 9 17l-5-5"/>
                            </svg>
                            Copied!
                        </span>
                    </div>
                    <div class="result-output" style="display:none;">
                        <table class="result-table">
                            <thead>
                                <tr>
                                    <th>FullName</th>
                                    <th>DepartmentName</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr><td>Alice Johnson</td><td>IT</td></tr>
                                <tr><td>Bob Smith</td><td>Finance</td></tr>
                                <tr><td>Carol White</td><td>IT</td></tr>
                                <tr><td>David Lee</td><td>HR</td></tr>
                                <tr><td>Eve Parker</td><td>Finance</td></tr>
                                <tr><td>Frank Murphy</td><td>Marketing</td></tr>
                                <tr><td>Grace Liu</td><td>HR</td></tr>
                                <tr><td>Henry Chan</td><td>IT</td></tr>
                            </tbody>
                        </table>
                        <p class="text-sm text-gray-600 mt-2">
                            <em>Note: In this specific dataset, all employees have matching departments, so the result is identical to an INNER JOIN. If an employee had a `DepartmentID` not found in the `Departments` table, `DepartmentName` would be NULL for that employee.</em>
                        </p>
                    </div>
                </div>
            </div>

            <!-- RIGHT JOIN -->
            <div class="sql-query-block">
                <h3>RIGHT JOIN: All from Right Table, Matched from Left</h3>
                <div class="venn-diagram-container">
                    <div class="venn-diagram right-highlight">
                        <div class="circle circle-A"></div>
                        <div class="circle circle-B" style="left: 50px;"></div>
                        <div class="venn-label label-A">Table A</div>
                        <div class="venn-label label-B" style="right: 10px;">Table B</div>
                        <div class="intersection"></div>
                    </div>
                </div>
                <div class="sql-query-container">
                    <pre class="language-sql"><code>SELECT e.FullName, d.DepartmentName
FROM Employees e
RIGHT JOIN Departments d ON e.DepartmentID = d.DepartmentID;</code></pre>
                    <div class="toggle-container">
                        <button class="btn btn-primary toggle-result">Show Result</button>
                        <button class="btn btn-copy" onclick="copyCode(this)">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-copy">
                                <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>
                                <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
                            </svg>
                            Copy Query
                        </button>
                        <span class="copy-message">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-check">
                                <path d="M20 6 9 17l-5-5"/>
                            </svg>
                            Copied!
                        </span>
                    </div>
                    <div class="result-output" style="display:none;">
                        <table class="result-table">
                            <thead>
                                <tr>
                                    <th>FullName</th>
                                    <th>DepartmentName</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr><td>Alice Johnson</td><td>IT</td></tr>
                                <tr><td>Carol White</td><td>IT</td></tr>
                                <tr><td>Henry Chan</td><td>IT</td></tr>
                                <tr><td>Bob Smith</td><td>Finance</td></tr>
                                <tr><td>Eve Parker</td><td>Finance</td></tr>
                                <tr><td>David Lee</td><td>HR</td></tr>
                                <tr><td>Grace Liu</td><td>HR</td></tr>
                                <tr><td>Frank Murphy</td><td>Marketing</td></tr>
                            </tbody>
                        </table>
                        <p class="text-sm text-gray-600 mt-2">
                            <em>Note: In this dataset, all departments have at least one employee, so the result is similar to an INNER JOIN. If a department existed with no employees, `FullName` would be NULL for that department.</em>
                        </p>
                    </div>
                </div>
            </div>

            <!-- FULL OUTER JOIN -->
            <div class="sql-query-block">
                <h3>FULL OUTER JOIN: All from Both Tables</h3>
                <div class="venn-diagram-container">
                    <div class="venn-diagram full-highlight">
                        <div class="circle circle-A"></div>
                        <div class="circle circle-B" style="left: 50px;"></div>
                        <div class="venn-label label-A">Table A</div>
                        <div class="venn-label label-B" style="right: 10px;">Table B</div>
                        <div class="intersection"></div>
                    </div>
                </div>
                <div class="sql-query-container">
                    <pre class="language-sql"><code>SELECT e.FullName, d.DepartmentName
FROM Employees e
FULL OUTER JOIN Departments d ON e.DepartmentID = d.DepartmentID;</code></pre>
                    <div class="toggle-container">
                        <button class="btn btn-primary toggle-result">Show Result</button>
                        <button class="btn btn-copy" onclick="copyCode(this)">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-copy">
                                <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>
                                <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
                            </svg>
                            Copy Query
                        </button>
                        <span class="copy-message">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-check">
                                <path d="M20 6 9 17l-5-5"/>
                            </svg>
                            Copied!
                        </span>
                    </div>
                    <div class="result-output" style="display:none;">
                        <table class="result-table">
                            <thead>
                                <tr>
                                    <th>FullName</th>
                                    <th>DepartmentName</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr><td>Alice Johnson</td><td>IT</td></tr>
                                <tr><td>Carol White</td><td>IT</td></tr>
                                <tr><td>Henry Chan</td><td>IT</td></tr>
                                <tr><td>Bob Smith</td><td>Finance</td></tr>
                                <tr><td>Eve Parker</td><td>Finance</td></tr>
                                <tr><td>David Lee</td><td>HR</td></tr>
                                <tr><td>Grace Liu</td><td>HR</td></tr>
                                <tr><td>Frank Murphy</td><td>Marketing</td></tr>
                            </tbody>
                        </table>
                        <p class="text-sm text-gray-600 mt-2">
                            <em>Note: Given this dataset, there are no unmatched rows in either table, so the result is identical to an INNER JOIN. In scenarios with unmatched rows, it would return all data from both tables, with NULLs where no match exists.</em>
                        </p>
                    </div>
                </div>
            </div>
        </section>

        <!-- Common Table Expressions (CTE) Section -->
        <section class="sql-section">
            <h2>
                <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-code">
                    <polyline points="16 18 22 12 16 6"/>
                    <polyline points="8 6 2 12 8 18"/>
                </svg>
                Common Table Expressions (CTE)
            </h2>
            <p class="text-gray-700 mb-4">
                CTEs are temporary, named result sets that you can reference within a single SQL statement. They improve readability and organization of complex queries.
            </p>

            <div class="sql-query-block">
                <h3>Query: Employees with Average Total Salary Above 4900</h3>
                <div class="sql-query-container">
                    <pre class="language-sql"><code>WITH AvgSalary AS (
    SELECT EmpID, AVG(BaseSalary + Bonus) AS TotalAvg
    FROM Salaries
    GROUP BY EmpID
)
SELECT e.FullName, a.TotalAvg
FROM AvgSalary a
JOIN Employees e ON a.EmpID = e.EmpID
WHERE a.TotalAvg > 4900;</code></pre>
                    <div class="toggle-container">
                        <button class="btn btn-primary toggle-result">Show Result</button>
                        <button class="btn btn-copy" onclick="copyCode(this)">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-copy">
                                <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>
                                <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
                            </svg>
                            Copy Query
                        </button>
                        <span class="copy-message">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-check">
                                <path d="M20 6 9 17l-5-5"/>
                            </svg>
                            Copied!
                        </span>
                    </div>
                    <div class="result-output" style="display:none;">
                        <table class="result-table">
                            <thead>
                                <tr>
                                    <th>FullName</th>
                                    <th>TotalAvg</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr><td>Alice Johnson</td><td>5150.000000</td></tr>
                                <tr><td>Bob Smith</td><td>4950.000000</td></tr>
                                <tr><td>Eve Parker</td><td>4925.000000</td></tr>
                                <tr><td>Frank Murphy</td><td>5400.000000</td></tr>
                                <tr><td>Henry Chan</td><td>5365.000000</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </section>

        <!-- CASE Statement Section -->
        <section class="sql-section">
            <h2>
                <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-switch">
                    <path d="M16 8h3a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h3"/>
                    <path d="M12 2v16"/>
                    <path d="m19 15-3 3-3-3"/>
                    <path d="m5 9 3-3 3 3"/>
                </svg>
                CASE Statement
            </h2>
            <p class="text-gray-700 mb-4">
                The `CASE` statement allows you to implement IF/THEN/ELSE logic directly within your SQL queries.
            </p>

            <div class="sql-query-block">
                <h3>Query: Assigning Salary Grades for January Salaries</h3>
                <div class="sql-query-container">
                    <pre class="language-sql"><code>SELECT EmpID, BaseSalary,
        CASE
            WHEN BaseSalary >= 5000 THEN 'High'
            WHEN BaseSalary >= 4600 THEN 'Medium'
            ELSE 'Low'
        END AS SalaryGrade
FROM Salaries
WHERE SalaryMonth = 'JAN';</code></pre>
                    <div class="toggle-container">
                        <button class="btn btn-primary toggle-result">Show Result</button>
                        <button class="btn btn-copy" onclick="copyCode(this)">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-copy">
                                <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>
                                <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
                            </svg>
                            Copy Query
                        </button>
                        <span class="copy-message">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-check">
                                <path d="M20 6 9 17l-5-5"/>
                            </svg>
                            Copied!
                        </span>
                    </div>
                    <div class="result-output" style="display:none;">
                        <table class="result-table">
                            <thead>
                                <tr>
                                    <th>EmpID</th>
                                    <th>BaseSalary</th>
                                    <th>SalaryGrade</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr><td>1</td><td>5000.00</td><td>High</td></tr>
                                <tr><td>2</td><td>4800.00</td><td>Medium</td></tr>
                                <tr><td>3</td><td>4700.00</td><td>Medium</td></tr>
                                <tr><td>4</td><td>4600.00</td><td>Medium</td></tr>
                                <tr><td>5</td><td>4900.00</td><td>Medium</td></tr>
                                <tr><td>6</td><td>5100.00</td><td>High</td></tr>
                                <tr><td>7</td><td>4500.00</td><td>Low</td></tr>
                                <tr><td>8</td><td>5200.00</td><td>High</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </section>

        <!-- BETWEEN, IN, ORDER BY Section -->
        <section class="sql-section">
            <h2>
                <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-calendar">
                    <rect width="18" height="18" x="3" y="4" rx="2" ry="2"/>
                    <line x1="16" x2="16" y1="2" y2="6"/>
                    <line x1="8" x2="8" y1="2" y2="6"/>
                    <line x1="3" x2="21" y1="10" y2="10"/>
                </svg>
                BETWEEN, IN, and ORDER BY
            </h2>
            <p class="text-gray-700 mb-4">
                These clauses provide powerful ways to filter and sort your data.
            </p>

            <div class="sql-query-block">
                <h3>Query: Employees Hired Between 2018-2021 in Yangon or Mandalay</h3>
                <div class="sql-query-container">
                    <pre class="language-sql"><code>SELECT * FROM Employees
WHERE HireDate BETWEEN '2018-01-01' AND '2021-12-31'
AND City IN ('Yangon', 'Mandalay');</code></pre>
                    <div class="toggle-container">
                        <button class="btn btn-primary toggle-result">Show Result</button>
                        <button class="btn btn-copy" onclick="copyCode(this)">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-copy">
                                <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>
                                <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
                            </svg>
                            Copy Query
                        </button>
                        <span class="copy-message">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-check">
                                <path d="M20 6 9 17l-5-5"/>
                            </svg>
                            Copied!
                        </span>
                    </div>
                    <div class="result-output" style="display:none;">
                        <table class="result-table">
                            <thead>
                                <tr>
                                    <th>EmpID</th>
                                    <th>FullName</th>
                                    <th>Gender</th>
                                    <th>DepartmentID</th>
                                    <th>Position</th>
                                    <th>HireDate</th>
                                    <th>City</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr><td>1</td><td>Alice Johnson</td><td>F</td><td>101</td><td>Developer</td><td>2018-01-10</td><td>Yangon</td></tr>
                                <tr><td>2</td><td>Bob Smith</td><td>M</td><td>102</td><td>Accountant</td><td>2019-03-15</td><td>Mandalay</td></tr>
                                <tr><td>3</td><td>Carol White</td><td>F</td><td>101</td><td>QA Engineer</td><td>2020-07-22</td><td>Yangon</td></tr>
                                <tr><td>8</td><td>Henry Chan</td><td>M</td><td>101</td><td>Sys Admin</td><td>2020-05-20</td><td>Mandalay</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div class="sql-query-block">
                <h3>Query: All Salaries Ordered by Employee ID and Month</h3>
                <div class="sql-query-container">
                    <pre class="language-sql"><code>SELECT EmpID, SalaryMonth, Year, BaseSalary, Bonus FROM Salaries
ORDER BY EmpID, SalaryMonth;</code></pre>
                    <div class="toggle-container">
                        <button class="btn btn-primary toggle-result">Show Result</button>
                        <button class="btn btn-copy" onclick="copyCode(this)">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-copy">
                                <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>
                                <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
                            </svg>
                            Copy Query
                        </button>
                        <span class="copy-message">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-check">
                                <path d="M20 6 9 17l-5-5"/>
                            </svg>
                            Copied!
                        </span>
                    </div>
                    <div class="result-output" style="display:none;">
                        <table class="result-table">
                            <thead>
                                <tr>
                                    <th>EmpID</th>
                                    <th>SalaryMonth</th>
                                    <th>Year</th>
                                    <th>BaseSalary</th>
                                    <th>Bonus</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr><td>1</td><td>FEB</td><td>2023</td><td>5000.00</td><td>100.00</td></tr>
                                <tr><td>1</td><td>JAN</td><td>2023</td><td>5000.00</td><td>200.00</td></tr>
                                <tr><td>2</td><td>FEB</td><td>2023</td><td>4800.00</td><td>300.00</td></tr>
                                <tr><td>2</td><td>JAN</td><td>2023</td><td>4800.00</td><td>0.00</td></tr>
                                <tr><td>3</td><td>FEB</td><td>2023</td><td>4700.00</td><td>200.00</td></tr>
                                <tr><td>3</td><td>JAN</td><td>2023</td><td>4700.00</td><td>150.00</td></tr>
                                <tr><td>4</td><td>JAN</td><td>2023</td><td>4600.00</td><td>100.00</td></tr>
                                <tr><td>5</td><td>FEB</td><td>2023</td><td>4900.00</td><td>50.00</td></tr>
                                <tr><td>5</td><td>JAN</td><td>2023</td><td>4900.00</td><td>0.00</td></tr>
                                <tr><td>6</td><td>JAN</td><td>2023</td><td>5100.00</td><td>300.00</td></tr>
                                <tr><td>7</td><td>FEB</td><td>2023</td><td>4500.00</td><td>0.00</td></tr>
                                <tr><td>7</td><td>JAN</td><td>2023</td><td>4500.00</td><td>100.00</td></tr>
                                <tr><td>8</td><td>FEB</td><td>2023</td><td>5200.00</td><td>180.00</td></tr>
                                <tr><td>8</td><td>JAN</td><td>2023</td><td>5200.00</td><td>150.00</td></tr>
                            </tbody>
                        </table>
                        <p class="text-sm text-gray-600 mt-2">
                            <em>Note: `SalaryMonth DESC` orders 'JAN' after 'FEB' alphabetically, so 'JAN' is considered 'latest' when ordering by `SalaryMonth DESC` for the two months provided.</em>
                        </p>
                    </div>
                </div>
            </div>
        </section>

        <!-- ALTER / UPDATE / DELETE / ROW_NUMBER Section -->
        <section class="sql-section">
            <h2>
                <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-settings">
                    <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.38a2 2 0 0 0-.73-2.73l-.15-.1a2 2 0 0 1-1-1.72v-.51a2 2 0 0 1 1-1.74l-.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/>
                    <circle cx="12" cy="12" r="3"/>
                </svg>
                Data Manipulation (DML) & Definition (DDL)
            </h2>
            <p class="text-gray-700 mb-4">
                These statements allow you to modify the structure of tables (DDL) or the data within them (DML).
            </p>

            <div class="sql-query-block">
                <h3>Query: Add a New 'Email' Column to Employees</h3>
                <div class="sql-query-container">
                    <pre class="language-sql"><code>ALTER TABLE Employees ADD Email VARCHAR(100);</code></pre>
                    <div class="toggle-container">
                        <button class="btn btn-primary toggle-result">Show Expected Outcome</button>
                        <button class="btn btn-copy" onclick="copyCode(this)">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-copy">
                                <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>
                                <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
                            </svg>
                            Copy Query
                        </button>
                        <span class="copy-message">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-check">
                                <path d="M20 6 9 17l-5-5"/>
                            </svg>
                            Copied!
                        </span>
                    </div>
                    <div class="result-output" style="display:none;">
                        <p>Expected Outcome: Query OK. A new column named `Email` is added to the `Employees` table. Existing rows will have `NULL` in this column until updated.</p>
                        <p class="text-sm text-gray-600 mt-2">
                            <em>Note: DDL statements like ALTER TABLE typically return success messages rather than result sets.</em>
                        </p>
                    </div>
                </div>
            </div>

            <div class="sql-query-block">
                <h3>Query: Update Eve Parker's City to Bago</h3>
                <div class="sql-query-container">
                    <pre class="language-sql"><code>UPDATE Employees
SET City = 'Bago'
WHERE FullName = 'Eve Parker';</code></pre>
                    <div class="toggle-container">
                        <button class="btn btn-primary toggle-result">Show Expected Outcome</button>
                        <button class="btn btn-copy" onclick="copyCode(this)">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-copy">
                                <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>
                                <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
                            </svg>
                            Copy Query
                        </button>
                        <span class="copy-message">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-check">
                                <path d="M20 6 9 17l-5-5"/>
                            </svg>
                            Copied!
                        </span>
                    </div>
                    <div class="result-output" style="display:none;">
                        <p>Expected Outcome: Query OK, 1 row affected. Eve Parker's `City` will change from 'Yangon' to 'Bago'.</p>
                        <p class="text-sm text-gray-600 mt-2">
                            <em>Note: DML statements like UPDATE return affected row counts.</em>
                        </p>
                    </div>
                </div>
            </div>

            <div class="sql-query-block">
                <h3>Query: Delete Employees Hired Before 2017</h3>
                <div class="sql-query-container">
                    <pre class="language-sql"><code>DELETE FROM Employees
WHERE HireDate < '2017-01-01';</code></pre>
                    <div class="toggle-container">
                        <button class="btn btn-primary toggle-result">Show Expected Outcome</button>
                        <button class="btn btn-copy" onclick="copyCode(this)">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-copy">
                                <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>
                                <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
                            </svg>
                            Copy Query
                        </button>
                        <span class="copy-message">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-check">
                                <path d="M20 6 9 17l-5-5"/>
                            </svg>
                            Copied!
                        </span>
                    </div>
                    <div class="result-output" style="display:none;">
                        <p>Expected Outcome: Query OK, 1 row affected. The employee 'Frank Murphy' (hired 2016-12-05) will be removed from the `Employees` table.</p>
                        <p class="text-sm text-gray-600 mt-2">
                            <em>Note: DML statements like DELETE return affected row counts.</em>
                        </p>
                    </div>
                </div>
            </div>

            <h3 class="mt-8 text-xl font-semibold text-gray-700 flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-list-ordered">
                    <line x1="10" x2="17" y1="6" y2="6"/>
                    <line x1="10" x2="21" y1="12" y2="12"/>
                    <line x1="10" x2="21" y1="18" y2="18"/>
                    <path d="M4 6h1v4"/>
                    <path d="M4 10h2"/>
                    <path d="M6 18H4c0-1.1.9-2 2-2h0c1.1 0 2 .9 2 2v0c0 1.1-.9 2-2 2Z"/>
                </svg>
                Window Functions: ROW_NUMBER()
            </h3>
            <p class="text-gray-700 mb-4">
                Window functions perform calculations across a set of table rows that are related to the current row. `ROW_NUMBER()` assigns a unique number to each row within a partition.
            </p>

            <div class="sql-query-block">
                <h3>Query: Identify Duplicate Salaries (Conceptual Example)</h3>
                <div class="sql-query-container">
                    <pre class="language-sql"><code>WITH RankedSalaries AS (
    SELECT *,
            ROW_NUMBER() OVER (PARTITION BY EmpID, SalaryMonth ORDER BY Year DESC) AS row_num
    FROM Salaries
)
-- Now filter to see rows that would be considered duplicates (row_num > 1)
SELECT EmpID, SalaryMonth, Year, BaseSalary, Bonus, row_num
FROM RankedSalaries
WHERE row_num > 1;</code></pre>
                    <div class="toggle-container">
                        <button class="btn btn-primary toggle-result">Show Result</button>
                        <button class="btn btn-copy" onclick="copyCode(this)">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-copy">
                                <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>
                                <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
                            </svg>
                            Copy Query
                        </button>
                        <span class="copy-message">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-check">
                                <path d="M20 6 9 17l-5-5"/>
                            </svg>
                            Copied!
                        </span>
                    </div>
                    <div class="result-output" style="display:none;">
                        <table class="result-table">
                            <thead>
                                <tr>
                                    <th>EmpID</th>
                                    <th>SalaryMonth</th>
                                    <th>Year</th>
                                    <th>BaseSalary</th>
                                    <th>Bonus</th>
                                    <th>row_num</th>
                                </tr>
                            </thead>
                            <tbody>
                                <!-- No rows will be returned with current dataset as there are no duplicates for (EmpID, SalaryMonth) -->
                            </tbody>
                        </table>
                        <p class="text-sm text-gray-600 mt-2">
                            <em>Result: Empty. For the given dataset, there are no true duplicates for `(EmpID, SalaryMonth)`, so `row_num` will always be 1. This query demonstrates how to find potential duplicates if they existed.</em>
                        </p>
                    </div>
                </div>
            </div>

            <div class="sql-query-block">
                <h3>Query: Keep Only Latest Salary per Employee</h3>
                <div class="sql-query-container">
                    <pre class="language-sql"><code>WITH LatestSalary AS (
    SELECT *,
            ROW_NUMBER() OVER (PARTITION BY EmpID ORDER BY Year DESC, SalaryMonth DESC) AS rn
    FROM Salaries
)
SELECT EmpID, SalaryMonth, Year, BaseSalary, Bonus
FROM LatestSalary
WHERE rn = 1;</code></pre>
                    <div class="toggle-container">
                        <button class="btn btn-primary toggle-result">Show Result</button>
                        <button class="btn btn-copy" onclick="copyCode(this)">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-copy">
                                <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>
                                <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
                            </svg>
                            Copy Query
                        </button>
                        <span class="copy-message">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-check">
                                <path d="M20 6 9 17l-5-5"/>
                            </svg>
                            Copied!
                        </span>
                    </div>
                    <div class="result-output" style="display:none;">
                        <table class="result-table">
                            <thead>
                                <tr>
                                    <th>EmpID</th>
                                    <th>SalaryMonth</th>
                                    <th>Year</th>
                                    <th>BaseSalary</th>
                                    <th>Bonus</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr><td>1</td><td>JAN</td><td>2023</td><td>5000.00</td><td>200.00</td></tr>
                                <tr><td>2</td><td>JAN</td><td>2023</td><td>4800.00</td><td>0.00</td></tr>
                                <tr><td>3</td><td>JAN</td><td>2023</td><td>4700.00</td><td>150.00</td></tr>
                                <tr><td>4</td><td>JAN</td><td>2023</td><td>4600.00</td><td>100.00</td></tr>
                                <tr><td>5</td><td>JAN</td><td>2023</td><td>4900.00</td><td>0.00</td></tr>
                                <tr><td>6</td><td>JAN</td><td>2023</td><td>5100.00</td><td>300.00</td></tr>
                                <tr><td>7</td><td>JAN</td><td>2023</td><td>4500.00</td><td>100.00</td></tr>
                                <tr><td>8</td><td>JAN</td><td>2023</td><td>5200.00</td><td>150.00</td></tr>
                            </tbody>
                        </table>
                        <p class="text-sm text-gray-600 mt-2">
                            <em>Note: `SalaryMonth DESC` orders 'JAN' after 'FEB' alphabetically, so 'JAN' is considered 'latest' when ordering by `SalaryMonth DESC` for the two months provided.</em>
                        </p>
                    </div>
                </div>
            </div>
        </section>

        <!-- New Section: Advanced SQL Functions - Window Functions -->
        <section class="sql-section">
            <h2>
                <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-bar-chart-2">
                    <line x1="18" x2="18" y1="20" y2="10"/>
                    <line x1="12" x2="12" y1="20" y2="4"/>
                    <line x1="6" x2="6" y1="20" y2="14"/>
                </svg>
                Advanced SQL Functions: Window Functions
            </h2>
            <p class="text-gray-700 mb-4">
                Window functions perform calculations across a set of table rows that are related to the current row, producing a result for each row without collapsing them.
            </p>

            <div class="sql-query-block">
                <h3>Query: Calculate Previous Day's Sales (LAG)</h3>
                <div class="sql-query-container">
                    <pre class="language-sql"><code>-- Assuming a 'sales' table with 'sale_date' and 'daily_sales'
SELECT
    sale_date,
    daily_sales,
    LAG(daily_sales, 1, 0) OVER (ORDER BY sale_date) as previous_day_sales,
    daily_sales - LAG(daily_sales, 1, 0) OVER (ORDER BY sale_date) as daily_sales_change
FROM
    (VALUES
        ('2023-01-01', 100),
        ('2023-01-02', 120),
        ('2023-01-03', 110),
        ('2023-01-04', 150)
    ) AS sales(sale_date, daily_sales)
ORDER BY sale_date;</code></pre>
                    <div class="toggle-container">
                        <button class="btn btn-primary toggle-result">Show Result</button>
                        <button class="btn btn-copy" onclick="copyCode(this)">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-copy">
                                <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>
                                <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
                            </svg>
                            Copy Query
                        </button>
                        <span class="copy-message">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-check">
                                <path d="M20 6 9 17l-5-5"/>
                            </svg>
                            Copied!
                        </span>
                    </div>
                    <div class="result-output" style="display:none;">
                        <table class="result-table">
                            <thead>
                                <tr><th>sale_date</th><th>daily_sales</th><th>previous_day_sales</th><th>daily_sales_change</th></tr>
                            </thead>
                            <tbody>
                                <tr><td>2023-01-01</td><td>100</td><td>0</td><td>100</td></tr>
                                <tr><td>2023-01-02</td><td>120</td><td>100</td><td>20</td></tr>
                                <tr><td>2023-01-03</td><td>110</td><td>120</td><td>-10</td></tr>
                                <tr><td>2023-01-04</td><td>150</td><td>110</td><td>40</td></tr>
                            </tbody>
                        </table>
                        <p class="text-sm text-gray-600 mt-2">
                            <em>This query uses `LAG()` to fetch the `daily_sales` from the previous row based on `sale_date` order. The third argument `0` is the default value if there is no previous row.</em>
                        </p>
                    </div>
                </div>
            </div>

            <div class="sql-query-block">
                <h3>Query: Assign Salary Quartiles (NTILE)</h3>
                <div class="sql-query-container">
                    <pre class="language-sql"><code>SELECT
    EmpID,
    BaseSalary,
    NTILE(4) OVER (ORDER BY BaseSalary DESC) as salary_quartile
FROM
    Salaries
WHERE SalaryMonth = 'JAN'
ORDER BY BaseSalary DESC;</code></pre>
                    <div class="toggle-container">
                        <button class="btn btn-primary toggle-result">Show Result</button>
                        <button class="btn btn-copy" onclick="copyCode(this)">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-copy">
                                <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>
                                <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
                            </svg>
                            Copy Query
                        </button>
                        <span class="copy-message">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-check">
                                <path d="M20 6 9 17l-5-5"/>
                            </svg>
                            Copied!
                        </span>
                    </div>
                    <div class="result-output" style="display:none;">
                        <table class="result-table">
                            <thead>
                                <tr><th>EmpID</th><th>BaseSalary</th><th>salary_quartile</th></tr>
                            </thead>
                            <tbody>
                                <tr><td>8</td><td>5200.00</td><td>1</td></tr>
                                <tr><td>6</td><td>5100.00</td><td>1</td></tr>
                                <tr><td>1</td><td>5000.00</td><td>2</td></tr>
                                <tr><td>5</td><td>4900.00</td><td>2</td></tr>
                                <tr><td>2</td><td>4800.00</td><td>3</td></tr>
                                <tr><td>3</td><td>4700.00</td><td>3</td></tr>
                                <tr><td>4</td><td>4600.00</td><td>4</td></tr>
                                <tr><td>7</td><td>4500.00</td><td>4</td></tr>
                            </tbody>
                        </table>
                        <p class="text-sm text-gray-600 mt-2">
                            <em>`NTILE(4)` divides the employees into 4 salary quartiles based on their `BaseSalary` in descending order.</em>
                        </p>
                    </div>
                </div>
            </div>
        </section>

        <!-- New Section: Advanced SQL Joins -->
        <section class="sql-section">
            <h2>
                <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-git-merge">
                    <circle cx="18" cy="18" r="3"/>
                    <circle cx="6" cy="6" r="3"/>
                    <path d="M6 21v-3.88a1.88 1.88 0 0 1 2-1.87H12a2 2 0 0 0 2-2V7.5"/>
                    <path d="M10 6h4"/>
                </svg>
                Advanced SQL Joins
            </h2>
            <p class="text-gray-700 mb-4">
                Explore more specialized join types for complex data relationships.
            </p>

            <div class="sql-query-block">
                <h3>Query: Cartesian Product of Employees and Departments (CROSS JOIN)</h3>
                <div class="sql-query-container">
                    <pre class="language-sql"><code>SELECT E.FullName, D.DepartmentName
FROM Employees E
CROSS JOIN Departments D
ORDER BY E.FullName, D.DepartmentName;</code></pre>
                    <div class="toggle-container">
                        <button class="btn btn-primary toggle-result">Show Result</button>
                        <button class="btn btn-copy" onclick="copyCode(this)">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-copy">
                                <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>
                                <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
                            </svg>
                            Copy Query
                        </button>
                        <span class="copy-message">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-check">
                                <path d="M20 6 9 17l-5-5"/>
                            </svg>
                            Copied!
                        </span>
                    </div>
                    <div class="result-output" style="display:none;">
                        <table class="result-table">
                            <thead>
                                <tr><th>FullName</th><th>DepartmentName</th></tr>
                            </thead>
                            <tbody>
                                <tr><td>Alice Johnson</td><td>Finance</td></tr>
                                <tr><td>Alice Johnson</td><td>HR</td></tr>
                                <tr><td>Alice Johnson</td><td>IT</td></tr>
                                <tr><td>Alice Johnson</td><td>Marketing</td></tr>
                                <tr><td>Bob Smith</td><td>Finance</td></tr>
                                <tr><td>Bob Smith</td><td>HR</td></tr>
                                <tr><td>Bob Smith</td><td>IT</td></tr>
                                <tr><td>Bob Smith</td><td>Marketing</td></tr>
                                <tr><td>Carol White</td><td>Finance</td></tr>
                                <tr><td>Carol White</td><td>HR</td></tr>
                                <tr><td>Carol White</td><td>IT</td></tr>
                                <tr><td>Carol White</td><td>Marketing</td></tr>
                                <tr><td>David Lee</td><td>Finance</td></tr>
                                <tr><td>David Lee</td><td>HR</td></tr>
                                <tr><td>David Lee</td><td>IT</td></tr>
                                <tr><td>David Lee</td><td>Marketing</td></tr>
                                <tr><td>Eve Parker</td><td>Finance</td></tr>
                                <tr><td>Eve Parker</td><td>HR</td></tr>
                                <tr><td>Eve Parker</td><td>IT</td></tr>
                                <tr><td>Eve Parker</td><td>Marketing</td></tr>
                                <tr><td>Frank Murphy</td><td>Finance</td></tr>
                                <tr><td>Frank Murphy</td><td>HR</td></tr>
                                <tr><td>Frank Murphy</td><td>IT</td></tr>
                                <tr><td>Frank Murphy</td><td>Marketing</td></tr>
                                <tr><td>Grace Liu</td><td>Finance</td></tr>
                                <tr><td>Grace Liu</td><td>HR</td></tr>
                                <tr><td>Grace Liu</td><td>IT</td></tr>
                                <tr><td>Grace Liu</td><td>Marketing</td></tr>
                                <tr><td>Henry Chan</td><td>Finance</td></tr>
                                <tr><td>Henry Chan</td><td>HR</td></tr>
                                <tr><td>Henry Chan</td><td>IT</td></tr>
                                <tr><td>Henry Chan</td><td>Marketing</td></tr>
                            </tbody>
                        </table>
                        <p class="text-sm text-gray-600 mt-2">
                            <em>A `CROSS JOIN` returns all possible combinations of rows from both tables. With 8 employees and 4 departments, you get 32 rows (8 * 4).</em>
                        </p>
                    </div>
                </div>
            </div>

            <div class="sql-query-block">
                <h3>Query: Latest Employee Hire Date Per Department (LATERAL JOIN - PostgreSQL example)</h3>
                <div class="sql-query-container">
                    <pre class="language-sql"><code>-- This query demonstrates LATERAL JOIN for PostgreSQL.
-- Other databases like SQL Server use CROSS APPLY/OUTER APPLY.
SELECT
    d.DepartmentName,
    e.FullName AS LatestHiredEmployee,
    e.HireDate AS LatestHireDate
FROM
    Departments d,
    LATERAL (
        SELECT FullName, HireDate
        FROM Employees
        WHERE Employees.DepartmentID = d.DepartmentID
        ORDER BY HireDate DESC
        LIMIT 1
    ) AS e
ORDER BY d.DepartmentName;</code></pre>
                    <div class="toggle-container">
                        <button class="btn btn-primary toggle-result">Show Result</button>
                        <button class="btn btn-copy" onclick="copyCode(this)">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-copy">
                                <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>
                                <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
                            </svg>
                            Copy Query
                        </button>
                        <span class="copy-message">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-check">
                                <path d="M20 6 9 17l-5-5"/>
                            </svg>
                            Copied!
                        </span>
                    </div>
                    <div class="result-output" style="display:none;">
                        <table class="result-table">
                            <thead>
                                <tr><th>DepartmentName</th><th>LatestHiredEmployee</th><th>LatestHireDate</th></tr>
                            </thead>
                            <tbody>
                                <tr><td>Finance</td><td>Eve Parker</td><td>2017-04-11</td></tr>
                                <tr><td>HR</td><td>Grace Liu</td><td>2022-02-01</td></tr>
                                <tr><td>IT</td><td>Henry Chan</td><td>2020-05-20</td></tr>
                                <tr><td>Marketing</td><td>Frank Murphy</td><td>2016-12-05</td></tr>
                            </tbody>
                        </table>
                        <p class="text-sm text-gray-600 mt-2">
                            <em>`LATERAL JOIN` allows the subquery `e` to reference columns from `d` for each row of `d`, effectively finding the latest hired employee for each department.</em>
                        </p>
                    </div>
                </div>
            </div>
        </section>

        <!-- New Section: JSON Handling Functions -->
        <section class="sql-section">
            <h2>
                <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-code-2">
                    <path d="M10 12H8"/>
                    <path d="M16 12h-2"/>
                    <path d="M14 6l4 6-4 6"/>
                    <path d="M8 6l-4 6 4 6"/>
                </svg>
                JSON Handling Functions
            </h2>
            <p class="text-gray-700 mb-4">
                Modern SQL databases provide functions to interact with JSON data stored in columns.
            </p>
            <p class="text-gray-700 mb-4 text-sm italic">
                Note: For these examples, imagine a table `products_json` with a column `details` of JSON type,
                and `orders_json` with a column `order_data` of JSON type.
                The example queries will use placeholder data to illustrate.
            </p>

            <div class="sql-query-block">
                <h3>Query: Extracting a Value from JSON (JSON_EXTRACT / ->>)</h3>
                <div class="sql-query-container">
                    <pre class="language-sql"><code>-- MySQL/SQL Server syntax:
SELECT JSON_EXTRACT('{"name": "Laptop", "price": 1200.00, "specs": {"cpu": "i7", "ram_gb": 16}}', '$.specs.cpu') AS CPU;

-- PostgreSQL syntax (using text output operator '->>'):
SELECT '{"name": "Laptop", "price": 1200.00, "specs": {"cpu": "i7", "ram_gb": 16}}'::jsonb->'specs'->>'cpu' AS CPU;
</code></pre>
                    <div class="toggle-container">
                        <button class="btn btn-primary toggle-result">Show Expected Result</button>
                        <button class="btn btn-copy" onclick="copyCode(this)">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-copy">
                                <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>
                                <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
                            </svg>
                            Copy Query
                        </button>
                        <span class="copy-message">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-check">
                                <path d="M20 6 9 17l-5-5"/>
                            </svg>
                            Copied!
                        </span>
                    </div>
                    <div class="result-output" style="display:none;">
                        <table class="result-table">
                            <thead>
                                <tr><th>CPU</th></tr>
                            </thead>
                            <tbody>
                                <tr><td>i7</td></tr>
                            </tbody>
                        </table>
                        <p class="text-sm text-gray-600 mt-2">
                            <em>`JSON_EXTRACT` (or `->>` in PostgreSQL) allows you to pull specific values from a JSON string using a path.</em>
                        </p>
                    </div>
                </div>
            </div>

            <div class="sql-query-block">
                <h3>Query: Aggregate Data into JSON Array (JSON_AGG / JSON_ARRAYAGG)</h3>
                <div class="sql-query-container">
                    <pre class="language-sql"><code>-- PostgreSQL syntax (using JSON_AGG)
SELECT
    d.DepartmentName,
    JSON_AGG(
        JSON_BUILD_OBJECT('employee_name', e.FullName, 'hire_date', e.HireDate)
    ) AS employees_json_list
FROM
    Departments d
JOIN
    Employees e ON d.DepartmentID = e.DepartmentID
GROUP BY
    d.DepartmentName
ORDER BY
    d.DepartmentName;

-- MySQL syntax (using JSON_ARRAYAGG)
-- SELECT
--     d.DepartmentName,
--     JSON_ARRAYAGG(
--         JSON_OBJECT('employee_name', e.FullName, 'hire_date', e.HireDate)
--     ) AS employees_json_list
-- FROM
--     Departments d
-- JOIN
--     Employees e ON d.DepartmentID = e.DepartmentID
-- GROUP BY
--     d.DepartmentName
-- ORDER BY
--     d.DepartmentName;
</code></pre>
                    <div class="toggle-container">
                        <button class="btn btn-primary toggle-result">Show Expected Result</button>
                        <button class="btn btn-copy" onclick="copyCode(this)">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-copy">
                                <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>
                                <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
                            </svg>
                            Copy Query
                        </button>
                        <span class="copy-message">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-check">
                                <path d="M20 6 9 17l-5-5"/>
                            </svg>
                            Copied!
                        </span>
                    </div>
                    <div class="result-output" style="display:none;">
                        <table class="result-table">
                            <thead>
                                <tr><th>DepartmentName</th><th>employees_json_list</th></tr>
                            </thead>
                            <tbody>
                                <tr><td>Finance</td><td>[{"employee_name": "Bob Smith", "hire_date": "2019-03-15"}, {"employee_name": "Eve Parker", "hire_date": "2017-04-11"}]</td></tr>
                                <tr><td>HR</td><td>[{"employee_name": "David Lee", "hire_date": "2021-10-01"}, {"employee_name": "Grace Liu", "hire_date": "2022-02-01"}]</td></tr>
                                <tr><td>IT</td><td>[{"employee_name": "Alice Johnson", "hire_date": "2018-01-10"}, {"employee_name": "Carol White", "hire_date": "2020-07-22"}, {"employee_name": "Henry Chan", "hire_date": "2020-05-20"}]</td></tr>
                                <tr><td>Marketing</td><td>[{"employee_name": "Frank Murphy", "hire_date": "2016-12-05"}]</td></tr>
                            </tbody>
                        </table>
                        <p class="text-sm text-gray-600 mt-2">
                            <em>`JSON_AGG` (PostgreSQL) or `JSON_ARRAYAGG` (MySQL) collects values into a JSON array, useful for nested data structures.</em>
                        </p>
                    </div>
                </div>
            </div>
        </section>

        <!-- Course Conclusion -->
        <section class="mt-8 p-6 bg-green-50 border border-green-200 rounded-lg">
            <h2 class="text-2xl font-semibold text-green-800 mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-graduation-cap">
                    <path d="M21.43 14.83a2 2 0 0 0-1.41-1.41l-4.17-1.41a2 2 0 0 0-2.22 0L8.57 13.42a2 2 0 0 0-1.41 1.41L2.83 19a2 2 0 0 0 1.41 3.41l4.17-1.41a2 2 0 0 0 2.22 0l4.17 1.41a2 2 0 0 0 1.41-1.41L21.43 14.83z"/>
                    <path d="M2 13v-2a6 6 0 0 1 6-6h8a6 6 0 0 1 6 6v2"/>
                    <line x1="8" x2="16" y1="3" y2="3"/>
                    <line x1="12" x2="12" y1="3" y2="6"/>
                </svg>
                Congratulations!
            </h2>
            <p class="text-gray-700 leading-relaxed">
                You've now explored a wide array of essential SQL queries and concepts.
                The best way to solidify your understanding is through consistent practice.
                Try modifying these queries, create new ones, and challenge yourself with different data scenarios.
            </p>
            <p class="text-gray-700 leading-relaxed mt-4">
                Keep practicing, and you'll become a SQL master in no time!
                Feel free to connect with me if you have any questions or need further guidance.
            </p>
        </section>

        <!-- Footer -->
        <footer class="text-center mt-8 pt-4 border-t border-gray-200 text-gray-500 text-sm">
            &copy; 2025 Kaung Myat Kyaw | For Educational Use Only
        </footer>
    </div>

    <!-- LinkedIn Popup HTML -->
    <div id="linkedinPopup" class="popup-overlay">
        <div class="popup-content">
            <button class="popup-close">&times;</button>
            <!-- Profile Photo Placeholder -->
<img src="https://avatars.githubusercontent.com/u/185877470?s=400&u=876d45fd1ac930f3e20022da7ab059c1e7473e1c&v=4" alt="Kaung Myat Kyaw" class="profile-photo" onerror="this.src='https://placehold.co/150x150/A855F7/FFFFFF?text=KMK'">

            <h3>Connect with Kaung Myat Kyaw!</h3>
<p class="text-gray-700 leading-relaxed text-sm">
    <span class="font-semibold text-gray-800 block mb-1">Experienced Professional: Data Analysis, Operations & Management</span>
    I am an experienced professional with over 10 years of expertise in office administration, production management, sales, marketing, and data analysis.
    
    <span class="font-medium block mt-2">Key Roles & Contributions:</span>
    • <span class="font-medium">Telecom Data Analyst:</span> Gathered and analyzed telecom data, developed insightful reports, and ensured data accuracy, contributing to informed decision-making.
    • <span class="font-medium">Production Assistant Manager:</span> Coordinated production schedules, supervised teams, and implemented process improvements that enhanced efficiency and reduced costs. My leadership experience, combined with my operational expertise, allowed me to manage teams and projects effectively.
    
    <span class="font-medium block mt-2">Technical & Professional Development:</span>
    • <span class="font-medium">Self-Study:</span> Proficient in MySQL, Python, and R programming, which I utilize to automate tasks and analyze large datasets. My passion for continuous learning has significantly enhanced my data analysis and technical skills.
    • <span class="font-medium">Professional Training:</span> Completed training in SOP, ISO 22000, Customer Service, and Leadership and Management, further expanding my operational excellence and team management capabilities.
    
    <span class="italic block mt-2 text-center">
        Highly motivated, detail-oriented, and committed to driving results and delivering excellence.
    </span>
</p>

            <h4 class="text-md font-semibold text-gray-700 mb-2">Top Skills:</h4>
            <div class="flex flex-wrap justify-center gap-2 mb-3">
    <span class="px-3 py-1 bg-gradient-to-r from-indigo-500 to-indigo-700 text-white text-xs font-medium rounded-full shadow-sm">SQL</span>
    <span class="px-3 py-1 bg-gradient-to-r from-blue-500 to-blue-700 text-white text-xs font-medium rounded-full shadow-sm">Data Analysis</span>
    <span class="px-3 py-1 bg-gradient-to-r from-green-500 to-green-700 text-white text-xs font-medium rounded-full shadow-sm">Python</span>
    <span class="px-3 py-1 bg-gradient-to-r from-red-500 to-red-700 text-white text-xs font-medium rounded-full shadow-sm">R Programming</span>
    <span class="px-3 py-1 bg-gradient-to-r from-amber-500 to-amber-700 text-white text-xs font-medium rounded-full shadow-sm">Tableau</span>
    <span class="px-3 py-1 bg-gradient-to-r from-yellow-500 to-yellow-700 text-white text-xs font-medium rounded-full shadow-sm">Power BI</span>
    <span class="px-3 py-1 bg-gradient-to-r from-purple-500 to-purple-700 text-white text-xs font-medium rounded-full shadow-sm">Data Viz</span>
    <span class="px-3 py-1 bg-gradient-to-r from-pink-500 to-pink-700 text-white text-xs font-medium rounded-full shadow-sm">DB Management</span>
</div>

                <a href="https://www.linkedin.com/in/kaung-myat-kyaw-96705231a/" target="_blank" rel="noopener noreferrer" class="btn btn-primary mt-4">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-linkedin">
                    <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/>
                    <rect width="4" height="12" x="2" y="9"/>
                    <circle cx="4" cy="4" r="2"/>
                </svg>
                <span class="font-bold text-white">Visit My LinkedIn Profile</span>
            </a>
        </div>
    </div>

    <!-- Prism.js for syntax highlighting -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-sql.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            // Toggle result visibility
            document.querySelectorAll('.toggle-result').forEach(button => {
                button.addEventListener('click', () => {
                    const resultDiv = button.closest('.sql-query-container').querySelector('.result-output');
                    if (resultDiv.style.display === 'none' || resultDiv.style.display === '') {
                        resultDiv.style.display = 'block';
                        button.textContent = 'Hide Result';
                        button.classList.remove('btn-primary');
                        button.classList.add('btn-secondary');
                    } else {
                        resultDiv.style.display = 'none';
                        button.textContent = 'Show Result';
                        button.classList.remove('btn-secondary');
                        button.classList.add('btn-primary');
                    }
                });
            });

            // Copy to clipboard functionality
            window.copyCode = async (button) => {
                const codeBlock = button.closest('.sql-query-container').querySelector('pre code').textContent;
                const messageSpan = button.nextElementSibling; // Get the span for "Copied!" message

                try {
                    // Try navigator.clipboard first
                    await navigator.clipboard.writeText(codeBlock);
                    showMessage(messageSpan);
                } catch (err) {
                    // Fallback for environments where navigator.clipboard is not available (e.g., some iframes)
                    const textarea = document.createElement('textarea');
                    textarea.value = codeBlock;
                    textarea.style.position = 'fixed'; // Avoid scrolling to bottom
                    textarea.style.left = '-9999px'; // Hide off-screen
                    document.body.appendChild(textarea);
                    textarea.select();
                    try {
                        document.execCommand('copy');
                        showMessage(messageSpan);
                    } catch (execErr) {
                        console.error('Failed to copy using execCommand:', execErr);
                        // Using a simple alert for fallback as per prior instructions, though custom modal is preferred.
                        alert('Copy failed: Please copy the code manually.');
                    } finally {
                        document.body.removeChild(textarea);
                    }
                }
            };

            function showMessage(span) {
                span.classList.add('show');
                setTimeout(() => {
                    span.classList.remove('show');
                }, 1500);
            }

            // LinkedIn Popup Logic
            const linkedinPopup = document.getElementById('linkedinPopup');
            const popupCloseButton = linkedinPopup.querySelector('.popup-close');

            setTimeout(() => {
                linkedinPopup.classList.add('show');
            }, 1000); // Show after 2 seconds

            // Auto-hide after 5 seconds if not closed manually (2s show delay + 3s visible duration)
            setTimeout(() => {
                linkedinPopup.classList;
            }, 10000);

            popupCloseButton.addEventListener('click', () => {
                linkedinPopup.classList.remove('show');
            });

            // Optionally, hide if user clicks outside the content (on the overlay)
            linkedinPopup.addEventListener('click', (event) => {
                if (event.target === linkedinPopup) {
                    linkedinPopup.classList.remove('show');
                }
            });
        });
    </script>
</body>
</html>
"""

# Define the output directory and filename
output_directory = r'D:\Git\HTML' # Using a raw string for Windows paths to avoid issues with backslashes
output_filename = 'sql_course_for_mmp.html'
output_filepath = os.path.join(output_directory, output_filename)

# Create the directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)

with open(output_filepath, 'w', encoding='utf-8') as f:
    f.write(html_content)
print(f"HTML file successfully saved to: {output_filepath}")
