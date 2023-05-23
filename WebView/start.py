#from tendo import singleton
#me = singleton.SingleInstance()

import os, time

from flask import Flask
from flask import request
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
	path = os.path.dirname(os.path.realpath(__file__))
	page = '''
		Loading: <span id="loading"></span><br />
		<button id="refresh">Refresh</button><br />
		<input type="text" id="keys" /> <button id="send">Send</button><br />
		<img src="static/page.png" style="border:1px solid #000;" />
		
		<script src="https://code.jquery.com/jquery-3.5.0.js"></script>
		<script type="text/javascript">
		$(document).ready(function() {
		command_in_progress = false;
		$("img").on("click", function(event) {
				command_in_progress = true;
				var x = event.pageX - this.offsetLeft;
				var y = event.pageY - this.offsetTop;
				console.log("X Coordinate: " + x + " Y Coordinate: " + y);

				$.ajax({
					url: "/click",
					method: "GET",
					data: { x: x, y: y }
				});
			});
		});

		$("#refresh").click(function(){
			command_in_progress = true;
			$.ajax({
				url: "/refresh",
				method: "GET",
				success: function(){
					location.reload(); 
				}
			});
		});

		$("#send").click(function(){
			command_in_progress = true;
			$.ajax({
				url: "/keys",
				method: "GET",
				data: { k: $("#keys").val() }
			});
		});

		setInterval(function(){
			if(command_in_progress)
				$("#loading").html("true");
			else
				$("#loading").html("false");
			$.ajax({
				url: "/progress",
				method: "GET",
				success: function(e){
					if(e == "false" && command_in_progress){
						command_in_progress = false;
						location.reload()
					}
				}
			});
		}, 1000);
		</script>

	'''

	return page

def launch_command(cmd):
	path = os.path.dirname(os.path.realpath(__file__))

	f = open("todo.txt", "w")
	f.write(cmd)
	f.close()

@app.route('/click')
def click():
	launch_command("click "+request.args.get("x")+" "+request.args.get("y"))
	return "click"

@app.route('/keys')
def keys():
	launch_command("keys "+request.args.get("k"))
	return "keys"

@app.route('/refresh')
def refresh():
	launch_command("refresh ")
	return "refresh"

@app.route('/progress')
def progress():
	f = open("todo.txt", "r")
	content = f.read()
	f.close()
	time.sleep(1)
	if content.strip() == "":
		return "false"
	else:
		return "true"

app.run(host='0.0.0.0', port=9322, debug=True)