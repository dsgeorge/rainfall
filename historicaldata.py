#!/bin/env python3
# read historical data CSVs, filter relevant station and sum total for day
# write out in json format for graphing

#import datetime
import pandas as pd
import matplotlib as mpl
mpl.use('Agg') # no X display
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import urllib
import datetime
station='417417TP'
# Ham Island, Old Windsor: https://environment.data.gov.uk/flood-monitoring/id/stations/417417TP.html

def readOrigData(station,startdate,enddate):
    dates=[]
    totals=[]
    print("Trying to fetchg data for dates from",startdate,"to",enddate)
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
        print(d.date(),total)
    data={'date':dates,'rainfall':totals}
    return data

# read last line of file and work out the next day for a new data download
def nextDay(filename):
    with open(filename) as f:
        for line in f:
            pass
        lastLine = line
    lastDate=lastLine.split(',')[1]
    theNextDay=pd.to_datetime(lastDate)+datetime.timedelta(days=1)
    return str(theNextDay)

import sys
if len(sys.argv)>1 and sys.argv[1]=='readnew':
    startdate=nextDay('rainfall.csv')
    enddate=str(datetime.datetime.today().date())
    data=readOrigData(station,startdate,enddate)
    df=pd.DataFrame.from_dict(data)
    df.to_csv('rainfall_new.csv')
    exit()
########

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()


df=pd.read_csv('rainfall.csv',usecols=[1,2],index_col=0,parse_dates=True)

(fig,ax)=plt.subplots(nrows=3,ncols=1,sharex='none',figsize=(8,9))

#df.index=df.date
title="Daily rainfall (mm) at station {}".format(station)
#df.plot(kind='line',title=title, ax=ax[0])
ax[0].bar(df.index,df['rainfall'],width=1.0)
#ax[0].title=title
#ax.figure.savefig('rainfall_daily.png')

#title="Average daily rainfall (mm) per week at station {}".format(station)
#df.rainfall.resample('W').mean().plot(ax=ax[0])
#ax.figure.savefig('rainfall_weekm.png')

#title="Total daily rainfall (mm) per week at station {}".format(station)
#df.rainfall.resample('W').sum().plot(legend=False,title=title)
#ax.figure.savefig('rainfall_weeks.png')

#title="Average daily rainfall (mm) per month at station {}".format(station)
monthly=df.rainfall.resample('M').mean()
monthly.columns=['mean']
ax[0].plot(monthly.index,monthly.values,color='green')
#ax.figure.savefig('rainfall_monthm.png')

ax[0].xaxis.set_major_locator(mdates.MonthLocator(bymonthday=1,interval=2))
ax[0].xaxis.set_minor_locator(mdates.MonthLocator(bymonthday=1,interval=1))
ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%d-%b-%y'))
ax[0].legend(['Mean per week','Daily total'])
ax[0].grid(axis='x',which='both')
ax[0].grid(axis='y',which='major')
ax[0].tick_params(axis='x', rotation=45)
ax[0].title.set_text(title)
ax[0].set_ylabel('mm')

# recent
title="Recent daily rainfall (mm) at station {}".format(station)
recent_start='2021-01-01'
dfr=df[recent_start:]
#dfr.plot(kind='bar',title=title, ax=ax[1],legend=False)
ax[1].bar(dfr.index,dfr['rainfall'])

#set ticks every week
ax[1].xaxis.set_major_locator(mdates.DayLocator(interval=14))
ax[1].xaxis.set_minor_locator(mdates.DayLocator(interval=7))
#set major ticks format
ax[1].xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
ax[1].grid(axis='x',which='both')
ax[1].grid(axis='y',which='major')
ax[1].set_xlim([min(dfr.index),max(dfr.index)])
ax[1].title.set_text(title)
ax[1].set_ylabel('mm')

# dry days per month
title="Number of dry days per month at station {}".format(station)
#dfm=df.groupby(pd.Grouper(freq='M')).agg((('total','sum'),('drydays',lambda x: (x==0).sum())))
dfm=df.groupby(pd.Grouper(freq='M')).agg((('total','sum'),('drydays',lambda x: 100.0*(x==0).sum()/x.count())))
#ax[2].bar(dfm.index,dfm.rainfall.drydays)
dfm.index=dfm.index.strftime('%b-%y')
dfm.plot.bar(ax=ax[2],secondary_y='drydays',width=0.8)
#ax[2].xaxis.set_major_locator(mdates.MonthLocator(bymonthday=1,interval=2))
#ax[2].xaxis.set_minor_locator(mdates.MonthLocator(bymonthday=1,interval=1))
#ax[2].xaxis.set_major_formatter(mdates.DateFormatter('%b-%y'))
ax[2].legend(['Monthly rainfall in mm','Percentage of dry days'])
ax[2].set_ylabel('mm or %')
ax[2].grid(axis='y',which='major')
ax[2].tick_params(axis='x', rotation=45)
ax[2].title.set_text(title)

plt.tight_layout()
fig.savefig('rainfall_plot.png')

