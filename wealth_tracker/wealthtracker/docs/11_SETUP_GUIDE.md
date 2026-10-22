# 11. Complete Windows Setup Guide: From Scratch

This document provides step-by-step instructions for running the project on a fresh Windows system.

---

## Prerequisites
1. **Python 3.13** installed (ensure *"Add Python to PATH"* was checked during installation).
2. **MySQL Server 8.0** installed and running on port `3306`.
3. **Git** and **VS Code**.

---

## Step 1: Open Terminal & Navigate to Project Directory
Open PowerShell or Command Prompt:
```cmd
cd c:\Users\Parinika\OneDrive\Desktop\wealth_tracker\wealth_tracker\wealthtracker
```

---

## Step 2: Virtual Environment Setup
If virtual environment already exists:
```cmd
..\venv\Scripts\activate
```

If setting up fresh:
```cmd
python -m venv ..\venv
..\venv\Scripts\activate
```

---

## Step 3: Install Required Dependencies
Ensure pinned versions are installed:
```cmd
pip install Django==5.1.5 mysqlclient scikit-learn pandas numpy joblib python-dateutil
```

---

## Step 4: MySQL Database Configuration
Open **MySQL Workbench** or the MySQL Command Line Client, and run:
```sql
CREATE DATABASE IF NOT EXISTS wealth_tracker_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Verify your credentials in `wealthtracker/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'wealth_tracker_db',
        'USER': 'root',
        'PASSWORD': 'your_mysql_password',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```

---

## Step 5: Apply Database Migrations
Run the standard Django schema migrations:
```cmd
python manage.py migrate
```

Verify that system checks pass without errors:
```cmd
python manage.py check
```

---

## Step 6: Train ML Models & Seed Demo Data
To train the initial Naive Bayes and Linear Regression models:
```cmd
python manage.py train_ml_models
```

To seed realistic 6 months of test records for immediate demonstration:
```cmd
python manage.py seed_demo_data
```

---

## Step 7: Run the Development Server
Start the local server:
```cmd
python manage.py runserver 127.0.0.1:8000
```

---

## Step 8: Access the Application
1. Open your browser and navigate to: **`http://127.0.0.1:8000/`**
2. You will be greeted by the **Public Landing Page**.
3. Click **"Sign In"** and use the demo credentials:
   - **Username:** `shadow`
   - **Password:** `shadow123`
4. Or register a brand new account at **`http://127.0.0.1:8000/signup/`**.
