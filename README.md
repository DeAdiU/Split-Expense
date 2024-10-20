# Daily Expenses Sharing Application

A backend API for managing daily shared expenses, built using Django REST Framework (DRF). The app supports splitting expenses equally, by exact amounts, or by percentages, with features for user management, expense management, and balance sheet generation.

## Features

- User registration, authentication (JWT-based).
- Expense creation and splitting among multiple users.
- Support for splitting:
  - Equally
  - By exact amounts
  - By percentages
- Balance sheet generation to track owed and paid amounts.

## Requirements

- Python 3.12+
- Django 4.x
- Django REST Framework
- PyJWT

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/expenses-sharing-app.git
   cd expenses-sharing-app
