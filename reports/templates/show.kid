<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:py="http://purl.org/kid/ns#"
      py:extends="'master.kid'">
<head>
<title> ${name} - NeoWiki </title>
<script language="javascript">

  window.addEventListener('load', function() {setTimeout('init()', 10)}, false);

  function init() {
    var request = new XMLHttpRequest(); 
	  request.open("get", "?op=waitForChange", false); 
	  request.send(null);
	  if(request.status == 205){
	    request.open("get", "?op=show", false); 
	    request.send(null);	    
	    if(request.status == 200){
        original = document.getElementById("view");
  	    replacement = request.responseXML.getElementById("view");
	      document.getElementById("main_content").replaceChild(original, replacement);
	    }
	  }
  }
</script>
</head>
<body>
  <div class="main_content">
    <div id="view" py:replace="XML(data)">Page text goes here.</div>
  </div>    
</body>
</html>
