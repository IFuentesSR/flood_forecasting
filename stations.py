import os

from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import geopandas as gpd
from geopandas.tools import sjoin


def display_basins():
    """print list of possible basin names.

    """
    polys = gpd.GeoDataFrame.from_file(os.path.join(os.getcwd(),
                                                    'basins',
                                                    'rbasin_polygon.shp'))
    basins = polys['BNAME'].unique().tolist()
    print(basins)


def get_stations(basin):
    """retrieves list of stations within a basin.

    Parameters
    ----------
    basin : str
        Name of basin to get hydrological stations.

    Returns
    -------
    list
        list containing stations ID.

    """
    points = gpd.GeoDataFrame.from_file(os.path.join(os.getcwd(),
                                                     'Station',
                                                     'stations.shp'))
    polys = gpd.GeoDataFrame.from_file(os.path.join(os.getcwd(),
                                                    'basins',
                                                    'rbasin_polygon.shp'))
    poly_subset = polys[polys['BNAME'] == basin]
    pointInPolys = sjoin(points,
                         poly_subset,
                         how='left')
    grouped = pointInPolys.groupby('index_right')
    list_of_stations = list(grouped)
    basin_stations = list_of_stations[0][1]
    basin_stations_list = basin_stations['ID'].tolist()
    return list(set(basin_stations_list))


def get_files(stations):
    """retrieves list of files containing hydrologic data.

    Parameters
    ----------
    stations : list
        list containing stationsID.

    Returns
    -------
    list
        list of streamflow files.

    """
    allFiles = os.listdir(os.getcwd())
    Disc_Files = [n for n in allFiles if n.startswith('Dis_')]
    return [n for n in Disc_Files if n[4:-4] in stations]


def get_lagged_Discharge(file, date, lag):
    """Allow to obtain lagged discharge timeseries.

    Parameters
    ----------
    file : str
        Name of file associated to hydrologic gauge.
    date : str
        date as string with format YYYY-mm-dd HH:MM:SS.
    lag : int
        Lag interval for subsetting.

    Returns
    -------
    dataframe
        returns dataframe with lagged discharges.

    """
    def dateparse(x):
        return pd.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
    # dateparse = lambda x: pd.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
    DF = pd.read_csv(file,
                     parse_dates=['Datetime'],
                     date_parser=dateparse,
                     index_col='Datetime')
    if isinstance(date, datetime):
        date_format = date
    else:
        date_format = datetime.strptime(date, '%Y-%m-%d')
    lagged_date = date_format - timedelta(days=lag)
    mask = (DF.index >= lagged_date) & (DF.index <= date)
    subset = DF[mask]
    return subset


def get_flood_dates(basin, single_event=True, lag=16):
    """Retrieve list of dates with floods events given a basin.

    Parameters
    ----------
    basin : str
        string with the name of analised basin.
    single_event : boolean
        if True, the function returns only a single date without intercepting
        other flood date events.
    lag: int
        Lag interval without overlapping floods.

    Returns
    -------for subsetting
    list
        List of dates where floods occur within the basin.

    """
    DF = pd.read_csv('Areass2.csv')
    DF = DF[DF['catchment'] == basin]
    DF['date'] = pd.to_datetime(DF['date'], format='%Y_%m_%d')
    DF = DF.set_index('date').sort_index()
    DF = DF[DF['proportion'] > 0.7]
    threshold = np.nanpercentile(DF['area'], 99.5)
    flood_dates = DF[DF['area'] > threshold].index.tolist()
    if single_event:
        d = timedelta(days=lag)
        logic = [True] + (np.diff(flood_dates) > d).tolist()
        flood_dates = [f for f, l in zip(flood_dates, logic) if l]
    return flood_dates


def get_dry_dates(basin, lag=16):
    """Retrieve list of dates without flood events given a basin.

    Parameters
    ----------
    basin : str
        string with the name of analised basin.
    lag: int
        Lag interval without overlapping floods.

    Returns
    -------for subsetting
    list
        List of dates where floods do not occur within the basin.

    """
    DF = pd.read_csv('Areass2.csv')
    DF = DF[DF['catchment'] == basin]
    DF['date'] = pd.to_datetime(DF['date'], format='%Y_%m_%d')
    DF = DF.set_index('date').sort_index()
    DF = DF[DF['proportion'] > 0.7]
    threshold = np.nanpercentile(DF['area'], 99.5)
    floods = DF[DF['area'] > threshold].index.tolist()
    lagged_floods = [[n - timedelta(days=m) for m in range(lag)]
                     for n in floods]
    flatten = list(set([n for sublist in lagged_floods for n in sublist]))
    # maybe this (positive lag as well)
    # flatten = [[n + timedelta(days=m) for m in range(lag)]
    #            for n in flatten]
    # flatten = list(set([n for sublist in flatten for n in sublist]))
    ############
    dry_dates = [n for n in DF.index.tolist() if n not in flatten]
    return dry_dates


get_flood_dates('GWYDIR RIVER')

import time
start_time = time.time()
dry_dates = get_dry_dates('GWYDIR RIVER')[:]
print("--- %s seconds ---" % (time.time() - start_time))


speed = timeit.timeit(get_dry_dates('GWYDIR RIVER'), number=1)


import matplotlib.pyplot as plt
import numpy as np
%matplotlib inline


display_basins()

stats = get_stations('GWYDIR RIVER')
files = get_files(stats)
la = get_lagged_Discharge(files[0], dates[0], 16)
DF = pd.read_csv('Areass2.csv')
basins = DF['catchment'].unique().tolist()
MODIS = DF[DF['catchment'] == 'NAMOI RIVER']
MODIS['date'] = pd.to_datetime(MODIS['date'], format='%Y_%m_%d')
MODIS = MODIS.set_index('date').sort_index()
MODIS = MODIS[MODIS['proportion'] > 0.7]
threshold = np.nanpercentile(MODIS['area'], 99)
flood_dates = MODIS[MODIS['area'] > threshold].index.tolist()
days_before = [[n - timedelta(m) for m in range(1, 16)] for n in flood_dates]
flatten_days_before = [n for sublist in days_before for n in sublist]
unique_flood_dates = [n for n in flood_dates if n not in flatten_days_before]

lag = 16

DF = pd.read_csv('Areass2.csv')
DF = DF[DF['catchment'] == 'NAMOI RIVER']
DF['date'] = pd.to_datetime(DF['date'], format='%Y_%m_%d')
DF = DF.set_index('date').sort_index()
DF = DF[DF['proportion'] > 0.7]
threshold = np.nanpercentile(DF['area'], 99.5)
floods = DF[DF['area'] > threshold].index.tolist()
lagged_floods = [[n - timedelta(days=m) for m in range(lag)]
                 for n in flood_dates]
flatten = list(set([n for sublist in lagged_flood_dates for n in sublist]))
dry_dates = [n for n in DF.index.tolist() if n not in flatten]
return dry_dates

sum([len(get_flood_dates(n)) for n in basins])


te = get_flood_dates(basins[np.random.randint(len(basins), size=1)[0]], single_event=False)
get_flood_dates('GWYDIR RIVER', single_event=False)
dates = get_flood_dates('GWYDIR RIVER', single_event=True)



DF = pd.read_csv('Areass2.csv')
DF = DF[DF['catchment'] == 'NAMOI RIVER']
DF['date'] = pd.to_datetime(DF['date'], format='%Y_%m_%d')
DF = DF.set_index('date').sort_index()
DF = DF[DF['proportion'] > 0.7]
threshold = np.nanpercentile(DF['area'], 99.5)
flood_dates = DF[DF['area'] > threshold].index.tolist()
flood_dates = [datetime.fromtimestamp(datetime.timestamp(n)) for n in flood_dates]





days_before = [[n - timedelta(m) for m in range(1, 16)]
               for n in flood_dates]
flatten_days_before = [n for sublist in days_before for n in sublist]


plt.plot(MODIS.index, np.repeat(value, len(MODIS)))
plt.scatter(MODIS.index, MODIS['area'])
