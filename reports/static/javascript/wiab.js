var insertTools = function() {
  insertPiMenu();
  insertSelectionTool();
};
var insertPiMenu = function() {
  toolTemplate = '\
    <img id="wiab_image" src="/static/images/1.png" /> \
        <a rel="nofollow" class="wiab_n wiab"><br /></a> \
        <a rel="nofollow" class="wiab_ne wiab"><br /></a> \
        <a rel="nofollow" class="wiab_e wiab"><br /></a> \
        <a rel="nofollow" class="wiab_se wiab"><br /></a> \
        <a rel="nofollow" class="wiab_s wiab"><br /></a> \
        <a rel="nofollow" class="wiab_sw wiab"><br /></a> \
        <a rel="nofollow" class="wiab_w wiab"><br /></a> \
        <a rel="nofollow" class="wiab_nw wiab"><br /></a> \
    ';

  $("body").prepend('<div id="wiab_tool_1" class="wiab_tool" >' + toolTemplate + '</div>');
  $("body").prepend('<div id="wiab_tool_2" class="wiab_tool" >' + toolTemplate + '</div>');
  $('.wiab_tool>.wiab').hover(function(){
    $(this).addClass('wiab_active')
  }, function(){
    $(this).removeClass('wiab_active')
  });
    
  var toolDiv = true;
  var getMenu = function(){  
    toolDiv = !toolDiv
    if (toolDiv){
      return $('#wiab_tool_1');
    } else {
      return $('#wiab_tool_2');
    }
  };
  
  item = function(label, style, action) {
    var item = Object();
    item.label = label;
    item.style = style;
    item.action = action;
    return item;
  }; 
  piMenu = function(selector, menu) {
    var pi = getMenu();    
    var all = '.wiab_w,.wiab_e,.wiab_n,.wiab_s,.wiab_nw,.wiab_se,.wiab_ne,.wiab_sw';
    var children = pi.children(all);
    children.css({display: 'none'});
    
    var show = '';
    for (direction in menu.items){
      _class = '.wiab_' + direction
      show += _class + ',';
      // 
      children.filter(_class)
        .addClass(menu.items[direction].style)
        .html("<br/>" + menu.items[direction].label)
        .unbind('mouseup')
        .mouseup(menu.items[direction].action); 
    }
    children.filter(show).css({display: 'block'})

    var cancels = [];
    var target = null;
    var originalLocation = {x: null, y: null};
    var moved = function(e){
      return Math.abs(e.clientX-originalLocation.x) > 2 || Math.abs(e.clientY-originalLocation.y) > 5;
    };
    
    var targetMouseDown = function(e) {
      if (e.button != 0)
        return;
      e.stopPropagation();
      originalLocation = { x: e.clientX, y: e.clientY };
      
      var timeouts = [];
      var checkMouse = function(e){
        if (moved(e)){
          for (i in timeouts)
            clearTimeout(timeouts.pop());
          while (cancels.length > 0)
            cancels.pop()();
        }
      };

      // Is there no better way to do an intersection of two jquery objects!?
      parents = $(e.target).parents().andSelf().get();
      while(parents.length > 0){
        node = parents.pop();        
        target = selector.filter(function(index) { return selector.get(index) == node; });
        if (target.length > 0)
          break;
      }
      
      if ($(e.target).is("a"))
        e.preventDefault();

      cancels.push(function(){
        for (i in timeouts)
          clearTimeout(timeouts.pop());
        target.removeClass('active');
        $('body')
          .unbind('mousemove', checkMouse)
          .unbind('mouseout', checkMouse)
          .unbind('mouseup', defaultMouseUp);
      });

      $('body').mouseup(defaultMouseUp);              
      timeouts.push(setTimeout(function() {
        $('body')
          .unbind('mousemove', checkMouse)
          .unbind('mouseout', checkMouse);
        document.body.focus();
        target.addClass('active');    
        pi.css({ position: 'absolute', left: e.pageX, top: e.pageY }).fadeIn(100);       
        cancels.push(function(){
          pi.fadeOut(100);
        });
      }, 300));
      
      $('body').mousemove(checkMouse).mouseout(checkMouse);      
    };
    var selectionMouseUp = function(e) {
      while (cancels.length > 0)
        cancels.pop()();
      //menu items handled above
    };
    var defaultMouseUp = function(e) {
      while (cancels.length > 0)
        cancels.pop()();
      if (!moved(e)){
        if (menu.default){
          menu.default(e);
        }
      } else {
        if (menu.cancel){
          menu.cancel(e);
        }
      }
    };
           
    selector.mousedown(targetMouseDown);
  }
};
var insertSelectionTool = function() {
  $("body").prepend('\
      <div id="wiab_selection">\
        <div class="wiab_n" />\
        <div class="wiab_ne" />\
        <div class="wiab_e" />\
        <div class="wiab_se" />\
        <div class="wiab_s" />\
        <div class="wiab_sw" />\
        <div class="wiab_w" />\
        <div class="wiab_nw" />\
      </div>');
  selectionHandles = function(element) {
    $('#wiab_selection>.wiab_n' ).css({left: element.offset().left+element.width()/2, top: element.offset().top});
    $('#wiab_selection>.wiab_ne').css({left: element.offset().left+element.width(), top: element.offset().top});
    $('#wiab_selection>.wiab_e' ).css({left: element.offset().left+element.width(), top: element.offset().top+element.height()/2});
    $('#wiab_selection>.wiab_se').css({left: element.offset().left+element.width(), top: element.offset().top+element.height()});
    $('#wiab_selection>.wiab_s' ).css({left: element.offset().left+element.width()/2, top: element.offset().top+element.height()});
    $('#wiab_selection>.wiab_sw').css({left: element.offset().left, top: element.offset().top+element.height()});
    $('#wiab_selection>.wiab_w' ).css({left: element.offset().left, top: element.offset().top+element.height()/2});
    $('#wiab_selection>.wiab_nw').css({left: element.offset().left, top: element.offset().top});
    
    var timeouts = [];
    var cancels = [];
    var target = null;
    var originalLocation = {x: null, y: null};
    var startMove = function(e) {
      if (e.button != 0)
        return;    
      e.stopPropagation();
        
      target = $(e.target).parents(selector);

      var pageX = e.pageX;
      var pageY = e.pageY;
      originalLocation = { x: e.clientX, y: e.clientY };

      for (i in timeouts)
        clearTimeout(timeouts.pop());
    
    };
    var stopMove = function(e) {
    };
    
    $('#wiab_selection>*').mousedown(startMove);
  };
};

var click = function(e){  
  onClick = $(e.target).filter('a').attr('onClick');
  if (onClick){
    $(e.target).click();
  }  
  href = $(e.target).filter('a').attr('href');
  if (href){
    window.location = href;
  }
}

var mainMenu = function() {
  piMenu($('.cell'), {
    default: click,
    cancel: null,
    items: {
      s: item('Move', 'wiab_arrow', null),
      se: item('Edit', 'wiab_arrow', null),
      sw: item('Select', 'wiab_button', null),
      w: item('Paste', 'wiab_button', null),
    },
  }); 
};

$(function(){
  insertTools();
  mainMenu();
});
