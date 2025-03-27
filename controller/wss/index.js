const Websocket = require("ws");
const { exec } = require('child_process');
const wss = new Websocket.Server({ port: 8081 });
console.log("Websocket server started");
var ip = null
wss.on("connection", ws => {
	console.log("connected");

	ws.on("message", data => {
		if (`${data}` == 'start') {
			if (ip == null) {
				console.error("server IP was not recived");
			}
			else {
				exec('./stream_start.sh', [ip], error => {
					if (error) {
						console.log(`${error}`);
					}
				});
			}
		}
		else if (`${data}` == 'stop') {
			exec('./stream_stop.sh', error => {
				if (error) {
					console.log(`${error}`);
				}
			});
		}
		else if (isJsonString(`${data}`)) {
			const mdata = JSON.parse(`${data}`);

			if (mdata.serverIP) {
				ip = mdata.serverIP;	//edit stream ip
			}
		}
	});


	ws.on("close", () => {
		console.log("disconnected");
	});
});

function isJsonString(str) {
	try {
		JSON.parse(str);
	} catch (e) {
		return false;
	}
	return true;
}
