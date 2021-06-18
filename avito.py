from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyodbc
path = "output.csv"
def find(driver,css):
    try:
        driver.find_element_by_css_selector(str(css))
        return 1
    except:
        return 0
def f(l):
    n = []
    for i in l:
        if i not in n:
            n.append(i)
    return n

def pars(driver):
    data=[]
    elem = driver.find_elements_by_css_selector('div[data-marker="item"]')
    for i in elem:
        try:
            url = i.find_element_by_css_selector('a[data-marker="item-title"]').get_attribute("href")
            title=i.find_element_by_css_selector('a[data-marker="item-title"]').text
            price=i.find_element_by_css_selector('span[data-marker="item-price"]').text
            address=i.find_element_by_css_selector('div[data-marker="item-address"]').text
            data.append([url,title,price,address])
            print(f'{url} {title} {price} {address}')
            #file.write(f'{url}|{title}|{price}|{address}\n')
        except Exception as e:
            print(str(e))
    return data
url=input("Введите url для парсинга:")
server=input("Введите сервер базы данных:")
name=input("Введите имя базы данных:")
driver = webdriver.Chrome()
driver.set_page_load_timeout(60)
driver.get(url)

data = pars(driver)
#for i in range(len(data)):
#driver.get(data[0][0])
#driver.save_screenshot("screenshot/0.png")

#driver.close()
while True:
    try:
        while driver.find_element_by_css_selector('span[data-marker="pagination-button/next"]').get_attribute("class").find("readonly") == -1:
        #for i in range(1):
            button_next = driver.find_element_by_css_selector('span[data-marker="pagination-button/next"]')
            button_next.click()
            #driver.implicitly_wait(2)
            #wait = WebDriverWait(driver, 10)
            #element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'span[data-marker="pagination-button/next"]')))
            data.extend(pars(driver))
        break
    except:
        driver.refresh()
data=f(data)
for i in range(len(data)):
    while True:
        try:
            print(i)
            driver.get(data[i][0])
            if find(driver,'a[class="item-closed-warning"]') == 1 or find(driver,'div[class="item-view-warning-content"]') == 1:
                driver.save_screenshot(f"screenshot/{i}.png")
                data[i].extend([f"screenshot/{i}.png", "Объявление снято с публикации", "Объявление снято с публикации"])
            else:
                driver.save_screenshot(f"screenshot/{i}.png")
                lat = driver.find_element_by_css_selector('div[data-map-type="dynamic"]').get_attribute("data-map-lat")
                lon = driver.find_element_by_css_selector('div[data-map-type="dynamic"]').get_attribute("data-map-lon")
                data[i].extend([f"screenshot/{i}.png", lat, lon])
            break
        except:
            pass
driver.close()
with open(path, "w", encoding="utf-8") as file:
    for i in data:
        file.write(f'{i[0]}|{i[1]}|{i[2]}|{i[3]}|{i[4]}|{i[5]}|{i[6]}\n')
#conn = pyodbc.connect('DRIVER={SQL Server};SERVER=localhost\SQLEXPRESS01;DATABASE=avito;Trusted_Connection=yes')
conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+name+';Trusted_Connection=yes')

cursor = conn.cursor()

query1 = """
        CREATE TABLE avito(
            "URL" varchar(255),
            "Название" varchar(255),
            "Цена" varchar(255),
            "Адрес" varchar(255),
            "Скриншот" varchar(255),
            "Широта" varchar(255),
            "Долгота" varchar(255)
        )"""
query = """
        INSERT INTO avito (
            "URL",
            "Название",
            "Цена",
            "Адрес",
            "Скриншот",
            "Широта",
            "Долгота"
        ) VALUES (?, ?, ?, ?, ?, ?, ?)"""
try:
    cursor.execute(query1)
    conn.commit()
except pyodbc.ProgrammingError:
    pass
cursor.execute("TRUNCATE TABLE avito")
cursor.execute("SELECT count(*) FROM avito")
for r in data:
    cursor.execute(query, tuple(r))
conn.commit()
conn.close()