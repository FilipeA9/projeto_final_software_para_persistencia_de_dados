-- PostgreSQL Initialization Script
-- This script runs automatically when the container is first created

-- The database 'turistando_db' and user 'turistando' are already created by environment variables

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Grant all privileges to turistando user
GRANT ALL PRIVILEGES ON DATABASE turistando_db TO turistando;
