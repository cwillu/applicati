<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:py="http://purl.org/kid/ns#"
      py:extends="'master.kid'">
<head>
<meta content="text/html; charset=utf-8"
      http-equiv="Content-Type" py:replace="''"/>
<title> ${name} - NeoWiki </title>
</head> 
<body>
    <div class="main_content">
        <table border="0" >
        <tr></tr>
        <tr py:for="name, link in results" class="operations" >
          <div class="permissions">
            <td><div class="id">${name}</div></td>
            <td>
              <a href="${link}">/home/${link}</a>
            </td>
          </div>
        </tr>
        </table>      
    </div>
</body>
</html>



