fetch('https://environment.data.gov.uk/flood-monitoring/id/stations/417417TP/readings.json?parameter=rainfall&today&_limit=1000')
        .then(function (response) {
                return response.text();
        })
        .then(function (text) {
                let series = text;
                //console.log(series.items);
                renderChart(series.items);
        })
        .catch(function (error) {
                //Something went wrong
                console.log(error);
        });


function renderChart(series) {
    JSC.Chart('chartDiv', {
	type: "line",
        series: series,
	parsing: {
	    xAxisKey: 'dateTime',
	    yAxiskey: 'value'
	},
	xAxis_scale_type: "time",
    });
}
