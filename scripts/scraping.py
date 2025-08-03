import requests
from bs4 import BeautifulSoup
import pandas as pd
import regex as re


###############################################################################################################################
def get_data():
    """
    Main function to scrape UCSD course catalog and save all departments and their courses to CSV files.
    """
    departments = get_departments()
    for department in departments:
        scrape_courses(department)
        print(f"Created {department}.csv")
    print("All departments scraped successfully.")


###############################################################################################################################
def get_departments():
    """
    Scrapes the UCSD course catalog to get all departments with a course listing.
    """
    url = "https://catalog.ucsd.edu/front/courses.html#jsoe"
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    departments = set()
    for a in soup.find_all("a", href=True):
        match = re.match(r"\.\./courses/([A-Z]+)\.html", a["href"]) # finding department codes that have course lists
        if match:
            departments.add(match.group(1))

    return sorted(list(departments))


###############################################################################################################################
def scrape_courses(department):
    '''
    Scrape course information from UCSD catalog for a given department.
    Save course code, title, description, and prerequisites to a CSV file.
    '''
    url = f"https://catalog.ucsd.edu/courses/{department}.html"
    resp = requests.get(url)
    resp.raise_for_status() # Ensure the request was successful
    soup = BeautifulSoup(resp.text, "html.parser")

    courses = []

    for header in soup.find_all("p", class_="course-name"):
        text = header.get_text(strip=True)
        match = re.match(rf"({department}\s+\d+)\.\s*(.*?)\s*\((\d)\)", text)
        if not match:
            continue
        code = match.group(1) # Extract course code
        name = match.group(2) # Extract course name
        units = match.group(3) # Extract course units
        
        try:
            desc = header.find_next_sibling("p", class_="course-descriptions") # Get Descriptions
            description = desc.get_text(strip=True) if desc else ""
        except AttributeError:
            description = ""

        split_desc = description.split("Prerequisites:", 1) # Split description into description and prerequisites
        description = split_desc[0].strip() if split_desc else description.strip()
        prerequisites = split_desc[1].strip() if len(split_desc) > 1 else ""
        
        courses.append({"code": code, "name": name, "units": units, "description": description, "prerequisites": prerequisites})

    df = pd.DataFrame(courses)#.set_index("code")
    df.to_csv(f"data/{department}_courses.csv", encoding="utf-8")



