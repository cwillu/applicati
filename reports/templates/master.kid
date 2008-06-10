<!DOCTYPE html>
<?python import sitetemplate ?>
<?python import random ?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">
<head py:match="item.tag=='{http://www.w3.org/1999/xhtml}head'" py:attrs="item.items()">
    <meta name="verify-v1" content="tasE1XaBrCBulc5wEzuT4RocTBnZ0f18824WGAwujmE=" />    <meta content="text/html; charset=UTF-8" http-equiv="content-type" />
    <title py:replace="''">Your title goes here</title>
    <style type="text/css">
        #pageLogin
        {
            font-size: 10px;
            font-family: verdana;
            text-align: right;
        }
    </style>
    <style type="text/css">
      @import "${tg.url('/static/css/style.css')}";
    </style>
    <style type="text/css" media="screen">
      @import "${tg.url('/static/css/screen.css')}";
    </style>
    <style type="text/css" media="print">
      @import "${tg.url('/static/css/print.css')}";
    </style>
    <script src="${tg.url('/static/javascript/shortcut.js')}" language="javascript" >
    </script>
    <meta py:replace="item[:]"/>
</head>

<body py:match="item.tag=='{http://www.w3.org/1999/xhtml}body'" py:attrs="item.items()" >  <div class="top toolbar"> 
    <div class="left">
      <a href="/"><img style="display: inline; position: absolute; bottom: 1px; left: 6px; margin: -20px 0px;" src="${tg.url([
        '/static/images/mantis-angle.png', 
        '/static/images/mantis-angle.png', 
        '/static/images/mantis-angle.png', 
        '/static/images/mantis-straight.png', 
        '/static/images/mantis-right.png', 
        '/static/images/mantis-right.png', 
        '/static/images/mantis-up.png', 
        '/static/images/mantis-rolled.png', 
        '/static/images/mantis-left.png', 
        ][random.randrange(6)])}" /></a>    
    </div>
    <div class="left" style="padding-left: 48px;">
      <div ><span id="selected"><a href="${'/'.join(('',)+path[1:])}/">${path[-1]}</a></span></div>
      <div class="path">
        <span style="z-index: 10; margin: -16px;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><!--
        --><span py:for="index, link in enumerate(path[:-1])">/<a href="${'/'.join(('',)+path[1:index+1])}/">${link}</a></span><!--
        --><span id="selected">/<a href="${'/'.join(('',)+path[1:])}/">${path[-1]}</a></span><!--
        --><span py:for="index, link in enumerate(session.get('path',[])[len(path)-1:])">/<a href="${'/'.join(('',)+session['path'][:index+len(path)])}/">${link}</a></span><!--
        --><span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
      </div>  
    </div>  
    
    <div class="right" >
      <span>
        <form name="search" action="/" method="get">               
          <input type="hidden" name="op" value="search" />
          <input id="search" type="text" name="query" />
          <a href="?op=search" onClick="document.search.submit(); return false;">Search</a>      
        </form>
      </span>
      <span py:if="root[-1] == 'guest'">
        | <a href="/?op=login">Log in</a>
      </span>
      <span py:if="root[-1] != 'guest'">
        | ${root[-1]} | <a href="/?op=logout">Log out</a>
      </span>               
    </div> 
  </div>
  <div class="middle">
    <div id="viewer">
      <div class="spacer" />
      <div class="shadow" id="shadow1">
        <div class="shadow" id="shadow2">
        <div class="shadow" id="shadow3">
        <div class="shadow" id="shadow4">
        <div class="shadow" id="shadow5">
 <div py:if="False" onClick="document.getElementById('status_block').style.display='none'" id="status_block" class="flash" >Foo</div>
          <div onClick="document.getElementById('status_block').style.display='none'" id="status_block" class="flash" py:if="value_of('tg_flash', None)" py:content="tg_flash" />
          <div id="main_content" py:replace="[item.text]+item[:]"/>  
        </div>
        </div>
        </div>
        </div>
      </div>
      <div class="spacer" />
    </div>    <div class="bot"><div class="toolbar"> 
      <div class="left">
          <form name="edit" action="?op=edit" method="POST">
            <a href="#edit" onClick="document.edit.submit(); return false;">Edit</a>
          </form>
        | <a href="?op=links">Links</a>
        | <form name="select" action="?op=copy" method="POST">
            <a href="#select" onClick="document.select.submit(); return false;">Select</a>
          </form>
        | <form name="paste" action="?op=write" method="POST">
            <a href="#paste" onClick="document.paste.submit(); return false;">Paste</a>
          </form>
      </div>
      <div class="right">
      
        <span py:for="perm in ['read', 'modify', 'replace', 'cross', 'override']">
          <img py:if="obj.permissions and obj.permissions[0] and perm in obj.permissions[1]"
            src="/static/images/${'set' if perm in obj.permissions[0] else 'unset'}.png" title="${perm}, changed" />
          <img py:if="obj.permissions and obj.permissions[0] and perm not in obj.permissions[1]"
            src="/static/images/${'set-off' if perm in obj.permissions[0] or 'override' in obj.permissions[0] else 'unset-off'}.png" title="${perm}"/>
          <img py:if="not obj.permissions or not obj.permissions[0] "
            src="/static/images/${'set-off'}.png" title="${perm}" />
        </span>
      </div>
    </div>
  </div>

  </div>
  


  
</body>

</html>
