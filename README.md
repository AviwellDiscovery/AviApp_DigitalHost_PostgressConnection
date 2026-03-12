# AviApp - Digital Host Postgress Connection

A production-ready Django application for managing avian biological data, omics analysis, and research studies with PostgreSQL database integration.

## Overview

AviApp is a web-based data management platform designed for researchers and scientists working with avian host data, omics studies, and biological correlations. It provides a RESTful API and interactive dashboard for managing biological samples, studies, host information, and tissue correlation data.

## Features

- **Data Management**: Comprehensive CRUD operations for biological samples, hosts, studies, and pens
- **Omics Integration**: Support for genomics, transcriptomics, and other omics data types
- **Correlation Analysis**: Pre-computed tissue correlation data for ileum, muscle, liver, OTU, acid, metabolite, and functional datasets
- **RESTful API**: Full Django REST Framework integration with Swagger documentation
- **Data Visualization**: Built-in support for Plotly Dash dashboards
- **Authentication**: JWT-based authentication for secure API access
- **PostgreSQL Database**: Robust relational database with advanced indexing for performance

## Tech Stack

- **Backend**: Django 5.2
- **Database**: PostgreSQL
- **API**: Django REST Framework
- **Authentication**: JWT (SimpleJWT)
- **Visualization**: Plotly Dash, Bokeh
- **Data Processing**: Pandas, NumPy, Scikit-learn, SciPy
- **Frontend**: Bootstrap 5, django-bootstrap-v5

## Prerequisites

- Python 3.9+
- PostgreSQL 12+
- pip
- Git

## Installation

### 1. Clone the Repository

```bash
git clone <REPOSITORY_URL>
cd AviApp_DigitalHost_PostgressConnection
```

### 2. Create Virtual Environment

```bash
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
cd Django/app
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables

The project uses environment variables for secure configuration. Copy the example file and update with your settings:

```bash
cp .env.example .env
```

Edit `.env` with your database credentials:

```env
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=your_django_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

> **Security Note**: Never commit `.env` files to version control. The `.env.example` file is provided as a template.

### 5. Run Migrations

```bash
python manage.py migrate
```

### 6. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 7. Start Development Server

```bash
python manage.py runserver
```

The application will be available at: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Project Structure

```
Django/app/
├── app/                    # Django project configuration
│   ├── asgi.py            # ASGI config for async support
│   ├── wsgi.py            # WSGI config for production
│   └── settings.py        # Project settings
├── Avapp/                  # Main Django application
│   ├── models.py          # Database models
│   ├── views.py           # API views
│   ├── serializers.py     # DRF serializers
│   ├── urls.py            # URL routing
│   ├── admin.py           # Admin configuration
│   ├── forms.py           # Django forms
│   └── migrations/        # Database migrations
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
└── .env.example          # Environment template
```

## API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: [http://127.0.0.1:8000/api/schema/swagger/](http://127.0.0.1:8000/api/schema/swagger/)
- **ReDoc**: [http://127.0.0.1:8000/api/schema/redoc/](http://127.0.0.1:8000/api/schema/redoc/)

## Database Models

The application manages the following core entities:

- **Study**: Research studies with metadata
- **Host**: Biological host subjects (tag, sex, weight)
- **Pen**: Experimental pens with treatment information
- **Sample**: Biological samples with collection dates
- **Omics**: Omics data types and platforms
- **Analysis**: Analysis configurations and parameters
- **Gene/Genome**: Genetic data management
- **Feature**: Biological features tracking
- **Correlation Data**: Pre-computed tissue correlations (Ileum, Muscle, Liver, OTU, Acid, Metabolite, Functional)

## Deployment

### Production Setup

For production deployment, consider the following:

1. **Set `DEBUG=False`** in environment variables
2. **Configure `ALLOWED_HOSTS`** with your production domain
3. **Use environment variables or a secrets manager** for sensitive data
4. **Run collectstatic**: `python manage.py collectstatic`
5. **Use a production WSGI server** (Gunicorn, uWSGI)

### Using Gunicorn

```bash
pip install gunicorn
gunicorn app.wsgi:application --bind 0.0.0.0:8000
```

### Docker Deployment (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "app.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### PostgreSQL Production Notes

- Ensure proper indexing on frequently queried columns
- Configure connection pooling for better performance
- Enable SSL/TLS for database connections in production

## Development Commands

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Shell access
python manage.py shell

# Check for issues
python manage.py check

# Run tests
python manage.py test
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the Aviwelll License - R@

## Acknowledgments

- Django Community
- PostgreSQL Documentation
- Django REST Framework