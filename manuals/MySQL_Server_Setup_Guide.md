# MySQL Server Installation and Configuration Guide

This guide will instruct you on how to install MySQL Server on an Ubuntu system and how to set up a new database and user.

## Installing MySQL Server

Firstly, update your package manager and install MySQL Server.

```bash
sudo apt update
sudo apt install mysql-server
```

Once installed, you should run a security script to enhance the security of your MySQL server.

```bash
sudo mysql_secure_installation
```

This script will guide you through some security settings such as setting the root password, removing anonymous users, disabling root user remote login, etc.

## Configuring MySQL User

Next, you need to create a new user for MySQL. First, log into MySQL as the root user.

```bash
sudo mysql
```

At the MySQL prompt, change the authentication method for the root user and set a new password (replace with your own password).

```sql
ALTER USER 'root'@'localhost' IDENTIFIED WITH 'mysql_native_password' BY 'new_root_password';
```

Create a new MySQL user and set a password for it (please replace `your_username` and `your_password`).

```sql
CREATE USER 'your_username'@'%' IDENTIFIED BY 'your_password';
```

Grant full privileges on all databases to the new user.

```sql
GRANT ALL PRIVILEGES ON *.* TO 'your_username'@'%' WITH GRANT OPTION;
```

## Creating a New Database

Create a new database which your application will use to store data.

```sql
CREATE DATABASE your_database_name;
```

Grant full privileges on the new database to the new user.

```sql
GRANT ALL PRIVILEGES ON your_database_name.* TO 'your_username'@'%';
```

Do not forget to flush the privileges to make the changes take effect.

```sql
FLUSH PRIVILEGES;
```

## Logging into MySQL

Finally, you can log into the MySQL database using the newly created user.

```bash
mysql -u your_username -p -h your_database_host
```

In the above command, `your_database_host` is the IP address or hostname of your database server.

---

Ensure to replace all example usernames, passwords, and database names with your requirements throughout the installation and configuration process.
This document provides basic steps for installing and configuring a MySQL server on an Ubuntu system, including how to create users and databases. Adjust the usernames, passwords, and database names as per your specific requirements.