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
	  request.open("get", "?op=waitForChange", true); 
    request.onreadystatechange = function() {
      if (request.readyState == 4) {
//        if (request.responseText)
//        {
//            callbackFunction(request.responseText);
//        }
        setTimeout('window.location.reload();', 500)
        
      }
    };
	  
	  request.send(null);
//	  if(request.status == 205){

//	  }
  }
  
  function refresh() {
    
  }
</script>
</head>
<body>
  <div py:replace="XML(data)">Page text goes here.</div>

</body>
</html>
