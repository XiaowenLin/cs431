var hostIp = '172.17.235.66'
var currentImage = "";
var currentTtc = "";

/* IMAGE SERVER CONNECTION */

DASH.info.imageConnection = net.connect({port: 11111, host: hostIp}, function() {
   console.log('connected to image server');
});
DASH.info.imageConnection.on('data', function(data) {

    var result = data.toString();

    for (var i = 0; i != result.length; i++) {
        if (result[i] == "\n") {
            document.getElementById("imageDisplay").src = "data:image/jpeg;base64," + currentImage;
            currentImage = "";
        } else {
            currentImage += result[i];
        }
    }
});
DASH.info.imageConnection.on('end', function() {
   console.log('disconnected from image server');
});

function round_value(value) {
    if (value == 'Infinity') {
        return value;
    }
    return value.toFixed(1);
}


/* TTC SERVER CONNECTION */

DASH.info.ttcConnection = net.connect({port: 22222, host: hostIp}, function() {
   console.log('connected to ttc server');
});
DASH.info.ttcConnection.on('data', function(data) {

    var result = data.toString();

    for (var i = 0; i != result.length; i++) {
        if (result[i] == "\n") {
            var object = JSON.parse(currentTtc);
            var min = round_value(object['min-ttc']);
            var right = round_value(object['right-ttc']);
            var left = round_value(object['left-ttc']);
            updateTtc(min, right, left);
            currentTtc = "";
        } else {
            currentTtc += result[i];
        }
    }
});
DASH.info.imageConnection.on('end', function() {
   console.log('disconnected from ttc server');
});