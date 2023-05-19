import argparse
import requests


parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-job', help='job name to run')
parser.add_argument('-env', help='Used used to determine prod or test env')

args = parser.parse_args()

if args.job is None:
    print('Job name was not provided!')
    exit(0)
if args.env is None:
    print('Env name was not provided!')
    exit(0)
if args.job == 'refresh':
    if args.env == 'prod':
        upload_portal_url = "http://tools.hl-display.com/api/crossDockingRefresh"
    else:
        upload_portal_url = "http://bma-dev-704:8300/api/crossDockingRefresh"
    r = requests.post(upload_portal_url)
    if r.status_code == 200:
        print(f"CrossDocking data was refreshed for env {args.env}")
    else:
        print(f"Problem with refreshing CrossDocking data for env {args.env}")
        print(r.json())
elif args.job == 'report':
    if args.env == 'prod':
        upload_portal_url = "http://tools.hl-display.com/api/crossDockingSummaryEmail"
    else:
        upload_portal_url = "http://bma-dev-704:8300/api/crossDockingSummaryEmail"
    r = requests.post(upload_portal_url)
    if r.status_code == 200:
        print(r.json()['Data'])
    else:
        print(f"Problem with sending CrossDocking report email for env {args.env}")
        print(r.json())
elif args.job == 'cab_refresh':
    if args.env == 'prod':
        upload_portal_url = "http://tools.hl-display.com/api/cab_refresh"
    else:
        upload_portal_url = "http://bma-dev-704:8300/api/cab_refresh"
    r = requests.post(upload_portal_url)
    if r.status_code == 200:
        print(r.json()['Data'])
    else:
        print(f"Problem with refreshing FreshService data for env {args.env}")
        print(r.json())
else:
    print('Job with that name not configured')
