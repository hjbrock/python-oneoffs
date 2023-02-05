import googleapiclient.errors
from pyquery import PyQuery

import os

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from ride import Ride


def get_rides():
    rides_page_pq = PyQuery(url='http://www.lagoonpark.com/what-to-do/rides-attractions/')
    ride_links = rides_page_pq('div.rides')('a.ride')  # todo error handling

    rides = []
    for ride_link in ride_links:
        name = PyQuery(ride_link)('div.info-caption').text()
        min_height = ride_link.attrib['data-rideminheight']
        thrill_level = ride_link.attrib['data-thrilllevel']
        splash_level = ride_link.attrib['data-splashlevel']
        ride_type = ride_link.attrib['data-ridetype']
        url = ride_link.attrib['href']
        ride = Ride(name, min_height, thrill_level, splash_level, ride_type, url)
        ride.fetch_details()
        rides.append(ride)
    return rides


def create_sheet(sheets_service):
    body = {
        'properties': {
            'title': 'Lagoon Rides'
        },
        'sheets': [{
            'properties': {
                'title': 'Rides'
            }
        }]
    }
    spreadsheet = sheets_service.create(body=body, fields='spreadsheetId').execute()
    return spreadsheet.get('spreadsheetId')


def add_sheet_to_spreadsheet(sheet_id, sheets_service):
    add_sheet_request = {
        'requests': [{
            'addSheet': {
                'properties': {
                    'title': 'Rides'
                }
            }
        }]
    }
    sheets_service.batchUpdate(spreadsheetId=sheet_id, body=add_sheet_request).execute()


def write_rides_to_gsheet(sheet_id, service_file, rides):
    creds = Credentials.from_service_account_file(service_file)
    service = build('sheets', 'v4', credentials=creds)
    sheets = service.spreadsheets()

    if sheet_id is None:
        sheet_id = create_sheet(sheets)

    try:
        sheets.values().clear(spreadsheetId=sheet_id, range='Rides!A1:Z').execute()
    except googleapiclient.errors.HttpError as err:
        match err.resp.status:
            case 404:
                raise Exception('Specified SHEET_ID is invalid')
            case 400:
                # sheet was probably missing, try adding it
                add_sheet_to_spreadsheet(sheet_id, sheets)
            case _:
                raise err

    rows = [
        ['Name', 'Type', 'Location', 'Min Height', 'Max Height', 'Thrill Level', 'Splash Level', 'Note', 'Details',
         'Toddler Suitable'],
    ]
    for ride in rides:
        rows.append([
            ride.name,
            ride.ride_type,
            ride.location,
            ride.min_height,
            ride.max_height,
            ride.thrill_level_str(),
            ride.splash_level_str(),
            ride.note,
            ride.url,
            ride.is_toddler_suitable(),
        ])

    sheets.values().batchUpdate(spreadsheetId=sheet_id, body={
        'data': [{
            'majorDimension': 'ROWS',
            'range': 'Rides!A1:Z',
            'values': rows,
        }],
        'valueInputOption': 'USER_ENTERED',
    }).execute()

    return sheet_id, len(rides)


def main():
    sheet_id = os.getenv('SHEET_ID')
    sheets_auth = os.getenv('SHEETS_AUTH')

    if sheets_auth is None:
        raise Exception('SHEETS_AUTH environment variable must be set with the path of a Google service file')

    rides = get_rides()
    sheet_id, ride_count = write_rides_to_gsheet(sheet_id, sheets_auth, rides)
    print(f'{ride_count} rides written to sheet ID {sheet_id}')


if __name__ == '__main__':
    main()
