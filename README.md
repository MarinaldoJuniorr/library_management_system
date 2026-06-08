# Library Management System

A local library management system built with Python, Streamlit, and Excel.

This project was developed to manage books, users, loans, and returns in small libraries that do not require a complex infrastructure or database server. The application runs locally and provides an intuitive interface for librarians to manage daily operations.

---

## Features

### Books

- Register books
- Search books
- Update book information
- Delete books
- Automatic availability control
- Automatic label generation
- Duplicate book code validation
- Protection against deletion when active loans exist

### Users

- Register users
- Search users
- Update user information
- Delete users
- Duplicate phone number validation
- Protection against deletion when active loans exist

### Loans

- Register loans
- Track active loans
- Control book availability
- Loan date validation
- Loan status tracking

### Returns

- Register returns
- Calculate overdue returns
- Return confirmation workflow

### Reports & Dashboard

- Library metrics dashboard
- Active loans report
- Overdue loans report
- Returns report
- Loan status chart
- Search and filtering tools
- Export reports to Excel

---

## Technologies

- Python
- Streamlit
- Pandas
- OpenPyXL
- Plotly

---

## Project Status

Current version: v1.0

### Completed Modules

- Books Management
- Users Management
- Loans Management
- Returns Management
- Reports Dashboard

### Future Improvements

- SQLite integration
- Advanced analytics
- Portfolio version (V2)

---

## Data Storage

This version uses Excel spreadsheets as the data source.

Future versions will migrate to SQL databases.

---

## Installation

Install the required dependencies:

bash pip install -r requirements.txt 

---

## Run Application

Start the application with:

bash streamlit run app.py 

---

## Project Structure

text library_management_system/ │ ├── app.py ├── requirements.txt ├── README.md │ ├── modules/ │   ├── books.py │   ├── users.py │   ├── loans.py │   └── returns.py │ ├── services/ │   ├── excel_service.py │   ├── dashboard_service.py │   └── label_service.py │ ├── assets/ ├── reports/ └── data/ 

---

## Author

Developed as a learning project focused on Python, Streamlit, data management, and software architecture fundamentals.