<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:py="http://purl.org/kid/ns#"
      py:extends="'master.kid'">
<head>
<title> ${name} - NeoWiki </title>
<script language="javascript">

  //window.addEventListener('load', init(), false);

  function monitor() {
    var hash = Math.ceil(Math.random()*10000)
    var request = new XMLHttpRequest(); 
    var loc = window.location
	  request.open("get", "?op=waitForChange;hash=" + hash, true); 
    
    request.onreadystatechange = function() {
      if (request.readyState == 4) {
  //      if (request.responseText.lastindexof("!", request.responseText.length-100)>=0){
          loc.reload();
        //}

        //
        //{
        //    callbackFunction(request.responseText);
        //}
        //setTimeout('window.location.reload();', 50)        
      }
    };	  
	  request.send(null);
    
//	  if(request.status == 205){

//	  }
  }

  window.addEventListener('load', function() {setTimeout('monitor()', 10)}, false);
</script>
</head>
<body>
  <!--<iframe src="/static/html/waiter.html" style="width:0px; height:0px; border: 0px" />-->

  <div py:replace="XML(data)">Page text goes here.</div>

</body>
</html>
