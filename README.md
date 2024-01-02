# Traffic-Violation-Report-System
The Traffic-Violation-Report-System is a comprehensive platform designed to enhance transparency in traffic law enforcement in Taiwan. The system empowers users to upload, share, and review responses from law enforcement agencies concerning traffic violations. Developed with Python's Django framework, this system integrates various technologies and services, providing a robust and user-friendly experience.

### Application Structure

The system comprises several Django apps, each catering to specific functionalities:

1. **Traffic Data App**: Manages traffic violation data, including storage and retrieval.

2. **Accounts App**: Handles user management functionalities, including registration with Gmail validation and login features.

3. **License Plate Insights App**: Integrates the [YOLOv8-License-Plate-Insights](https://github.com/yihong1120/YOLOv8-License-Plate-Insights) model for license plate recognition.

4. **LLM Customer Service App**: Integrates the Llama2 model or Gemini to enhance the customer response bot.

5. **Reports App**: Facilitates the creation and management of traffic violation reports.

### External Services and Integration

- **BigQuery & Google Cloud Platform (GCP)**: Utilizes GCP's BigQuery for efficient data analysis and storage.

- **Vision API**: Implements OCR techniques for automatic generation of traffic violation parameters.

- **Gemini API**: Enhances system functionalities with advanced capabilities.

- **Google Maps API**: Leverages this API to depict violation locations, numbers, and severity on an interactive map.

- **MySQL Database on Google Compute Engine**: Hosts the SQL database, ensuring robust and scalable data management.

### Deployment and Security

- Planned deployment on Raspberry Pi 5 with nginx redirection on Ubuntu 22.04.
- Procurement of a static domain from Chunghwa Telecom (CHT) for reliable hosting.
- Registration with Google Webmaster Tools for enhanced web management and analytics.
- Measures in place to obscure the real static file path, enhancing system security.

### File Structure

```
Traffic-Violation-Report-System/
│
├── traffic_data/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── ...
│
├── accounts/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── ...
│
├── license_plate_insights/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── ...
│
├── llm_customer_service/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── ...
│
├── reports/
│   ├── media/
│   ├── error_images/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── ...
│
├── utils/
│   ├── models.py
│   ├── views.py
│   ├── bigquery_utils.py
│   ├── utils.py
│   ├── mysql_utils.py
│   └── ...
│
├── static_root/
│   └── ...
│
├── templates/
│   └── ...
│
├── manage.py
└── requirements.txt
```

## To do list

- [ ] Utilise Python's Django to design functionalities for:
    - [x] uploading,
    - [x] displaying,
    - [x] user management,
    - [ ] login recaptcha,
    - [x] registration with Gmail validation,
- [ ] Log in with Google, Facebook, Twitter, Github account.
- [X] Attach the Llama2 model or Gemini to the customer response bot.
- [x] Integrate the [YOLOv8-License-Plate-Insights](https://github.com/yihong1120/YOLOv8-License-Plate-Insights) model to implement license plate recognition.
- [x] Use OCR techniques to automatically generate the parameters of traffic violations.
- [x] Design a SQL and BigQuery database on the cloud to store the information of violation, such as license plate, location, organiser(option), media, time.
- [x] Pull the location on Google map.
- [x] Leverage the Google Maps API to depict the location, number, and severity of traffic violations.
- [ ] Deploy the server on Raspberry Pi 5 and establish nginx redirection of data on Ubuntu 22.04.
- [ ] Procure a static domain from Chunghwa Telecom (CHT).
- [ ] Register for Google Webmaster Tools.
- [ ] Hide the real static file path.
