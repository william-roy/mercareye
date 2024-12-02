# search.py
# uses the mercapi library to interface with the mercari api

import os
import logging
log = logging.getLogger(__name__)
import json
import asyncio
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
scheduler = AsyncIOScheduler()

from mercapi import Mercapi
from mercapi.requests import SearchRequestData
m = Mercapi()

from config import config, data_path
from notify import sendNotification


searches_path = os.path.join(data_path, 'searches.json')
results_path = os.path.join(data_path, 'results.json')

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
        save()
    
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

def getCreatedTime(item):
    return item.created

# Returns most recently created item from a list of items
def getNewestItem(items):

    log.debug('Sorting items')
    items.sort(reverse=True,key=getCreatedTime)
    log.debug(f'Newest item: {items[0].created} - {items[0].name}')
    return items[0]
    
# Search Jobs ------------------------------------------------------------------

def addSearchJob(params):
    
    if not params['name']:
        log.warning('Search jobs must have a name')
        return
    
    if params['name'] in searches:
        log.warning('Search job names must be unique')
        return
    
    searches.append(params)

def deleteSearchJob(name):
    del searches[name]
    del results[name]

# Run a single mercari search and check for new entries
async def runSearchJob(search):

    log.debug(f'Running search {search['name']}')       
    if 'last_searched' in search:
        log.debug(f'(Last searched at {search['last_searched']})')

    # check required fields
    if 'query' not in search:
        log.warning('No keyword query present')

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
        sort_order=SearchRequestData.SortOrder.ORDER_DESC,
        status=[SearchRequestData.Status.STATUS_ON_SALE]
    )
    
    log.debug(f'Found {search_res.meta.num_found} results:')

    newest_item = getNewestItem(search_res.items)

    # check if the newest is newer than what we have stored
    if search['name'] not in results:
        setNewestTime(search['name'], newest_item.created)
        return

    if newest_item.created > getNewestTime(search['name']):
        log.info(f'New item detected in search {search['name']}:\n{newest_item.name}\n')

        sendNotification(
            search_name=search['name'],
            item_id=newest_item.id_, 
            item_name=newest_item.name, 
            item_price=newest_item.price, 
            item_thumbnail_url=newest_item.thumbnails[0])
        
        setNewestTime(search['name'], newest_item.created)
        

# Search Results ---------------------------------------------------------------

def setNewestTime(name, time):
    results[name] = time.strftime('%Y-%m-%d %H:%M:%S')
    saveResults()

def getNewestTime(name):
    return datetime.strptime(results[name], '%Y-%m-%d %H:%M:%S')

def saveResults():
    log.debug('Saving search results...')

    with open(results_path, 'w') as f:
        try:
            json.dump(results, f)
            log.info('Search results saved')
        except (IOError, OSError) as e:
            log.error(f'Unable to save search results\n{e}')
            return

def purgeResults(name):
    if not name:
        results = []
    else:
        del results[name]

# Schedule and start searches
async def start():

    log.debug('Scheduling searches...')

    for s in searches:

        # set defaults
        interval = config['SEARCH']['Interval']
        jitter = config['SEARCH']['Jitter']

        # override defaults
        if 'interval' in s:
            interval = s['interval']

        if 'jitter' in s:
            jitter = s['jitter'] 

        scheduler.add_job(runSearchJob, 'interval', 
                          seconds=interval, jitter=jitter, args=[s])

    log.debug('Scheduling complete')
    log.debug('Starting scheduler...')
    scheduler.start()

    print('Press Ctrl+{} to exit'.format('Break' if os.name == 'nt' else 'C'))

    while True:
        await asyncio.sleep(1000)

