import sqlite3
import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('API_KEY')

def get_zipcode(input_zipcode):

    conn = sqlite3.connect('database.sqlite3')
    c = conn.cursor()

    c.execute('SELECT latitude, longitude FROM deutschland_daten WHERE zipcode = ?', (input_zipcode,))
    
    rows = c.fetchall()

    latitude = rows[0][0]
    longitude = rows[0][1]

    conn.close()

    return latitude, longitude


def get_gas_infos(latitude, longitude, gas_type):

    url = f'https://creativecommons.tankerkoenig.de/json/list.php?lat={latitude}&lng={longitude}&rad=5.0&sort=dist&type=all&apikey={api_key}'
    response = requests.get(url)
    data = response.json()

    df = pd.DataFrame(data['stations'])

    df = df.drop(columns=['id', 'street', 'place', 'houseNumber', 'postCode', 'name'])
    df = df.rename(columns={'e5': 'super', 'e10': 'super plus', 'brand': 'name'})

    if gas_type == 'diesel':
        df = df.sort_values(by=['isOpen', 'diesel', 'dist'], ascending=[False, True, True])
    elif gas_type == 'super':
        df = df.sort_values(by=['isOpen', 'super', 'dist'], ascending=[False, True, True])
    elif gas_type == 'super plus':
        df = df.sort_values(by=['isOpen', 'super plus', 'dist'], ascending=[False, True, True])
    else:
        print('Error: Wrong gas type')

    df['diesel'] = df['diesel'].astype(str).str[:-1] + '⁹'
    df['super'] = df['super'].astype(str).str[:-1] + '⁹'
    df['super plus'] = df['super plus'].astype(str).str[:-1] + '⁹'
    df['diesel'] = df['diesel'].str.replace('.', ',', regex=False)
    df['super'] = df['super'].str.replace('.', ',', regex=False)
    df['super plus'] = df['super plus'].str.replace('.', ',', regex=False)
    df['isOpen'] = df['isOpen'].astype(str).str.replace('True', 'Open').replace('False', 'Closed')
    df['dist'] = df['dist'].astype(str) + ' km'

    if gas_type == 'diesel':
        df = df[['name', 'dist', 'diesel', 'isOpen']]
        print(df)
    elif gas_type == 'super':
        df = df[['name', 'dist', 'super', 'isOpen']]
        print(df)
    elif gas_type == 'super plus':
        df = df[['name', 'dist', 'super plus', 'isOpen']]
        print(df)
    else:
        print('Error: Wrong gas type')
    
input1 = input('Enter your zipcode: ')
input2 = input('Enter your gas type (diesel, super, super plus): ')

if input1 == '':
    input1 = '33775'
if input2 == '':
    input2 = 'diesel'

get_gas_infos(get_zipcode(input1)[0], get_zipcode(input1)[1], input2)
