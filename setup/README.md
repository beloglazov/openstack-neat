1. Create a MySQL database and user for OpenStack Neat:

```
CREATE DATABASE neat;
GRANT ALL ON neat.* TO 'neat'@'controller' IDENTIFIED BY 'neatpassword';
```
