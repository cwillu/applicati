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
    
</head>
<body>
<div id="wiab_tool" class="wiab_tool">
  <img id="wiab_image" src="/static/images/1.png" />
  <a rel="nofollow" class="wiab wiab_sw"><br />Select</a>
  <a rel="nofollow" class="wiab wiab_s wiab_arrow_s"><br />Select</a>
  <a rel="nofollow" class="wiab wiab_se"><br />Select</a>
  <a rel="nofollow" class="wiab wiab_e wiab_arrow_e"><br />Select</a>
  <a rel="nofollow" class="wiab wiab_ne"><br />Select</a>
  <a rel="nofollow" class="wiab wiab_n wiab_arrow_n"><br />Select</a>
  <a rel="nofollow" class="wiab wiab_nw"><br />Select</a>
  <a rel="nofollow" class="wiab wiab_w wiab_arrow_w"><br />Select</a>
</div>
  <!--<iframe src="/static/html/waiter.html" style="width:0px; height:0px; border: 0px" />-->

  <div id="main_content"><div py:replace="XML(data)">Page text goes here.</div></div>

</body>
</html>
