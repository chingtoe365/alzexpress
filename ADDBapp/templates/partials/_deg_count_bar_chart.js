// expects:
// graph_labels
// graph_datasets

// modifies:
// #line-chart
// #chart-legend


$(function() {
    // var canvas_id_name = "bar-chart";
    // var legend_id_name = "chart-legend";
    // var element = document.getElementById(canvas_id_name);
    element = $('#barchart');
    console.log(element);
    element.highcharts({
        chart: {
            type: 'column'
        },

        title:{
            text: 'DEG & Unique feature number accross different groups'
        },
        
        xAxis: {
            categories: {{ collection_names | safe}}
        },

        yAxis:{
            // labels:{
            //     formatter : function(){
            //         return this.value * 100 + '%'
            //     }
            // },
            title:{
                text: 'Number'
            }
        },

        colors : ['rgba(0, 205, 0, 0.2)', 'rgba(0, 0, 205, 0.2)'],

        plotOptions: {
            series: {
                minPointLength: 3
            }
        },
        
        credits: {
            enabled: false
        },
        
        legend: {
            title: {
                // text: '',
                style: {
                    color: (Highcharts.theme && Highcharts.theme.textColor) || 'black'
                }
            },
            align: 'right',
            verticalAlign: 'top',
            // floating: true,
            layout: 'vertical',
            valueDecimals: 0,
            backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || 'rgba(255, 255, 255, 0.85)',
            symbolRadius: 0,
            symbolHeight: 14
        },
        
        // tooltip: {
        //     pointFormatter: function() {
        //         return this.series.name + ': <b>' + this.y * 100 + '%</b><br/>';
        //     },
        //     // shared: true
        // },

        series: [

            {
                data : {{ common_deg_number_list }},
                name : 'DEG number'
            }, {
                data : {{ unique_symbol_num_list }},
                name : 'Unique feature number'
            }

        ]
    });
});