### Setup & Installation
This project is fully Dockerized. You can run the entire stack with one command.

Prerequisites
- Docker & Docker Compose

Quick Start

```bash
# 1. Clone the repository
git clone <repo_url>
cd whatbytes/core
mkdir logs
cd ..

# 2. make whatbytes/.env file and add the following environment variables
DB_HOST=localhost 
DB_NAME=admin_tool
DB_USER=postgres
DB_PASS=ANAGH@8077045850
REDIS_PASSWORD=mypilluiscute123456832165
ALLOWED_HOSTS=127.0.0.1,localhost
DEBUG=True
SECRET_KEY=django-insecure-ux)0c1v(x%u4_kq3ubi&#%5*fid*ti8gx53(%#5#a8bgbtjb(f


# 3. Build and Start Services
docker-compose up --build


# 4. Apply Migrations (In a new terminal)
# it autohandles migrations on startup, this is optional
docker-compose exec core python manage.py migrate

# 5. Ingest Initial Data (Async Task)
docker-compose exec core python manage.py ingest_data

# 6. Create Superuser (For Admin Panel)
docker-compose exec core python manage.py createsuperuser
```

