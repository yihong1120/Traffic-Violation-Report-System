# Update the package listings for your system
sudo apt update

# Install the MySQL server package
sudo apt install mysql-server

# Run the script that will help you to secure your MySQL installation
sudo mysql_secure_installation

# Log in to the MySQL command-line client
sudo mysql -u root -p

# Start the Django development server only if the application is not stopped
if [[ "$(gcloud app describe --format='value(state)')" != "STOPPED" ]]; then
    gcloud app deploy
fi
CREATE DATABASE TrafficViolationDB;

# Select the newly created database for use
USE TrafficViolationDB;

# Create a table for traffic violations, defining the structure of your data
CREATE TABLE TrafficViolations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    license_plate VARCHAR(10) NOT NULL,
    date DATE,
    time TIME,
    violation VARCHAR(100),
    status VARCHAR(50),
    location VARCHAR(255),
    officer VARCHAR(255) DEFAULT NULL
);

# Create a table for media files with a foreign key that links to the traffic violations table
CREATE TABLE MediaFiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    traffic_violation_id INT,
    file_path VARCHAR(255),
    FOREIGN KEY (traffic_violation_id) REFERENCES TrafficViolations(id) ON DELETE CASCADE
);

# Exit the MySQL client
exit;

# Start the Django development server
python manage.py runserver
