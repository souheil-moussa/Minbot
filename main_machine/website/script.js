function connect() {
	const serverIP = localStorage.getItem('server_IPAddress')
	const savedIPAddress = localStorage.getItem('cont_IPAddress');
	const statusDiv = document.querySelector('.status');
	const ws = new WebSocket("ws://" + savedIPAddress + ":8081");
	var stream_status = false
	console.log()

	ws.onerror = (event) => {
		document.getElementById('wss').innerHTML = "Ws server: Disconnected "
		console.log(`${event.data}`)
		setTimeout(connect, 5000)
	}

	ws.onopen = () => {
		document.getElementById('wss').innerHTML = "Ws server: Connected "
		statusDiv.classList.add('status-connected');
		console.log('Connected to WebSocket server');
		ws.send(JSON.stringify({ serverIP: serverIP }));



	};

	ws.onmessage = (event) => {
		console.log(`Server: ${event.data}`);
	};
	ws.onclose = () => {
		document.getElementById('wss').innerHTML = "Ws server: Disconnected "
		setTimeout(connect, 5000)
		statusDiv.classList.remove('status-connected')

	}


	document.getElementById('start').addEventListener('click', () => {
		if (stream_status) {
			ws.send('stop');
			stream_status = false;
			document.getElementById("start").innerHTML = "Start Meeting"
		}
		else {
			ws.send('start');
			stream_status = true;
			document.getElementById("start").innerHTML = "Stop Meeting"
		}
	});
}
connect();
