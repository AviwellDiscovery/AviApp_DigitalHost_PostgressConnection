# Database dump and restore

## Overview

The PostgreSQL dump used for the Digital Host project is not stored in this Git repository because it is too large, the link to get it is threw the shared Aviwell drive 

'link in process ....'

## Dump storage

The full dump is stored externally on Google Drive or internal storage.


## Dump creation command

The PostgreSQL dump used for this project was generated using the following command:
```bash
pg_dump -U reda -h localhost -p 5432 devdatabase_16_11 > database_dump_16_11_digitalhostPg.sql
```
Explanation

pg_dump : PostgreSQL database export tool
-U reda : database user
-h localhost : database host
-p 5432 : PostgreSQL port
devdatabase_16_11 : database name
> : redirects the output to a SQL dump file

## Expected database

- Engine: PostgreSQL
- Database name: devdatabase_16_11
- Host: localhost
- Port: 5432

## Important

- Do not commit the real dump into Git
- The `.env` file must contain the correct database credentials
- Download the dump locally before restoring it

## Example `.env`

```env
DB_NAME=devdatabase_16_11
DB_USER=reda
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=5432
```


## Recommended workflow

1-Clone the repository
2-Create and activate the virtual environment
3-Install dependencies
4-Create the .env file from .env.example
5-Download the PostgreSQL dump from Google Drive
6-Restore the dump locally
7-Run migrations if needed
8-Start the Django application
