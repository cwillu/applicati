<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:py="http://purl.org/kid/ns#"
      py:extends="'master.kid'">
<head>
<title> ${name} - NeoWiki </title>
<script language="javascript">

  //window.addEventListener('load', init(), false);

  function monitor() {
    var f = document.createElement('iframe');
    f.setAttribute('id', 'monitor');
    f.style.border='0px';
    f.style.width='0px';
    f.style.height='0px';
    f = document.body.appendChild(f);
    
    f.contentDocument.location.replace("?op=waitForChange");
    return false;
//	  if(request.status == 205){

//	  }
  }

  window.addEventListener('load', function() {setTimeout('monitor()', 10);}, false);
</script>
</head>
<body>
  <!--<iframe src="/static/html/waiter.html" style="width:0px; height:0px; border: 0px" />-->

  <div py:replace="XML(data)">Page text goes here.</div>

</body>
</html>
