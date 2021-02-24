# API documentation: https://wshero07.herobase.com/api-docs 
import requests
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta 
from secrets import HERO_BASE_AUTH 
import pandas as pd 
import boto3 
import logging

base_url = 'https://wshero07.herobase.com/api'
auth_headers = {
    'Authorization': f'Basic {HERO_BASE_AUTH}', 
    'Accept': 'application/json'
    }

def get_organizationalunits():
    '''
    Method Input params: None
    Method Result: List of Organization Codes
    API Input params: None. (Result depends only on the authenticated user's role.)
    API Result: An array of orgUnits within Telia. Each one has an OrgCode that will be needed as input parameters for future calls.
    '''
    try:
        url = f'{base_url}/organizationalunits'
        response = requests.get(url, headers = auth_headers)
        response.raise_for_status()
        org_array = response.json()
        codes = []
        for item in org_array: 
            codes.append(item['orgCode'])  
    except requests.exceptions.HTTPError as err:
        logging.error(err)
    except requests.exceptions.RequestException as err:  
        logging.error(err)
    return codes

def get_calls(org_codes):
    '''
    Method Input params: List of OrgCodes returned by get_organizationalunits() 
    Method Result: DataFrame with schema ['org_code', 'lead_status', 'load_timestamp']
    API Input params: 
    - OrgCode: Take from the array of orgUnits found previously.
    - StartTime: Now-3 years
    - TimeSpan: 3 years
    API Result: An array of calls for the specified orgUnit. Each call has a property called leadClosure, which indicates if a sale was made. Loop through all found orgUnits and accumulate all calls.
    '''
    start_dt = datetime.now() - relativedelta(years=3)
    calls_array = []
    time_period = 'P3Y' 
    for org_code in org_codes:
        url = f'{base_url}/calls?OrgCode={org_code}&StartTime={start_dt.isoformat()}&TimeSpan={time_period}'
        try:
            response = requests.get(url, headers = auth_headers)
            response.raise_for_status()
            calls_array = calls_array + response.json()
        except requests.exceptions.HTTPError as err:
            logging.error(err)
        except requests.exceptions.RequestException as err:  
            logging.error(err)
    return calls_array

def get_simpleleads():
    '''
    Method Input params: None
    Method Result: DataFrame with schema [telia_order_id, load_timestamp]
    API Input params:  
    - Project: *
    - ModifiedFrom: It should probably be Now - 3 years.
    API Result: Each lead in the result has a "CustomData" property that should contain a Telia order ID. 
    '''
    three_yrs_ago = datetime.now() - relativedelta(years=3)
    try:
        url = f'{base_url}/simpleleads?Projects=*&ModifiedFrom={three_yrs_ago.isoformat()}&AllClosedStatuses=true&AllOpenStatuses=true'
        response = requests.get(url, headers = auth_headers)
        response.raise_for_status()
        leads_array = response.json()
    except requests.exceptions.HTTPError as err:
        logging.error(err)
    except requests.exceptions.RequestException as err:  
        logging.error(err)
    return leads_array 

def dump(data, tmp_fname): 
    '''
    Method Input param: 
    - Data 
    - Filename: Optional
    Method Result: Returns none
    '''
    try:
        with open(tmp_fname, 'w') as f:
            f.write(data)
    except Exception as err:
        raise SystemExit(err)


def s3_upload(local_file_path, bucket_name, s3_path):
    '''
    Method Input param: 
    - File path
    - Bucket name 
    - Path in bucket where to upload
    Method Result: Uploads file to specified location in S3, returns None
    '''
    try:
        s3 = boto3.resource('s3')
        s3.meta.client.upload_file(local_file_path, bucket_name, s3_path)
    except Exception as err:
        raise SystemExit(err)

# MAIN
if __name__ == '__main__':
    org_unit_codes = get_organizationalunits() 
    calls = get_calls(org_unit_codes)
    dump(calls, 'dump/calls.json')
    leads = get_simpleleads()
    dump(leads, 'dump/leads.json')
    s3_upload('dump/calls.json', 'ddata-atdk', 'herobase/calls/calls.json')
    s3_upload('dump/leads.json', 'ddata-atdk', 'herobase/leads/leads.json')
