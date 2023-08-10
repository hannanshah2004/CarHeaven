import requests
import csv
from bs4 import BeautifulSoup as bs4
import urllib.parse


# The main function that scrapes Craigslist listings and filters based on user input
def main(url_base, user_car, min_price, max_price):
    # Create a URL with user-provided parameters
    url_craig = url_base
    params = dict()
    rsp = requests.get(url_craig, params=params)

    # Print the URL being accessed
    print('Reading from:' + "\n\t" + rsp.url + "\n")
    print("Filters Currently On: \n")
    for key in params.keys():
        print(key, ": ", params.get(key))

    # Parse the HTML content of the Craigslist page
    html = bs4(rsp.text, 'html.parser')
    cars = html.findAll("li", {"class": "cl-static-search-result"})

    car_links = []
    car_info = []

    # Extract links from the HTML content
    for a in html.find_all('a', href=True):
        href_value = a['href']
        if href_value != '#' and href_value != '/' and \
                href_value not in ['https://nwct.craigslist.org/search/suvs',
                                   'https://nwct.craigslist.org/search/classic-cars',
                                   'https://nwct.craigslist.org/search/electric-cars',
                                   'https://nwct.craigslist.org/search/pickups-trucks']:
            car_links.append(href_value)

    car_name = html.findAll('div', class_='title')
    car_price = html.findAll('div', class_='price')

    # Iterate through the listings and gather relevant information
    for name, price, link in zip(car_name, car_price, car_links):
        car_price_numeric = int(price.get_text().replace("$", "").replace(",", ""))
        # Check if the user's car name is in the listing title and if the price is within the user's specified range
        if user_car.lower() in name.get_text().lower() and min_price <= car_price_numeric <= max_price:
            car_info.append({
                "Car Name": name.get_text(),
                "Car Price": price.get_text(),
                "Car Link": link
            })

    # Write car information to a CSV file
    csv_file_path = 'car_information.csv'
    csv_columns = ["Car Name", "Car Price", "Car Link"]

    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for car in car_info:
            writer.writerow(car)

    print("Car information has been written to", csv_file_path)

    # Print car information
    for car in car_info:
        print("Car Name:", car["Car Name"])
        print("Car Price:", car["Car Price"])
        print("Car Link:", car["Car Link"])
        print()  # Add an empty line between each car's details

    print("\n" + "Results: " + str(len(cars)))


if __name__ == "__main__":
    # Get user input for state, car name, minimum price, and maximum price
    user_state = input("What state would you like to purchase your car? ").replace(" ", "")
    user_car = input("What car would you like? : ")
    min_price = float(input("Enter the minimum price: "))
    max_price = float(input("Enter the maximum price: "))

    # Replace spaces with %20 in the car input
    user_car_encoded = urllib.parse.quote(user_car, safe='')

    # Construct the URL
    url = f"https://{user_state}.craigslist.org/search/cta?query={user_car_encoded}"

    # Call the main function with user inputs
    main(url, user_car, min_price, max_price)
