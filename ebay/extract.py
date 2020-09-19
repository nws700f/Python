import csv
from time import sleep
import datetime
import os.path
import pandas as pd
import requests
import pathlib
import random
import re
import subprocess
import glob
import openpyxl
import itertools
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from itertools import zip_longest
from os import listdir

# Path
Search_list = "/Users/micksmith/home/work/Crowd Works/ebay/Search_list.csv"
Translation = "/Users/micksmith/home/work/Crowd Works/ebay/Translation.csv"
Submit_Mercari_path = "/Users/micksmith/home/work/Crowd Works/ebay/Submit_Mercari"
Submit_Yahoo_path = "/Users/micksmith/home/work/Crowd Works/ebay/Submit_Yahoo"
Submit_Rakuma_path = "/Users/micksmith/home/work/Crowd Works/ebay/Submit_Rakuma"
eliminate_list = "/Users/micksmith/home/work/Crowd Works/ebay/elimitate.txt"
img_dir = "/Users/micksmith/home/work/Crowd Works/ebay/image/"

# Parameter
d_today = datetime.date.today()

# ブラウザの設定(オプション)
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage') 
driver = webdriver.Chrome(executable_path="/Users/micksmith/chromedriver", chrome_options=options)

# 入力チェック
def input_num():
    try:
        status = int(input())
    except:
        print("Please enter 0 or 1...")
        return input_num()
    if status == 0 or status == 1:
        return status
    else:
        print("Please enter 0 or 1...")
        return input_num()

# スクロール
def scroll(class_name):
    element = driver.find_element_by_class_name(class_name)
    actions = ActionChains(driver)
    actions.move_to_element(element)
    actions.perform()
    sleep(1)
    driver.execute_script("window.scrollTo(0, 500);")

# 画像保存
def save_image(df):
    for item in df['Image URL']:
        dfs = df[df['Image URL'] == item]
        try:
            response = requests.get(item)
            image = response.content
            tentative = list(dfs.values.flatten())
            print(tentative)
            item_id = tentative[1] 
        
            filename = img_dir + str(item_id) + ".jpg"
            with open(filename, 'wb') as f:
                f.write(image)
                sleep(random.uniform(0.5, 2.0))
        except:
            pass

# 画像取得
def get_image():
    sleep(2)
    try:
        element = driver.find_element_by_id('mainImgHldr')
        image = element.find_element_by_id('icImg')
        image_url = image.get_attribute("src")
    except:
        image_url = ""
    
    if(image_url == ""):
        try:
            element = driver.find_element_by_class_name('galleryPicturePanel')
            image = element.find_element_by_tag_name('img')
            image_url = image.get_attribute("src")
        except:
            #print("except")
            image_url = ""
            
    return image_url

# 商品リストの読み込み
def reading_csv():
    # 除去する単語の読み込み
    with open (eliminate_list) as file:
        eliminate_words = [s.strip() for s in file.readlines()]
    print(eliminate_words)    
    df = pd.read_csv(Search_list)
    print("initial_num")
    initial_num = int(input())
    print("final_num")
    final_num = int(input())
    df = df[initial_num:final_num]
    #df = df[:3]
    # print(df)
    retail_titles = df['Title'].values.tolist()
    #print(retail_titles)
    urls = df['Item URL'].values.tolist()
    Prices = df['Price'].values.tolist()
    Categories = df['Category'].values.tolist()
    WatchCounts = df['WatchCount'].values.tolist()
    
    return df, retail_titles, urls, Prices, Categories, WatchCounts, eliminate_words, initial_num, final_num

# 商品タイトルを日本語に翻訳    
def get_translate(retail_titles, eliminate_words):
    translate_japanese_list = []
    for retail_title in retail_titles:
        # 該当する単語を削除
        retail_title_list = retail_title.split()
        retail = []
        
        # 該当文字を Title から削除
        for item in retail_title_list:
            Flag = True
            for eliminate_word in eliminate_words:
                if(eliminate_word in item):
                    Flag = False
            if(Flag):
                retail.append(item)

        retail_title = ' '.join(retail)
        
        #print(retail_title)
        # 翻訳サイトにて変換    
        retail_title_revise = retail_title.replace(" ","%20")
        #print(retail_title_revise)
        translate_url = "https://translate.google.co.jp/?hl=ja"
        translate_url = translate_url + "&op=translate&sl=en&tl=ja&text=" + retail_title_revise
        #print(translate_url)
        driver.get(translate_url)
        sleep(random.uniform(2.0, 3.0))
        try:
            translate_japanese = driver.find_element_by_class_name('result-shield-container.tlid-copy-target')
        except:
            translate_japanese = ""
        try:
            #print(translate_japanese.text)
            translate_japanese_list.append(translate_japanese.text)
        except:
            translate_japanese_list.append("")
    
    return translate_japanese_list
        

# 画像 URL の取得
def get_image_url(urls):
    image_list = []
    # 画像 URL を取得
    for url in urls:
        driver.get(url)
        image_url = get_image()
        print(image_url)
        image_list.append(image_url)
    
    return image_list

# メルカリ
def get_mercari(url, ebay_url, item):
    info = []
    driver.get(url)
    sleep(random.uniform(1.0, 3.0))

    element = driver.find_element_by_class_name('item-detail-table')
    # print(element.text)
    # テーブルの取得
    keys = element.find_elements_by_tag_name('th')
    values = element.find_elements_by_tag_name('td')
    # 辞書に登録
    mercari_keys = []
    mercari_values= []
    for key, value in zip(keys, values):
        mercari_keys.append(key.text)
        mercari_values.append(value.text)

    dictionary = dict(zip(mercari_keys, mercari_values))
        
    # 商品価格の取得
    retail_title = driver.find_element_by_class_name('item-name')
    price = driver.find_element_by_xpath('/html/body/div[1]/section/div[2]')
    price = price.text
    # print(price)
    
    # 商品説明分の取得
    description = driver.find_element_by_class_name('item-description.f14')
    print(description.text)
    
    dictionary['Title'] = retail_title.text
    dictionary['商品 URL'] = driver.current_url
    dictionary['ebay URL'] = ebay_url
    dictionary['商品価格'] = price
    dictionary['ID'] = item
    dictionary['EC Site'] = "メルカリ"
    dictionary['商品説明'] = description.text
    
    info.append(dictionary)
    
    print(info)
    return info

# ヤフオク
# 即決価格がある場合のみ取得
def get_yahoo(url, item):
    info = []
    driver.get(url)
    sleep(random.uniform(1.0, 3.0))
    
    try:
        element = driver.find_element_by_class_name('Price.Price--buynow')
        price = element.find_element_by_class_name('Price__value')  # 即決価格
        title = driver.find_element_by_class_name('ProductTitle__title')        # 商品タイトル
        description = driver.find_element_by_class_name('ProductExplanation__commentBody.js-disabledContextMenu')  # 説明文
        tax = element.find_element_by_class_name('Price__tax')  # 税
        postage = element.find_element_by_class_name('Price__postage')  # 送料
        # テーブルの取得
        keys = ['Title', '商品価格', 'Tax', 'Postage']
        values = [title.text, price.text, tax.text, postage.text]
        # 辞書に登録
        yahoo_keys = []
        yahoo_values= []
        for key, value in zip(keys, values):
            yahoo_keys.append(key)
            yahoo_values.append(value)

        dictionary = dict(zip(yahoo_keys, yahoo_values))
        
        dictionary['商品 URL'] = driver.current_url
        dictionary['ID'] = item
        dictionary['EC Site'] = "ヤフオク"
        dictionary['商品説明'] = description.text
        
        info.append(dictionary)

    except:
        pass
    
    print(info)    
    return info

# ラクマ
def get_rakuma(url, item):
    info = []
    driver.get(url)
    sleep(random.uniform(1.0, 3.0))
    
    title = driver.find_element_by_class_name('item__name') # タイトル
    price = driver.find_element_by_class_name('item__value_area.hidden-xs') # 本体価格(税込)
    postage = driver.find_element_by_class_name('icon_item_tag')    # 送料
    description = driver.find_element_by_class_name('item__description') 
    
    scroll('item-status')
    element = driver.find_element_by_class_name('item-status')
    table = element.find_element_by_tag_name('table')
    # テーブルの取得
    keys = table.find_elements_by_tag_name('th')
    values = table.find_elements_by_tag_name('td')
    
    # 辞書に登録
    rakuma_keys = []
    rakuma_values= []
    for key, value in zip(keys, values):
        rakuma_keys.append(key.text)
        rakuma_values.append(value.text)

    dictionary = dict(zip(rakuma_keys, rakuma_values))
    
    dictionary['商品 URL'] = driver.current_url
    dictionary['ID'] = item
    dictionary['Title'] = title.text
    dictionary['商品価格'] = price.text
    dictionary['Postage'] = postage.text
    dictionary['EC Site'] = "ラクマ"
    dictionary['商品価格'] = description.text
    
    info.append(dictionary)
    
    print(info)
    return info
    
# 画像の表示
def show_images(df):
    images = [filename for filename in listdir(img_dir) if not filename.startswith('.')]
    #print(images)
    image_list = []
    for img in images:
        img = img.replace(".jpg", "")
        img = int(img)
        image_list.append(img)
    
    print("image_list")
    print(image_list)
    id_list = list(df['ItemId'].values.flatten())
    print("id_list")
    print(id_list)
    ebay_urls_mercari = []
    ebay_urls_yahoo = []
    ebay_urls_rakuma = []
    mercari_infos = []
    yahoo_infos = []
    rakuma_infos = []
    for item in id_list:
        for img in image_list:
            if(item == img):
                subprocess.call(["open", img_dir + str(img) + ".jpg"])
                # メルカリ
                print("-------------------------------------------------------------------------------------")
                dfs = df[df['ItemId'] == item]
                print("Title", dfs['Title'].values.flatten())
                print("Price", dfs['Price'].values.flatten())
                print("Mercari URL")
                print("None → 0, Exist → 1")
                print("-------------------------------------------------------------------------------------")
                check_1 = input_num()
                if(check_1):
                    print("Input Mercari URL")
                    try:
                        mercari_url = input()
                        print("Input eBay URL")
                        ebay_url_mercari = input()
                        mercari_info = get_mercari(mercari_url, ebay_url_mercari, item)
                        mercari_infos.append(mercari_info)
                    except:
                        pass
                        
                #ヤフオク
                # print("-------------------------------------------------------------------------------------")
                # dfs = df[df['ItemId'] == item]
                # print("Title", dfs['Title'].values.flatten())
                # print("Price", dfs['Price'].values.flatten())
                # print("Yahoo URL")
                # print("None → 0, Exist → 1")
                # print("-------------------------------------------------------------------------------------")
                # check_1 = input_num()
                # if(check_1):
                #     print("Input Yahoo URL")
                #     try:
                #         yahoo_url = input()   
                #         yahoo_info = get_yahoo(yahoo_url, item)
                #         yahoo_infos.append(yahoo_info)
                #     except:
                #         pass
                #     print("Input eBay URL")
                #     try:
                #         ebay_url_yahoo = input()
                #         # mercari_info = get_mercari(mercari_url, item)
                #         ebay_urls_yahoo.append(ebay_url_yahoo)
                #     except:
                #         pass
        
                #ラクマ
                # print("-------------------------------------------------------------------------------------")
                # dfs = df[df['ItemId'] == item]
                # print("Title", dfs['Title'].values.flatten())
                # print("Price", dfs['Price'].values.flatten())
                # print("Rakuma URL")
                # print("None → 0, Exist → 1")
                # print("-------------------------------------------------------------------------------------")
                # check_1 = input_num()
                # if(check_1):
                #     print("Input Rakuma URL")
                #     try:
                #         rakuma_url = input()
                #         rakuma_info = get_rakuma(rakuma_url, item)
                #         rakuma_infos.append(rakuma_info)
                #     except:
                #         pass
                #     print("Input eBay URL")
                #     try:
                #         ebay_url_rakuma = input()
                #         # mercari_info = get_mercari(mercari_url, item)
                #         ebay_urls_rakuma.append(ebay_url_rakuma)
                #     except:
                #         pass
    #print(mercari_infos)
    return mercari_infos, yahoo_infos, rakuma_infos, ebay_urls_mercari, ebay_urls_yahoo, ebay_urls_rakuma

# main
def main():
    df, retail_titles, urls, Prices, Categories, WatchCounts, eliminate_words, initial_num, final_num = reading_csv()    # 商品リストの読み込み
    translate_japanese_list = get_translate(retail_titles, eliminate_words)  # 翻訳結果
    image_list = get_image_url(urls)    # 画像 URL 
    #print(image_list)
    
    df.insert(3, "Title_Japanese", translate_japanese_list)
    df.insert(4, "Image URL", image_list)
    df.to_csv(Translation)
    
    save_image(df)
    mercari_infos, yahoo_infos, rakuma_infos, ebay_urls_mercari, ebay_urls_yahoo, ebay_urls_rakuma = show_images(df)
    # リストを平坦化
    mercari_infos = list(itertools.chain.from_iterable(mercari_infos))
    yahoo_infos = list(itertools.chain.from_iterable(yahoo_infos))
    rakuma_infos = list(itertools.chain.from_iterable(rakuma_infos))
    
    #print("mercari", mercari_infos)
    
    # csv に出力
    df_Mercari = pd.json_normalize(mercari_infos)   # 辞書→pandas
    os.chdir(Submit_Mercari_path)   # ディレクトリ移動
    Mercari_dir_time =  str(d_today)# 日時に基づいたディレクトリ名
    try:
        os.mkdir(Mercari_dir_time)  # ディレクトリ作成
    except:
        pass
    os.chdir(Mercari_dir_time)
    
    Submit_Mercari_file = str(initial_num) + "-" + str(final_num) + ".csv"    
    df_Mercari.to_csv(Submit_Mercari_file)  # csv 作成

    # df_Yahoo = pd.json_normalize(yahoo_infos)   # 辞書→pandas
    # Yahoo_dir_time = Submit_Yahoo_path + str(initial_num) + "-" + str(final_num) + ".csv"
    # df_Yahoo.to_csv(Submit_Yahoo_file)
    
    # df_Rakuma = pd.json_normalize(rakuma_infos) # 辞書→pandas
    # Submit_Rakuma_file = Submit_Rakuma_path + str(initial_num) + "-" + str(final_num) + ".csv"
    # df_Rakuma.to_csv(Submit_Rakuma_file)
    
    driver.close()

if __name__ == "__main__":
    main()