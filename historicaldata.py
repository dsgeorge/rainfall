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
station='417417TP'
# Ham Island, Old Windsor: https://environment.data.gov.uk/flood-monitoring/id/stations/417417TP.html

def readOrigData(station):
    dates=[]
    totals=[]
    startdate="2021-04-01"
    enddate="2021-04-06"
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

#data=readOrigData(station)
#df=pd.DataFrame.from_dict(data)
#df.to_csv('rainfall_new.csv')
#exit()
########


df=pd.read_csv('rainfall.csv',usecols=[1,2],index_col=0,parse_dates=True)

fig,ax=plt.subplots(nrows=2,ncols=1,sharex='none',figsize=(8,6))

#df.index=df.date
title="Daily rainfall (mm) at station {}".format(station)
df.plot(kind='line',title=title, ax=ax[0])
#ax.figure.savefig('rainfall_daily.png')

#title="Average daily rainfall (mm) per week at station {}".format(station)
df.rainfall.resample('W').mean().plot(ax=ax[0])
#ax.figure.savefig('rainfall_weekm.png')

#title="Total daily rainfall (mm) per week at station {}".format(station)
#df.rainfall.resample('W').sum().plot(legend=False,title=title)
#ax.figure.savefig('rainfall_weeks.png')

#title="Average daily rainfall (mm) per month at station {}".format(station)
#df.rainfall.resample('M').mean().plot(ax=ax[0])
#ax.figure.savefig('rainfall_monthm.png')

ax[0].xaxis.set_major_locator(mdates.MonthLocator(byMonthDay=1))
ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%d-%b-%y'))
ax[0].legend(['Daily total','Mean per week'])
ax[0].grid()


# recent
title="Recent daily rainfall (mm) at station {}".format(station)
recent_start='2021-01-01'
dfr=df[recent_start:]
#dfr.plot(kind='bar',title=title, ax=ax[1],legend=False)
ax[1].bar(dfr.index,dfr['rainfall'])

#set ticks every week
ax[1].xaxis.set_major_locator(mdates.DayLocator(interval=7))
#set major ticks format
ax[1].xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
ax[1].grid(which='major')

#ticklabels = ['']*len(dfr)
##skip = len(dfr)//7
#skip=7
##ticklabels[::skip] = dfr.index[::skip].strftime('%Y-%m-%d')
#ticklabels[::skip] = dfr.index[::skip].strftime('%b-%d')
#ax[1].xaxis.set_major_formatter(mpl.ticker.FixedFormatter(ticklabels))
#fig.autofmt_xdate()

## fixes the tracker
## https://matplotlib.org/users/recipes.html
#def fmt(x, pos=0, max_i=len(ticklabels)-1):
#    i = int(x) 
#    i = 0 if i < 0 else max_i if i > max_i else i
#    return dates[i]
#ax[1].fmt_xdata = fmt


plt.tight_layout()
fig.savefig('rainfall_plot.png')

