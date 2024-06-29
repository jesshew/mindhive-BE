from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from app.models import Outlet, OpeningHours,db
import re
import time

"""
    Scrape Subway outlets' information from the given URL filtered by location.

    Args:
        url (str): The URL of the Subway outlets page to scrape.
        location (str): The location to filter the search results by.

    Returns:
        list[dict]: A list of dictionaries containing scraped outlet data with keys 'name', 'address', 'hours', and 'waze_link'.

    Raises:
        WebDriverException: If there is an error initializing or interacting with the Selenium WebDriver.
        TimeoutException: If the elements required for scraping do not appear within the given time.

    Example:
        outlets = scrape_subway_outlets("https://subway.com.my/find-a-subway", "Kuala Lumpur")
"""
def scrape_subway_outlets(url, location):
    driver = webdriver.Chrome()
    driver.get(url)

    try:
        # Wait until the search bar is visible and interactable (max 10 seconds)
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "fp_searchAddress"))
        )

        # Locate the search bar by its ID and enter the location
        search_bar = driver.find_element(By.ID, "fp_searchAddress")
        search_bar.send_keys(location)
        
        # Locate the search button by its ID and click it
        search_button = driver.find_element(By.ID, "fp_searchAddressBtn")
        search_button.click()
        
        # Get the HTML of the result section
        time.sleep(2) 

        # Use JavaScript to filter out hidden locations
        result_html = driver.execute_script("""
            const list = document.getElementById('fp_locationlist');
            const items = Array.from(list.querySelectorAll('div[class^="fp_listitem fp_list_marker"]'));

            const filteredHTML = items
            .filter(item => item.style.display !== 'none')
            .map(item => item.outerHTML)
            .join('');

            return filteredHTML;
        """)

    finally:
        driver.quit()

    # Parse the filtered HTML using BeautifulSoup
    soup = BeautifulSoup(result_html, 'html.parser')

    # Find all outlet containers
    outlets = soup.find_all('div', class_='fp_listitem')

    scraped_outlets = []

    # Iterate over each outlet container and extract details
    for outlet in outlets:

        # Extract the outlet name
        name = outlet.find('h4').text.strip()
        
        # Extract the address and operating hours if present
        infoboxcontent = outlet.find('div', class_='infoboxcontent')
        if infoboxcontent:
            address = infoboxcontent.find('p').text.strip()
            
            # Regular expression to match day names
            # The date format is inconsistent. Some outlet uses full form (Monday), some uses short form (Sunday)
            day_pattern = re.compile(r"\b(Mon(day)?|Tue(sday)?|Wed(nesday)?|Thur(sday)?|Fri(day)?|Sat(urday)?|Sun(day)?)\b", re.IGNORECASE)

            # Find all <p> tags that match day names to extract operating hours
            hours_p = infoboxcontent.find_all('p', string=day_pattern)

            # Extract and clean the text from matching <p> tags
            hours = [p.text.strip() for p in hours_p if p.text.strip()]

            # Handle multiple time entries by splitting them if separated by semicolons
            hours_text = "; ".join(hours).split('; ') if hours else ["Hours not available"]

        # Extract the Waze link for directions if available
        waze_link = ""
        direction_button = outlet.find('div', class_='directionButton')
        if direction_button:
            waze_anchor = direction_button.find('a', href=lambda href: 'waze.com' in href if href else False)
            if waze_anchor:
                waze_link = waze_anchor['href']

        # Add the extracted outlet details to the scraped_outlets list
        scraped_outlets.append({
            'name': name,
            'address': address,
            'hours': hours_text,
            'waze_link': waze_link
        })

    return scraped_outlets


def add_outlets_to_database(scraped_outlets):
    # print("Adding scraped outlets to the database...")
    with db.session.no_autoflush:
        for outlet_data in scraped_outlets:
            # print(f"Outlet Data: {outlet_data}")

            new_outlet = Outlet(
                name=outlet_data['name'],
                address=outlet_data['address'],
                waze_link=outlet_data['waze_link'],
                latitude=outlet_data['latitude'],
                longitude=outlet_data['longitude']
            )
            db.session.add(new_outlet)
            db.session.commit()  # Commit Outlet first to get outlet_id for OpeningHours
            # print(f"Added outlet: {new_outlet.name} ({new_outlet.id})")

            # Add OpeningHours if hours exist
            if outlet_data['hours'] != ["Hours not available"]:
                hours_list = outlet_data['hours']
                # hours_list = hours_text.split(';')  # Split by ;

                for hours_text in hours_list:
                    new_hours = OpeningHours(
                        description=hours_text.strip(),  # Trim leading/trailing spaces
                        outlet_id=new_outlet.id
                    )
                    db.session.add(new_hours)
                    # print(f"Added opening hours: {new_hours.description} for outlet {new_outlet.name}")
                
                db.session.commit()

    print("Scraped outlets added to the database successfully.")
