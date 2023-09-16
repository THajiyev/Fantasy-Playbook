var data = {};

const teamColors = {
    Rushing: 'blue',
    Receiving: 'orange'
};

var selectedDataType = 'TDs';
var selectedValueType = 'raw';

function updateChart() {
    const teamLabels = Object.keys(data);
    const sortedIndices = teamLabels.map((_, index) => index)
        .sort((a, b) => {
            const totalA = selectedValueType === 'percentage' ?
                (data[teamLabels[a]][selectedDataType][0] / data[teamLabels[a]][selectedDataType][1]) * 100 :
                data[teamLabels[a]][selectedDataType][0] + data[teamLabels[a]][selectedDataType][1];
            const totalB = selectedValueType === 'percentage' ?
                (data[teamLabels[b]][selectedDataType][0] / data[teamLabels[b]][selectedDataType][1]) * 100 :
                data[teamLabels[b]][selectedDataType][0] + data[teamLabels[b]][selectedDataType][1];
            return totalA - totalB;
        });

    var selectedTeamData = sortedIndices.map(index => {
        const team = teamLabels[index];
        const selectedDataTypeValues = data[team][selectedDataType];
        const sumOfValues = data[team][selectedDataType][0] + data[team][selectedDataType][1];
        const value = selectedValueType === 'percentage' ?
            (selectedDataTypeValues[0] / sumOfValues) * 100 :
            selectedDataTypeValues[0];
        const opposingValue = selectedValueType === 'percentage' ?
            (selectedDataTypeValues[1] / sumOfValues) * 100 :
            selectedDataTypeValues[1];
        if (value+opposingValue>0){
            return {
                x: [value, opposingValue],
                y: [team + "  ", team + "  "],
                type: 'bar',
                orientation: 'h',
                marker: {
                    color: [teamColors.Rushing, teamColors.Receiving]
                },
                text: [
                    roundUp(value, 2) + (selectedValueType === 'percentage' ? '%' : ''),
                    roundUp(opposingValue, 2) + (selectedValueType === 'percentage' ? '%' : '')
                ],
                textposition: 'inside',
                hoverinfo: 'none'
            };
        }
    });

    selectedTeamData = selectedTeamData.filter(item => item !== null && item !== undefined);

    const layout = {
        barmode: 'stack',
        showlegend: false,
        xaxis: {
            title: selectedDataType + (selectedValueType === 'percentage' ? ' (%)' : ''),
            rangemode: 'tozero',
            tickangle: -45,
            tickfont: {
                size: 14
            }
        },
        yaxis: {
            showticklabels: true,
            titlefont: {
                size: 16
            },
            tickfont: {
                size: 14,
            }
        },
        margin: {
            l: 150,
            r: 50,
            t: 80
        },
        height: 1200,
        width: window.innerWidth * .75,
        autosize: false,
    };

    const config = {
        responsive: true
    };

    Plotly.newPlot('barChart', selectedTeamData, layout, config);
}

document.getElementById('dataType').addEventListener('change', function() {
    selectedDataType = this.value;
    updateChart();
});

document.getElementById('valueType').addEventListener('change', function() {
    selectedValueType = this.value;
    updateChart();
});

document.addEventListener("DOMContentLoaded", function() {
    fetch_data('offense_comparison').then((data_json) => {
            data = data_json.data;
            updateChart();
        })
    .catch((error) => {
        console.error('Error:', error);
    });
})