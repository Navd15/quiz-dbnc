from ast import arg
from utils import toCSV,getDataFromUrl,validateCSV
import os
import sys

# get raw html from
scrap_url=sys.argv[1] if len(sys.argv)>1 else None  

html_raw_data=getDataFromUrl(scrap_url or os.getenv('SCRP_URL')   )
# optional file path of csv
csv_path=os.getenv('CSV_PATH')
file_path=toCSV(html_raw_data,csv_path)
validateCSV(file_path)