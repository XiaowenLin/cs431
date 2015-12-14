var currentCoords = "";

var origin_x = -99;
var origin_y = -99;

var origin_prev_x = -99;
var origin_prev_y = -99;

var dest_x = -99;
var dest_y = -99;

var direction = 0;


function calculateDirection() {
    var x_offset = (orgin_x - origin_prev_x);
    var y_offset = (orgin_y - origin_prev_y);
    if (y_offset == 0 && x_offset > 0) {
        direction = 0;
    } else if (y_offset == 0 && x_offset < 0) {
        direction = 180;
    }
    direction = Math.atan(x_offset /  y_offset);

    if (x_offset < 0) {
        direction += 180.0;
    }
    direction = (direction * Math.PI) / 180.0;
}

var server = net.createServer(function(connection) {
   console.log('client connected');
   connection.on('end', function() {
      console.log('client disconnected');
   });
   connection.on('data', function(data) {
       var result = data.toString();

        for (var i = 0; i != result.length; i++) {
            if (result[i] == "\n") {
                var object = JSON.parse(currentCoords);

                if ("ox" in object) {
                    origin_x = object['ox'];
                    origin_y = object['oy'];
                    if (dest_x !== -99 && DASH.info.moving == 1 && DASH.info.auto == 1) {
                        // if (origin_prev_x != -99) {
                        //     calculateDirection();
                        // }
                        sendCommand('{"topic": "coordinates", "origin": [' + origin_x + ',' + origin_y + '], "destination": [' + dest_x + ', ' + dest_y + ']}');
                        // origin_prev_x = origin_x;
                        // origin_prev_y = origin_y;
                    }
                    updateOrigin(origin_x, origin_y);
                } else if ("dx" in object) {
                    dest_x = object['dx'];
                    dest_y = object['dy'];
                    if (origin_x !== -99 && DASH.info.moving == 1 && DASH.info.auto == 1) {
                        sendCommand('{"topic": "coordinates", "origin": [' + origin_x + ',' + origin_y + '], "destination": [' + dest_x + ', ' + dest_y + ']}');
                    }
                    updateDestination(dest_x, dest_y);
                }

                currentCoords = "";
            } else {
                currentCoords += result[i];
            }
        }
   });
});
server.listen(12347, function() {
  console.log('server is listening');
});