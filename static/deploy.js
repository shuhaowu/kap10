var deploy_button = document.getElementById("deploy");

function trigger_deploy() {
  var name = document.getElementById("name").value;
  var commit = document.getElementById("commit").value;
  var pass = document.getElementById("pass").value;
  var posturl = document.getElementById("posturl").value;
  var sseurl = document.getElementById("sseurl").value;
  var out = document.getElementById("output");

  if (!commit || !pass || !name) {
    alert("You must enter a commit, a name, and a password!");
    return;
  }

  var setup_console = function() {
    out.innerHTML = "";
    var sse = new EventSource(sseurl);
    sse.onmessage = function(message) {
      out.innerHTML += message.data + "\n";
    };
  };

  var req = new XMLHttpRequest();
  req.open("post", posturl, true);

  var data = JSON.stringify({commit: commit, pass: pass, name: name});
  req.setRequestHeader("Content-type", "application/json");
  req.setRequestHeader("Content-length", data.length);
  req.setRequestHeader("Connection", "close");

  req.onreadystatechange = function() {
    if (req.readyState == 4) {
      if (req.status == 200) {
        setup_console();
      } else if (req.status == 403) {
        alert("Check your password.");
        deploy_button.onclick = trigger_deploy;
        deploy_button.classList.remove("disabled");
      } else {
        alert("Error: " + req.status);
      }
    }
  };
  req.send(data)
  deploy_button.classList.add("disabled");
  deploy.onclick = null;
}


deploy_button.onclick = trigger_deploy;
