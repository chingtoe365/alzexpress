// expects:
// graph_labels
// graph_datasets

// modifies:
// #heatmap-chart
// #chart-legend
{% load dictionary_extras %}

$(function () {
    {% for dataset in dataset_names %}
        var dataset_name = "{{ dataset }}";
        var canvas_id_name = "heatmap-chart-" + dataset_name;
        // alert(canvas_id_name);
        var element = document.getElementById(canvas_id_name);
	    $('#test').highcharts({
	        chart: {
	            type: 'heatmap',
	            // marginTop: 40,
	            // marginBottom: 40
	        },


	        title: {
	            text: 'Expression levels displayed in heatmap'
	        },

	        xAxis: {
	            // Period
	            // categories: ['Alexander', 'Marie', 'Maximilian']
	            gridLineColor : 'white',
	            gridLineWidth : 0,
	            minorGridLineWidth: 0,
	            categories : {{ sample_state_list | access:dataset | safe}}
	        },

	        yAxis: {
	            // Partner country names
	            // categories: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
	            // categories: ['Monday', 'Tuesday', 'Wednesday'],
	            gridLineWidth : 0,
	            minorGridLineWidth: 0,
	            categories : {{ feature_list | access:dataset | safe }},
	            title: null
	        },

	        // colors:['rgba(102,0,102,0.1)', 'rgba(102,0,102,0.8)'],
	        
	        colorAxis: {
	            min: 0,
	            minColor: '#FFFFFF',
	            maxColor: Highcharts.getOptions().colors[0]
	        },

	        legend: {
	            align: 'right',
	            layout: 'vertical',
	            margin: 0,
	            verticalAlign: 'top',
	            y: 25,
	            // symbolHeight: 320
	            symbolHeight: 15
	        },

	        tooltip: {
	            formatter: function () {
	                // return '<b>' + this.series.xAxis.categories[this.point.x] + '</b> sold <br><b>' +
	                //     this.point.value + '</b> items on <br><b>' + this.series.yAxis.categories[this.point.y] + '</b>';
	                // return '<b>' + this.series.xAxis.categories[this.point.x] + '</b><br>' +
	                //     '</b> Volatility > 20% <br><b>' + 'with <b>' + this.series.yAxis.categories[this.point.y] + '</b>'; 
	                return '<b>' + this.series.xAxis.categories[this.point.x] + '</b><br>' 
	                        + '</b>Flag : ' + this.point.value + '<br><b>'
	                        + 'with <b>' + this.series.yAxis.categories[this.point.y] + '</b>';

	            }
	        },

	        series: [{
	            name: 'Sales per employee',
	            borderColor: 'rgba(129,129,129,1)',
	            borderWidth: 0,
	            data : {{ heatmap_datasets | access:dataset }},
	            dataLabels: {
	                enabled: false,
	                color: 'black',
	                style: {
	                    textShadow: 'none'
	                }
	            },
	            states:{
	                hover : {
	                    color: 'black',
	                    borderWidth : 1
	                }
	            }
	        }]

	    });
    {% endfor %}
    
});