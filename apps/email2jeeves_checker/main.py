import sentry_sdk
from sentry_sdk import api
from lib.api import integrator
import sys


try:
    env = sys.argv[1]
except IndexError:
    env = 'dev'

if env == 'prod':
    config = 'config_prod'
elif env == 'test':
    config = 'config_test'
else:
    config = 'config_dev'

sentry_sdk.init(
    "https://d36b1375bf924c46b967b1676ff8b49b@o229295.ingest.sentry.io/5609631",
    traces_sample_rate=1.0,
    environment=env
)
print("Config info:", config)
api_object = integrator(config)
api_object.ms_move_old_emails_to_new_folder()
customer_emails = api_object.ms_get_mails_from_folder_new()
if len(customer_emails) == 0:
    print('NO NEW MAILS')
else:
    print('NEW EMAILS FOUND')
    for item in customer_emails:
        api_object.ms_post_move2folder('InProgress', mail_id=item['id'])
        api_object.ms_get_mail_by_id()
        api_object.appPortal_fetch_config()  # if config not found end here and forward email
        api_object.log2console()
        if api_object.order_info.customerName != '':
            if api_object.order_info.file_extension == 'body':
                print("Converting order from body to html")
                api_object.ms_convert_body_to_base64()
            else:
                api_object.ms_get_mail_attachments()
            api_object.appPortal_create_order()
