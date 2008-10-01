<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:py="http://purl.org/kid/ns#"
      py:extends="'master.kid'">
<head>
<meta content="text/html; charset=utf-8"
      http-equiv="Content-Type" py:replace="''"/>

<title> ${name} - NeoWiki </title>
<style type="text/css">
  @import "${tg.url('/static/css/wiab.css')}";
</style>
<script src="/static/javascript/jquery-1.2.6.js"></script>
<script src="/static/javascript/ui.core.js"></script>
<script src="${tg.url('/static/javascript/shortcut.js')}"></script>

<script  src="/static/javascript/wiab.js"></script>
<script language="javascript">
  shortcut.add("Ctrl+s", function() {
    document.edit.submit();
    return false;
  }, { 'type': 'keydown', 'propagate': false, 'target': document });
</script>
<?python
  globalTemplate = """
    #main_content {
      width: %spx;
    }
    """ % pageWidth
    
  itemTemplate = """
    #a%s {
      width: %spx;
      %s
    }
    """

  style = [globalTemplate]
  for cell in data:
    style.append(itemTemplate % (cell.index, cell.width, ''.join(cell.css)))
  
  style = ''.join(style)
?>
<style py:content="style" />
</head>
<body>
  <div id="main_content">
    <div class="cell" id="a${cell.index}" py:for="cell in data">
      ${XML(cell.data)}
    </div>
  </div>

</body>
</html>
