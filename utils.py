from requests import get, post
from bs4 import BeautifulSoup as BS
import csv
import dotenv
# load .env file
dotenv.load_dotenv('.env')
import os
import sys

""" 
returns tables or slice of tables array from 
the raw html string using BeautifulSoup
 """


def _getTableFromBS(html_str, idx=None):
    return BS(html_str, features='html.parser').find_all(
        'table') if idx else BS(html_str).find_all('table')[:idx]


""" 
returns data from BS table to 
csv string for further processing
"""


def _processTable(tables):
    str_data = ''
    # for each table
    for table in tables:
        # check each row, start from 2nd row as first row is column numbers
        for row in table.find_all('tr')[1:13]:
            temp = ''
            # check each row data <td> and append it to temp , use only first 5 columns
            for row_data in row.find_all('td')[:5]:
                if row_data.text != '':
                    # separate by ,
                    temp += row_data.text + ','
            # break by new line \n
            temp = temp[:-1] + '\n'
            str_data += temp
    return str_data


""" gets csv formatted string, 
file name and writes csv file in th"""


def toCSV(data_str, file_name='python_data.csv'):
    try:
        str_data = _processTable(_getTableFromBS(data_str, 1))
        file_path = os.path.join(os.getcwd(), file_name)
        # open a new file in cwd and initiate csv writer
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            # split the data with new line \n and convert into list & write to csv file
            # first line should be a header
            writer.writerow(str_data.split('\n')[0].split(','))
            writer.writerows(
                [row.split(',') for row in str_data.split('\n')[1:-2]])
    except Exception as E:
        print('hello')
        sys.exit(1)
    else:
        print(f'File {file_name} written at {file_path}')
        return file_path


""" takes url & returns 
raw html string """


def getDataFromUrl(url=None):
    try:
        assert type(url) == type('') and (
            url.startswith('https://') or url.startswith('http://')
        ), f"type error: url should be a valid url string"

        data = get(url).text
    except Exception as E:
        print(E)
        sys.exit(1)
    else:
        return data


""" takes keys, vals & 
returns dict for formdata """


def _makeFormData(keys, vals):
    return dict(zip(keys, vals))


""" checks if the given data has
 valid address returns boolean 
"""


def _isValid(data):
    # get current validation url from .env file
    url = os.getenv('VAL_URL')
    # makes a post request to url with form-data as data & given headers
    req = post(
        url,
        data=data,
        headers={
            'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 Edg/97.0.1072.62'
        })
    return True if req.json()['resultStatus'] == 'SUCCESS' else False


""" method that reads the old csv file and then validates 
each row and overwrite the old file with new column
 """


def validateCSV(csvPath):
    # saves the reponses from the _isValid function
    res = []
    # form-data key values
    keys = ('companyName', 'address1', 'city', 'state', 'zip')
    # save all the lines from the old csv file
    lines = []
    """ open csvPath csv file and read new lines 
    and then again take cursor back to first line to overwrite the old file
    """
    with open(csvPath, 'r+', newline='') as file:
        csv_reader = csv.reader(file)
        for row in list(csv_reader)[1:]:
            lines.append(row)
        file.seek(0)
        csv_writer = csv.writer(file, delimiter=',')
        # first header row with new column Valid ?
        csv_writer.writerow(
            ['Company', 'Street', 'City', 'St', 'ZIPCode', 'Valid ?'])
        # for each line check if the address is valid & save the file
        for row in lines:
            form_data = _makeFormData(keys, row)
            res.append(_isValid(form_data))
            csv_writer.writerow(row + [res[-1]])
    print(f'Validate csv written at {csvPath}')
