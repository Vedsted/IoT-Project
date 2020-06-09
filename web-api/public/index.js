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
    var color = document.getElementById('inpColor').value;

    if(!ctl || !grp){
        document.getElementById('msg').innerText = 'Controller and group must be set!'
        return;
    }

    // clean up hex color string and parse to ints -> [r,g,b]
    color = color.match(/[A-Za-z0-9]{2}/g);
    color = color.map(i => parseInt(i, 16));
    
    body = {controller: ctl, group: grp, red: color[0], green: color[1], blue: color[2]};
    
    fetch(server+'api/setrgb', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(body)
    }).then(response => response.json())
    .then(data => document.getElementById('msg').innerText = data.msg); 
})


document.getElementById('btnPlot').addEventListener('click', event => {
    document.getElementById('btnPlot').disabled = true

    var inpStart = document.getElementById('inpStart');
    var inpEnd = document.getElementById('inpEnd');
    var ctl = document.getElementById('inpController').value;
    var grp = document.getElementById('inpGroup').value;

    var start = new Date(inpStart.value).getTime()*1000000;
    var end = new Date(inpEnd.value).getTime()*1000000;

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
    
        document.getElementById('msg').innerText = "Data received from server.\nNumber of data points: " + data.length

        if (data.length == 0) {
            document.getElementById('btnPlot').disabled = false
            return
        }

        // data = [{timestamp, lux_formula_value, setpoint, light_red},....]

        plotData = data.map(e => { 
            return {
                timestamp : parseInt(e.timestamp) / 1000000,
                intensity : e.light_red,
                luxError : (e.lux_formula_value - e.setpoint)
            };
        })

        

        let vlPlot = {
            $schema: "https://vega.github.io/schema/vega-lite/v4.json",
            description: "Light level and setpoint over time.",
            width: 400,
            height: 400,
            data: {
                values: plotData,
            },
            mark: "line",
            layer: [
                {
                  mark: {type: "line", color: "#85C5A6"},
                  encoding: {
                    y: {
                      field: "luxError",
                      type: "quantitative",
                      axis: {title: "Lux Level", titleColor: "#85C5A6"}
                    }
                  }
                },
                {
                  mark: {color: "#FF1010", type: "line"},
                  encoding: {
                    y: {
                      field: "intensity",
                      type: "quantitative",
                      axis: {title: "Intensity", titleColor:"#FF1010", scale: {domain: [0, 255]}}
                    }
                  }
                }
              ],
            encoding: {
              x: {field: "timestamp", type: "temporal"},
            },
            resolve: {scale: {y: "independent"}}
            
        }


        vegaEmbed('#plot', vlPlot);
        document.getElementById('btnPlot').disabled = false
    });
})