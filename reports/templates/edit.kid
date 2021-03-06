<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:py="http://purl.org/kid/ns#"
      py:extends="'master.kid'">
<head>
<meta content="text/html; charset=utf-8"
      http-equiv="Content-Type" py:replace="''"/>
<title> Editing ${name} - NeoWiki </title>
    <script language="javascript">
        shortcut.add("Ctrl+s", function() {
            document.editor.submit();
            return false;
          }, { 'type': 'keydown', 'propagate': false, 'target': document });
        
    </script>
</head>
<body>
    <div id="main_content">
      <form name="editor" id="editor" action="?op=save;prototype=${prototype}" method="post">               
        <textarea name="data" py:content="data" rows="${max(19, sum([-((len(line)+1)/-55) for line in data.splitlines()]))+1}" cols="60"/><br/>
        <input type="submit" name="save" value="Save"/>
        <input type="reset" name="_reset" value="Reset"/>
      </form>
    </div>
</body>
</html> 
