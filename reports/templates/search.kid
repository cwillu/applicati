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
    <div id="main_content">
        <table border="0" >
        <tr></tr>
        <tr py:for="rank, index, name, id, link in results">
            <td>
            ${name}
            <div class="path" style="float: left; clear: left;"><a href="/${'/'.join(link)}">/${'/'.join(link)}</a></div>
            <div class="id">${id} - (${-rank}/${index})</div>
            </td>
          
        </tr>
        </table>      
    </div>
</body>
</html>



