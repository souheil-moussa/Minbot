const Websocket = require("ws");
const { exec } = require('child_process');
const wss = new Websocket.Server({ port: 8081 });
console.log("Websocket server started");
wss.on("connection", ws => {
	console.log("connected");

	ws.on("message", data => {
		if (`${data}` == 'start') {
			exec('./stream_start.sh', error => {
				if (error) {
					console.log(`${error}`);
				}
			});
		}
		else if (`${data}` == 'stop') {
			exec('./stream_stop.sh', error => {
				if (error) {
					console.log(`${error}`);
				}
			});
		}
	});


	ws.on("close", () => {
		console.log("disconnected");
	});
});


