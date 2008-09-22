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
    <script src="/static/javascript/jquery-1.2.6.js"></script>
    <script src="/static/javascript/ui.core.js"></script>
    <script src="${tg.url('/static/javascript/shortcut.js')}"></script>
    
    <script type="text/javascript"> 
    <!--
    wiab_tool = function(){
      tool = $('#wiab_tool');
      if (tool.length > 0)
        return tool;
//      $("body").append('<div id="wiab_tool" class="wiab_tool">test<br>test  \
//      </div>'); 
      alert("fail");
      return $('#wiab_tool');
      
    };

    var pageX = null;
    var pageY = null;    
    var mouseX = null;
    var mouseY = null;
    var cancels = [];
    var timeouts = [];
    var was = null;
    $(document).ready(function(){
      $(".wiab").hover(function(){
        $(this).addClass("wiab_active")
      }, function(){
        $(this).removeClass("wiab_active")
      }).mouseup(function(){
        onClick = $(this).filter('a').attr('onClick')
        if (onClick){
          $(this).click()
        }  
        href = $(this).filter('a').attr('href')
        if (href)
          window.location = href
      });

      
    //mousedown( fn )
      $("*").mousedown(function(e){
        if (e.button != 0)
          return;
        was = $(this)
        e.stopPropagation();
        if (was.filter("a").length > 0)
          e.preventDefault();

        pageX = e.pageX;
        pageY = e.pageY;
        mouseX = e.clientX;
        mouseY = e.clientY;

        was.addClass("active");

        for (i in timeouts)
          clearTimeout(timeouts.pop());
        
        var checkMouse = function(e){
          //alert(e.clientX + ", " + mouseX + ", ");
          if (Math.abs(e.clientX-mouseX) > 2 || Math.abs(e.clientY-mouseY) > 2) 
            for (i in timeouts)
              clearTimeout(timeouts.pop());                           
        }

        cancels.push(function(){          
          was.removeClass("active moreActive");
          was.unbind('mousemove', checkMouse);
          was.unbind('mouseout', checkMouse);    
        });

        timeouts.push(setTimeout(function(){
          was.addClass("moreActive");
          wiab_tool().css({position: 'absolute', left: pageX, top: pageY}).fadeIn(100);
          was.focus();          
          cancels.push(function(){
            wiab_tool().fadeOut(100);
          });
        }, 300));

        $(this).mousemove(checkMouse).mouseout(checkMouse);
        //return false;
      }).mouseup(function(e){
        e.stopPropagation();
        for (i in timeouts)
          clearTimeout(timeouts.pop());

        while (cancels.length > 0)
          cancels.pop()();

        if (!(Math.abs(e.clientX-mouseX) > 2 || Math.abs(e.clientY-mouseY) > 2)){
          href = was.filter('a').attr('href')
          if (href)
            window.location = href
        }
      });
      
    });



      
      //  $("*").droppable({
//          accept: '*',
//          activeClass: 'droppable-active', 
//        	hoverClass: 'droppable-hover' 
//        });


//        $("*").droppable("destroy");

-->
  </script>
    <style>
    .active {
	    //outline: 1px solid black;
    }
    .moreActive {
	    //outline: 3px dotted black;
    }
    .wiab_tool {
      display: none;
      position: relative;
      width: 0px;
      height: 0px;
      left: 300px;
      top: 200px;  
      z-index: 11;    
    }
    .wiab {
      position: absolute;
      text-align: center;
      text-decoration: none;
      font-weight: bold;      
      line-height: 20px;
      color: #333333;
      width: 64px;
      height: 64px;      
      background: url("/static/images/button.png");
    }
    .wiab_active {
      color: #000044;
      background: url("/static/images/button-active.png");
    }
    .wiab img {
      position: absolute; 
      left: -128px;
      top: -128px;
      height: 256px; 
      width: 256px; 
      color: white;
    }
    .wiab_w {
      left: -128px;
      top: -32px;  
    }
    .wiab_sw {
      left: -96px;  
      bottom: -80px;
    }
    .wiab_s {
      left: -32px;
      bottom: -96px;
    }
    .wiab_se {
      right: -96px;  
      bottom: -80px;
    }
  </style>
    <meta py:replace="item[:]"/>
</head>

<body py:match="item.tag=='{http://www.w3.org/1999/xhtml}body'" py:attrs="item.items()" >
<div id="wiab_tool" class="wiab_tool">
  <img id="wiab_image" src="/static/images/1.png" />
  <a href="#select" onClick="document.select.submit(); return false;" rel="nofollow" class="wiab wiab_sw"><br />Select</a>
  <a href="?op=links" rel="nofollow" class="wiab wiab_se"><br />Links</a>
  <a href="#paste" onClick="document.paste.submit(); return false;" rel="nofollow" class="wiab wiab_w"><br />Paste</a>
  <a href="#edit" onClick="document.edit.submit(); return false;" rel="nofollow" class="wiab wiab_s"><br />Edit</a>
</div>  <div class="top toolbar"> 
    <div class="left">
      <a href="/"><img style="display: inline; position: absolute; bottom: 0px; left: 6px; margin: -20px 0px;" src="${tg.url([
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
      <div ><span id="selected"><a href="${path[1][path[0]][0]}/">${name}</a></span></div>
      <div class="path">
        <!-- /foo/bar/BAZ/bing/bob/ -->
        <span style="z-index: 10; margin: -16px;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><!--
        --><span py:for="segment in path[1][:path[0]]">/<a href="${segment[0]}">${segment[1]}</a></span><!--
        --><span id="selected">/<a href="${path[1][path[0]][0]}">${path[1][path[0]][1]}</a></span><!--
        --><span py:for="segment in path[1][path[0]+1:]">/<a href="${segment[0]}">${segment[1]}</a></span><!--
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
        | <a href="/login">Log in</a>
      </span>
      <span py:if="root[-1] != 'guest'">
        | ${root[-1]} | <a href="/logout">Log out</a>
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
