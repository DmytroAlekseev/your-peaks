import pandas as pd


def convert_data(text):
    for row in text:
        row = row.split()
        if row[2].isnumeric() and row[1] != 'Висота' and row[4] == 'м.':
            NAME.append(row[1])
            HEIGHT.append(int(row[2] + row[3]))
            LONGITUDE.append(row[5:8])
            LATITUDE.append(row[8:])
        elif row[2].isnumeric() is False and row[5] == 'м.':
            NAME.append(row[1] + ' ' + row[2])
            HEIGHT.append(int(row[3] + row[4]))
            LONGITUDE.append(row[6:9])
            LATITUDE.append(row[9:])
        elif row[2].isnumeric() and row[1] == 'Висота' and row[5] == 'м.':
            NAME.append(row[1] + ' ' + row[2])
            HEIGHT.append(int(row[3] + row[4]))
            LONGITUDE.append(row[6:9])
            LATITUDE.append(row[9:])
        elif row[2].isnumeric() and row[1] != 'Висота' and row[3] == 'м.':
            NAME.append(row[1])
            HEIGHT.append(int(row[2]))
            LONGITUDE.append(row[4:7])
            LATITUDE.append(row[7:])
        else:
            NAME.append(row[1] + ' ' + row[2])
            HEIGHT.append(int(row[3]))
            LONGITUDE.append(row[5:8])
            LATITUDE.append(row[8:])

    data = {'Name': NAME, 'Height': HEIGHT, 'Longitude': LONGITUDE, 'Latitude': LATITUDE}

    return data


NAME = []
HEIGHT = []
LONGITUDE = []
LATITUDE = []