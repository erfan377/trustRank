from base64 import urlsafe_b64encode
from attr import attr
import requests
from bs4 import BeautifulSoup
import fire
import json
from selenium import webdriver


def gecko_nft(name='gecko_nft'):

    link_list = []
    for page in range(1, 3):
        print('page', page)
        result = requests.get(
            "https://www.coingecko.com/en/nft?page=" + str(page))
        soup = BeautifulSoup(result.text, 'html.parser')
        nfts = soup.find_all('tr')
        for nft in nfts:
            try:
                res = nft.find('a')
                link = 'https://www.coingecko.com' + res.attrs['href']
                link_list.append(link)
            except:
                print('fail')

    nft_dict = dict()
    for nft_link in link_list:
        try:
            nft_page = requests.get(nft_link)
            soup = BeautifulSoup(nft_page.text, 'html.parser')
            title = soup.find('h1', attrs={
                'class': 'tw-text-3xl tw-font-extrabold tw-text-gray-900 dark:tw-text-white tw-ml-3'})
            websites = soup.find_all('a', attrs={'class': 'mr-4'})
            print(title.text[1:-1])
            clean_title = title.text[1:-1]
            for tag_a in websites:
                web = ''
                twitter = ''
                discord = ''
                if tag_a.text == 'Website':
                    web = tag_a.attrs['href']
                if tag_a.text == 'Twitter':
                    twitter = tag_a.attrs['href']
                if tag_a.text == 'Discord':
                    discord = tag_a.attrs['href']
                nft_dict[clean_title] = {'website': web,
                                         'twitter': twitter,
                                         'discord': discord}
        except:
            print('fail2')
    with open(name + '.json', 'w') as fp:
        json.dump(nft_dict, fp,  indent=4)


def gecko_spot(name='gecko_spot'):

    link_list = []
    for page in range(1, 7):
        print('page', page)
        result = requests.get(
            "https://www.coingecko.com/en/exchanges?page=" + str(page))
        soup = BeautifulSoup(result.text, 'html.parser')
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
    for link in link_list:
        try:
            new_page = requests.get(link)
            soup = BeautifulSoup(new_page.text, 'html.parser')
            section = soup.find('div', text='Website')
            parent = section.parent
            url = parent.find('a').attrs['href']
            title = soup.find(
                'div', attrs={'class': 'exchange-name font-weight-bold'})
            clean_title = title.text[1:-1]
            exchg_dict[clean_title] = url
            print(clean_title)
        except:
            print('fail2')
    print(exchg_dict)
    with open(name + '.json', 'w') as fp:
        json.dump(exchg_dict, fp,  indent=4)


def dapp_rank(name='dappradar_'):

    import time
    from bs4 import BeautifulSoup
    from selenium import webdriver
    from webdriver_manager.chrome import ChromeDriverManager
    import pandas as pd

    # data = []

    link_list = []
    for page in range(1, 396):
        url = "https://dappradar.com/rankings/{page}".format(
            page=page)

        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.maximize_window()
        time.sleep(8)
        driver.get(url)
        time.sleep(10)

        soup = BeautifulSoup(driver.page_source, 'lxml')
        driver.close()
        table = soup.find('div', attrs={
            'sc-jHwEXd bJCvGT rankings-table'})
        rows = table.find_all('a')
        dict_name = {}
        for row in rows:
            try:
                surl = 'https://dappradar.com' + row.attrs['href']
                link_list.append(surl)
                driver = webdriver.Chrome(ChromeDriverManager().install())
                driver.maximize_window()
                time.sleep(8)
                driver.get(surl)
                time.sleep(10)
                soup = BeautifulSoup(driver.page_source, 'lxml')
                title_box = soup.find('div', attrs={'class':
                                                    'article-page__brand-info'})
                title = title_box.find('h1').text
                twitter_url = ''
                discord_url = ''
                address_tag = ''

                try:
                    address_tag = soup.find(
                        'a', attrs={'class': 'sc-gCEpsI eRYsQQ'}).attrs['href']
                except:
                    print('no address')
                # print('address_tag', address_tag)
                # socials = soup.find('div', attrs={'class':
                #                                   'article-page__social'})

                try:
                    twitter = soup.find('div', attrs={'data-original-title':
                                                      'twitter'})
                    twitter_url = twitter.find('a').attrs['href']
                    discord = soup.find('div', attrs={'data-original-title':
                                                      'discord'})
                    discord_url = discord.find('a').attrs['href']
                except:
                    print('didnt get twitter')
                dict_name[title] = {'website': address_tag,
                                    'twitter': twitter_url, 'discord': discord_url}
            except:
                print('furl', url)
        with open(name + str(page) + '.json', 'w') as fp:
            json.dump(dict_name, fp,  indent=4)


if __name__ == '__main__':
    fire.Fire()
