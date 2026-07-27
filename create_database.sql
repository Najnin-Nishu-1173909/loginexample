CREATE TYPE user_role AS ENUM ('customer', 'staff', 'admin');

CREATE TABLE users (
  user_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  username VARCHAR(20) NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  email VARCHAR(254) NOT NULL,
  user_role user_role NOT NULL
);