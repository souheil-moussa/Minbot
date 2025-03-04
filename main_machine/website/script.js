function connect() {
	const ws = new WebSocket('ws://192.168.1.15:8081');
	var stream_status = false

	ws.onerror = (event) => {
		document.getElementById('wss').innerHTML = "Ws server: Disconnected "
		console.log(`${event.data}`)
		setTimeout(connect, 5000)
	}

	ws.onopen = () => {
		document.getElementById('wss').innerHTML = "Ws server: Connected "
		console.log('Connected to WebSocket server');

	};

	ws.onmessage = (event) => {
		console.log(`Server: ${event.data}`);
	};
	ws.onclose = () => {
		document.getElementById('wss').innerHTML = "Ws server: Disconnected "
		setTimeout(connect, 5000)

	}


	document.getElementById('start').addEventListener('click', () => {
		if (stream_status) {
			ws.send('stop');
			stream_status = false;
			document.getElementById("start").innerHTML = "Start Stream"
		}
		else {
			ws.send('start');
			stream_status = true;
			document.getElementById("start").innerHTML = "Stop Stream"
		}
	});
}
connect();
