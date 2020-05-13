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

    if(!ctl || !grp){
        document.getElementById('msg').innerText = 'Controller and group must be set!'
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

document.getElementById('btnSetpointError').addEventListener('click', event => {
    var ctl = document.getElementById('inpController').value;
    var grp = document.getElementById('inpGroup').value;
    var se = document.getElementById('inpSetpointError').value;

    if(!ctl || !grp){
        document.getElementById('msg').innerText = 'Controller and group must be set!'
        return;
    }

    body = {controller: ctl, group: grp, setpoint_error: se};
    
    fetch(server+'api/setsetpoint_error', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(body)
    }).then(response => response.json())
    .then(data => document.getElementById('msg').innerText = data.msg); 
})

document.getElementById('btnRGB').addEventListener('click', event => {
    var ctl = document.getElementById('inpController').value;
    var grp = document.getElementById('inpGroup').value;
    var red = document.getElementById('inpRed').value;
    var green = document.getElementById('inpGreen').value;
    var blue = document.getElementById('inpBlue').value;

    if(!ctl || !grp){
        document.getElementById('msg').innerText = 'Controller and group must be set!'
        return;
    }

    body = {controller: ctl, group: grp, red: red, green: green, blue: blue};
    
    fetch(server+'api/setrgb', {
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

    var start = new Date(inpStart.value).getTime()*1000000;
    console.log('Start: ' + start)
    var end = new Date(inpEnd.value).getTime()*1000000;
    console.log('End: ' + end)

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
        data.forEach(e => e.timestamp = Math.floor(e.timestamp/1000000))
        console.log(data);
        

        document.getElementById('msg').innerText = "Data received from server.\nNumber of data points: " + labels.length

        let vlPlot = {
            $schema: "https://vega.github.io/schema/vega-lite/v4.json",
            description: "Light level and setpoint over time.",
            data: {
                values: data,
                format: {
                    parse: {
                        timestamp: "number"
                    }
                }
            },
            //"transform": [{"filter": "datum.symbol==='GOOG'"}],
            mark: "line",
            encoding: {
              x: {field: "timestamp", type: "temporal"},
              y: {field: "lux1", type: "quantitative"}
            }
        }


        vegaEmbed('#plot', vlPlot);
        
    });
})