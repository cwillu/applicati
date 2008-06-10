<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
          "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:py="http://purl.org/kid/ns#"
      py:extends="'../master.kid'">
<head>
<meta content="text/html; charset=utf-8"
      http-equiv="Content-Type" py:replace="''"/>
<title> ${page.name} - NeoWiki </title>
</head>
<body>
    <div class="main_content">
        <table border="0">
        <tr py:for="link in (page.data and page.data.links or [])">
        <td><a href="${link}">${link}</a></td>
        </tr>
        </table>       
    </div>
</body>
</html>
