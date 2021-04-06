#!/bin/env python3
# read historical data CSVs, filter relevant station and sum total for day
# write out in json format for graphing

#import datetime
import pandas as pd
import matplotlib.pyplot as plt
station='417417TP'


def readOrigData(station):
    dates=[]
    totals=[]
    startdate="2019-12-01"
    enddate="2021-04-01"
    for d in pd.date_range(startdate,enddate):
        url = "http://environment.data.gov.uk/flood-monitoring/archive/readings-{:04d}-{:02d}-{:02d}.csv".format(d.year,d.month,d.day)
        try:
            df=pd.read_csv(url)
        except urllib.error.HTTPError:
            print("No data for {}".format(d.date()))
            continue
    
        df2=df[df.measure.str.contains(station)]
        total=pd.to_numeric(df2.value,errors='coerce').sum()
        totals.append(total)
        dates.append(d)
    #print(d.date(),total)
    data={'date':dates,'rainfall':totals}
    return data

#data=readOrigData(station)
#df=pd.DataFrame.from_dict(data)
#df.to_csv('rainfall.csv')
########

df=pd.read_csv('rainfall.csv',usecols=[1,2],index_col=0,parse_dates=True)

#df.index=df.date
title="Daily rainfall (mm) at station {}".format(station)
ax=df.plot(legend=False,title=title)
ax.figure.savefig('rainfall_daily.png')

title="Average daily rainfall (mm) per week at station {}".format(station)
ax=df.rainfall.resample('W').mean().plot(legend=False,title=title)
ax.figure.savefig('rainfall_weekm.png')

title="Average daily rainfall (mm) per week at station {}".format(station)
ax=df.rainfall.resample('W').sum().plot(legend=False,title=title)
ax.figure.savefig('rainfall_weeks.png')

title="Average daily rainfall (mm) per month at station {}".format(station)
ax=df.rainfall.resample('M').mean().plot(legend=False,title=title)
ax.figure.savefig('rainfall_monthm.png')

