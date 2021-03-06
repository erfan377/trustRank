from importlib import find_loader
from traceback import TracebackException
import requests
from bs4 import BeautifulSoup
import fire
import json
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from os import access, listdir
from os.path import isfile, join
from urllib.parse import urlparse
from selenium.webdriver.common.by import By
import re
import tweepy
from constants import *


def gecko_nft(name='gecko_nft', low=0, high=100):
    link_list = []
    nft_dict = dict()
    # populating links first
    driver = webdriver.Chrome(ChromeDriverManager().install())
    for page in range(low, high):
        print('page', page)

        driver.get("https://www.coingecko.com/en/nft?page=" + str(page))
        for i in range(1, 21):
            driver.execute_script(
                "window.scrollTo(0, {num}*document.body.scrollHeight/{denum});".format(num=i, denum=10))

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        nfts = soup.find_all('tr')
        # go through table of links
        for nft in nfts:
            try:
                res = nft.find('a')
                link = 'https://www.coingecko.com' + res.attrs['href']
                link_list.append(link)
            except:
                print('fail')

    # open each link and get the links from the pacge
    for i in range(len(link_list)):
        nft_link = link_list[i]
        try:
            driver.get(nft_link)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            title = soup.find('h1', attrs={
                'class': 'tw-text-3xl tw-font-extrabold tw-text-gray-900 dark:tw-text-white tw-ml-3'})

            websites = soup.find_all('a', attrs={'class': 'mr-4'})
            # # cleaning the token ids from the names
            clean_title = title.text[1:-1]
            clean_title = re.sub("\(.*?\)", "", clean_title).strip()

            # if infomation can't be found just have empty string to keep data consistent for later
            web = ''
            twitter = ''
            discord = ''
            for tag_a in websites:
                if tag_a.text == 'Website':
                    web = tag_a.attrs['href']
                if tag_a.text == 'Twitter':
                    twitter = tag_a.attrs['href']
                if tag_a.text == 'Discord':
                    discord = tag_a.attrs['href']
            nft_dict[clean_title] = {'website': web,
                                     'twitter': twitter,
                                     'discord': discord}
        except Exception as e:
            time.sleep(120)
            print('fail2', e)
            i -= 1

    export = {'source': 'CoinGecko', 'websites': nft_dict}

    with open(name + '.json', 'w') as fp:
        json.dump(export, fp,  indent=4)


def gecko_spot(name='gecko_spot', low=0, high=100):

    link_list = []
    driver = webdriver.Chrome(ChromeDriverManager().install())
    for page in range(low, high):
        print('page', page)
        driver.get("https://www.coingecko.com/en/exchanges?page=" + str(page))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table = soup.find('tbody', attrs={
            'data-target': 'exchanges-list.tableRows'})
        exchgs = table.find_all('tr')
        for exchg in exchgs:
            try:
                res = exchg.find('a')
                link = 'https://www.coingecko.com' + \
                    res.attrs['href'] + '#about'
                link_list.append(link)
            except:
                print('fail')

    exchg_dict = dict()
    for i in range(len(link_list)):
        link = link_list[i]
        try:
            driver.get(link)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            section = soup.find('div', text='Website')
            parent = section.parent
            # we put address before title in case if we don't have an address we don't title as well
            url = parent.find('a').attrs['href']
            title = soup.find(
                'div', attrs={'class': 'exchange-name font-weight-bold'})
            clean_title = title.text[1:-1]
            clean_title = re.sub("\(.*?\)", "", clean_title).strip()
            exchg_dict[clean_title] = {'website': url}
        except Exception as e:
            print('fail2', e)
            time.sleep(120)
            i -= 1

    export = {'source': 'CoinGecko', 'websites': exchg_dict}
    with open(name + '.json', 'w') as fp:
        json.dump(export, fp,  indent=4)


def daocentral(name='daocentral_'):
    link_list = []
    data_dict = dict()
    # populating links first
    result = requests.get("https://daocentral.com/explore/")
    soup = BeautifulSoup(result.text, 'html.parser')
    daos = soup.find_all('div', attrs={'class': 'not-prose'})
    # go through table of links
    for dao in daos:
        try:
            res = dao.find('a')
            link = 'https://daocentral.com/' + res.attrs['href']
            link_list.append(link)
        except:
            print('fail')

    # open each link and get the links from the pacge
    for dao_link in link_list:
        try:
            page = requests.get(dao_link)
            soup = BeautifulSoup(page.text, 'html.parser')
            title = soup.find('h1', attrs={
                'class': 'font-cal text-3xl sm:text-5xl tracking-wide'}).text

            websites = soup.find('div', attrs={
                'class': 'flex md:justify-start justify-center items-center space-x-3 mt-4'})
            websites_a = websites.find_all('a')
            print(title)
            # if infomation can't be found just have empty string to keep data consistent for later
            web = ''
            twitter = ''
            discord = ''
            for tag_a in websites_a:
                if tag_a.find('p', attrs={"class": "hidden lg:block"}).text == 'Website':
                    web = tag_a.attrs['href']
                if tag_a.find('p', attrs={"class": "hidden lg:block"}).text == 'Twitter':
                    twitter = tag_a.attrs['href']
                if tag_a.find('p', attrs={"class": "hidden lg:block"}).text == 'Discord':
                    discord = tag_a.attrs['href']
            data_dict[title] = {'website': web,
                                'twitter': twitter,
                                'discord': discord}
        except:
            print('fail2')

    export = {'source': 'DAOCentral', 'websites': data_dict}
    with open(name + '.json', 'w') as fp:
        json.dump(export, fp,  indent=4)


def dapp_rank(name='dappradar_', low=0, high=100):

    # open the ranking list go through each row of the table
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # driver = webdriver.Chrome(options=options)
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    for page in range(low, high):
        url = "https://dappradar.com/rankings/{page}".format(
            page=page)

        driver.get(url)

        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        time.sleep(5)
        # This parts needs to be updated whenever we fetch because the change the class name
        table = soup.find('div', attrs={
            'sc-ePsPkC jpnrxT rankings-table'})
        rows = table.find_all('a')
        dict_name = {}

        # for each website get the link and open the dappradar inner website
        for row in rows:
            try:
                surl = 'https://dappradar.com' + row.attrs['href']
                chains = row.find_all(
                    'div',  attrs={'class': 'sc-gLTcDU iQdKRx'})

                # save list of chains
                chain_list = []
                for chain in chains:
                    chain_list.append(chain.text)
                options = webdriver.ChromeOptions()
                options.add_experimental_option(
                    'excludeSwitches', ['enable-logging'])
                # driver = webdriver.Chrome(options=options)
                driver = webdriver.Chrome(
                    ChromeDriverManager().install(), options=options)
                driver.get(surl)
                soup = BeautifulSoup(driver.page_source, 'lxml')
                title_box = soup.find('div', attrs={'class':
                                                    'article-page__brand-info'})
                title = ''
                twitter_url = ''
                discord_url = ''
                address_tag = ''

                try:
                    # we put address before title in case if we don't have an address we don't title as well
                    address_tag = soup.find(
                        'a', attrs={'class': 'sc-bxdjLI fnXxvA'}).attrs['href']
                    title = title_box.find('h1').text
                    twitter = soup.find('div', attrs={'data-original-title':
                                                      'twitter'})
                    twitter_url = twitter.find('a').attrs['href']
                    discord = soup.find('div', attrs={'data-original-title':
                                                      'discord'})
                    discord_url = discord.find('a').attrs['href']
                except:
                    print('didnt get twitter')
                dict_name[title] = {'website': address_tag,
                                    'twitter': twitter_url, 'discord': discord_url, 'chain': chain_list}
            except:
                print('furl', url)
        with open(name + str(page) + '.json', 'w') as fp:
            json.dump(dict_name, fp,  indent=4)


def deepdao(name='deepdao_', low=1, high=100):

    # open the ranking list go through each row of the table
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    url = "https://deepdao.io/organizations"

    driver.get(url)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    # This parts needs to be updated whenever we fetch because the change the class name
    table = soup.find_all('div', attrs={
        'styles_tableRow__M0cR-'})
    dict_name = {}

    # for each website get the link and open the deepdao inner website
    for row in range(low, high):
        try:
            driver.find_element(By.XPATH, "//span[.='{}']".format(row)).click()
            time.sleep(2)
            soup = BeautifulSoup(driver.page_source, 'lxml')
            title = soup.find(
                'h2', attrs={'class': 'styles_organizationName__14PZx'}).text
            print(title)
            twitter_url = ''
            discord_url = ''
            address_tag = ''

            try:
                # we put address before title in case if we don't have an address we don't title as well
                address_tag = soup.find('img', attrs={
                                        'src': '/static/media/website_logo_white.b2a32920.svg'}).parent.attrs['href']
                twitter_url = soup.find('img', attrs={
                    'src': '/static/media/twitter_logo_white.d7beecf1.svg'}).parent.attrs['href']
                discord_url = soup.find('img', attrs={
                    'src': '/static/media/discord_logo_white.0b3d7d68.svg'}).parent.attrs['href']
            except:
                print('didnt get twitter')
            dict_name[title] = {'website': address_tag,
                                'twitter': twitter_url, 'discord': discord_url, 'chain': []}
            export = {'source': 'DeepDAO', 'websites': dict_name}
            with open(name + str(row) + '.json', 'w') as fp:
                json.dump(export, fp,  indent=4)
            time.sleep(4)

            driver.execute_script("window.history.go(-1)")
            time.sleep(3)
        except:
            print('furl', url)


def dapp_clean(path, new_path):

    files = [f for f in listdir(path) if isfile(join(path, f))]
    if '.DS_Store' in files:  # sometimes we get this file
        files.remove('.DS_Store')
    files.sort()  # to go from first page

    for item in files:
        f = open(path + "/" + item)
        data = json.load(f)
        driver = webdriver.Chrome(ChromeDriverManager().install())

        for name in data.keys():
            url = data[name]['website']
            try:
                print(name)
                driver.get(url)
                new_url = driver.current_url
                data[name]['website'] = new_url
            except:
                # if can't load the url delete the key
                data[name]['website'] = ""
                print('didn work')

        export = {'source': 'DappRadar', 'websites': data}
        with open(new_path + '/' + item, 'w') as fp:
            json.dump(export, fp,  indent=4)


def cryptoslam(name='cryptoslam', low=1, high=100):

    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get('https://cryptoslam.io/nfts')
    dict_name = {}

    for page in range(low, high):
        soup = BeautifulSoup(driver.page_source, 'lxml')
        table = soup.find_all('tr')
        for row in table:
            title = ''
            twitter_url = ''
            discord_url = ''
            address_tag = ''
            chain = ''
            try:
                # put address before name so in case it fails we don't need to store name
                address_tag = row.find(
                    'img', attrs={'class': 'website-img'}).parent.attrs['href']
                title = row.find(
                    'span', attrs={'class': 'summary-sales-table__column-product-abbreviation truncate-nfts'}).text
                print(title)
                twitter_url = row.find(
                    'img', attrs={'class': 'twitter-img'}).parent.attrs['href']
                discord_url = row.find(
                    'img', attrs={'class': 'discord-img'}).parent.attrs['href']

                chain = row.find(
                    'img', attrs={'class': 'marketplace-sale-icon marketplace-sale-icon--image'}).attrs['data-original-title']
            except:
                print('didnot work')
            dict_name[title] = {'website': address_tag,
                                'twitter': twitter_url, 'discord': discord_url, 'chain': [chain]}

        # can't use url to go to next page, so we find button on page and click on it
        driver.find_element(By.LINK_TEXT, "Next").click()
    export = {'source': 'CryptoSlam', 'websites': dict_name}
    with open(name + '.json', 'w') as fp:
        json.dump(export, fp,  indent=4)


def coinmarket_dex(name='coin_spot'):

    # multiple links that we can visit which follows the same format
    links = ["https://coinmarketcap.com/rankings/exchanges/",
             'https://coinmarketcap.com/rankings/exchanges/lending/',
             "https://coinmarketcap.com/rankings/exchanges/dex/"]

    dict_name = {}
    for link in links:
        result = requests.get(link)
        soup = BeautifulSoup(result.text, 'html.parser')
        table = soup.find_all('tr')
        for row in table:
            address_tag = ''
            title = ''
            twitter = ''
            try:
                res = row.find('a').attrs['href']
                url = 'https://coinmarketcap.com' + res
                result = requests.get(url)
                soup = BeautifulSoup(result.text, 'html.parser')
                title = soup.find(
                    'h2', attrs={'class': 'sc-1q9q90x-0 sc-1xafy60-3 dzkWnG'}).text
                print(title)
                address_tag = soup.find(
                    'svg', attrs={'title': 'Website'}).parent.find('a').attrs['href']
                twitter = soup.find(
                    'svg', attrs={'title': 'Twitter'}).parent.find('a').attrs['href']

            except:
                print('dont work')

            dict_name[title] = {'website': address_tag,
                                'twitter': twitter}
    export = {'source': 'CoinMarketCap', 'websites': dict_name}
    with open(name + '.json', 'w') as fp:
        json.dump(export, fp,  indent=4)


def coinmarket_nft(name='coin_nft', low=1, high=100):

    dict_name = {}
    driver = webdriver.Chrome(ChromeDriverManager().install())
    for page in range(low, high):
        url = 'https://coinmarketcap.com/nft/collections/?page='+str(page)

        driver.get(url)
        # you have to scroll down to get the
        time.sleep(3)
        for i in range(1, 21):
            driver.execute_script(
                "window.scrollTo(0, {num}*document.body.scrollHeight/{denum});".format(num=i, denum=10))
            time.sleep(0.5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table = soup.find('tbody')  # getting the table
        for row in table:
            address_tag = ''
            title = ''
            chain = ''
            try:
                address_tag = row.find('a').attrs['href']
                title = row.find('span').text
                print(title)
                chain = row.find(
                    'span', attrs={'class': 'logo'}).text
            except Exception as e:
                print('dont work', address_tag, e)
            # putting chain in list for consistency of aggregating data later
            dict_name[title] = {'website': address_tag, 'chain': [chain]}
    export = {'source': 'CoinMarketCap', 'websites': dict_name}
    with open(name + '.json', 'w') as fp:
        json.dump(export, fp,  indent=4)


def coinmarket_dao(name='coin_dao', low=1, high=100):

    dict_name = {}
    driver = webdriver.Chrome(ChromeDriverManager().install())
    for page in range(low, high):
        url = 'https://coinmarketcap.com/view/dao/?page='+str(page)

        driver.get(url)
        # you have to scroll down to get the
        time.sleep(3)
        for i in range(1, 21):
            driver.execute_script(
                "window.scrollTo(0, {num}*document.body.scrollHeight/{denum});".format(num=i, denum=10))
            time.sleep(0.5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table = soup.find('tbody')  # getting the table
        for row in table:
            address_tag = ''
            title = ''
            chain = ''
            try:
                res = row.find('a').attrs['href']
                url = 'https://coinmarketcap.com' + res
                result = requests.get(url)
                soup = BeautifulSoup(result.text, 'html.parser')

                title = soup.find(
                    'h2', attrs={'class': 'sc-1q9q90x-0 jCInrl h1'}).text
                print(title)
                content = soup.find(
                    'div', attrs={'class': 'sc-16r8icm-0 sc-10up5z1-1 eUVvdh'})
                address_tag = content.find_all('a')[0].attrs['href']

            except:
                print('dont work')
            # putting chain in list for consistency of aggregating data later
            dict_name[title] = {'website': address_tag, 'chain': [chain]}
    export = {'source': 'CoinMarketCap', 'websites': dict_name}
    with open(name + '.json', 'w') as fp:
        json.dump(export, fp,  indent=4)


def clean_aggregate(new, old, ignore, output):
    new_data = json.load(open(new))
    old_data = json.load(open(old))
    ignore_data = json.load(open(ignore))
    final_dict = dict()
    for key in new_data:
        if key in old_data or key in ignore_data:
            pass
        else:
            final_dict[key] = new_data[key]
    print(len(final_dict))
    with open(output + '.json', 'w') as fp:
        json.dump(final_dict, fp,  indent=4)


def aggregate(path, new_path='all'):
    files = [f for f in listdir(path) if isfile(join(path, f))]
    if '.DS_Store' in files:
        files.remove('.DS_Store')

    dict_all = {}
    for item in files:
        print(item)
        f = open(path + "/" + item)
        data = json.load(f)
        for name in data['websites']:
            # sometimes we dont have a valid website but we don't want it to fail
            url = data['websites'][name].get('website', '')
            # if can't find website just skip the whole thing
            if url == '':
                continue
            twitter = data['websites'][name].get('twitter', '')
            discord = data['websites'][name].get('discord', '')
            # we use set in case we have repeating chain indicators
            chain = set()
            if 'chain' in data['websites'][name]:
                chain.update(data['websites'][name]['chain'])

            # we clean url netloc here
            netloc = urlparse(url).netloc

            # we populate name and source here since we know both will always exist
            if netloc not in dict_all:
                dict_all[netloc] = {'name': {name},
                                    'sources': {data['source']},
                                    'chain': set(),
                                    'twitter': None,
                                    'discord': None}

            else:
                # if we have seen the netloc we just add the new source we're getting it from
                dict_all[netloc]['sources'].add(data['source'])
                # to avoid having repeating names, we convert all names to CAP and check in the dict
                if name.upper() not in map(lambda x: x.upper(), dict_all[netloc]['name']):
                    dict_all[netloc]['name'].add(name)
            # we use update for twitter and discord since there shouldn't be more than one link for each
            # for chain we actually add new chain values to existing values
            if twitter != "":
                tweety = twitter_fetch(twitter)
                dict_all[netloc].update(
                    {'twitter': {"link": twitter, "data": tweety}})
            if discord != "":
                dict_all[netloc].update({'discord': discord})
            if len(chain) != 0:
                dict_all[netloc]['chain'].update(chain)
    # we convert sets to lists for saving in json
    for item in dict_all:
        dict_all[item] = {'name': list(dict_all[item]['name']),
                          'sources': list(dict_all[item]['sources']),
                          'twitter': dict_all[item]['twitter'],
                          'discord': dict_all[item]['discord'],
                          'chain': list(dict_all[item]['chain'])}
    del dict_all[""]  # edge data due to try: except: so we just delete it
    with open(new_path + '.json', 'w') as fp:
        json.dump(dict_all, fp,  indent=4)


def extension_check(path, lookup='safe'):

    f = open(path)
    data = json.load(f)
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_extension('./PhishFort---Protect.crx')
    options.add_extension('./UPPward--Network-Defence-Security-.crx')
    options.add_extension('./WOT-Website-Security---Browsing-Protection.crx')
    options.add_extension('./Hexatorch.crx')
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.get('https://www.google.com/')
    val = input("press enter to continue")
    phishfort = 0
    uppward = 0
    wot = 0
    key_list = list(data[lookup].keys())
    web = "https://" + key_list[0]
    print(0, " ", web)
    driver.get(web)
    i = 0
    while i < len(key_list):
        val = input(
            " f for phishfot \n u for uppward \n w for wot \n p for print \n n for next\n")
        if val == 'f':
            phishfort += 1
        elif val == 'u':
            uppward += 1
        elif val == 'w':
            wot += 1
        elif val == 'p':
            print("phishfort ", phishfort, " uppward ", uppward, " wot ", wot)
        elif val == 'n':
            i += 1
            web = "https://" + key_list[i]
            print(i, " ", web)
            try:
                driver.get(web)
            except:
                print("failed to get website")
                print(i, " ", web)
                print("phishfort ", phishfort,
                      " uppward ", uppward, " wot ", wot)

    print("phishfort ", phishfort, " uppward ", uppward, " wot ", wot)


def twitter_fetch(url):

    auth = tweepy.OAuth1UserHandler(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET
    )

    api = tweepy.API(auth, wait_on_rate_limit=True)

    try:
        name = urlparse(url).path[1:]  # curring the / at beginning of path
        user = api.get_user(screen_name=name)
        follower_cnt = user._json["followers_count"]
        link_list = []  # usually it's just one url, but in case we need to add to it
        try:
            for item in user._json["entities"]["url"]["urls"]:
                link_list.append(item["expanded_url"])
        except:
            print('couldnt fetch link from twitter')
        return {"follower_cnt":  format(follower_cnt, ","), "link_list": link_list if link_list != [] else None}
    except Exception as e:
        print(e)
        return {"follower_cnt":  None, "link_list": None}


def filter(load_name, save_name="filtered_all"):
    """filter the curated JSON from the websites based on your criteria

    Args:
        load_name (str): input JSON
        save_name (str, optional): Filtered JSON name to save. Defaults to "filtered_all".
    """
    f = open(load_name)
    data = json.load(f)
    filtered_data = {}
    i = 0  # count how many are kept
    for url in data:
        detail = data[url]
        # determined how many sources it should have been appeared in
        if len(detail["sources"]) > 1:
            filtered_data[url] = detail
            i += 1
    print(i)
    with open(save_name + '.json', 'w') as fp:
        json.dump(filtered_data, fp,  indent=4)


if __name__ == '__main__':
    fire.Fire()
