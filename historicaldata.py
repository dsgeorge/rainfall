#!/bin/env python3
# read historical data CSVs, filter relevant station and sum total for day
# write out in json format for graphing

import pandas as pd
import matplotlib as mpl
mpl.use('Agg') # no X display
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import urllib, urllib.error
import datetime
import calmap
import numpy as np
station='417417TP'
# Ham Island, Old Windsor: https://environment.data.gov.uk/flood-monitoring/id/stations/417417TP.html

def readOrigData(station,startdate,enddate):
    dates=[]
    totals=[]
    print("Trying to fetch data for dates from",startdate,"to",enddate)
    for d in pd.date_range(startdate,enddate):
        url = "http://environment.data.gov.uk/flood-monitoring/archive/readings-{:04d}-{:02d}-{:02d}.csv".format(d.year,d.month,d.day)
        dtype={'dateTime':str, 'measure':str, 'value':object}
        try:
#            df=pd.read_csv(url,dtype=dtype,error_bad_lines=False,warn_bad_lines=True)
             df=pd.read_csv(url,dtype=dtype,on_bad_lines='warn')
        except urllib.error.HTTPError:
            print("No data for {}".format(d.date()))
            continue
    
        df['fvalue']=pd.to_numeric(df.value,errors='coerce')
        # data sanity check: should not have over 100 mm in a 15 min interval
        # according to https://en.wikipedia.org/wiki/United_Kingdom_weather_records#Rainfall 
        # the highest 5 min total in the UK is 32mm, and the highest 30 min total is 80 mm.
        max_allowed=100. 
        # values above max_allowed:
        sus=df[(df.measure.str.contains(station)) & (df.fvalue>100.)]
        if len(sus)>0:
            print("WARNING: unfeasable suspicious data value(s) skipped",sus)
        # filter out any suspicious values
        df2=df[(df.measure.str.contains(station)) & (df.fvalue<=100.)]
        total=df2.fvalue.sum()
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

import sys,shutil
if len(sys.argv)>1 and sys.argv[1]=='readnew':
    startdate=nextDay('rainfall.csv')
    enddate=str(datetime.datetime.today().date())
    data=readOrigData(station,startdate,enddate)
    df=pd.DataFrame.from_dict(data)
    shutil.copy('rainfall.csv','rainfall_old.csv')
    df.to_csv('rainfall.csv',mode='a',header=False) # append to file
    #exit()
    print("New data appended to file")
########

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()


df=pd.read_csv('rainfall.csv',usecols=[1,2],index_col=0,parse_dates=True)

#(fig,ax)=plt.subplots(nrows=3,ncols=1,sharex='none',figsize=(8,10))
(fig,ax)=plt.subplots(nrows=2,ncols=1,sharex='none',figsize=(8,7))

#df.index=df.date
#title="Daily rainfall (mm) at station {}".format(station)
#df.plot(kind='line',title=title, ax=ax[0])
#ax[0].bar(df.index,df['rainfall'],width=1.0)
#ax[0].title=title
#ax.figure.savefig('rainfall_daily.png')

#title="Average daily rainfall (mm) per week at station {}".format(station)
#df.rainfall.resample('W').mean().plot(ax=ax[0])
#ax.figure.savefig('rainfall_weekm.png')

#title="Total daily rainfall (mm) per week at station {}".format(station)
#df.rainfall.resample('W').sum().plot(legend=False,title=title)
#ax.figure.savefig('rainfall_weeks.png')

#title="Average daily rainfall (mm) per month at station {}".format(station)
#monthly=df.rainfall.resample('M').mean()
#monthly.columns=['mean']
#ax[0].plot(monthly.index,monthly.values,color='green')
#ax.figure.savefig('rainfall_monthm.png')

#ax[0].xaxis.set_major_locator(mdates.MonthLocator(bymonthday=1,interval=4))
#ax[0].xaxis.set_minor_locator(mdates.MonthLocator(bymonthday=1,interval=1))
#ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%d-%b-%y'))
#ax[0].legend(['Mean per week','Daily total'])
#ax[0].grid(axis='x',which='both')
#ax[0].grid(axis='y',which='major')
#ax[0].tick_params(axis='x', rotation=45)
#ax[0].title.set_text(title)
#ax[0].set_ylabel('mm')

def dailybar(df,title,ax):
    ax.bar(df.index,df['rainfall'])
    #set ticks every week
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonthday=1,interval=1))
    ax.xaxis.set_minor_locator(mdates.DayLocator(interval=7))
    #set major ticks format
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
    ax.grid(axis='x',which='both')
    ax.grid(axis='y',which='major')
    ax.set_xlim([min(df.index),max(df.index)])
    ax.title.set_text(title)
    ax.set_ylabel('mm')

def calmapplot(df,title,ax):
    pass

# annual cummulative overlays
def annualcumover(df,title,ax):
    dfa=df.copy(deep=True)
    dfa['year']=df.index.year
    dfa['dayofyear']=df.index.dayofyear
    table=pd.pivot_table(dfa,values=['rainfall'],index=['dayofyear'],columns=['year'])
    table.cumsum(skipna=True).plot(ax=ax,use_index=True,legend=True)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%b'))
    ax.title.set_text(title)
    ax.set_ylabel('mm')
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonthday=1,interval=1))
    ax.xaxis.set_minor_locator(mdates.DayLocator(interval=7))
    ax.grid(axis='y',which='major')
    ax.get_legend().set_title(None)

# recent daily
#title="Daily rainfall (mm) at station {}".format(station)
#halfyearago=(datetime.datetime.now()-datetime.timedelta(days=183))
#oneyearago=(halfyearago-datetime.timedelta(days=183))
#range0=u" {}\u2014{}".format(oneyearago.strftime("%d%b%Y"),(halfyearago-datetime.timedelta(days=1)).strftime("%d%b%Y"))
#range1=u" {}\u2014{}".format(halfyearago.strftime("%d%b%Y"),(max(df.index)).to_pydatetime().strftime("%d%b%Y"))
#dailybar(df[oneyearago:halfyearago],title+range0,ax[0])
#dailybar(df[halfyearago:],title+range1,ax[1])

# cumsum years overlayed
title="Annual rainfall cumulative sum (mm) at station {}".format(station)
annualcumover(df,title,ax[0])

# rain amount and dry days per month
title="Number of dry days per month at station {}".format(station)
#dfm=df.groupby(pd.Grouper(freq='M')).agg((('total','sum'),('drydays',lambda x: (x==0).sum())))
dfm=df.groupby(pd.Grouper(freq='M')).agg((('total','sum'),('drydays',lambda x: 100.0*(x==0).sum()/x.count())))
#ax[1].bar(dfm.index,dfm.rainfall.drydays)
dfm.index=dfm.index.strftime('%b/%y')
print(dfm)
dfm.plot.bar(ax=ax[1],secondary_y='drydays',width=0.8)
#ax[1].xaxis.set_major_locator(mdates.MonthLocator(bymonthday=1,interval=2))
#ax[1].xaxis.set_minor_locator(mdates.MonthLocator(bymonthday=1,interval=1))
#ax[1].xaxis.set_major_formatter(mdates.DateFormatter('%b-%y'))
ax[1].legend(['Monthly rainfall in mm','Percentage of dry days'])
ax[1].set_ylabel('mm or %')
ax[1].grid(axis='y',which='major')
ax[1].tick_params(axis='x', rotation=45)
ax[1].title.set_text(title)

plt.tight_layout()
fig.savefig('rainfall_plot.png')
print("plot updated: rainfall_plot.png")

#
#(fig,ax)=plt.subplots(nrows=8,ncols=1,sharex=True,figsize=(8,10))
#plt.matshow(ax=ax[0])

# plot frequency distribution of daily rainfall to guide choice of colormap boundaries
(fig,ax)=plt.subplots(nrows=1,ncols=1,sharex='none',figsize=(12,15))
df.rainfall.plot.hist(bins=int(df.rainfall.max()),ax=ax,logy=True)
fig.savefig('rainfall_freq.png')

# threshold in mm of rain for day to be coloured blue in calmap
threshold=5
#turn rainfall into integer, seems to work better for color mapping
dfc=df.copy(deep=True)
dfc['irainfall']=dfc.rainfall.astype(np.int64)
cmap=mpl.colors.ListedColormap(['white','blue'])
boundaries=[0,threshold,100]
norm=mpl.colors.BoundaryNorm(boundaries, cmap.N, clip=True)
norm.autoscale(boundaries)
(fig,ax)=calmap.calendarplot(dfc.irainfall,norm=norm,cmap=cmap,dayticks=[0, 2, 4, 6],yearlabel_kws={'fontsize':'xx-large','fontfamily':'sans-serif'},yearascending=False)
#plt.tight_layout()
fig.savefig('rainfall_calmap.png')
