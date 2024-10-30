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
   git clone https://github.com/DeAdiU/Split-Expense.git
   cd Split-Expense

2. Create a virtual environment and install dependencies:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

3. Apply migrations and run the server:
    ```bash 
    python manage.py makemigrations
    python manage.py migrate
    python manage.py runserver

## API Endpoints

1. Authentication:
    - Login - `/login`/ (POST)
    - Register - `/register`/ (POST)
2. User Expense Management:
    - Create Expense - `/create_expense/` (POST)
    - Get Balance - `/balance/` (GET)
    - Personal Expense - `/expenses/user/` (GET)
    - Overall Expense - `/expenses/overall/` (GET)
    - Balance Sheet - `/expenses/balance-sheet/` (GET)
3. API Documentation:
    - Swagger API Docs - `/swagger/` 

## API Documenatation

The project has integrated Swagger for easy API documentation. You can access the Swagger UI by navigating to the `/swagger/` URL when the server is running. Please use Authorize (enter JWT token) to use protected routes.
    
## Contributing

Contributions are welcome! Please fork the repository and create a pull request to submit changes.
