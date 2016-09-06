// Volcano plot for each dataset
// Scatterplot of 

$(function () {
    $('#volcano').highcharts({
        chart: {
            type: 'scatter',
            zoomType: 'xy'
        },
        title: {
            text: 'Volcano plot'
        },
        xAxis: {
            allowDecimals : false,
            title: {
                enabled: true,
                text: 'log2(fold change)'
            }
        },
        yAxis: {
            title: {
                text: '-log10(p-value)'
            }
        },
        // legend: {
        //     layout: 'vertical',
        //     align: 'left',
        //     verticalAlign: 'top',
        //     x: 100,
        //     y: 70,
        //     floating: true,
        //     backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF',
        //     borderWidth: 1
        // },
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
                }
            }
        },
        tooltip: {
                formatter: function () {
                    // console.log(this.point.series.index);
                    // console.log({{volcano_features | safe }});
                    seriesIndex = this.point.series.index;
                    dataPointIndex = this.point.index;
                    if(seriesIndex == 0){
                        return {{ volcano_deg_features | safe }}[dataPointIndex];
                    }
                    else
                    {
                        return {{ volcano_normal_features | safe }}[dataPointIndex];
                    }
                }
            },
        series: [{
            name: 'DEGs (abosolute fold change greater than 3 and p-value < 0.05)',
            color: 'rgba(223,83,83,.5)',
            data: {{ volcano_deg_data_series }}
        }, {
            name: 'Normally expressed molecules',
            color:'rgba(119,152,191,.5)',
            data: {{ volcano_normal_data_series }}
        }]
    });

})