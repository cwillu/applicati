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
	  if(request.status == 204){
	    request.open("get", "?op=show", false); 
	    request.send(null);	    
	    if(request.status == 200){
        original = document.getElementByClass("document")[0];
  	    replacement = request.responseXML.getElementByClass("document")[0];
	      document.getElementById("viewer").replaceChild(replacement, original);
	    }
	  }
  }
  
  function refresh() {
  }
</script>
</head>
<body>
  <div py:replace="XML(data)">Page text goes here.</div>

</body>
</html>
