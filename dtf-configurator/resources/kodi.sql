# DO NOT USE FLUSH PRIVILEGES ! Otherwise the container hangs with root authentication error
USE mysql;
DROP DATABASE IF EXISTS tempdb;
GRANT ALL ON *.* TO 'kodi';
