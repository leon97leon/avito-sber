from selenium import webdriver
driver = webdriver.Chrome()
driver.get("https://www.avito.ru/groznyy/zemelnye_uchastki/uchastok_10_sot._izhs_1827643478")
driver.find_element_by_css_selector('a[class="item-closed-warning"]')