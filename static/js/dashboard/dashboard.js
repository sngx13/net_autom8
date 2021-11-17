google.charts.load('current', { 'packages': ['corechart'] });

function drawDeviceInventoryChart(ChartData) {
    var data = new google.visualization.DataTable(ChartData);
    var options = {
        title: 'Devices',
        colors: ['red', 'green', 'blue', 'orange', 'brown'],
        pieHole: 0.4,
        pieSliceTextStyle: {
            color: 'white',
            bold: true,
            fontSize: 8,
            fontName: 'Roboto'
        },
        tooltip: {
            text: 'value',
            textStyle: {
                color: 'black',
                bold: 1,
                fontSize: 10,
                fontName: 'Roboto'
            }
        },
        legend: {
            position: 'left',
            textStyle: {
                color: 'black',
                bold: 1,
                fontSize: 12,
                fontName: 'Roboto'
            }
        }
    };
    var chart = new google.visualization.PieChart(document.getElementById('DashboardDevicesInventory'));
    chart.draw(data, options);
};

function drawDeviceCountChart(ChartData) {
    var data = new google.visualization.DataTable(ChartData);
    var options = {
        title: 'Device Count',
        colors: ['red'],
        legend: 'none',
        pieSliceText: 'value',
        pieSliceTextStyle: {
            fontName: 'Roboto',
            fontSize: '42',
            color: 'white',
            bold: 1
        },
        tooltip: {
            text: '',
            textStyle: {
                color: 'black',
                bold: 1,
                fontSize: 10,
                fontName: 'Roboto'
            }
        }
    };
    var chart = new google.visualization.PieChart(document.getElementById('DashboardDevicesCount'));
    chart.draw(data, options);
};
