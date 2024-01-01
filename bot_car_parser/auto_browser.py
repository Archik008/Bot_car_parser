import pickle, datetime, pytz, threading, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from data.config import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from change_filename import return_formatted_file_name


def add_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("window-size=1400,600")
    #options.add_argument("--no-sandbox")
    #options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomaticControlled")
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=options)
    return driver


def find(text,driver):#поиск элемента по тексту
    element = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//*[text()='"+str(text)+"']")))
    return (element)


def autor(driver,login,passw): #авторизация
    driver.get("https://cubedcommunity.xcira.com")
    driver.set_window_size(1920, 1080)
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, "adornment-email"))).send_keys(login)
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, "adornment-password"))).send_keys(passw)
    try:
        find("Accept All Cookies",driver).click()
    except:
        pass
    find("Login",driver).click()
    return driver


def get_info_car(driver):
    WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.CLASS_NAME,"image-gallery-image")))
    element=find("Details",driver)
    for i in range(2):
        element=element.find_element(By.XPATH,'..')
    info=element.text
    info=info.split("\n")
    #print(info)
    
    #получение LIGHTS
    element=driver.find_element(By.CLASS_NAME,"css-1qaqelx-root")
    elements=element.find_elements(By.XPATH,".//*")
    lights_list=["green","yellow","red","blue","white"]
    lights=[]
    n=0
    for element in elements:
        if element.get_attribute("class")!="css-ze5wd9-root":
            lights.append(lights_list[n])
        n+=1

    #получение фото
    image_url=[]
    elements=driver.find_elements(By.CLASS_NAME,"image-gallery-image")
    for elm in elements:
        image_url.append(elm.get_attribute("src"))


    characteristics=["VIN","MMR", "GRADE", "BODY STYLE","TRIM","INTERIOR COLOR","EXTERIOR COLOR","INTERIOR MATERIAL","MILEAGE","ODOMETER STATUS","ENGINE","FUEL TYPE","DRIVE","TRANSMISSION"]
    #формируем результат
    info_car={"LIGHTS":lights,"IMAGE":image_url}
    for i in info:
        if i in characteristics:
            info_car[i]=info[info.index(i)+1]
    info_car['CAR NAME'] = driver.find_element(By.CLASS_NAME, 'css-vcuvf9-root').find_element(By.CLASS_NAME, 'css-jx2uny-header').find_element(By.TAG_NAME, 'h1').text
    return info_car


def update_list_car(auction,driver):#получение списка всех авто
    driver.get("https://cubedcommunity.xcira.com/inventory")
    driver.set_window_size(1920, 1080)
    try:
        find("Accept All Cookies",driver).click()
    except:
        pass
    try:
        find("My Saved Search",driver).click()
    except:
        pass
    try:
        find("Clear All",driver).click()
    except:
        pass
    element=find("Quick Search",driver)
    id_element=element.get_attribute("id").split("-")[0]
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, id_element))).send_keys(auction)
    element=find(auction,driver).click()
    for i in range(2):
        driver.execute_script("window.scrollTo(0,"+str(i*300)+")")#прокрутка
    try:
        find("No vehicles found.",driver)
        return []
    except:
        pass
    car_list=[]
    n=1
    #получение марок
    elements=driver.find_elements(By.CLASS_NAME,"MuiList-root")
    element=elements[1]
    try:
        element.find_element(By.XPATH, "//*[text()='Show More']").click()
    except:
        pass
    time.sleep(0.5)
    elements=element.find_elements(By.CLASS_NAME,"css-onb3pj-primaryTextWrapper")
    brands=[]
    for elm in elements:
        brand=elm.text
        brand=brand.split("\n")[0]
        brands.append(brand)
        #print(brands)
    for brand in brands:
        try:
            elm=element.find_element(By.XPATH, f"//*[text()='{brand}']")
        except:
            continue
        actions = ActionChains(driver)
        actions.move_to_element(elm)
        actions.perform()
        time.sleep(1)
        elm.click()
        #ищем по моделям
        time.sleep(1)
        driver.find_element(By.XPATH, "//*[text()='Model']").click()
        time.sleep(1)
        driver.execute_script("window.scrollTo(0,300);")#прокрутка
        elements_2=driver.find_elements(By.CLASS_NAME,"MuiList-root")
        element_2=elements_2[2]
        try:
            element_2.find_element(By.XPATH, "//*[text()='Show More']").click()
        except:
            pass
        time.sleep(1)
        elements_2=element_2.find_elements(By.CLASS_NAME,"MuiButtonBase-root")
        for elm_2 in elements_2:
            time.sleep(1)
            try:
                model = elm_2.text
            except:
                continue
            model=model.split("\n")[0]
            actions = ActionChains(driver)
            actions.move_to_element(elm_2)
            actions.perform()
            time.sleep(1)
            elm_2.click()
            #получаем список авто
            if model=='':
                continue
            else:
                time.sleep(1.5)
                while True:
                    try:
                        find("Inventory List",driver)
                    except:
                        break
                    elements_3=driver.find_elements(By.CLASS_NAME,"MuiCard-root")
                    if elements_3 == []:
                        break
                    for elm_3 in elements_3:
                        try:
                            info=elm_3.text
                            #print(info)
                        except:
                            continue
                        info=info.split("\n")
                        lot=info[0]
                        year=info[1][:4]
                        info=str(info[1])+" "+str(info[5])
                        id_car=elm_3.get_attribute("id")
                        if not (year=="PEND") and not (year=="SOLD"):
                            car_list.append({"info":info,"id_car":id_car,"model":model,"year":year,"brand":brand,"lot":lot})
                            n+=1
                    elements_4=driver.find_elements(By.CLASS_NAME,"css-cs55g8-buttonText")
                    try:
                        elements_4[1].click()
                        time.sleep(1.5)
                    except:
                        break
        actions = ActionChains(driver)
        actions.move_to_element(elm)
        actions.perform()
        time.sleep(1)
        elm.click()
        time.sleep(2)
    return car_list        



def update(auction):
    state_auction = return_formatted_file_name(auction) + '_state'
    while True:
        with open(f'data/{state_auction}.txt', 'w', encoding='utf-8') as file:
            file.write('updating...')
        file.close()
        try:
           driver=add_driver()
           driver=autor(driver,login,passw)
           time.sleep(10)
           car_list=update_list_car(auction,driver)
        except Exception as e:
           print(f'An exception with driver happened:\n{e}')
           print('Re-creating the driver...')
           driver.close()
           driver.quit()
           time.sleep(120)
           continue
        driver.quit()
        my_pickled_object = pickle.dumps(car_list)
        formatted_auction_name = return_formatted_file_name(auction)
        with open(f'data/{formatted_auction_name}.txt','wb+') as f:#запись
            f.write(my_pickled_object)
        f.close()
        with open(f'{state_auction}.txt', 'w', encoding='utf-8') as file2:
            file2.write('updated')
        file2.close()
        time.sleep(60)
        while True:
             miami_timezone = pytz.timezone('America/New_York')
             current_time_in_miami = datetime.datetime.now(miami_timezone).strftime('%H:%M')
             time.sleep(4)
             if current_time_in_miami == time_1 or current_time_in_miami == time_2:
                     break



#Updating of two car auctions, their data can be modified. I put two auction files of other auctions
# list_auction=["Lawton Auto Auction","Mainheim Halifax"]
# for auction in list_auction:
#     th = threading.Thread(target=update, name=auction, args=(auction,))
#     th.start()
             
