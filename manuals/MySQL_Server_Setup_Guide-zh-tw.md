🇬🇧 [English](./MySQL_Server_Setup_Guide.md) | 🇹🇼 [繁體中文](./MySQL_Server_Setup_Guide-zh-tw.md)

#MySQL 伺服器安裝與設定指南

本指南將指導您如何在 Ubuntu 系統上安裝 MySQL 伺服器，以及如何設定一個新的資料庫和使用者。

## 安裝 MySQL 伺服器

首先，更新您的套件管理器並安裝 MySQL 伺服器。

```bash
sudo apt update
sudo apt install mysql-server
```

完成安裝後，您應該執行一個安全腳本來增強 MySQL 伺服器的安全性。

```bash
sudo mysql_secure_installation
```

此腳本將引導您完成一些安全性設置，例如設定 root 密碼、刪除匿名使用者、禁止 root 使用者遠端登入等。

## 設定 MySQL 用戶

接下來，您需要為 MySQL 建立一個新使用者。 首先，以 root 使用者身分登入 MySQL。

```bash
sudo mysql
```

在 MySQL 提示符號下，更改 root 使用者的身份驗證方法並設定新密碼（替換您自己的密碼）。

```sql
ALTER USER 'root'@'localhost' IDENTIFIED WITH 'mysql_native_password' BY 'new_root_password';
```

建立一個新的 MySQL 用戶，並為其設定密碼（請取代 `your_username` 和 `your_password`）。

```sql
CREATE USER 'your_username'@'%' IDENTIFIED BY 'your_password';
```

為新使用者授予對所有資料庫的全部權限。

```sql
GRANT ALL PRIVILEGES ON *.* TO 'your_username'@'%' WITH GRANT OPTION;
```

## 建立新資料庫

建立一個新資料庫，您的應用程式將使用這個資料庫來儲存資料。

```sql
CREATE DATABASE your_database_name;
```

為新使用者授予對新資料庫的全部權限。

```sql
GRANT ALL PRIVILEGES ON your_database_name.* TO 'your_username'@'%';
```

不要忘記刷新權限以使更改生效。

```sql
FLUSH PRIVILEGES;
```

## 登入 MySQL

最後，您可以使用新建立的使用者登入 MySQL 資料庫。

```bash
mysql -u your_username -p -h your_database_host
```

在上面的指令中，`your_database_host` 是您的資料庫伺服器的 IP 位址或主機名稱。

---

確保在安裝和配置過程中替換所有範例使用者名稱、密碼和資料庫名稱以符合您的需求。
此文件提供了在 Ubuntu 系統上安裝和設定 MySQL 伺服器的基本步驟，包括如何建立使用者和資料庫。 請根據您的具體情況調整使用者名稱、密碼和資料庫名稱。