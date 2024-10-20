Expense Sharing Application - Backend API

This project is a backend API for an expense sharing application built with Django REST Framework (DRF). The API allows users to manage and share expenses, authenticate using JWT tokens, and retrieve their personal data along with their expense details.
Features

    User Authentication using JWT tokens.
    Expense Management: Create, view, and manage expenses.
    User-specific Data: Retrieve expenses for a specific user based on the authenticated token.
    Secure API Endpoints: All endpoints are protected using JWT authentication.

Technologies Used

    Django (Python Web Framework)
    Django REST Framework (for building REST APIs)
    PyJWT (for JWT-based authentication)
    drf-yasg (for auto-generating Swagger/OpenAPI documentation)
    SQLite (or any other database supported by Django)

Prerequisites

    Python 3.10+
    pip (Python package manager)

Installation

    Clone the repository:

    bash

git clone https://github.com/yourusername/expense-sharing-app.git
cd expense-sharing-app

Create a virtual environment:

bash

python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install the dependencies:

bash

pip install -r requirements.txt

Apply database migrations:

bash

python manage.py migrate

Run the development server:

bash

    python manage.py runserver

Configuration

    Set up a .env file to define the secret key and other environment variables:

    bash

    SECRET_KEY=your_secret_key
    DEBUG=True

    Optionally configure other settings such as database configuration in settings.py.

API Endpoints
Authentication

    Login - /login/ (POST)
        Description: Log in the user and generate a JWT token.
        Request:

        json

{
  "email": "user@example.com",
  "password": "password123"
}

Response:

json

        {
          "token": "jwt_token_string",
          "user": {
            "id": 1,
            "email": "user@example.com",
            "name": "John Doe"
          }
        }

User Data

    Get User Expenses - /user/expenses/ (GET)
        Description: Get all expenses related to the authenticated user.
        Headers:
            Authorization: Bearer <token>
        Response:

        json

        [
          {
            "id": 1,
            "amount": 100.00,
            "description": "Dinner",
            "created_at": "2024-10-20T12:34:56Z"
          },
          ...
        ]

Expense Management

    Create Expense - /expenses/ (POST)
        Description: Add a new expense for the authenticated user.
        Request:

        json

{
  "amount": 50.75,
  "description": "Lunch with friends"
}

Response:

json

        {
          "id": 2,
          "amount": 50.75,
          "description": "Lunch with friends",
          "created_at": "2024-10-20T15:12:00Z"
        }

Swagger API Documentation

The project has integrated Swagger for easy API documentation. You can access the Swagger UI by navigating to the /swagger/ URL when the server is running.
JWT Authentication Flow

    User Login: When a user logs in with valid credentials, they receive a JWT token in the response.
    Authenticated Requests: For any subsequent API requests, the token must be passed in the Authorization header as Bearer <token>.
    Token Validation: The backend verifies the token, and if it's valid, allows the request. If not, it returns an appropriate error message (e.g., 401 Unauthorized).

Error Handling

    401 Unauthorized: Raised when the token is invalid, missing, or expired.
    404 Not Found: Raised when the requested resource (like a user or expense) cannot be found.
    400 Bad Request: Raised when the input validation fails (e.g., missing or invalid fields).

Testing

You can run tests using Django's built-in testing framework. Tests for authentication, expense management, and user-specific requests are provided.

    Run the tests:

    bash

    python manage.py test

Future Enhancements

    Add the ability to split expenses between multiple users.
    Add more detailed financial reports for users.
    Implement user roles (e.g., admin, regular user) with different levels of access.

Contributing

Contributions are welcome! Please fork the repository and create a pull request to submit changes.
License

This project is licensed under the MIT License.