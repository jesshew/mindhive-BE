from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from app.models import Outlet, OpeningHours,db
import re
import time

def scrape_subway_outlets(url, location):
    driver = webdriver.Chrome()
    driver.get(url)

    try:
        # Wait until the search bar is visible
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "fp_searchAddress"))
        )
        search_bar = driver.find_element(By.ID, "fp_searchAddress")
        search_bar.send_keys(location)
        
        # Click the search button
        search_button = driver.find_element(By.ID, "fp_searchAddressBtn")
        search_button.click()
        
        # Get the HTML of the result section
        time.sleep(2) 

        # Use JavaScript to filter out hidden locations
        result_html = driver.execute_script("""
            const list = document.getElementById('fp_locationlist');
            const items = list.querySelectorAll('div[class^="fp_listitem fp_list_marker"]');
            let filteredHTML = '';
            items.forEach(item => {
                if (item.style.display !== 'none') {
                    filteredHTML += item.outerHTML;
                }
            });
            return filteredHTML;
        """)

    finally:
        driver.quit()

    # Parse result with BeautifulSoup
    soup = BeautifulSoup(result_html, 'html.parser')

    # Find all outlet containers
    outlets = soup.find_all('div', class_='fp_listitem')

    scraped_outlets = []

    for outlet in outlets:
        name = outlet.find('h4').text.strip()
        
        infoboxcontent = outlet.find('div', class_='infoboxcontent')
        if infoboxcontent:
            address = infoboxcontent.find('p').text.strip()
            
            # Regular expression to match day names
            day_pattern = re.compile(r"\b(Mon(day)?|Tue(sday)?|Wed(nesday)?|Thur(sday)?|Fri(day)?|Sat(urday)?|Sun(day)?)\b", re.IGNORECASE)

            # Find all <p> tags within infoboxcontent containing day names
            hours_p = infoboxcontent.find_all('p', string=day_pattern)

            # Extract and clean the text from matching <p> tags
            hours = [p.text.strip() for p in hours_p if p.text.strip()]

            # Split hours by semicolon if present to handle multiple times
            hours_text = "; ".join(hours).split('; ') if hours else ["Hours not available"]

        # Extract waze link 
        waze_link = ""
        direction_button = outlet.find('div', class_='directionButton')
        if direction_button:
            waze_anchor = direction_button.find('a', href=lambda href: 'waze.com' in href if href else False)
            if waze_anchor:
                waze_link = waze_anchor['href']

        # Create Outlet object and add to scraped_outlets list
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
