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
file_path = "./Submit_Mercari/"
Submit_Mercari_path = "./Submit_Mercari/"
Submit_Yahoo_path = "./Submit_Yahoo/"
Submit_Rakuma_path = "./Submit_Rakuma/"
Combine_Mercari = "./Combine_Mercari.csv"
Combine_Yahoo = "./Combine_Yahoo.csv"
Combine_Rakuma = "./Combine_Rakuma.csv"

# csv を統合
def combine_csv(file_path):
    files = os.listdir(file_path)
    num = lambda val : int(re.sub("\\D", "", val))
    files = sorted(files, key = num)
    print(files)
    
    # 辞書データに変換
    data = []
    for file in files:
        if(os.path.getsize(file_path + file) > 3):    
            with open( file_path + file, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(row)
    #print(data)
    
    df = pd.json_normalize(data)
    df = df[['EC Site', '商品 URL','ebay URL', '商品価格']]

    # 商品価格を成形
    prices = [] 
    price_list = list(df['商品価格'].values.flatten())
    price_list = [ prices.append(int(re.sub('[^0-9]', '', price))) for price in price_list]   # 数字以外を取り除く(正規表現))]
    df['商品価格'] = prices
    #print(df)
    return df
    
# main
def main():
    df = combine_csv(Submit_Mercari_path)
    df.to_csv(Combine_Mercari)
    #df = combine_csv(Submit_Yahoo_path)
    #df.to_csv(Combine_Yahoo)
    #df = combine_csv(Submit_Rakuma_path)
    #df.to_csv(Combine_Rakuma)    

if __name__ == "__main__":
    main()