<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:py="http://purl.org/kid/ns#"
      py:extends="'master.kid'">
<head>
<title> ${name} - NeoWiki </title>
</head>
<body>
  <iframe src="/static/html/waiter.html" style="width:0px; height:0px; border: 0px" />

  <div py:replace="XML(data)">Page text goes here.</div>

</body>
</html>
