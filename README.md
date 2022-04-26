# Web3 Scrapers

## Keys
Get the api key files (`hexatorch-erfan.json`, `constants.py`) from drive and add them to the folder.

## How to use the TrustRank

command: `python scraping.py [function name] [optional: name of file]`

For example: `python scraping.py gecko_spot` or `python scraping.py gecko_spot spot_file`

function list for fetching data:
- gecko_spot (CoinGecko)
- gecko_nft (CoinGecko)
- dapp_rank (DappRadar)
- cryptoslam (cryptoslam)
- coinmarket_dex (CoinMarketCap)
- coinmarket_nft (CoinMarketCap)

for dappradar you need to clean the data after fetching them. Put the exported jsons in a folder and run the `dapp_clean` function like  
`python scraping.py dapp_clean [folder containing original jsons] [folder to export the clean jsons into]`

Later you have to put the outputs from all the scraping functions into a folder and run the `aggregate` function to identify which website can be trusted the most   
`python scraping.py aggregate [path to folder containing all jsons]`

## How to upload data to Firestore

function list for fetching data:
 - `filter`: function to filter json output data from the `aggregate` funtion based on paramaters you want
   - `python firestore.py filter example_all.json`
 - `upload_safe`: upload json to the firestore database.
  -  `python firestore.py upload_safe example_filtered.json [path to json key]
 - `upload_safe_man`: upload json data that was curated manually to the firestore database.
  -  `python firestore.py upload_safe_man example_manual.json [path to json key]


