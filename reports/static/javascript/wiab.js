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
var menu = null;

var item = function(label, style, action) {
  var item = Object();
  item.label = label;
  item.style = style;
  item.action = action;
  return item;
}; 

wiab_pi = function(){  
  _tool_div = !_tool_div
  if (_tool_div){
    menu = {
      s: item('Edit', 'wiab_button', null),
      se: item('Links', 'wiab_button', null),
      sw: item('Select', 'wiab_button', null),
      w: item('Paste', 'wiab_button', null),
    };
    return $('#wiab_tool_1');
  } else {
    menu = {
      n: item('', 'wiab_arrow', null),
      s: item('', 'wiab_arrow', null),
      e: item('', 'wiab_arrow', null),
      w: item('', 'wiab_arrow', null),
      ne: item('Layout', 'wiab_button', null),
      se: item('Links', 'wiab_button', null),
      sw: item('Delete', 'wiab_button', null),
      nw: item('', 'wiab_button', null),
    };  
    return $('#wiab_tool_2');
  }
};

wiab_tool = function() {
  var div = wiab_pi();    
  var all = '.wiab_w,.wiab_e,.wiab_n,.wiab_s,.wiab_nw,.wiab_se,.wiab_ne,.wiab_sw';
  var children = div.children(all);
  children.css({display: 'none'});
  
    var show = '';
    for (direction in menu){
      _class = '.wiab_' + direction
      show += _class + ',';
      children.filter(_class).addClass(menu[direction].style).html("<br/>" + menu[direction].label);
    }
    //show = '.wiab_w,.wiab_e,.wiab_n,.wiab_s';
    children.filter(show).css({display: 'block'})
  
  return div;
}



layout = function() {
  alert($(this));
};

var defaultDownAction = function(dom, e){
  if (e.button != 0)
    return;
  was = dom;
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
    if (moved(e)) 
      for (i in timeouts)
        clearTimeout(timeouts.pop());                           
  }

  cancels.push(function(){          
    was.removeClass("active moreActive");
    was.unbind('mousemove', checkMouse);
    was.unbind('mouseout', checkMouse);    
  });

//  var all = '.wiab_w,.wiab_e,.wiab_n,.wiab_s,.wiab_nw,.wiab_se,.wiab_ne,.wiab_sw';
//  var show ='.wiab_w,.wiab_e,.wiab_n,.wiab_s';  //,.wiab_nw,.wiab_se,.wiab_ne,.wiab_sw
//  currentTool.children(all)
//    .css({display: 'none'}).filter(show)
//      .css({display: 'block'})
//    .end()
//  .end();
    
  timeouts.push(setTimeout(function(){
    was.addClass("moreActive");
    currentTool.css({position: 'relative', left: mouseX, top: mouseY}).fadeIn(100);
    document.body.focus();
    cancels.push(function(){
      currentTool.fadeOut(100);
    });
  }, 300));

  was.mousemove(checkMouse).mouseout(checkMouse);
  //return false;
};

function moved(e){
  return Math.abs(e.clientX-mouseX) > 2 || Math.abs(e.clientY-mouseY) > 5;
}

var defaultUpAction = function(dom, e){
  e.stopPropagation();
  for (i in timeouts)
    clearTimeout(timeouts.pop());

  while (cancels.length > 0)
    cancels.pop()();

  if (!moved(e)){
    var href = was.filter('a').attr('href')
    if (href)
      window.location = href
  }
};

var was = null;
var pageX = null;
var pageY = null;    
var mouseX = null;
var mouseY = null;
var cancels = [];
var timeouts = [];
var clickStack = [{down: defaultDownAction, up: defaultUpAction}];


$(document).ready(function(){
  $("body").prepend('\
    <div id="wiab_tool_1" class="wiab_tool" > \
      <img id="wiab_image" src="/static/images/1.png" /> \
      <a rel="nofollow" class="wiab_n wiab"><br /></a> \
      <a rel="nofollow" class="wiab_ne wiab"><br /></a> \
      <a rel="nofollow" class="wiab_e wiab"><br /></a> \
      <a rel="nofollow" class="wiab_se wiab"><br /></a> \
      <a rel="nofollow" class="wiab_s wiab"><br /></a> \
      <a rel="nofollow" class="wiab_sw wiab"><br /></a> \
      <a rel="nofollow" class="wiab_w wiab"><br /></a> \
      <a rel="nofollow" class="wiab_nw wiab"><br /></a> \
    </div>');
  $("body").prepend('\
    <div id="wiab_tool_2" class="wiab_tool" > \
      <img id="wiab_image" src="/static/images/1.png" /> \
      <a rel="nofollow" class="wiab_n wiab"><br /></a> \
      <a rel="nofollow" class="wiab_ne wiab"><br /></a> \
      <a rel="nofollow" class="wiab_e wiab"><br /></a> \
      <a rel="nofollow" class="wiab_se wiab"><br /></a> \
      <a rel="nofollow" class="wiab_s wiab"><br /></a> \
      <a rel="nofollow" class="wiab_sw wiab"><br /></a> \
      <a rel="nofollow" class="wiab_w wiab"><br /></a> \
      <a rel="nofollow" class="wiab_nw wiab"><br /></a> \
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
    action.down($(this), e)
  }).mouseup(function(e){
    action = clickStack.pop();
    if (clickStack.length == 0)
      clickStack.push(action)
    action.up($(this), e)
  });
});



      
      //  $("*").droppable({
//          accept: '*',
//          activeClass: 'droppable-active', 
//        	hoverClass: 'droppable-hover' 
//        });


//        $("*").droppable("destroy");


