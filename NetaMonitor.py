# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 20:34:21 2019

@author: Andy

Monitor for NETA supply of VAPES. Posts to gravys disco server (production)
Currently set to be kicked off by NETA task in windows task scheduler.
"""
#import os
#import sys

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumwire import webdriver 
from discord_webhook import DiscordWebhook, DiscordEmbed
#from apscheduler.schedulers.blocking import BlockingScheduler
import time
from time import sleep
import pickle
#theres a slew of unused selenium references...the idea is that I will add some more functionality...just not yet.

url = 'https://embed.neta.stickyguide.com/?dispensary_id=6391&menu_type=pickup&url=https://netacare.org/reserveahead/northampton/&online_ordering=true&data_user_type=null&access=undefined'
title = 'NETA'
reserve_ahead = 'https://netacare.org/reserveahead/northampton/'
environment = 'prod'
#environment = 'test'



class vape_object:
    def __init__(self, name, strain, img, cost, tac):
        self.name = name
        self.strain = strain
        self.img = img
        self.cost = cost
        self.tac = tac

    def debug_post(self):
        print("Product Name:" + self.name)
        print("Strain:" + self.strain)
        print("Product Image:" + self.img)
        print("Cost:" + self.cost)
        print("Tac:" + self.tac)
        
def postToDisco(imageURL, title, description, price, strain, tac, environment):
    print(imageURL, title, description, price, strain, tac)
    #have moved webhooks to local file in script folder. this way i can publish on git without exposing the url.
    if environment == 'prod':
        try:
            with open('I:/projects/netamonitor/productionwebhook.txt', 'rb') as file:
                production_webhook = file.read()
                webhook = DiscordWebhook(url=production_webhook)
        except FileNotFoundError:
            print("Production Webhook not found")
    elif environment == 'test':
        try:
            with open('I:/projects/netamonitor/testwebhook.txt', 'rb') as file:
                test_webhook = file.read()
                webhook = DiscordWebhook(url=test_webhook)
        except FileNotFoundError:
            print("Test Webhook not found")
            
  
    # create embed object for webhook
    #embed = DiscordEmbed(title='Your Title', description='Lorem ipsum dolor sit', color=242424)
    embed = DiscordEmbed(title=title, description="[" + description + "](" + reserve_ahead + ")", color=242424)
    #embed = DiscordEmbed(title=title, description="[" + description + "], color=242424)
    
    
    # set thumbnail
    embed.set_thumbnail(url=imageURL)
    
    # set footer
    embed.set_footer(text='FrostyMiniTeets NETA Monitor')
    
    # set timestamp (default is now)
    #below is supposedly all i need but the timestamp wasnt updating?
    # i do the time stuff and it doesnt seem to work, but the timestamp is updating now...
    #embed.set_timestamp()
    ts = time.gmtime()
    embed.set_timestamp(time.strftime("%Y-%m-%d %H:%M:%S", ts))

    

    embed.add_embed_field(name='Category\n', value='Vape')
    embed.add_embed_field(name='Strain\n', value=strain)
    embed.add_embed_field(name='TAC\n', value=tac)
    embed.add_embed_field(name='Price\n', value=price)
    
    
    # add embed object to webhook
    webhook.add_embed(embed)
    
    response = webhook.execute()
    sleep(.75)

def setup():
    # instantiate a chrome options object so you can set the size and headless preference
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920x1080")
    #this hides the browser
    chrome_options.headless = True

    chrome_driver = 'I:/projects/netamonitor/chromedriver.exe'
    driver = webdriver.Chrome(options=chrome_options, executable_path=chrome_driver)
    driver.header_overrides = {
            'Referer': 'https://embed.neta.stickyguide.com/?dispensary_id=6391&menu_type=pickup&url=https://netacare.org/reserveahead/northampton/&online_ordering=true&data_user_type=null&access=undefined',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
            }
    return driver
    

def new_item_test(vapes, new_items, v1):
    if (vapes.text in new_items):
        new_items.remove(vapes.text)
    else:
        new_items.append(vapes.text)
        postToDisco(v1.img, "NEW ITEM", v1.name, v1.cost, v1.strain, environment)

def test_search_in_python_org(driver, url):
    driver.get(url)
    assert "Sticky Guide" in driver.title
    time.sleep(3)
    menus_list = driver.find_element_by_xpath("//ul[@class='main_list']")
    #print(menus_list2.get_attribute("class"))
    menus_list = driver.find_element_by_css_selector('ul.main_list')
    #print(menus_list3.get_attribute("innerHTML"))
    menus = menus_list.find_elements_by_tag_name('li')
    for menu in menus:
        #text = menu.get_attribute("value")
        #print(text)
        #print(menu.get_attribute("href"))
        menus2 = menu.find_element_by_tag_name('a')
        #print(menus2.get_attribute("innerHTML"))
        #print(menus2.text)
        #if i take away this if i can literally loop each page and get everything
        if menus2.text == 'VAPES':
            #print('we vapin')
            menus2.click()
            time.sleep(3)
            vape_product_name = driver.find_elements_by_xpath("//h2[@class='product_name_dynamic']")
            #vape_product_name = driver.find_element_by_class_name('product_name_dynamic')
            #print(vape_product_name.text)
            #print(vapetest.text)
            vape_types = driver.find_elements_by_xpath("//span[@class='prod_details_type prod_categ']")
            vape_image = driver.find_elements_by_xpath("//img[@class='main_prod_img']")
            vape_cost = driver.find_elements_by_xpath("//span[@class='value_sup']")
            vape_tac = driver.find_elements_by_xpath("//span[@class='tac_percnt']")
            count = 1
            amount = []
            newfile = 'mypickle.pk'
            try:
                with open(newfile, 'rb') as fi:
                    items = pickle.load(fi)
            except FileNotFoundError:
                    items = []
            # i have to do below because inexplicably there are a number of empty elements specific to the amount
            for cost in vape_cost:
                #print("cost test")
                #print(cost.text)
                if cost.text != '':
                    amount.append(cost.text)
            #i start at 1 because the first item is the kit...i need to handle better...
            #also vape tac is -1 because the kit doesnt have a tac so it should start at 0 item instead of 1
            for vapes in vape_product_name[1:]:
                #print("vapes test")
                v1 = vape_object(vapes.text, vape_types[count].text, vape_image[count].get_attribute("src"), amount[count], vape_tac[count - 1].text) 
                #v1.debug_post()
                #i think there is a logic fallacy here...where if a previous strain shows up again later on...it wont be new...
                # because it never got deleted from items.
                #well maybe not, I dont know if pickle stores it?...the way around this would be to delete the pickle file 
                # just before the pickle.dump...then its always just the latest and fixes this.
                if (vapes.text in items):
                    postToDisco(v1.img, title, v1.name, v1.cost, v1.strain, v1.tac, environment)
                else:
                    items.append(vapes.text)
                    postToDisco(v1.img, "**NEW ITEM**\n" + title, v1.name, v1.cost, v1.strain, v1.tac, environment)

                #print(vapes.text)
                #print(vape_types[count].text)
                #print(vape_image[count].get_attribute("src"))
                count += 1
            
        else: 
            continue
        #this should be a function
        print(items)
        with open(newfile, 'wb') as fi:
            pickle.dump(items, fi)



'''scheduling
scheduler = BlockingScheduler()
scheduler.add_job(test_search_in_python_org, 'interval',  minutes=1, args=[setup(), url])
scheduler.start()
'''
test_search_in_python_org(setup(),url)