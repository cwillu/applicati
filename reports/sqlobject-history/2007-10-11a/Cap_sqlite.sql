-- Exported definition from 2007-10-11T00:31:08
-- Class reports.model.Cap
-- Database: sqlite
CREATE TABLE cap (
    id INTEGER PRIMARY KEY,
    source_id INT CONSTRAINT source_id_exists REFERENCES object(id) ,
    target_id INT CONSTRAINT target_id_exists REFERENCES object(id) ,
    permissions TEXT
)
