# T-001: Django Project Setup and Configuration

## AI Coding Brief
**Role**: Backend Developer
**Objective**: Set up Django project with proper structure and configuration
**Related Story**: S-001 (Vehicle Fleet Management)

## Constraints
**Allowed File Paths**:
- /config/*
- /apps/__init__.py
- /manage.py
- /requirements/*
- /.gitignore
- /pyproject.toml

**Forbidden Paths**: None for initial setup

## Deliverables
- [ ] Django 5.x project created with `config` as settings module
- [ ] Split settings (base.py, development.py, production.py)
- [ ] PostgreSQL database configuration
- [ ] Environment variable handling with python-decouple
- [ ] apps/ directory for Django applications
- [ ] Static and media file configuration
- [ ] Requirements files (base.txt, development.txt, production.txt)
- [ ] .gitignore for Python/Django projects
- [ ] pytest configuration

## Technical Specifications

### Project Structure
```
car-rental/
├── manage.py
├── config/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   └── __init__.py
├── templates/
├── static/
├── media/
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
└── .gitignore
```

### Key Configurations
- DEBUG from environment variable
- SECRET_KEY from environment variable
- DATABASE_URL parsing for PostgreSQL
- ALLOWED_HOSTS configuration
- Static files with whitenoise
- Media files configuration
- Timezone: America/Chicago (or configurable)

## Definition of Done
- [ ] Project runs with `python manage.py runserver`
- [ ] Database connection works
- [ ] Static files served correctly
- [ ] Tests can be run with pytest
- [ ] No hardcoded secrets in code
- [ ] Documentation in code comments
