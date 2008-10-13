var fadeOutTime = 300;

var scope = function(){      
  var intervals = [];
  var timeouts = [];
  var cancels = [];
  var scope = {      
    stop: function() {
      while (timeouts.length > 0) {
        clearTimeout(timeouts.pop());
      }
      while (intervals.length > 0) {
        clearInterval(intervals.pop());
      }
      while(cancels.length > 0) {
        cancels.pop()();        
      }
    },
    after: function(func) {
      cancels.push(func);
      return scope;
    },
    bind: function(query, bindings) {
      cancels.push(function() {
        for (var event in bindings){
          query.unbind(event, bindings[event]);
        }
      });
      
      for (var event in bindings) {          
        query.bind(event, bindings[event]);
      }        
      return scope;
    },
    interval: function(func, time) {
      intervals.push(setInterval(func, time));
      return scope;
    },
    timeout: function(func, time) {
      timeouts.push(setTimeout(func, time));
      return scope;
    }
  };
  return scope;
};
var whichParent = function(selector, node) {
  var parents = node.parents().andSelf().get();
  var target = [];
  while(parents.length > 0){
    var parent = parents.pop();        
    target = selector.filter(function(index) { return selector.get(index) === parent; });
    if (target.length > 0){        
      break;
    }
  }
  return target.length > 0 ? target : null;
};
    
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
    
    var whileMenuShown = scope();
    var originalTarget = null;
    var target = null;
    var originalLocation = {x: null, y: null};
    var moved = function(e){
      return Math.abs(e.clientX-originalLocation.x) > 2 || Math.abs(e.clientY-originalLocation.y) > 5;
    };
    
    var showMenu = function(e) {
      whileMenuShown.stop();
      whileMenuShown.bind($('body'), { mouseup: defaultMouseUp });
      document.body.focus();
      target.addClass('active');    
    
      var show = '';
      for (direction in menu.items) {
        _class = '.wiab_' + direction
        show += _class + ',';
        children.filter(_class)
          .addClass(menu.items[direction].style)
          .html("<br/>" + menu.items[direction].label);
        if (menu.items[direction].action) {
          var action = menu.items[direction].action;                  
          whileMenuShown.bind(children, { mouseup: function() { action(target); } }); 
        }
      }
      children.filter(show).css({display: 'block'})
      
      pi.css({ position: 'absolute', left: e.pageX, top: e.pageY }).show();       
      whileMenuShown.after(function(){
        target.removeClass('active');
        pi.fadeOut(fadeOutTime);
      });
    };
    
    //var cancels = [];
    
    var targetMouseDown = function(e) {
      if (e.button != 0)
        return;
      //e.stopPropagation();
      originalLocation = { x: e.clientX, y: e.clientY };
      
      var timeouts = [];
      var checkMouse = function(e){
        if (moved(e)){
          whileMenuShown.stop();
        }
      };
      originalTarget = e.target;
      target = whichParent(selector, $(e.target));

      
      if ($(e.target).is("a"))
        e.preventDefault();

      

      whileMenuShown.bind($('body'), { mouseup: defaultMouseUp });
      whileMenuShown.timeout(function() {
        showMenu(e);
      }, 300);
      
      whileMenuShown.bind($('body'), { mousemove: checkMouse, mouseout: checkMouse });      
    };
    var selectionMouseUp = function(e) {
      whileMenuShown.stop();
      //menu items handled above
    };
    var defaultMouseUp = function(e) {
      whileMenuShown.stop();
      if (!moved(e)){
        e.target = originalTarget;
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
  $("body").prepend('<div id="wiab_guide_horizontal" /><div id="wiab_guide_vertical" />');
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
          
  var isWest = function(query){
    return query.is('div.wiab_w,div.wiab_sw,div.wiab_nw');
  };
  var isEast = function(query){
    return query.is('div.wiab_e,div.wiab_se,div.wiab_ne');
  };
  var isNorth = function(query){
    return query.is('div.wiab_n,div.wiab_nw,div.wiab_ne');
  };
  var isSouth = function(query){
    return query.is('div.wiab_s,div.wiab_sw,div.wiab_se');
  };  
  var updateSelectionBox = function(element) {      
    $('#wiab_selection>.wiab_n' ).css({left: element.offset().left+element.width()/2, top: element.offset().top});
    $('#wiab_selection>.wiab_ne').css({left: element.offset().left+element.width(), top: element.offset().top});
    $('#wiab_selection>.wiab_e' ).css({left: element.offset().left+element.width(), top: element.offset().top+element.height()/2});
    $('#wiab_selection>.wiab_se').css({left: element.offset().left+element.width(), top: element.offset().top+element.height()});
    $('#wiab_selection>.wiab_s' ).css({left: element.offset().left+element.width()/2, top: element.offset().top+element.height()});
    $('#wiab_selection>.wiab_sw').css({left: element.offset().left, top: element.offset().top+element.height()});
    $('#wiab_selection>.wiab_w' ).css({left: element.offset().left, top: element.offset().top+element.height()/2});
    $('#wiab_selection>.wiab_nw').css({left: element.offset().left, top: element.offset().top});
    $('#wiab_selection').show();
  };      
      
  var whileSelected = scope();      
  select = function(element) {
    whileSelected.stop();
    var selection = element;
    var initialClick = { x: null, y: null };
    var initialDelta = { x: null, y: null };
    var currentLocation = { x: null, y: null };
    var x = null, y = null;
    var target = null;
    var whileDragging = scope();
    if (!element) {
      setTimeout(function() { $('#wiab_selection').fadeOut(fadeOutTime); }, 0);
      return false;
    }

    updateSelectionBox(element);

    var startDrag = function(e) {
      if (e.button != 0)
        return;    
      e.stopPropagation();
      e.preventDefault();
               
      target = $(e.target);        
      x = isWest(target) || isEast(target);
      y = isNorth(target) || isSouth(target);
      initialClick = { x: e.pageX, y: e.pageY };
      initialDelta = { x: target.offset().left - e.pageX, y: target.offset().top - e.pageY };      
      if (isEast(target)) {
        initialDelta.x++;
      }
      if (isSouth(target)) {
        initialDelta.y++;
      }  
      
      drag(e);
      updateLocation(e);
      if (y){
        $('#wiab_guide_horizontal').show();
      }
      if (x){
        $('#wiab_guide_vertical').show();
      }

      whileDragging.interval(updateLocation, 15);
      whileDragging.bind($('*'), {
        mousemove: drag,
        mouseup: stopDrag
      });    
    };
    var drag = function(e) {
      e.stopPropagation();
      currentLocation = { x: e.pageX, y: e.pageY, pageX: e.pageX - e.clientX, pageY: e.pageY - e.clientY };
    };
    var _odd = false
    var updateLocation = function() {
      _odd = !_odd;          
      if (_odd && x){ 
        $('#wiab_guide_vertical').css({ left: currentLocation.x + initialDelta.x, top: currentLocation.pageY });
      } 
      if (!_odd && y){
        $('#wiab_guide_horizontal').css({ left: currentLocation.pageX, top: currentLocation.y + initialDelta.y });
      }
    };    
    var stopDrag = function(e) {
      $('#wiab_guide_horizontal,#wiab_guide_vertical').fadeOut(fadeOutTime);
      whileDragging.stop();
      var finalLocation = currentLocation;
      selection.each(function() {
        var location = $(this).position();
        var size = { width: $(this).width(), height: $(this).height() };
        var delta = { x: finalLocation.x - initialClick.x, y: finalLocation.y - initialClick.y }; 
        if (isWest(target)) {              
          $(this).css({ left: location.left + delta.x});
          $(this).width(size.width - delta.x);                            
        } else if (isEast(target)) {
          $(this).width(size.width + delta.x);
        }
        if (isNorth(target)) {
          $(this).css({ top: location.top + delta.y});
          $(this).height(size.height - delta.y);                            
        } else if (isSouth(target)) {
          $(this).height(size.height + delta.y);
        }
      });
      updateSelectionBox(selection);
    };    

    whileSelected.bind($('#wiab_selection>div'), { mousedown: startDrag });
    whileSelected.bind(element, { mousedown: function() { return false; } });
    whileSelected.bind($('body'), { mousedown: function() { return select(null); } });          
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
      s: item('Move', 'wiab_arrow', select),
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
