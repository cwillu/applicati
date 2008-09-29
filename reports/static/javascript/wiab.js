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


wiab_tool = function(){
  tool = $('#wiab_tool');
  if (tool.length > 0)
    return tool;
//      $("body").append('<div id="wiab_tool" class="wiab_tool">test<br>test  \
//      </div>'); 
  alert("fail");
  return $('#wiab_tool');
  
};

layout = function() {
  alert($(this));
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
      $('.wiab_w,.wiab_e,.wiab_n,.wiab_s').css({display: 'block'});
      was.addClass("moreActive");
      wiab_tool().css({position: 'absolute', left: pageX, top: pageY}).fadeIn(100);
      was.focus();          
      cancels.push(function(){
        wiab_tool().fadeOut(100, function(){$('.wiab_w,.wiab_e,.wiab_n,.wiab_s').css({display: 'none'})});
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


