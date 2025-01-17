# interview_papernest

# Network Coverage API

## Overview
The **Network Coverage API** is a project designed to fetch and display network coverage data for specific locations by querying a database. The project is implemented using two solutions: Flask-based and Django-based, both of which are Dockerized for easy deployment

## Features
- RESTful API to retrieve network coverage data for specific locations.
- PostgreSQL database with efficient querying capabilities.
- Integration with a geocoding service for address-to-coordinate conversion.
- Dockerized architecture for easy setup and deployment.
- Automated migrations and data seeding in the Django-based solution.
- Flexible, scalable solutions that can adapt to future requirements.

## Requirements

### Local Setup
- Python 3.11
- PostgreSQL 15
- Docker and Docker Compose
- pip for Python package management

### Environment Variables
The application uses the following environment variables:
- `POSTGRES_DB`: Name of the PostgreSQL database (default: `network_db`)
- `POSTGRES_USER`: PostgreSQL username (default: `postgres`)
- `POSTGRES_PASSWORD`: PostgreSQL password (default: `password`)
- `POSTGRES_HOST`: Hostname of the PostgreSQL server (default: `postgres`)
- `POSTGRES_PORT`: PostgreSQL port (default: `5432`)

## Setup and Deployment
### Using Docker Compose
To deploy the project with Docker Compose:

1. Clone the repository:
   ```bash
   git clone https://github.com/BohdanFSD/interview_papernest.git
   cd interview_papernest
   cd sample1 # for Flask solution
   cd sample2 # for Django solution
   ```

2. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

3. The API will be available at
- Flask Solution: `http://localhost:5000`
- Django Solution: `http://localhost:8000`

### Building and Running Individually
1. Build the Docker image:
   ```bash
   docker build -t network-coverage-api .
   ```

2. Run the PostgreSQL container:
   ```bash
   docker run -d \
       --name postgres_container \
       -e POSTGRES_USER=postgres \
       -e POSTGRES_PASSWORD=password \
       -e POSTGRES_DB=network_db \
       -p 5432:5432 \
       postgres:15
   ```

3. Run the API container:
   ```bash
   docker run -d \
       --name network-coverage-container \
       -e POSTGRES_HOST=postgres_container \
       -e POSTGRES_USER=postgres \
       -e POSTGRES_PASSWORD=password \
       -e POSTGRES_DB=network_db \
       -p 5000:5000 \
       network-coverage-api
   ```
# Flask-Based Solution
## API Endpoints
### GET `/api/`
#### Parameters:
- `q`: Address string to geocode and retrieve network coverage.

#### Example Request:
```bash
curl "http://localhost:5000/api/?q=42+rue+papernest+75011+Paris"
```

#### Example Response:
```json
{
  "Bouygues": {
    "2G": true,
    "3G": true,
    "4G": false
  },
  "Free": {
    "2G": false,
    "3G": true,
    "4G": true
  },
  "Orange": {
    "2G": false,
    "3G": false,
    "4G": false
  },
  "SFR": {
    "2G": true,
    "3G": false,
    "4G": false
  }
}
```

# Django-Based Solution
## Key Features
- Automated migrations.
- Data loading post-migration using Django's post_migrate signal.
- Built-in test coverage for API endpoints, commands, and utility functions.

## Setup (Without Docker)
1. install th dependencies:
```
pip install -r requirements.txt
```
2. Configure PostgreSQL:
- Create database and set environment variables in a `.env` file
3. Apply migrations and load data:
```commandline
python manage.py makemigrations
python manage.py migrate
python manage.py load_csv /path/to/your/data.csv
```
4. Start Django server:
```commandline
python manage.py runserver
```
5. Access the API at `http://127.0.0.1:8000`.

## API Endpoints
### GET `/api/`
#### Parameters:
- `q`: Address string to geocode and retrieve network coverage.

#### Example Request:
```bash
curl "http://localhost:8000/api/?q=42+rue+papernest+75011+Paris"
```

#### Example Response:
```json
{
  "Bouygues": {
    "2G": true,
    "3G": true,
    "4G": false
  },
  "Free": {
    "2G": false,
    "3G": true,
    "4G": true
  },
  "Orange": {
    "2G": false,
    "3G": false,
    "4G": false
  },
  "SFR": {
    "2G": true,
    "3G": false,
    "4G": false
  }
}
```

## Key Differences Between Flask and Django Solutions

| **Aspect**             | **Flask Solution**                        | **Django Solution**                          |
|-------------------------|-------------------------------------------|----------------------------------------------|
| **Framework**           | Flask                                    | Django                                       |
| **Database Management** | Managed manually                         | Automated migrations and post-migration seed |
| **Ease of Scaling**     | Requires more manual effort              | Built-in scalability tools                   |
| **Test Coverage**       | Minimal coverage included                | Detailed tests for API, utilities, and tasks |
| **Background Tasks**    | None                                     | Celery with Redis for background processing  |



#### Differences from Original Specification
In the task's example response, the precision requirement was lower, and coverage data was likely more specific to addresses. However, in this project, results are derived from searching within a **3,000-meter radius** around the provided location. This distance was chosen based on the average size of a town, ensuring results are sufficiently accurate while simplifying processing using the available data.

## Coordinate Conversion
The task initially provided the following formula for converting Lambert 93 coordinates to GPS:
```python
import pyproj

def lamber93_to_gps(x, y):
    lambert = pyproj.Proj('+proj=lcc +lat_1=49 +lat_2=44 +lat_0=46.5 +lon_0=3 +x_0=700000 +y_0=6600000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs')
    wgs84 = pyproj.Proj('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
    long, lat = pyproj.transform(lambert, wgs84, x, y)
    return long, lat
```
However, due to deprecations in the `pyproj` library, this formula was updated based on official documentation recommendations to use the newer `Transformer` API:
```python
from pyproj import Transformer

def lambert93_to_wgs84(x, y):
    transformer = Transformer.from_crs("EPSG:2154", "EPSG:4326", always_xy=True)
    lon, lat = transformer.transform(x, y)
    return lon, lat
```
This ensures compatibility with the latest versions of `pyproj`.

## Rationale for Choosing PostgreSQL
Although querying a CSV file is marginally faster in this specific use case tached , PostgreSQL was chosen as the database for the following reasons:

1. Scalability: PostgreSQL can handle larger datasets and more complex queries, which may be necessary if the service scales or integrates additional features.
2. Concurrency: PostgreSQL can support multiple concurrent users querying the data, whereas a CSV file could create bottlenecks if multiple read/write operations are required.
3. Data Integrity: PostgreSQL offers robust data integrity and ensures ACID compliance, making it a more reliable choice for a production environment.
4. Indexing: The partitioned structure and indexes in PostgreSQL significantly optimize query times for large datasets compared to sequentially reading a CSV.
5. Maintainability: PostgreSQL offers tools and features like backups, replication, and extensions that enhance maintainability over time.


## Contributing
Contributions are welcome! Please submit issues or pull requests on the [GitHub repository](https://github.com/BohdanFSD/interview_papernest).

## Summary
This project offers two scalable solutions to handle network coverage queries: Flask for simplicity and Django for robustness. Both solutions are Dockerized, ensuring easy deployment and scalability. Whether you prefer minimal frameworks like Flask or comprehensive ones like Django, this project demonstrates how both approaches can solve real-world problems effectively.







