# Library Management System

A local library management system built with Python, Streamlit, and Excel.

This project was developed to manage books, users, loans, and returns in small libraries that do not require a complex infrastructure or database server. The application runs locally and provides an intuitive interface for librarians to manage daily operations.

## Features

### Books
- Register books
- Search books
- Update book information
- Delete books
- Automatic availability control
- Automatic label generation
- Protection against deletion when active loans exist

### Users
- Register users
- Search users
- Update user information
- Delete users

### Loans
- Register loans
- Track active loans
- Control book availability

### Returns
- Register returns
- Calculate overdue returns

### Reports
- Library metrics dashboard
- Active loans report
- Overdue loans report
- Returns report

## Technologies

- Python
- Streamlit
- Pandas
- OpenPyXL

## Project Status

Current version: v0.1

Completed modules:
- Books Management
- Users Management

Modules under development:
- Loans Management
- Returns Management
- Reports Improvements

## Installation

bash pip install -r requirements.txt 

## Run Application

bash streamlit run app.py 
