import requests
from bs4 import BeautifulSoup
import json
import re
import csv
from datetime import datetime	
import time

def get_cube_ids(page_count, params, query):
    page = requests.get('https://cubecobra.com/search/'+query+'/'+str(page_count), params=params)
    soup = BeautifulSoup(page.text, 'html.parser')
    cleaned_props=str(soup.find_all('script')[-2]).replace('<script type="text/javascript">window.reactProps = ','').replace(';</script>','')
    props_dict=json.loads(cleaned_props)
    for cube in props_dict["cubes"]:
        cube_lists.append(cube["_id"])
    print(props_dict['count'])
    if props_dict['count'] > props_dict['perPage'] *(page_count +1):
        page_count= page_count+1
        print(page_count)
        time.sleep(2)
        get_cube_ids(page_count, params=params, query=query)

def get_cube_contents(cube_id, excluded_ids):
    if cube_id in excluded_ids:
        return

    html_page=requests.get("https://cubecobra.com/cube/list/"+ cube_id)
    soup = BeautifulSoup(html_page.text, 'html.parser')
    cleaned_props = str(soup.find_all('script')[-2]).replace('<script type="text/javascript">window.reactProps = ','').replace(';</script>','')
    cleaner_props= re.sub(r'new Date\([^\)]*\)', '""', cleaned_props)
    props_dict=json.loads(cleaner_props)
    cards=props_dict['cube']['cards']
    if len(cards)==0:
        print("Empty cube!")
    for card in cards:
        try:
            cube_contents[card['details']['name']]['count'] = cube_contents[card['details']['name']]['count'] + 1
        except:
            try:
                cube_contents[card['details']['name']] = {'name':card['details']['name'], 'power': card['details']['power'], 'toughness': card['details']['toughness'], 'color_id': ''.join(card['details']['color_identity']), 'elo': card['details']['elo'], 'count': 1, 'cmc': card['details']['cmc']}
            except:
                try:
                    cube_contents[card['details']['name']] = {'name':card['details']['name'], 'power': '', 'toughness': '', 'color_id': ''.join(card['details']['color_identity']), 'elo': card['details']['elo'], 'count': 1, 'cmc': card['details']['cmc']}
                except:
                    cube_contents[card['details']['name']] = {'name':card['details']['name'], 'power': '', 'toughness': '', 'color_id': ''.join(card['details']['color_identity']), 'elo': '', 'count': 1, 'cmc': card['details']['cmc']}
    pass

# Create list and dictionary to store data from the requests
cube_lists = []
cube_contents ={}

# set query values
page=0
query="cards%3E400%20category:%22Pauper%22"
params={'order':'alpha'}

# ids of cubes to exclude
# In the initial case these were either cubes with strange categorization or were just made of the same cards repeated over and over
excluded_ids=['5e761c2b6f01105bb0b657e8','5e0669caeead874688a7a28d','5ecd7e664022a8067a2cf7d4',"5ecfce407b7511525ceb1c84","5e70d15640eaf0158e08b22b"]

#get IDs of all cubes that match the query
get_cube_ids(page, params=params, query=query)
#iterate using each id to get the contents of each cube
for id in cube_lists:
    get_cube_contents(id, excluded_ids)
    time.sleep(2)

with open('cube_output-'+datetime.today().strftime('%Y-%m-%d-%H_%M_%S')+'.csv', mode='w') as csv_file:
    csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow(['name','cmc','power', 'toughness', 'color_id', 'count', 'elo'])
    for card in cube_contents.values():
        print(card)
        csv_writer.writerow([card['name'],card['cmc'],card['power'],card['toughness'],card['color_id'],card['count'], card["elo"]])
