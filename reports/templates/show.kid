<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:py="http://purl.org/kid/ns#"
      py:extends="'master.kid'">
<head>
<title> ${name} - NeoWiki </title>
</head>
<body>
  <div class="main_content">
    <div py:replace="XML(data)">Page text goes here.</div>
  </div>    
</body>
</html>
