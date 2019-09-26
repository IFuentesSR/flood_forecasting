import os

import pandas as pd
import numpy as np


def VIC_Discharge(file, skip):
    """Read Victoria dataframes.

    Parameters
    ----------
    file : str
        name of csv file with hydrologic time series data.
    skip : int
        index of non usable rows in file.

    Returns
    -------
    Dataframe
        Returns a dataframe with dates as index and hydrologic data.

    """
    DF = pd.read_csv(file,
                     error_bad_lines=False,
                     skiprows=skip)
    DF['Datetime'] = pd.to_datetime(DF['Datetime'],
                                    format='%d/%m/%Y %H:%M:%S')
    return DF


def NSW_Discharge(file):
    """Read NSW dataframes.

    Parameters
    ----------
    file : str
        name of csv file with hydrologic time series data.

    Returns
    -------
    Dataframe
        Returns a dataframe with dates as index and hydrologic data.

    """
    DF = pd.read_csv(file,
                     error_bad_lines=False,
                     skiprows=4,
                     usecols=[0, 1, 2],
                     names=['Datetime', 'discharge', 'QC']
                     )
    DF['Datetime'] = pd.to_datetime(DF['Datetime'],
                                    format='%H:%M:%S %d/%m/%Y')
    return DF


def QLD_Discharge(file, skip):
    """Read Queensland dataframes.

    Parameters
    ----------
    file : str
        name of csv file with hydrologic time series data.
    skip : list
        list of indexes of non usable rows in file.

    Returns
    -------
    Dataframe
        Returns a dataframe with dates as index and hydrologic data.

    """
    DF = pd.read_csv(file,
                     error_bad_lines=False,
                     skiprows=[0, 1, 2, 3, 4, skip[0], skip[1]],
                     usecols=[0, 1, 2],
                     names=['Datetime', 'discharge', 'QC']
                     )
    DF['Datetime'] = pd.to_datetime(DF['Datetime'],
                                    format='%H:%M:%S %d/%m/%Y')
    return DF


def common_DF_processing(Data):
    """Returns a pandas dataframe sorted and cleaned.

    Parameters
    ----------
    Data : pandas dataframe
        Dataframe with dates as index and hydrologic data.

    Returns
    -------
    pandas dataframe
        Returns a dataframe with dates and discharges.

    """
    Data = Data.set_index('Datetime')
    Data['QC'][(Data['QC'] == 180) | (Data['QC'] == 255) | (Data['QC'] == 130)] = np.nan
    Data = Data.dropna(how='any')
    Data = Data.drop(columns=['QC'])
    Data.columns = ['Discharge']
    return Data


def getting_discharge(file):
    """Save csv files containing dates and discharges.

    Parameters
    ----------
    file : str
        Name of csv file with hydrologic time series data.

    """
    with open(file) as txt:
        check = txt.readlines()
        txt.close()
    lookup = 'Datetime'
    if "Quality Codes (QC)" in check[0]:
        index = [i for i, n in enumerate(check) if lookup in n][0]
        DF = VIC_Discharge(file, index)
        DF = common_DF_processing(DF)
    elif 'qld.gov.au' in check[-1]:
        index = [i for i, n in enumerate(check) if 'qld.gov.au' in n]
        DF = QLD_Discharge(file, index)
        DF = common_DF_processing(DF)
    else:
        DF = NSW_Discharge(file)
        DF = common_DF_processing(DF)
    DF.index = DF.index.date
    DF.to_csv('monthly/Dis_{}'.format(file[8:]), index_label='Datetime')


files = [n for n in os.listdir(os.path.join(os.getcwd(), 'monthly')) if n.endswith('.csv')]
len(files)
fails = []
for n in files[:]:
    try:
        getting_discharge(os.path.join('monthly', n))
    except:
        fails.append(n)
        print(n)
