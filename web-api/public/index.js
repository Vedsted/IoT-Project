var ctx = document.getElementById('myChart')//.getContext('2d');

function getServerAddress(){
    var url = window.location.href
    var arr = url.split("/");
    return arr[0] + "//" + arr[2] + '/'
}

var server = getServerAddress();

/**
 * Set setpoint.
 * Sends controller name and setpoint
 */
document.getElementById('btnSetpoint').addEventListener('click', event => {
    var ctl = document.getElementById('inpController').value;
    var grp = document.getElementById('inpGroup').value;
    var sp = document.getElementById('inpSetpoint').value;

    if(!ctl || !sp){
        document.getElementById('msg').innerText = 'Controller and setpoint must be set!'
        return;
    }

    body = {controller: ctl, group: grp, setpoint: sp};
    
    fetch(server+'api/setsetpoint', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(body)
    }).then(response => response.json())
    .then(data => document.getElementById('msg').innerText = data.msg); 
})

document.getElementById('btnPlot').addEventListener('click', event => {

    var inpStart = document.getElementById('inpStart');
    var inpEnd = document.getElementById('inpEnd');
    var ctl = document.getElementById('inpController').value;
    var grp = document.getElementById('inpGroup').value;

    var start = new Date(inpStart.value).getTime() / 1000;
    var end = new Date(inpEnd.value).getTime() / 1000;

    body = {
        controller: ctl,
        group: grp,
        start: start,
        end: end
    }
    
    fetch(server+'api/data', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(body)
    }).then(response => response.json())
    .then(data => {
        
        let labels = data.map(e => e.timestamp);
        let lux1 = data.map(e => e.lux1);
        let lux2 = data.map(e => e.lux2);
        let setpoints = data.map(e => e.setpoint);

        document.getElementById('msg').innerText = "Data received from server.\nNumber of data points: " + labels.length

        var myChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        data: lux1,
                        label: 'Lux 1',
                        borderColor: 'rgb(255, 99, 132)',
                        fill: false
                    },
                    {
                        data: lux2,
                        label: 'Lux 2',
                        borderColor: 'rgb(51, 255, 87)',
                        fill: false
                    },
                    {
                        data: setpoints,
                        label: 'Setpoint',
                        borderColor: 'rgb(50, 50, 50)',
                        fill: false,
                        borderDash: [10,5]
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                title: {
                  display: true,
                  text: 'Daylight Harvesting'
                },
                scales: {
					xAxes: [{
						display: true,
						scaleLabel: {
							display: true,
							labelString: 'Time'
						}
					}],
					yAxes: [{
						display: true,
						scaleLabel: {
							display: true,
							labelString: 'Lux'
						}
					}]
				}
            }
        });
        
    });
})