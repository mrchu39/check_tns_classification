import numpy as np
import pandas as pd
import json, simplejson
import requests
from pprint import pprint

GETTOKEN = '' # Fritz token
API_KEY = '' # TNS ZTF Bot key
YOUR_BOT_ID = '48869' # TNS ZTF Bot ID
YOUR_BOT_NAME = 'ZTF_Bot1' # TNS ZTF Bot Name

def get_TNSname(ztfname):

    ''' Info : Query the TNS name for any source
        Input : ZTFname
        Returns : ATname
    '''

    try:

        url = 'https://fritz.science/api/alerts_aux/'+ztfname
        headers = {'Authorization': f'token {GETTOKEN}'}

        response = requests.get(url, headers=headers)

        if response.status_code == 404:
            req_data = {
                "ra": "",
                "dec": "",
                "radius": "",
                "units": "",
                "objname": "",
                "objname_exact_match": 0,
                "internal_name": ztfname,
                "internal_name_exact_match": 0,
                "objid": ""
            }

            data = {'api_key' : API_KEY, 'data' : json.dumps(req_data)}
            headers={'User-Agent':'tns_marker{"tns_id":'+str(YOUR_BOT_ID)+', "type":"bot", "name":"'+YOUR_BOT_NAME+'"}'}
            #pprint(headers)

            response = requests.post('https://www.wis-tns.org/api/get/search', headers=headers, data=data)

            return json.loads(response.text)['data']['reply'][0]['prefix'] + ' ' + json.loads(response.text)['data']['reply'][0]['objname']

        IAU = json.loads(response.text)['data']['cross_matches']['TNS']


        if not IAU:
            IAU = "Not reported to TNS"

        else:
            IAU = IAU[0]['name']

    except KeyError as e:
        IAU = "Error"

    return IAU

def check_TNS_class(ztfname):

    ''' Info : Checks TNS page for other classification reports
        Input : ZTFname
        Returns : Group that reported classification
    '''

    if len(get_TNSname(ztfname)) == 0:
        return
    tns_name = get_TNSname(ztfname)[3:]
    data = {'api_key' : API_KEY}
    headers={'User-Agent':'tns_marker{"tns_id":'+str(YOUR_BOT_ID)+', "type":"bot", "name":"'+YOUR_BOT_NAME+'"}'}
    response = requests.get('https://www.wis-tns.org/object/'+tns_name, headers=headers, data=data)
    class_data = response.text.split('Classification Reports', 2)[1]

    if 'no-data' in class_data.split('class="clear"')[0]:
        return None, None

    class_info = class_data.split('<tbody>', maxsplit=1)[1].split('</div></fieldset>')[0].split('\n')

    c = 0
    while c < len(class_info):
        if 'cell-classifier_name' not in class_info[c]:
            class_info.pop(c)
        else:
            c += 1

    times = []
    groups = []
    users = []
    classes = []

    for c in class_info:
        times.append(c.split('cell-time_received">')[1].split('<')[0])
        groups.append(c.split('cell-source_group_name">')[1].split('<')[0])
        users.append(c.split('cell-user_name">')[1].split('<')[0])
        classes.append(c.split('cell-type">')[1].split('<')[0])

    return pd.DataFrame(np.vstack((times, groups, users, classes)).T, columns=['Uploaded', 'Group', 'User', 'Classification'])
