<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:py="http://purl.org/kid/ns#"
      py:extends="'master.kid'">
<head>
<meta content="text/html; charset=utf-8"
      http-equiv="Content-Type" py:replace="''"/>
<title> Editing ${name} - NeoWiki </title>
</head>
<body>
    <div id="main_content">
      <form action="?op=save&amp;prototype=${prototype}" method="post">               
        <textarea name="data" py:content="data" rows="20" cols="60"/>
        <input type="submit" name="submit" value="Save"/>
      </form>
    </div>
</body>
</html> 
