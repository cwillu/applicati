//  <a href="#select" onClick="document.select.submit(); return false;" rel="nofollow" class="wiab wiab_sw"><br />Select</a>
//  <a href="?op=links" rel="nofollow" class="wiab wiab_se"><br />Links</a>
//  <a href="#paste" onClick="document.paste.submit(); return false;" rel="nofollow" class="wiab wiab_w"><br />Paste</a>
//  <a href="#edit" onClick="document.edit.submit(); return false;" rel="nofollow" class="wiab wiab_s"><br />Edit</a>
//  <a href="#foo" onClick="layout();" rel="nofollow" class="wiab wiab_e"><br />Layout</a>

//  <a rel="nofollow" class="wiab wiab_sw"><br />Select</a>
//  <a href="?op=links" rel="nofollow" class="wiab wiab_se"><br />Links</a>
//  <a href="#paste" onClick="document.paste.submit(); return false;" rel="nofollow" class="wiab wiab_w"><br />Paste</a>
//  <a href="#edit" onClick="document.edit.submit(); return false;" rel="nofollow" class="wiab wiab_s"><br />Edit</a>
//  <a href="#foo" onClick="layout();" rel="nofollow" class="wiab wiab_e"><br />Layout</a>

_tool_div = true;

wiab_tool = function(){  
  _tool_div = !_tool_div
  if (_tool_div)
    return $('#wiab_tool_1');
  else
    return $('#wiab_tool_2');
};

layout = function() {
  alert($(this));
};

var defaultDownAction = function(e){
  if (e.button != 0)
    return;
  var was = $(this);
  var currentTool = wiab_tool();
  e.stopPropagation();
  if (was.filter("a").length > 0)
    e.preventDefault();

  var pageX = e.pageX;
  var pageY = e.pageY;
  var mouseX = e.clientX;
  var mouseY = e.clientY;

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

  var all = '.wiab_w,.wiab_e,.wiab_n,.wiab_s,.wiab_nw,.wiab_se,.wiab_ne,.wiab_sw';
  var show ='.wiab_w,.wiab_e,.wiab_n,.wiab_s';  //,.wiab_nw,.wiab_se,.wiab_ne,.wiab_sw
  currentTool.children(all).css({display: 'none'}).filter(show).css({display: 'block'}).end().end();
  timeouts.push(setTimeout(function(){  
    currentTool.css({position: 'relative', left: mouseX, top: mouseY}).fadeIn(100);
    was.focus();          
    cancels.push(function(){
      currentTool.fadeOut(100);
    });
  }, 300));

  $(this).mousemove(checkMouse).mouseout(checkMouse);
  //return false;
};

var defaultUpAction = function(e){
  e.stopPropagation();
  for (i in timeouts)
    clearTimeout(timeouts.pop());

  while (cancels.length > 0)
    cancels.pop()();

  if (!(Math.abs(e.clientX-mouseX) > 2 || Math.abs(e.clientY-mouseY) > 2)){
    var href = was.filter('a').attr('href')
    if (href)
      window.location = href
  }
};

var pageX = null;
var pageY = null;    
var mouseX = null;
var mouseY = null;
var cancels = [];
var timeouts = [];
var was = null;
var clickStack = [{down: defaultDownAction, up: defaultUpAction}];


$(document).ready(function(){
  $("body").prepend('\
    <div id="wiab_tool_1" class="wiab_tool" > \
      <img id="wiab_image" src="/static/images/1.png" /> \
      <a rel="nofollow" class="wiab_arrow wiab_sw wiab"><br /></a> \
      <a rel="nofollow" class="wiab_arrow wiab_s wiab"><br /></a> \
      <a rel="nofollow" class="wiab_arrow wiab_se wiab"><br /></a> \
      <a rel="nofollow" class="wiab_arrow wiab_e wiab"><br /></a> \
      <a rel="nofollow" class="wiab_arrow wiab_ne wiab"><br /></a> \
      <a rel="nofollow" class="wiab_arrow wiab_n wiab"><br /></a> \
      <a rel="nofollow" class="wiab_arrow wiab_nw wiab"><br /></a> \
      <a rel="nofollow" class="wiab_arrow wiab_w wiab"><br /></a> \
    </div>');
  $("body").prepend('\
    <div id="wiab_tool_2" class="wiab_tool" > \
      <img id="wiab_image" src="/static/images/1.png" /> \
      <a rel="nofollow" class="wiab_arrow wiab_sw wiab"><br /></a> \
      <a rel="nofollow" class="wiab_arrow wiab_s wiab"><br /></a> \
      <a rel="nofollow" class="wiab_arrow wiab_se wiab"><br /></a> \
      <a rel="nofollow" class="wiab_arrow wiab_e wiab"><br /></a> \
      <a rel="nofollow" class="wiab_arrow wiab_ne wiab"><br /></a> \
      <a rel="nofollow" class="wiab_arrow wiab_n wiab"><br /></a> \
      <a rel="nofollow" class="wiab_arrow wiab_nw wiab"><br /></a> \
      <a rel="nofollow" class="wiab_arrow wiab_w wiab"><br /></a> \
    </div>');

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

  
  
  $("*").mousedown(function(e){
    action = clickStack.pop();
    if (clickStack.length == 0)
      clickStack.push(action)
    action.down(e)
  }).mouseup(function(e){
    action = clickStack.pop();
    if (clickStack.length == 0)
      clickStack.push(action)
    action.up(e)
  });
  
});



      
      //  $("*").droppable({
//          accept: '*',
//          activeClass: 'droppable-active', 
//        	hoverClass: 'droppable-hover' 
//        });


//        $("*").droppable("destroy");


