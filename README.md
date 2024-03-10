# Contacts Application

## Overview

This is a Python project that uses FastAPI, SQLAlchemy, and PostgreSQL to create a contacts application with
authentication and authorization. The application provides a RESTful API to manage contacts, including CRUD (Create,
Read, Update, Delete) operations, searching, and birthday reminders. Additionally, it implements user registration,
login, and token-based authentication for secure access. The application has been extended with new functionalities
including user email verification, API usage limits, user avatar changes via the Cloudinary service API, user caching
during authentication using Redis with TTL, and more.

## Features

- **User Authentication:**
    - Register new users with username, email, and password.
    - Login existing users with email and password.
    - Refresh access tokens using refresh tokens.
    - Confirm registered users' email addresses for verification.
    - Change user avatar using Cloudinary service API.
    - Cache current user during authentication using Redis with TTL.
- **Authorization:**
    - Secure API endpoints using token-based authentication.
    - Set limits for API usage (parameters set in .env).
- **Contact Management:**
    - Create new contacts with details like first name, last name, birthday, notes, email, and phone.
    - Retrieve the details of a contact by ID.
    - Update the details of an existing contact by ID.
    - Delete a contact by ID.
    - List all contacts.
    - Search for contacts by name, last name, or email.
    - Get a list of contacts who have birthdays in the next 7 days.

## Installation

### Prerequisites

- Python 3.10 or higher
- Docker
- PostgreSQL (in the Docker container)
- Redis (in the Docker container)

### Steps

1. **Create `.env` File and Set Parameters**

- Use `env.example` for reference.

2. **Setup PostgreSQL and Redis via Docker Compose**

  ```bash
  docker compose up -d 
  ```

You can modify `docker-compose.yml` to set Redis with Web GUI or not.

3. **Clone the Repository**
4. **Install Dependencies**

  ```bash
  poetry install --no-root
  ```

5. **Activate Virtual Environment**

  ```bash
  poetry shell
  ```

6. **Create and/or Apply Alembic Migrations**

**for the first time if no migrations - create**

  ```bash
  alembic init migration
  ```

  ```bash
  alembic revision --autogenerate -m 'Init with auth email verify limits and caching'
  ```

**if present - apply migrations**

  ```bash
  alembic upgrade head
  alembic upgrade heads
  ```

7. **Run the Application**

  ```bash
  uvicorn main:app --reload
  ```

**use this command to see maximum debug info from server**

  ```bash
  uvicorn main:app --reload --log-level trace
  ```

## Usage

**Easy way**

You can open in the browser address:

  ```
  http://localhost:8000/docs
  ```

You can create new user first, login with already created user and add contacts

**Advanced usage**

You can interact with the application using HTTP requests. For example, to create a new contact, you can send a `POST`
request to the `/api/contacts` endpoint with the contact details in the request body.

**Authentication:**

- **Register a new user:**
  ```bash
  curl -X POST http://localhost:8000/api/auth/signup -H "Content-Type: application/json" -d '{"username": "johndoe", "email": "johndoe@example.com", "password": "secretpassword"}'
  ```

- **Login:**
  ```bash
  curl -X POST http://localhost:8000/api/auth/login -H "Content-Type: application/json" -d '{"username": "johndoe@example.com", "password": "secretpassword"}'
  ```

The response will include an access token and a refresh token. Store these tokens securely for subsequent API
requests.

- **Refresh access token:**
  ```bash
  curl -X GET http://localhost:8000/api/auth/refresh_token -H "Authorization: Bearer <your_refresh_token>"
  ```

**Contact Management:**

- **Create a new contact:**
  ```bash
  curl -X POST http://localhost:8000/api/contacts -H "Authorization: Bearer <your_access_token>" -H "Content-Type: application/json" -d '{"first_name": "John", "last_name": "Doe", "email": "johndoe@example.com", "phone": "+1234567890"}'
  ```

- **List all contacts:**
  ```bash
  curl -X GET http://localhost:8000/api/contacts -H "Authorization: Bearer <your_access_token>"
  ```

- **Refer to the API documentation for detailed instructions on using other functionalities.**

## Documentation

You can generate Sphinx documentation for this project.

You can modify file `docs\conf.py` by changing theme:

```
html_theme = 'classic'
```

Build documentation

**Windows**

```bash
 .\make.bat html
```

**macOS / Linux**

```bash
 sphinx-build -M html ./docs ./docs/_build
```

The HTML pages with documentation are in docs/_build/html.

## Testing

You can run unit tests and end-to-end tests for this project.

Run unit tests:

```bash
pytest tests/test_unit_repository_contacts.py -v
```

Check coverage:

```bash
 pytest --cov=repository/
```

```
---------- coverage: platform darwin, python 3.11.7-final-0 ----------
Name                     Stmts   Miss  Cover
--------------------------------------------
repository/contacts.py      78      5    94%
repository/users.py         42      2    95%
--------------------------------------------
TOTAL                      120      7    94%
```

Coverage HTML written to dir htmlcov

```bash
pytest --cov=repository/ --cov-report html
```

Run all tests:

```bash
pytest tests/test* -v
```

<details>

<summary>All Test result</summary>

### Log

```
collected 52 items                                                                                                                                                                               

tests/test_e2e_auth.py::test_signup PASSED                                                                                                                                                 [  1%]
tests/test_e2e_auth.py::test_signup_duplicate_username PASSED           

tests/test_unit_repository_users.py::TestAsyncUser::test_update_token PASSED                                                                                                               [100%]
```

</details>

## Project Structure

- `alembic.ini`: The configuration file for Alembic.
- `conf/config.py`: Contains all settings for all services (sensitive data reads from .env).
- `db.py`: Contains the database session manager and a dependency to get the database session.
- `docs`: Contains the Sphinx documentation for the project.
- `entity/models.py`: Defines the SQLAlchemy models for users and contacts.
- `main.py`: The entry point of the application. It creates the FastAPI application and includes the routers for
  authentication and contacts.
- `migration/env.py`: Contains the Alembic environment configuration.
- `migration/versions`: Contains the Alembic migration scripts.
- `poetry.lock`, `poetry.toml`, `pyproject.toml`: Configuration files for the Python package manager Poetry.
- `README.md`: The markdown file you're reading now.
- `repository/contacts.py`: Contains the database queries for the contacts.
- `repository/users.py`: Contains the database queries.
- `routes/auth.py`: Defines the API endpoints for user registration, login, and token refresh.
- `routes/contacts.py`: Defines the API endpoints for CRUD operations, searching, and birthday reminders related to
  contacts.
- `routes/users.py`: Defines the API endpoints for user management.
- `schemas/contacts.py`: Defines the Pydantic models for contacts.
- `schemas/users.py`: Defines the Pydantic models for users, including authentication tokens.
- `services/auth.py`: Contains the authentication and authorization services.
- `services/email.py`: For sending email.
- `static`: Static directory in the root.
- `template`: Template directory in the root with `index.html` (displayed after opening the home page of the site).
- `tests`: Contains the unit and end-to-end tests for the project.

## Technologies Used

- FastAPI: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/): A modern, fast (high-performance), web
  framework for building APIs with Python 3.6+ based on standard Python type hints.
- SQLAlchemy: [https://www.sqlalchemy.org/](https://www.sqlalchemy.org/): The Python SQL Toolkit and Object-Relational
  Mapper that gives application developers the full power and flexibility of SQL.
- PostgreSQL: [https://www.postgresql.org/](https://www.postgresql.org/): A powerful, open source object-relational
  database system.
- Docker: [https://www.docker.com/](https://www.docker.com/): A platform to develop, ship, and run applications inside
  containers.
- Alembic: [https://alembic.sqlalchemy.org/en/latest/](https://alembic.sqlalchemy.org/en/latest/): A database migration
  tool for SQLAlchemy.
- Passlib: [https://passlib.readthedocs.io/en/stable/](https://passlib.readthedocs.io/en/stable/): A comprehensive
  password hashing library for Python.
- Gravatar: [https://gravatar.com/](https://gravatar.com/): A service that provides profile pictures for email
  addresses.
- Redis: [https://redis.io/](https://redis.io/): An open-source, in-memory data structure store, used as a database,
  cache, and message broker.
- Cloudinary: [https://cloudinary.com/](https://cloudinary.com/): A cloud-based service that provides an end-to-end
  image and video management solution.

## Whats New

- The application uses Docker Compose for PostgreSQL and Redis. The data for PostgreSQL is stored on the local user's
  device, as set in the `docker-compose.yml` file, and the credentials are used from `.env`. You can also
  modify `docker-compose.yml` to set Redis with Web GUI or not.
- The application uses `.env` for storing credentials and settings for the app. An `.env.example` is added in the root
  without data for references.
- The application uses `conf/config.py` file with all settings for all services. Sensitive data is read from `.env`.
- The application uses `services/email.py` for sending email.
- The application has added functionality to confirm registered users' email addresses - user verification.
- The application has set limits for using some APIs. The parameters are set in `.env`.
- The application has added changing user avatar by using Cloudinary service API.
- The application has added current user caching during authentication using Redis with TTL. The TTL is set in `.env`.
- The application has added a `static` directory in the root.
- The application has added a `template` directory in the root with `index.html`. This is displayed after opening the
  home page of the site.
- Added documentation generated by Sphinx
- Added unit and functional (end-t-end) tests

## Additional Notes

- This project demonstrates basic authentication and authorization using JWT tokens. Consider implementing more robust
  security measures in production environments.
- The API documentation can be accessed using a tool like Swagger or generated using a library like `drf-yasg`.
