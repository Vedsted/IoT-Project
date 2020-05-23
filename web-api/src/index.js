const express = require('express');
const path = require('path')
const mysql = require('mysql')
const bodyParser = require('body-parser');
const mqtt = require('mqtt')
const config = require('../config')

/*****************************
 *  Configure Express server *
 ****************************/
const app = express();
app.use(bodyParser());
app.use('/public', express.static(path.join(__dirname, '../public')));


/********************************
 * Set up connection to MariaDB *
 *******************************/
var con = null;
sqlOptions = {
    host: config.db.host,
    user: config.db.user,
    password: config.db.pass,
    database: config.db.database,
};

function connectToDB(){
    con = mysql.createConnection(sqlOptions);
    con.connect(function(err) {
        if (err) throw err;
        console.log("Connected to db!");
    });
}

/************************************
 * Set up connection to MQTT Broker *
 ************************************/
let host = config.mqtt.host;
let port = config.mqtt.port;
var client  = mqtt.connect('mqtt://'+host+':'+port)
client.on('connect', ()=> console.log('Broker connection established!'))

/****************************
 * Set available end points *
 ****************************/

/**
 * Main entry
 */
app.get('/', function (req, res) {
    res.sendFile(path.join(__dirname, '../public/index.html'));
});

/**
 * Get all measures.
 * Used for test and debugging
 */
app.get('/api/all', function (req, res) {
    connectToDB(); // connection times out. new connection is created when needed.
    con.query('SELECT * FROM Measurements', function (err, result) {
        if (err) throw err;
        res.send(result)
        con.end();
    });
});

/**
 * Set setpoint method for remote controlling light harvesting remotely
 */
app.post('/api/setsetpoint', function (req, res) {
    console.log('Incomming requset on: \'/api/setsetpoint\' for controller: ' + req.body.controller)

    let controller = req.body.controller;
    let group = req.body.group;
    let setpoint = req.body.setpoint;

    let o = {controller: controller,group: group,setpoint: setpoint};

    let topic = 'remote/' + controller + '/' + group + '/setpoint';
    client.publish(topic, JSON.stringify(o))

    let msgSetpoint = {msg: 'Setpoint sent successfully!'};
    res.send(JSON.stringify(msgSetpoint));
});

/**
 * Set RGB method for remote controlling light harvesting remotely
 */
app.post('/api/setrgb', function (req, res) {
    console.log('Incomming requset on: \'/api/rgb\' for controller: ' + req.body.controller)

    let controller = req.body.controller;
    let group = req.body.group;
    let red = req.body.red;
    let green = req.body.green;
    let blue = req.body.blue;

    let o = {controller: controller,group: group,red: red, green: green, blue: blue};

    let topic = 'remote/' + controller + '/' + group + '/rgb';
    client.publish(topic, JSON.stringify(o))

    let msgSetpoint = {msg: 'New RGB sent successfully!'};
    res.send(JSON.stringify(msgSetpoint));
});

/**
 * Set setpoint_error method for remote controlling light harvesting remotely
 */
app.post('/api/setsetpoint_error', function (req, res) {
    console.log('Incomming requset on: \'/api/setpoint_error\' for controller: ' + req.body.controller)

    let controller = req.body.controller;
    let group = req.body.group;
    let setpoint_error = req.body.setpoint_error;

    let o = {controller: controller,group: group,setpoint_error: setpoint_error};

    let topic = 'remote/' + controller + '/' + group + '/setpoint_error';
    client.publish(topic, JSON.stringify(o))

    let msgSetpoint = {msg: 'New setpoint error sent successfully!'};
    res.send(JSON.stringify(msgSetpoint));
});

/**
 * Retrieve data from a group in a given time period
 */
app.post('/api/data', function (req, res) {
    console.log('Incomming requset on: \'/api/data\' for controller: ' + req.body.group)
    
    let group = req.body.group;
    let start = req.body.start;
    let end = req.body.end;

    connectToDB(); // connection times out. new connection is created when needed.
    let sql = 'SELECT timestamp, lux_formula_value, setpoint, light_red FROM Measurements WHERE group_id = ? AND timestamp > ? AND timestamp < ?;'
    let values = [group, start, end]
    con.query(sql, values, function (err, result) {
        if (err) throw err;
        res.send(result)
        con.end();
    });
});


/**
 * Start server
 */
app.listen(3000, function () {
    console.log('Example app listening on port 3000!');
});