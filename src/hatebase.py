import requests
from bs4 import BeautifulSoup
import json
import csv
from concurrent.futures import ThreadPoolExecutor

lang = 'eng'

def extract_data_from_page(page_number):
    try:
        # Construct the URL for the current page
        current_page_url = f"https://hatebase.org/search_results/language_id=eng%7Cpage={page_number}"

        # Send an HTTP GET request to the current page
        current_page_response = requests.get(current_page_url)

        # Check if the request was successful (status code 200)
        if current_page_response.status_code == 200:
            # Parse the HTML content of the current page
            current_page_soup = BeautifulSoup(current_page_response.text, "html.parser")

            # Find the table with class "table-condensed table-hover"
            table = current_page_soup.find("table", class_="table table-condensed table-hover")

            # Initialize a list to store data from this page
            page_data = []

            # Find all <tr> elements within the <tbody>
            for tr in table.find("tbody").find_all("tr"):
                # Extract data from the <td> elements
                td_elements = tr.find_all("td")

                # Check if there are exactly 4 <td> elements
                if len(td_elements) == 4:
                    # Extract text from each <td> element and map to keys
                    data = {
                        "term": td_elements[0].get_text(strip=True),
                        "language": td_elements[1].get_text(strip=True),
                        "sightings": td_elements[2].get_text(strip=True),
                        "offense_level": td_elements[3].get_text(strip=True),
                    }

                    # Append the extracted data to the list
                    page_data.append(data)

            print(f"Processed page {page_number}")
            return page_data

        else:
            print(f"Failed to retrieve page {page_number}. Status code: {current_page_response.status_code}")
            return []

    except Exception as e:
        print(f"Error on page {page_number}: {str(e)}")
        return []

def main():
    # Initialize a list to store the extracted data from all pages
    extracted_data = []

    page_number = 1  # Start with the first page
    total_results = None

    while total_results is None or len(extracted_data) < total_results:

        print("Querying page ", page_number)
        # Construct the URL for the current page
        current_page_url = f"https://hatebase.org/search_results/language_id={lang}%7Cpage={page_number}"

        # Send an HTTP GET request to the current page
        current_page_response = requests.get(current_page_url)

        # Check if the request was successful (status code 200)
        if current_page_response.status_code == 200:
            # Parse the HTML content of the current page
            current_page_soup = BeautifulSoup(current_page_response.text, "html.parser")

            if total_results is None:
                # Find the <b> tag within the <p> tag
                total_results_tag = current_page_soup.find("p").find("b")

                # Extract the text from the <b> tag
                total_results_text = total_results_tag.text.strip()

                total_results = int(total_results_text.split(" ")[-2].replace(",", ""))
                # print("Total results:", total_results)

            # Find the table with class "table-condensed table-hover"
            table = current_page_soup.find("table", class_="table table-condensed table-hover")

            # Initialize a list to store data from this page
            page_data = []

            # Find all <tr> elements within the <tbody>
            for tr in table.find("tbody").find_all("tr"):
                # Extract data from the <td> elements
                td_elements = tr.find_all("td")

                # Check if there are exactly 4 <td> elements
                if len(td_elements) == 4:
                    # Extract text from each <td> element and map to keys
                    data = {
                        "term": td_elements[0].get_text(strip=True).replace("\n", ""),
                        "language": td_elements[1].get_text(strip=True),
                        "sightings": td_elements[2].get_text(strip=True),
                        "offense_level": td_elements[3].get_text(strip=True),
                    }

                    # Append the extracted data to the list
                    page_data.append(data)

            # Extend the extracted_data list with data from this page
            extracted_data.extend(page_data)

            print(extracted_data)
            print(len(extracted_data), " offensive lexicons collected")

            page_number += 1  # Move to the next page

        else:
            print(f"Failed to retrieve page {page_number}. Status code: {current_page_response.status_code}")

    # Sort the extracted data by the "term" key
    extracted_data.sort(key=lambda x: x["term"])

    # Define the CSV file name
    csv_file_name = "hatebase_data.csv"

    # Write the extracted data to a CSV file
    with open(csv_file_name, mode="w", newline="") as csv_file:
        fieldnames = ["term", "language", "sightings", "offense_level"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for data in extracted_data:
            writer.writerow(data)

    print(f"Data has been written to {csv_file_name}")

if __name__ == "__main__":
    main()
