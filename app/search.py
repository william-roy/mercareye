# search.py
# uses the mercapi library to interface with the mercari api

import os
import logging
log = logging.getLogger(__name__)
import json
import asyncio
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from mercapi import Mercapi
from mercapi.requests import SearchRequestData
m = Mercapi()

from discord_webhook import DiscordWebhook

from config import config

searches_path = os.path.join(config['OPTIONS']['DataDir'], 'searches.json')
results_path = os.path.join(config['OPTIONS']['DataDir'], 'results.json')

# user defined list of search job objects
searches = []   

# dictionary of most recent items from searches 'searchname': datetime.datetime
results  = {}   

def load():
    global searches, results

    if os.path.isfile(searches_path):
        log.info(f'Loading searches from \'{searches_path}\'...')
    
        with open(searches_path, 'r') as f:
            try:
                searches = json.load(f)

                log.info('Searches loaded:')
                searches_str = json.dumps(searches, indent=2)
                log.info(searches_str)

            except (IOError, OSError) as e:
                log.error(f'Unable to read searches file\n{e}')   
    else:
        log.warning('No searches file found')

    
    if os.path.isfile(results_path):
        log.debug(f'Loading search results from \'{results_path}\'...')

        with open(results_path, 'r') as f:
            try:
                results = json.load(f)
                
                log.debug('Search results loaded:')
                results_str = json.dumps(results, indent=2)
                log.debug(results_str)

            except (IOError, OSError) as e:
                log.error(f'Unable to read search results file\n{e}')
    else:
        log.warning('No search results file found')


def save():
    global searches, results

    log.debug('Saving searches...')

    with open(searches_path, 'w') as f:
        try:
            json.dump(searches, f)
            log.info('Searches saved')
        except (IOError, OSError) as e:
            log.error(f'Unable to save searches\n{e}')
            return
        
    saveResults()
        
def saveResults():
    log.debug('Saving search results...')

    with open(results_path, 'w') as f:
        try:
            json.dump(results, f)
            log.info('Search results saved')
        except (IOError, OSError) as e:
            log.error(f'Unable to save search results\n{e}')
            return

def sendNotification(msg):

    # Discord
    if config['NOTIFICATIONS']['DiscordWebhookURL']: 
        webhook = DiscordWebhook(url=config['NOTIFICATIONS']['DiscordWebhookURL'],username='mercareye',content=msg)
        res = webhook.execute()

    # Other webhooks, email, etc.

# Run a single mercari search and check for new entries
async def runSearch(search):

    log.debug(f'Running search {search['name']}')       
    if 'last_searched' in search:
        log.debug(f'(Last searched at {search['last_searched']})')

    # check required fields
    if 'query' not in search:
        log.warning('No query present, aborting search')
        return

    now = datetime.now()

    # check and add optional search fields
    categories = []
    if 'categories' in search:
        categories = search['categories']

    brands = []
    if 'brands' in search:
        brands = search['brands']

    sizes = []
    if 'sizes' in search:
        sizes = search['sizes']

    # run search
    search_res = await m.search(
        query=search['query'],
        categories=categories,
        brands=brands,
        sizes=sizes,
        sort_by=SearchRequestData.SortBy.SORT_CREATED_TIME,
        sort_order=SearchRequestData.SortOrder.ORDER_ASC,
        status=[SearchRequestData.Status.STATUS_ON_SALE]
    )
    
    log.debug(f'Found {search_res.meta.num_found} results:')
    
    if log.getEffectiveLevel() == logging.DEBUG:
        for i in range(len(search_res.items)):
            item = search_res.items[i]
            log.debug(f'{i} - {item.created} - {item.name} - {item.price}')

    # compare most recent result against past result
    
    # get newest result (since order of created is not guaranteed)
    newest_item = None
    for item in search_res.items:
        if newest_item == None:
            newest_item = item
            continue

        if item.created > newest_item.created:
            newest_item = item
            break

    log.debug(f'Newest item is {newest_item.created} - {newest_item.name} - {newest_item.price}')

    # check if the newest is newer than what we have stored
    if search['name'] in results:
        if newest_item.created > results[search['name']]:
            log.info(f'New item detected in search {search['name']}:\n{newest_item.name}\n')

            sendNotification(f'The search {search['name']} detected a new item listing:\n{newest_item.name}\nhttps://buyee.jp/mercari/item/{newest_item.id}')

            results[search['name']] = newest_item.created
            saveResults()

        log.info('No new items found')
    else:
        results[search['name']] = newest_item.created

# Schedule and start searches
async def start():

    log.debug('Scheduling searches...')

    scheduler = AsyncIOScheduler()

    for s in searches:

        # set defaults
        interval = config['SEARCH']['Interval']
        jitter = config['SEARCH']['Jitter']

        # override defaults
        if 'interval' in s:
            interval = s['interval']

        if 'jitter' in s:
            jitter = s['jitter'] 

        scheduler.add_job(runSearch, 'interval', seconds=interval, jitter=jitter, args=[s])

    log.debug('Scheduling complete')
    log.debug('Starting scheduler...')
    scheduler.start()

    print('Press Ctrl+{} to exit'.format('Break' if os.name == 'nt' else 'C'))

    while True:
        await asyncio.sleep(1000)

def purgeResults():
    results = []

def deleteSearch(name):
    del searches[name]
    del results[name]