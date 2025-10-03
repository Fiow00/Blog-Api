# Blog API Project

A sample blog API built with Django and Django REST Framework (DRF).  
This project demonstrates user authentication, registration, and CRUD operations for blog posts, suitable for learning and as a starter for more complex applications.

## Features

- User registration and authentication (login, logout, password change/reset) using [dj-rest-auth](https://dj-rest-auth.readthedocs.io/en/latest/).
- Token-based authentication and session authentication.
- Blog post CRUD endpoints.
- API schema and documentation with [drf-spectacular](https://drf-spectacular.readthedocs.io/en/latest/).
- CORS support for frontend integration.
- Static files served with WhiteNoise.
- Custom user model.

## Project Structure

- `accounts/` – Custom user model and authentication logic.
- `posts/` – Blog post models, serializers, views, and permissions.
- `django_project/` – Project settings and URL configuration.
- `schema.yml` – OpenAPI schema for the API.
- `static/`, `staticfiles/` – Static assets.

## Installation

1. **Clone the repository:**
   ```sh
   git clone git@github.com:Fiow00/Blog-Api.git
   cd Blog_api/
   ```

2. **Create and activate a virtual environment:**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   - Copy `.env.example` to `.env` and set your `SECRET_KEY` and `DATABASE_URL`.

5. **Apply migrations:**
   ```sh
   python manage.py migrate
   ```

6. **Create a superuser (optional, for admin access):**
   ```sh
   python manage.py createsuperuser
   ```

7. **Run the development server:**
   ```sh
   python manage.py runserver
   ```

## API Endpoints

- `/api/v1/dj-rest-auth/` – Authentication endpoints (login, logout, registration, password management).
- `/api/v1/posts/` – Blog post endpoints (list, create, retrieve, update, delete).
- `/api/schema/` – OpenAPI schema.
- `/api/schema/swagger-ui/` – Swagger UI documentation.
- `/api/schema/redoc/` – ReDoc documentation.

## Testing

Run tests with:
```sh
python manage.py test
```
