import time

import re
import pandas as pd
import os

import csv

import boto3


from selenium import webdriver

from selenium.webdriver import ChromeOptions, ActionChains

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(chrome_options=chrome_options)
# driver = webdriver.Chrome(ChromeDriverManager().install(),chrome_options=chrome_options)

s3_output_bucket = 'sureter-biodata-bucket'

s3 = boto3.resource('s3',aws_access_key_id=f'{os.getenv("aws_access_key")}',aws_secret_access_key=f'{"aws_access_key"}')

index = 1


def get_name(soup2):
    try:
        restaurant_name = soup2.select_one("h1.HjBfq")
        if restaurant_name:
            restaurant_name = restaurant_name.text
        else:
            restaurant_name = None
        # print("Restaurant Name: ", restaurant_name)
        return restaurant_name
    except Exception as e:
        print(e)


def get_address(soup2):
    try:
        restaurant_address = soup2.select("a.AYHFM")
        if restaurant_address:
            restaurant_address = restaurant_address[1].text
        else:
            restaurant_address = None
        # print("Restaurant Address: ", restaurant_address)
        return restaurant_address
    except Exception as e:
        print(e)


def get_website(soup2):
    try:
        website = soup2.select('span.DsyBj.cNFrA span a.YnKZo.Ci.Wc._S.C.AYHFM')
        time.sleep(0)
        # print(website)
        if website:
            for a in website:
                web_url = a['href']
                return web_url
        else:
            web_url = None
        return web_url
    except Exception as e:
        print(e)


def get_price_cuisines_diet(soup2):
    output = {'price': None, 'cuisines': None, 'special_diets': None}
    try:
        result = soup2.select("div.UrHfr div.BMlpu div")

        for r in result:
            header = r.select_one("div div.tbUiL.b")
            if header is not None:
                header_text = r.select_one("div div.SrqKb")
                print(header)
                if header.text == 'PRICE RANGE':
                    output['price'] = header_text.text.replace("\xa0", "")
                elif header.text == 'CUISINES':
                    output['cuisines'] = header_text.text
                elif header.text == 'Special Diets':
                    output['special_diets'] = header_text.text
        # print(output)
        return output
    except Exception as e:
        print(e)

# error
def get_cuisine(soup2):
    try:
        cuisine = soup2.find('div', text=re.compile("CUISINES"))
        if cuisine:
            cuisine = cuisine.next_sibling.text
        else:
            cuisine = None
        # print("Cuisine: ", cuisine)
        return cuisine
    except Exception as e:
        print(e)

# error
def get_diet(soup2):
    try:
        cuisine = soup2.find('div', text=re.compile("Special Diets"))
        if cuisine:
            cuisine = cuisine.next_sibling.text
        else:
            cuisine = None
        # print("Cuisine: ", cuisine)
        return cuisine
    except Exception as e:
        print(e)

# error
def get_price_range(soup2):
    try:
        price_range = soup2.find('div', text=re.compile("PRICE RANGE"))
        if price_range:
            price_range = price_range.next_sibling.text
            price_range = price_range.replace("\xa0", "")
            # price_range = price_range.text.replace("\xa0", "")
        else:
            price_range = None
        # print("Price Range: ", price_range)
        return price_range
    except Exception as e:
        print(e)


def get_phone_no(soup2):
    try:
        restaurant_phone_no = soup2.select_one("span.DsyBj.cNFrA span.AYHFM a.BMQDV._F.G-.wSSLS.SwZTJ")
        if restaurant_phone_no:
            restaurant_phone_no = restaurant_phone_no.text
        else:
            restaurant_phone_no = None
        # print("Restaurant Phone No: ", restaurant_phone_no)
        return restaurant_phone_no
    except Exception as e:
        print(e)


def get_logo(soup2):
    try:
        temp_logo = soup2.select_one(
            'div.large_photo_wrapper div.prw_rup.prw_common_basic_image.photo_widget.large.landscape div img.basicImg')
        logo = temp_logo.get('src')
        # print("Logo: ", logo)
        return logo
    except Exception as e:
        print(e)


def get_deliveroo_tag(soup2):
    try:
        deliveroo_tag = None
        d_link = soup2.select('a.YnKZo.Ci.Wc._S.C._R.Me.MC.FPPgD')
        # print(d_link)
        d = "p=Restaurants_Deliveroo&src"
        for l in d_link:
            deliveroo_tag = l.get('href')
            if d in deliveroo_tag:
                deliveroo_tag = "https://www.tripadvisor.co.uk" + deliveroo_tag
            else:
                deliveroo_tag = None
                # print("deliveroo_tag: ", deliveroo_tag)
        return deliveroo_tag
    except Exception as e:
        print(e)


def get_opening_hours_dict(soup2):
    complete_hours = {'Sun': "", 'Mon': "", 'Tue': "", 'Wed': "", 'Thu': "", 'Fri': "", 'Sat': ""}
    try:
        hours = soup2.select('div.ERxng.P6.Ci div.zuYLj div div.RiEuX.f')
        # print("hours",hours)
        for h in hours:
            index_1 = h.select_one('div.BhOTk').text
            complete_hours[index_1] = h.text.replace(index_1, '').replace("\xa0", '')
            # print(complete_hours)
        return complete_hours
    except Exception as e:
        print(e)


def tripadvisor_restaurant(row):
    try:
        global driver, index
        print('TripAdvisor Index: ', index)
        list_of_dict = list()
        temp = dict()
        url = row['restaurant_url']
        print('Current Url: ', url)
        # url="https://www.tripadvisor.com/Restaurant_Review-g1954855-d9862376-Reviews-The_Yew_Tree_Pub-Norton_Canes_Staffordshire_England.html"
        driver.get(url)
        time.sleep(0.2)
        url = driver.current_url
        try:

            link = driver.find_element(By.XPATH, "//*[@class='NehmB']")
            time.sleep(0)
            if link:
                actions = ActionChains(driver)
                # print(actions)
                actions.click(link)
                actions.perform()
        except Exception as e:
            print(e)
        time.sleep(0)

        soup2 = BeautifulSoup(driver.page_source, "html.parser")
        # p_c_d = get_price_cuisines_diet(soup2)
        temp['restaurant_name'] = get_name(soup2)
        temp['restaurant_address'] = get_address(soup2)
        temp['website'] = get_website(soup2)
        temp['phone_no'] = get_phone_no(soup2)
        temp['restaurant_opening_hours'] = get_opening_hours_dict(soup2)
        temp['diet'] = get_diet(soup2)
        temp['cuisine'] = get_cuisine(soup2)
        temp['price_range'] = get_price_range(soup2)
        temp['restaurant_logo'] = get_logo(soup2)
        temp['restaurant_url'] = url
        temp['deliveroo_tag'] = get_deliveroo_tag(soup2)
        list_of_dict.append(temp)
        # print('List OF DICT: ', list_of_dict)

        df = pd.DataFrame(list_of_dict)
        if not os.path.isfile('demo.csv'):
            df.to_csv('demo.csv', index=False)
        else:
            df.to_csv('demo.csv', mode='a', header=False, index=False)
        index += 1
    except Exception as e:
        print(e)


def main():
    global index
    with open('input.csv', 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        print("start")
        for row in csv_reader:
            tripadvisor_restaurant(row)

if __name__ == "__main__":
    main()
    file_name = 'Restaurant-bio-' + time.strftime("%Y-%m-%d") + '.csv'
    s3.meta.client.upload_file('./demo.csv', s3_output_bucket,file_name)
