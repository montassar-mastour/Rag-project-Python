## Run Alembic Migrations

### Configuration 

```bash
cd alembic.ini.example alembic.ini
```

- update the `alembic.ini` with your database credentials(`sqlalchemy.url`)

### (Optional)Create new Migration

```bash
alembic revision --autogenerate -m "Add .."
```

### Update the database

```bash
alembic upgrade head
```