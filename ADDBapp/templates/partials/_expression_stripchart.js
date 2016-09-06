$(function () {
    $('#stripchart').highcharts({
        chart: {
            type: 'scatter',
            zoomType: 'xy'
        },
        title: {
            text: 'Strip chart of all features'
        },
        // subtitle: {
        //     text: 'Strip chart of AD'
        // },
        xAxis: {
            allowDecimals : false,
            title: {
                enabled: true,
                text: 'Queried features'
            },
            labels:{
                formatter: function() {
                    var returnedString = {{ feature_list | safe }}[Math.floor(this.value / 2)];
                    return returnedString;
                }
            }
            // startOnTick: true,
            // endOnTick: true,
            // showLastLabel: true
        },
        yAxis: {
            title: {
                text: 'Expression level'
            }
        },
        legend: {
            layout: 'vertical',
            align: 'left',
            verticalAlign: 'top',
            x: 100,
            y: 70,
            floating: true,
            backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF',
            borderWidth: 1
        },
        plotOptions: {
            scatter: {
                marker: {
                    radius: 5,
                    states: {
                        hover: {
                            enabled: true,
                            lineColor: 'rgb(100,100,100)'
                        }
                    }
                },
                states: {
                    hover: {
                        marker: {
                            enabled: false
                        }
                    }
                },
                // tooltip: {
                //     headerFormat: '<b>{series.name}</b><br>',
                //     pointFormat: '{point.x} cm, {point.y} kg'
                // }
            }
        },
        series: [{
            name: '{{ state_1_name }}',
            color: 'rgba(223, 83, 83, .5)',
            data: {{ state_1_data_series }}

        }, {
            name: '{{ state_0_name }}',
            color: 'rgba(119, 152, 191, .5)',
            data: {{ state_0_data_series }}
        }]
    });

})