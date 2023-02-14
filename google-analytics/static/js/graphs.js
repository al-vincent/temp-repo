"use strict";

function main() {
    // Data setup
    const labels = [
		'January',
		'February',
		'March',
		'April',
		'May',
		'June',
		'July',
		'August',
		'September',
		'October',
		'November',
		'December'
	];

    const data = {
        labels: labels,
        datasets: [        
            {
                label: 'Dataset 1',
                data: [80, 40, -10, 20, -40, -25, 10, -15, -45, -63, -21, 30],
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.5)'
            },
            {
                label: 'Dataset 2',
                data: [23, 44, -67, 10, -30, -25, -60, 40, 71, 52, 20, -10],
                borderColor: 'rgb(54, 162, 235)',
                backgroundColor: 'rgba(54, 162, 235, 0.5)'
            }
        ]
    };

    // Config setup
    const config = {
        type: 'bar',
        data: data,
        options: {
            responsive: true,
            plugins: {
                legend: {
                position: 'top',
                },
                title: {
                display: true,
                text: 'A Random Bar Chart'
                }
            }
        },
    };

    const myChart = new Chart(
        document.getElementById('id-graph-bar'),
        config
    );
}

document.onload = main();

let myChart = document.getElementById("id-graph-bar");
myChart.addEventListener("click", function(){
    // simple debug message
    console.log("chart object clicked");

    // send the Google analytics event message (maybe...)
    gtag("event", "chart_clicked", {
        "event_category": "engagement",
        "event_label": "content_type"
    });
});