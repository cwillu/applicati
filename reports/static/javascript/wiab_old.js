var item = function(label, style, action) {
  var item = Object();
  item.label = label;
  item.style = style;
  item.action = action;
  return item;
}; 
 
var menu = {
  s: item('Move', 'wiab_button', layout_tool),
  se: item('Edit', 'wiab_button', null),
  sw: item('Select', 'wiab_button', null),
  w: item('Paste', 'wiab_button', null),
};

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
var clickStack = [];
//[{down: defaultDownAction, up: defaultUpAction}];

$(document).ready(function(){
  $('.wiab').hover(function(){
    $(this).addClass('wiab_active')
  }, function(){
    $(this).removeClass('wiab_active')
  });
  $('.wiab').mouseup(function(){    
    onClick = $(this).filter('a').attr('onClick')
    if (onClick){
      $(this).click()
    }  
    href = $(this).filter('a').attr('href')
    if (href)
      window.location = href
  });

  $('.cell,').mousedown(function(e){
    var action;
    if (clickStack.length == 0){
      action = showMenu;
    } else {
      action = clickStack.pop().down;
    }
    action((this), e)
  });
  $('body').mouseup(function(e){
    action = clickStack.pop();
    if (clickStack.length == 0)
      clickStack.push(action)
    action.up($(this), e)
  });
    
  $('#wiab_selection>*').mousedown(function(e) {
    e.preventDefault();
    e.stopPropagation();
  });


});



      
      //  $("*").droppable({
//          accept: '*',
//          activeClass: 'droppable-active', 
//        	hoverClass: 'droppable-hover' 
//        });


//        $("*").droppable("destroy");

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

