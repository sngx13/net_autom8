function drawDeviceInventoryChart(ChartData) {
    var data = new google.visualization.DataTable(ChartData);
    var options = {
        title: 'Devices',
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

function drawDeviceModelsChart(ChartData) {
    var data = new google.visualization.DataTable(ChartData);
    var options = {
        title: 'Device Models',
        legend: 'none',
        fontName: 'Roboto',
        fontSize: 12,
        bar: {
            groupWidth: '40%'
        },
        hAxis: {
            textStyle: {
                bold: true,
                italic: false
            }
        },
        vAxis: {
            textStyle: {
                fontSize: 10,
                bold: false,
                italic: true
            },
        },
    };
    var chart = new google.visualization.BarChart(document.getElementById('DashboardDeviceModels'));
    chart.draw(data, options);
};
