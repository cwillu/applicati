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

<script  src="/static/javascript/wiab.js"></script>

<?python
  globalTemplate = """
    #main_content {
      position: relative;
      left: -10px;
      width: %spx;
    }
    """ % 800 #(pageWidth)
    
  itemTemplate = """
    #a%s {
      position: absolute;
      left: %spx;
      top: %spx;      
      width: %spx;
      height: %spx;
      %s
    }    
    """

  style = [globalTemplate]
  for index, cell in enumerate(data):
    style.append(itemTemplate % (index, cell.x, cell.y, cell.width, cell.height, ';'.join(cell.css)+(';' if cell.css else '')))
  
  style = ''.join(style)
?>
<style py:content="style" />
</head>
<body>
  <div id="main_content">
    <div class="cell" id="a${index}" py:for="index, cell in enumerate(data)">
      <a href="#">Test</a>
      ${XML(cell.content)}
    </div>
  </div>
</body>
</html>
