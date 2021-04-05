fetch('https://environment.data.gov.uk/flood-monitoring/id/stations/417417TP/readings.json?parameter=rainfall&today&_limit=10000')
        .then(function (response) {
                return response.json();
        })
        .then(function (json) {
            let series = processData(json);
            //console.log(series);
            renderChart(series);
        })
        .catch(function (error) {
            //Something went wrong
            console.log(error);
        });

function processData(json) {
    let data = [];
    console.log(json);
    json.items.forEach(function (row) {
        //add either to Black, White arrays, or discard.
        data.push({x: row.dateTime, y: row.value});
    });
    console.log(data);
    return [
        {name: 'rainfall(mm)', points: data},
    ];
}

    
function renderChart(series) {
    JSC.Chart('chartDiv', {
	type: "line",
        series: series,
	//parsing: {
	//    xAxisKey: 'dateTime',
	//    yAxiskey: 'value'
	//},
	xAxis_scale_type: "time",
    });
}
