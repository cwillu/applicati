-- Exported definition from 2007-10-11T00:31:08
-- Class reports.model.Tokens
-- Database: sqlite
CREATE TABLE tokens (
    id INTEGER PRIMARY KEY,
    root TEXT NOT NULL UNIQUE,
    salt TEXT,
    password TEXT
)
