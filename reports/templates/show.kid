<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:py="http://purl.org/kid/ns#"
      py:extends="'master.kid'">
<head>
<meta content="text/html; charset=utf-8"
      http-equiv="Content-Type" py:replace="''"/>

<title> ${name} - NeoWiki </title>
    <script language="javascript">
        shortcut.add("Ctrl+s", function() {
            document.edit.submit();
            return false;
          }, { 'type': 'keydown', 'propagate': false, 'target': document });
        
    </script>
</head>
<body>
  <!--<iframe src="/static/html/waiter.html" style="width:0px; height:0px; border: 0px" />-->

  <div id="main_content"><div py:replace="XML(data)">Page text goes here.</div></div>

</body>
</html>
