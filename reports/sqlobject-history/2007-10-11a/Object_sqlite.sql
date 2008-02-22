-- Exported definition from 2007-10-11T00:31:08
-- Class reports.model.Object
-- Database: sqlite
CREATE TABLE object (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    data TEXT
)
