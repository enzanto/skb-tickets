import json
import requests
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
from datetime import datetime as dt, timedelta
import os

# set variables
gc = gspread.service_account("/usr/src/app/credentials.json")
email = os.getenv('EMAIL')
now = dt.now()


def get_matches():
    sh_matches = gc.open('matches')
    ws_matches = sh_matches.worksheet('Sheet1')
    df_matches = pd.DataFrame(ws_matches.get_all_records())
    df_matches['time'] = pd.to_datetime(df_matches['time'])
    df_matches = df_matches[df_matches['time'] > now + timedelta(minutes=35)]
    return df_matches


def get_sections(match_url):
    
    match_raw = requests.get(match_url + '/item_types.json').text
    match_data = json.loads(match_raw)

    sections = []
    for i in match_data['item_types']:
        for x in i['sections']:
            sections.append(x['id'])
    sections = set(sections)
    return sections

def open_sheet(sheet_name):
    try:
        sh = gc.open(sheet_name)
    except:
        sh = gc.create(sheet_name)
        sh.share(email, perm_type='user', role='writer')
    worksheets = ['oversikt','Main','Frydenbø','BT-BOB','SPV','Fjordkraft','VIP','timeline']
    for sheet in worksheets:
        try:
            sh.worksheet(sheet)
        except:
            sh.add_worksheet(sheet,"2000","20")
    return sh

def get_ticket_info(match_url,sections):
    df = pd.DataFrame(columns = ['Felt', 'feltnummer', 'Kapasitet', 'Ledig','Solgt', 'Andre', 'Prosent'])
    for i in sections:
        url =  match_url + 'sections/' + str(i) + '.json'
        request = requests.get(url)
        seat_map = json.loads(request.text)
        name = seat_map['seating_arrangements']['section_name']
        total = seat_map['seating_arrangements']['section_amount']
        seats = seat_map['seating_arrangements']['seats']
        sold = 0
        available = 0
        other = 0
        for dicts in seats:
            if dicts.get("status") == "sold":
                sold += 1
            elif dicts.get("status") == "available":
                available += 1
            else:
                other += 1
        prosent = (sold / total)
        prosent = round(prosent, 3)
    
        section_dict = {'Felt': [name], 'feltnummer': [i], 'Kapasitet': [total], 'Ledig': [available], 'Solgt': [sold], 'Andre': [other], 'Prosent': [prosent]}
        df = pd.concat([df,pd.DataFrame(section_dict, columns=df.columns)], ignore_index=True)
    return df
    
def update_sheet(df,sh):
    vip = df[df['Felt'].str.contains('VIP')]
    bob = df[df['Felt'].str.contains('BOB')]
    fjordkraft = df[df['Felt'].str.contains('FJORDKRAFT')]
    frydenbo = df[df['Felt'].str.contains('FRYDENBØ|STORE')]
    spv = df[df['Felt'].str.contains('SPV')]
    # tribuner = [frydenbo,spv,bob,fjordkraft,vip,df]

    df2 = df.sum(axis = 0, skipna= True)
    now = dt.now().strftime('%Y-%m-%d %H:%M:%S')
    timeline = pd.DataFrame(sh.worksheet('timeline').get_all_records())
    timeline_dict = {'timestamp': [now], 'total': [df2['Solgt']]}
    timeline = pd.concat([timeline,pd.DataFrame(timeline_dict)],ignore_index=True)

    sh.worksheet('oversikt').update('B2', now)
    set_with_dataframe(sh.worksheet('timeline'),timeline)
    set_with_dataframe(sh.worksheet('Main'),df)
    set_with_dataframe(sh.worksheet('Frydenbø'),frydenbo)
    set_with_dataframe(sh.worksheet('SPV'),spv)
    set_with_dataframe(sh.worksheet('BT-BOB'),bob)
    set_with_dataframe(sh.worksheet('Fjordkraft'),fjordkraft)
    set_with_dataframe(sh.worksheet('VIP'),vip)

if __name__ == "__main__":
    df_matches = get_matches()
    for i in df_matches.index:
        match_url = df_matches.loc[i]['kampurl']
        sheet_name = df_matches.loc[i]['sheet']
        sections = get_sections(match_url)
        df = get_ticket_info(match_url,sections)
        sh = open_sheet(sheet_name)
        update_sheet(df,sh)
