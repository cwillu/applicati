<!DOCTYPE html>
<?python import sitetemplate ?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="sitetemplate">

<head py:match="item.tag=='{http://www.w3.org/1999/xhtml}head'" py:attrs="item.items()">
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title py:replace="''">Your title goes here</title>
    <meta py:replace="item[:]"/>
    <style type="text/css">
        #pageLogin
        {
            font-size: 10px;
            font-family: verdana;
            text-align: right;
        }
    </style>
    <style type="text/css" media="screen">
@import "${tg.url('/static/css/style.css')}";
</style>
</head>

<body py:match="item.tag=='{http://www.w3.org/1999/xhtml}body'" py:attrs="item.items()" >  <div class="toolbar" style="position: absolute; z-index:1; top: 0; width: 100%"> 
    <div class="left path">
      <span py:for="index, link in enumerate(path[:-1])"> / <a href="${'/'.join(('',)+path[1:index+1])}/">${link}</a></span><!--
      --><span id="selected"> / <a href="${'/'.join(('',)+path[1:])}/">${path[-1]}</a>
        </span><!--
      --><span py:for="index, link in enumerate(session.get('path',[])[len(path)-1:])"> / <a href="${'/'.join(('',)+session['path'][:index+len(path)])}/">${link}</a></span> 
    </div>
    <div class="right"> 
      <span py:if="root[-1] == 'guest'">
        <a href="/?op=login">Log in</a>
      </span>
      <span py:if="root[-1] != 'guest'">
        ${root[-1]} | <a href="/?op=logout">Log out</a>
      </span>            
    </div>       
  </div>
  <div class="middle">
    <div id="main_content">
      <div class="spacer"> </div>
      <div onClick="document.getElementById('status_block').style.display='none'" id="status_block" class="flash" py:if="value_of('tg_flash', None)" py:content="tg_flash" />
      <div py:replace="[item.text]+item[:]"/>  
      <div class="spacer"> </div>
    </div>    <div class="bot"><div class="toolbar"> 
      <div class="left">
          <a href="?op=edit">Edit</a>
        | <a href="?op=links">Links</a>
        | <form name="select" action="?op=copy" method="POST">
            <a href="#select" onClick="document.select.submit()">Select</a>
          </form>
        | <form name="paste" action="?op=write" method="POST">
            <a href="#paste" onClick="document.paste.submit()">Paste</a>
          </form>
      </div>
      <div class="right">
        <span py:for="perm in ['read', 'modify', 'replace', 'cross', 'override']">
          <img py:if="obj.permissions and obj.permissions[0] and perm in obj.permissions[1]"
            src="/static/images/${'set' if perm in obj.permissions[0] else 'unset'}.png" />
          <img py:if="obj.permissions and obj.permissions[0] and perm not in obj.permissions[1]"
            src="/static/images/${'set-off' if perm in obj.permissions[0] or 'override' in obj.permissions[0] else 'unset-off'}.png" />
          <img py:if="not obj.permissions or not obj.permissions[0] "
            src="/static/images/${'set-off'}.png" />
        </span>
      </div>
    </div>
  </div>

  </div>
  


  
</body>

</html>
