var net = require("net");

var DASH = DASH || {};

DASH.info = new Info();

function Info() {
    this.imageConnection;
    this.ttcConnection;
    this.commandConnection;
    this.lastAngle = 0;
    this.direction = 0;
    this.moving = 0;
    this.auto = 1;
    this.x_dest = 0;
    this.y_dest = 0;
}


function sendCommand(commandString) {
    DASH.info.commandConnection = net.connect({port: 12346, host: hostIp}, function() {
        console.log('connected to command server');
    });
    DASH.info.commandConnection.on('data', function(data) {
    });
    DASH.info.commandConnection.on('end', function() {
       console.log('disconnected from image server');
    });
    DASH.info.commandConnection.write(commandString);
    DASH.info.commandConnection.pipe(DASH.info.commandConnection);
    DASH.info.commandConnection.end();
}


function highlightDirection() {
    var direction = DASH.info.direction;

    if (DASH.info.direction === -1) {
        $( "#forward" ).css("color", "#555");
        $( "#back" ).css("color", "#56a856");
    }

    if (DASH.info.direction === 1) {
        $( "#back" ).css("color", "#555");
        $( "#forward" ).css("color", "#56a856");
    }

    if (DASH.info.direction === 0) {
        $( "#back" ).css("color", "#555");
        $( "#forward" ).css("color", "#555");
    }
}


function updateOrigin(x, y) {
    $('#orig').text("Origin ( x:" + x + ", y: " + y + ")");
}

function updateDestination(x, y) {
    $('#dest').text("Destination ( x:" + x + ", y: " + y + ")");
}

function updateTtc(min, right, left) {
    $('#ttc').text("TTC ( min: " + min + ", left: " + left + ", right: " + right + ")");
}

toggleAuto();


function toggleAuto() {
    if($('#auto').is(':checked')){
        DASH.info.auto = 1;

        $("#switch_0").prop('disabled', true);
        $("#switch_1").prop('disabled', true);
        $("#switch_2").prop('disabled', true);
        $("#switch_3").prop('disabled', true);
        $("#switch_4").prop('disabled', true);
        $("#switch_5").prop('disabled', true);
        $("#switch_6").prop('disabled', true);
        $("#switch_7").prop('disabled', true);

    } else {
        DASH.info.auto = 0;

        $("#switch_0").prop('disabled', false);
        $("#switch_1").prop('disabled', false);
        $("#switch_2").prop('disabled', false);
        $("#switch_3").prop('disabled', false);
        $("#switch_4").prop('disabled', false);
        $("#switch_5").prop('disabled', false);
        $("#switch_6").prop('disabled', false);
        $("#switch_7").prop('disabled', false);
    }
}


/******************* TOGGLE AUTO ***************/

$('#auto').change(function(){
    toggleAuto();
});

var timerForward;
var timerBack;
/******************* DIRECTION *****************/

$('#forward').mousedown(function(){
    if (!DASH.info.moving || DASH.info.auto) return;
    DASH.info.direction = 1;
    highlightDirection();
    sendCommand('{"topic": "forward"}');
});

$('#forward').mouseup(function(){
    if (!DASH.info.moving || DASH.info.auto) return;
    DASH.info.direction = 0;
    highlightDirection();
    sendCommand('{"topic": "stop"}');
});


$('#back').mousedown(function(){
    if (!DASH.info.moving || DASH.info.auto) return;
    DASH.info.direction = -1;
    highlightDirection();
    sendCommand('{"topic": "backward"}');
});

$('#back').mouseup(function(){
    if (!DASH.info.moving || DASH.info.auto) return;
    DASH.info.direction = 0;
    highlightDirection();
    sendCommand('{"topic": "stop"}');
});



/******************* STOP/GO *******************/

$('#move').click(function(){
    if (!DASH.info.moving) {
        $( "#move" ).attr( "class", "fa fa-pause fa-3x" );
        DASH.info.moving = 1;
    } else {
        $( "#move" ).attr( "class", "fa fa-play fa-3x" );
        DASH.info.moving = 0;
        DASH.info.direction = 0;
        sendCommand('{"topic": "stop"}');
    }
    highlightDirection();
});




/****************** ANGLE ***********************/

$('#switch_0').change(function(){
  if (!DASH.info.moving || DASH.info.auto) return;
  if($(this).is(':checked')){
    var angle = $("label[for='switch_0']").text();
    var rotation = angle * -1;
    DASH.info.lastAngle = angle;
    sendCommand('{"topic": "angle", "turn": "' + rotation + '"}');
  }
});

$('#switch_1').change(function(){
  if (!DASH.info.moving || DASH.info.auto) return;
  if($(this).is(':checked')){
    var angle = $("label[for='switch_1']").text();
    var rotation = angle * -1;
    DASH.info.lastAngle = angle;
    sendCommand('{"topic": "angle", "turn": "' + rotation + '"}');
  }
});

$('#switch_2').change(function(){
  if (!DASH.info.moving || DASH.info.auto) return;
  if($(this).is(':checked')){
    var angle = $("label[for='switch_2']").text();
    var rotation = angle * -1;
    DASH.info.lastAngle = angle;
    sendCommand('{"topic": "angle", "turn": "' + rotation + '"}');
  }
});

$('#switch_3').change(function(){
  if (!DASH.info.moving || DASH.info.auto) return;
  if($(this).is(':checked')){
    var angle = $("label[for='switch_3']").text();
    var rotation = angle * -1;
    DASH.info.lastAngle = angle;
    sendCommand('{"topic": "angle", "turn": "' + rotation + '"}');
  }
});

$('#switch_4').change(function(){
  if (!DASH.info.moving || DASH.info.auto) return;
  if($(this).is(':checked')){
    var angle = $("label[for='switch_4']").text();
    var rotation = angle * -1;
    DASH.info.lastAngle = angle;
    sendCommand('{"topic": "angle", "turn": "' + rotation + '"}');
  }
});

$('#switch_5').change(function(){
  if (!DASH.info.moving || DASH.info.auto) return;
  if($(this).is(':checked')){
    var angle = $("label[for='switch_5']").text();
    var rotation = angle * -1;
    DASH.info.lastAngle = angle;
    sendCommand('{"topic": "angle", "turn": "' + rotation + '"}');
  }
});

$('#switch_6').change(function(){
  if (!DASH.info.moving || DASH.info.auto) return;
  if($(this).is(':checked')){
    var angle = $("label[for='switch_6']").text();
    var rotation = angle * -1;
    DASH.info.lastAngle = angle;
    sendCommand('{"topic": "angle", "turn": "' + rotation + '"}');
  }
});

$('#switch_7').change(function(){
  if (!DASH.info.moving || DASH.info.auto) return;
  if($(this).is(':checked')){
    var angle = $("label[for='switch_7']").text();
    var rotation = angle * -1;
    DASH.info.lastAngle = angle;
    sendCommand('{"topic": "angle", "turn": "' + rotation + '"}');
  }
});