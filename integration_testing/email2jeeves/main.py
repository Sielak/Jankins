import os
import sys
from helpers import Helpers, Jeeves


try:
    cso_emial = sys.argv[1]
except IndexError:
    cso_emial = 'dawid.wybierek@hl-display.com'


def main(cso_email):
    helpers = Helpers()
    jeeves_object = Jeeves(helpers.fetch_db_config_from_integration())
    if helpers.prepare_data(cso_email) is False:
        print("Problem with prepering data in integration")
        exit(1)
    jeeves_object.prepare_data_in_jeeves()
    helpers.convert2base64()
    order_numbers = []
    for item in os.listdir("files_base64"):
        customer_name = item.split(".")[0]
        file_base64 = helpers.fetch_base64_string_from_file(item)
        customer_config = helpers.search4config(customer_name)
        if customer_config is None:
            print(f"config not found for customer {customer_name}")
            continue
        email_subject = f"subject_test_{customer_name}"
        if customer_name == "ICA":
            email_subject = "Inköpsorder_IO615925_035404_EXTAPF"
        result = helpers.create_order(customer_name, email_subject, f"{customer_name}.{customer_config['file_extensions'][0]}", file_base64)
        orders = result['Message'].strip()
        order_numbers_splitted = orders.split("New EDI order ") 
        if customer_name == "Ariba":
            customer_config['foretagkod'] = '1810'
            customer_name = "Auchan"
        if len(order_numbers_splitted) == 1:
            print("----Order not created----")
            print(customer_name)
            print(result['Message'])
            print("----END----")
        elif len(order_numbers_splitted) > 2:
            for order in order_numbers_splitted:
                if order != '':
                    order_numbers.append(f"{customer_name}:{customer_config['foretagkod']}:{order.split(' has been')[0]}")
        else:
            order_numbers.append(f"{customer_name}:{customer_config['foretagkod']}:{order_numbers_splitted[1].split(' has been')[0]}")
        if result['success'] is False and len(order_numbers_splitted) != 1:
            print('Order creation was not successful')
            print(result['Message'])
    helpers.delete_all_base64_files()
    final_result = []
    print("--------------LOG--------------")
    for order in order_numbers:
        print(order)
        res = jeeves_object.check_order(order)
        final_result.append(res)
    if False in final_result:
        print("--------------ERROR LOG--------------")
        print("some orders were created with errors")
        exit(1)


if __name__ == '__main__':
    main(cso_emial)
