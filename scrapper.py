import os
import time
import requests
import pymongo
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

def fetch_image_urls(query:str , max_links_to_fetch : int , wd :webdriver, sleep_between_interactions: int = 1):
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0,document.body.scrollHeight);")

        time.sleep(sleep_between_interactions)

    # build the Google query
    search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"

    # load the page
    wd.get(search_url.format(q=query))  # This says replace the q  in search_url with the query term

    image_urls = set()  # It is declared as "set" type so that we will download only distinct images
    image_count = 0
    results_start = 0
    while image_count < max_links_to_fetch:
        scroll_to_end(wd)

        # get all thumbnail results
        thumbnail_results = wd.find_elements(By.CSS_SELECTOR,"img.Q4LuWd")
        # if we see the source we can see the image we want tp
        number_results = len(thumbnail_results)
        print(f"Found :{number_results} search results. Extracting links from {results_start}:{number_results}")

        for img in thumbnail_results[results_start:number_results]:
            # try to click every thumbnail such that we can get real image behind it
            try:
                img.click()
                time.sleep(sleep_between_interactions)
            except Exception:
                continue

            # extract image urls
            actual_images = wd.find_elements(By.CSS_SELECTOR,"img.sFlh5c")
            for actual_image in actual_images:
                if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute(
                        'src') and actual_image.get_attribute('src') != "NoneType":
                    image_urls.add(actual_image.get_attribute('src'))

            image_count = len(image_urls)

            if len(image_urls) >= max_links_to_fetch:
                print(f"Found: {len(image_urls)} image links,done!")
                break
        else:
            print("Found:",len(image_urls),"image links,looking for more .....")
            time.sleep(30)

            return
            load_more_button = wd.find_elements(By.CSS_SELECTOR,".mye4qd")
            if load_more_button:
                wd.execute_script("document.querySelector('.mye4qd').click()")

        # move the result startpoint further down
        results_start = len(thumbnail_results)

    return image_urls

def persist_image(folder_path:str,url:str,counter):
    try:
        image_content = requests.get(url).content

    except Exception as e:
        print(f"ERROR Could not download {url} - {e}")

    try:
        f = open(os.path.join(folder_path,'jpg'+"_"+str(counter)+".jpg"),'wb')
        f.write(image_content)
        f.close()
        print(url)
        print(f"SUCCESS - saved {url} - as {folder_path}")
    except Exception as e:
        print(f"ERROR - could not save {url} - {e}")


def search_and_download(search_term :str ,driver_path:str,target_path ='./images',number_images = 10):
    target_folder = os.path.join(target_path,'_'.join(search_term.lower().split(' ')))

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    service = Service(executbale_path = driver_path)
    with webdriver.Chrome(service=service) as wd:
        res = fetch_image_urls(search_term, number_images, wd=wd, sleep_between_interactions = 1)

    counter = 0
    for elem in res:
        persist_image(target_folder,elem,counter)
        counter+=1

DRIVER_PATH = r'C:\Users\Siddhant\ImageScrapper\chromedriver.exe'
search_term = "audi"
search_and_download(search_term = search_term , driver_path=DRIVER_PATH,number_images=10)

