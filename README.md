# MindHive Backend Repository

Welcome to the MindHive backend repository. This repository contains the scraper, database management, and server setup for the MindHive project.
Documentation : https://tinyurl.com/mindhive-jess

## Setup Instructions

To run the backend server and associated tasks, follow these steps:

1. **Install Dependencies**: Ensure you have Python installed. Use `pip` to install the required packages listed in `requirements.txt`:

```pip install -r requirements.txt```


2. **Run the Server**: Execute `main.py` to start the backend server
   
```python main.py```


## Functionality

- **Scraper**: Utilizes Selenium to scrape data from the Subway website.
- **Geocoding**: Geocodes outlet locations, which may take some time due to the volume of data.
- **Database Operations**: Adds all scraped data to the database for storage and retrieval.
- **API Server**: Serves API endpoints for accessing outlet information.

## Usage Notes

- Ensure all dependencies are installed before running `main.py`.
- The geocoding process may take some time depending on the number of outlets.
- Once set up, the API will be accessible for retrieving Subway outlet data.
