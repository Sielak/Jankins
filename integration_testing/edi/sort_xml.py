import xml.etree.ElementTree as ET
import sys
import os


def sort_and_save_file(folder, integration_name):
    tree = ET.parse('{0}/TEMP.xml'.format(folder))
    root = tree.getroot()
    root[:] = sorted(root, key=lambda child: (child.tag, int(child.get('Rad'))))
    filename = '{0}/{1}.xml'.format(folder, integration_name)
    tree.write(filename, encoding="UTF-8")
    os.remove('{0}/TEMP.xml'.format(folder))


integration = sys.argv[1]  # PROD
# integration = 'tieto'  # TEST

sort_and_save_file('models', integration)
sort_and_save_file('to_compare', integration)




