<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:py="http://purl.org/kid/ns#"
      py:extends="'master.kid'">
<head>
<title> ${name} - NeoWiki </title>
<script language="javascript">

  //window.addEventListener('load', init(), false);

  function monitor() {
    hash = Math.ceil(Math.random()*10000)
    var request = new XMLHttpRequest(); 
	  request.open("get", "?op=waitForChange;hash="+hash, false); 
//    request.onreadystatechange = function() {
//      if (request.readyState == 4) {
//        if (request.responseText)
//        {
//            callbackFunction(request.responseText);
//        }
//        window.location.reload();
//        //setTimeout('window.location.reload();', 50)
//        
//      }
//    };
	  
	  request.send(null);
    window.location.reload();	  
//	  if(request.status == 205){

//	  }
  }
  
  window.addEventListener('load', function() {setTimeout('monitor()', 10)}, false);
</script>
</head>
<body>
  <iframe>
  <body>
    test
  </body>
  </iframe>

  <div py:replace="XML(data)">Page text goes here.</div>

</body>
</html>
