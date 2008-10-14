var fadeOutTime = 300;

var scope = function () {      
  var intervals = [];
  var timeouts = [];
  var cancels = [];
  var scope = {      
    stop: function () {
      while (timeouts.length > 0) {
        clearTimeout(timeouts.pop());
      }
      while (intervals.length > 0) {
        clearInterval(intervals.pop());
      }
      while (cancels.length > 0) {
        cancels.pop()();        
      }
    },
    after: function (func) {
      cancels.push(func);
      return scope;
    },
    bind: function (query, bindings) {
      cancels.push(function () {
        for (var event in bindings) {
          query.unbind(event, bindings[event]);
        }
      });
      
      for (var event in bindings) {          
        query.bind(event, bindings[event]);
      }        
      return scope;
    },
    interval: function (func, time) {
      intervals.push(setInterval(func, time));
      return scope;
    },
    timeout: function (func, time) {
      timeouts.push(setTimeout(func, time));
      return scope;
    }
  };
  return scope;
};
var False = function () {
  return false;
};
var whichParent = function (selector, node) {
  var parents = node.parents().andSelf().get();
  var target = [];
  while (parents.length > 0) {
    var parent = parents.pop();        
    target = selector.filter(function (index) { 
      return selector.get(index) === parent; 
    });
    if (target.length > 0) {
      break;
    }
  }
  return target.length > 0 ? target : null;
};
var insertPiMenu = function () {
  var toolTemplate = '' +
    '<img id="wiab_image" src="/static/images/1.png" />' +
    '    <a rel="nofollow" class="wiab_n wiab"><br /></a>' +
    '    <a rel="nofollow" class="wiab_ne wiab"><br /></a>' +
    '    <a rel="nofollow" class="wiab_e wiab"><br /></a>' +
    '    <a rel="nofollow" class="wiab_se wiab"><br /></a>' +
    '    <a rel="nofollow" class="wiab_s wiab"><br /></a>' +
    '    <a rel="nofollow" class="wiab_sw wiab"><br /></a>' +
    '    <a rel="nofollow" class="wiab_w wiab"><br /></a>' +
    '    <a rel="nofollow" class="wiab_nw wiab"><br /></a>' +
    '';

  $("body").prepend('<div id="wiab_tool_1" class="wiab_tool" >' + toolTemplate + '</div>');
  $("body").prepend('<div id="wiab_tool_2" class="wiab_tool" >' + toolTemplate + '</div>');
  $('.wiab_tool>.wiab').hover(function () {
    $(this).addClass('wiab_active');
  }, function () {
    $(this).removeClass('wiab_active');
  });
    
  var toolDiv = true;
  var getMenu = function () {  
    toolDiv = !toolDiv;
    if (toolDiv) {
      return $('#wiab_tool_1');
    } else {
      return $('#wiab_tool_2');
    }
  };
  
  item = function (label, style, action) {
    return { label: label, style: style, action: action };
  }; 
  piMenu = function (selector, menu) {
    var pi = getMenu();    
    var all = '.wiab_w,.wiab_e,.wiab_n,.wiab_s,.wiab_nw,.wiab_se,.wiab_ne,.wiab_sw';
    var children = pi.children(all);
    children.css({display: 'none'});
    
    var whileMenuShown = scope();
    var originalTarget = null;
    var target = null;
    var originalLocation = {x: null, y: null};
    var moved = function (e) {
      return Math.abs(e.clientX - originalLocation.x) > 2 || Math.abs(e.clientY - originalLocation.y) > 5;
    };
    
    var defaultMouseUp = function (e) {
      whileMenuShown.stop();
      if (!moved(e)) {
        e.target = originalTarget;
        if (menu.primary) {
          menu.primary(e);
        }
      } else {
        if (menu.cancel) {
          menu.cancel(e);
        }
      }
    };
    
    var showMenu = function (e) {
      whileMenuShown.stop();
      whileMenuShown.bind($('body'), { mouseup: defaultMouseUp });
      document.body.focus();
      target.addClass('active');    
    
      var show = '';
      for (var direction in menu.items) {
        var class_ = '.wiab_' + direction;
        show += class_ + ',';
        children.filter(class_)
          .addClass(menu.items[direction].style)
          .html("<br/>" + menu.items[direction].label);
        if (menu.items[direction].action) {
          var action = menu.items[direction].action;                  
          whileMenuShown.bind(children, { 
            mouseup: function () { 
              whileMenuShown.stop();
              action(target); 
            } 
          }); 
        }
      }
      children.filter(show).css({display: 'block'});
      
      pi.css({ position: 'absolute', left: e.pageX, top: e.pageY }).show();       
      whileMenuShown.after(function () {
        target.removeClass('active');
        pi.fadeOut(fadeOutTime);
      });
    };
    
    //var cancels = [];
    
    var targetMouseDown = function (e) {
      if (e.button > 0) {
        return;
      }
      //e.stopPropagation();
      originalLocation = { x: e.clientX, y: e.clientY };
      
      var checkMouse = function (e) {
        if (moved(e)) {
          whileMenuShown.stop();
        }
      };
      originalTarget = e.target;
      target = whichParent(selector, $(e.target));

      if ($(e.target).is("a")) {
        e.preventDefault();
      }
      
      whileMenuShown.bind($('body'), { mouseup: defaultMouseUp });
      whileMenuShown.timeout(function () {
        showMenu(e);
      }, 300);
      
      whileMenuShown.bind($('body'), { mousemove: checkMouse, mouseout: checkMouse });      
    };
           
    selector.mousedown(targetMouseDown);
  };
};
var insertSelectionTool = function () {
  $("body").prepend('<div id="wiab_guide_horizontal" /><div id="wiab_guide_vertical" />');
  $("body").prepend('' +
    '<div id="wiab_selection">' +
    '  <div class="wiab_n" />' +
    '  <div class="wiab_ne" />' +
    '  <div class="wiab_e" />' +
    '  <div class="wiab_se" />' +
    '  <div class="wiab_s" />' +
    '  <div class="wiab_sw" />' +
    '  <div class="wiab_w" />' +
    '  <div class="wiab_nw" />' +
    '</div>');
          
  isWest = function (query) {
    return query.is('div.wiab_w,div.wiab_sw,div.wiab_nw');
  };
  isEast = function (query) {
    return query.is('div.wiab_e,div.wiab_se,div.wiab_ne');
  };
  isNorth = function (query) {
    return query.is('div.wiab_n,div.wiab_nw,div.wiab_ne');
  };
  isSouth = function (query) {
    return query.is('div.wiab_s,div.wiab_sw,div.wiab_se');
  };  
  var updateSelectionBox = function (element) {      
    $('#wiab_selection>.wiab_n ').css({ left: element.offset().left + element.width() / 2, top: element.offset().top });
    $('#wiab_selection>.wiab_ne').css({ left: element.offset().left + element.width(), top: element.offset().top });
    $('#wiab_selection>.wiab_e ').css({ left: element.offset().left + element.width(), top: element.offset().top + element.height() / 2 });
    $('#wiab_selection>.wiab_se').css({ left: element.offset().left + element.width(), top: element.offset().top + element.height() });
    $('#wiab_selection>.wiab_s ').css({ left: element.offset().left + element.width() / 2, top: element.offset().top + element.height() });
    $('#wiab_selection>.wiab_sw').css({ left: element.offset().left, top: element.offset().top + element.height() });
    $('#wiab_selection>.wiab_w ').css({ left: element.offset().left, top: element.offset().top + element.height() / 2 });
    $('#wiab_selection>.wiab_nw').css({ left: element.offset().left, top: element.offset().top });
    $('#wiab_selection').show();
  };      
      
  var whileSelected = scope();      
  select = function (element, actions) {
    whileSelected.stop();
    var selection = element;
    var initialClick = { x: null, y: null };
    var initialDelta = { x: null, y: null };
    var currentLocation = { x: null, y: null };
    var x = null, y = null;
    var target = null;
    var whileDragging = scope();
    if (!element) {
      setTimeout(function () { 
        $('#wiab_selection').fadeOut(fadeOutTime); 
      }, 0);
      return false;
    }

    updateSelectionBox(element);
    var drag = function (e) {
      e.stopPropagation();
      currentLocation = { x: e.pageX, y: e.pageY, pageX: e.pageX - e.clientX, pageY: e.pageY - e.clientY };
    };
    var odd_ = false;
    var updateLocation = function () {
      odd_ = !odd_;          
      if (odd_ && x) { 
        $('#wiab_guide_vertical').css({ left: currentLocation.x + initialDelta.x, top: currentLocation.pageY });
      } 
      if (!odd_ && y) {
        $('#wiab_guide_horizontal').css({ left: currentLocation.pageX, top: currentLocation.y + initialDelta.y });
      }
    };    
    var stopDrag = function (e) {
      $('#wiab_guide_horizontal,#wiab_guide_vertical').fadeOut(fadeOutTime);
      whileDragging.stop();
      var delta = { x: currentLocation.x - initialClick.x, y: currentLocation.y - initialClick.y }; 
      actions.moved(selection, target, delta);
      updateSelectionBox(selection);
    };  
    var startDrag = function (e) {
      if (e.button < 0) {
        return;    
      }
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
      if (y) {
        $('#wiab_guide_horizontal').show();
      }
      if (x) {
        $('#wiab_guide_vertical').show();
      }

      whileDragging.interval(updateLocation, 15);
      whileDragging.bind($('*'), {
        mousemove: drag,
        mouseup: stopDrag
      });    
    };

    whileSelected.bind($('#wiab_selection>div'), { mousedown: startDrag });
    whileSelected.bind(element, { mousedown: False });
    whileSelected.bind($('body'), { mousedown: function () { 
      return select(null); 
    } });          
  };
  select.actions = function (actions) {
    return function (element) {
      select(element, actions);
    };
  };

};


var click = function (e) {  
  var onClick = $(e.target).filter('a').attr('onClick');
  if (onClick) {
    $(e.target).click();
  }  
  var href = $(e.target).filter('a').attr('href');
  if (href) {
    window.location = href;
  }
};

var moveGuide = function (selection, handle, delta) {
  var edges = { x: [], y: [] };
  $.each(selection[0].className.split(' '), function () {
    query = this.match(/wiab_(\D+)(\d+)/);
    if (!query || !query[1].match(/north|south|east|west/)) {
      return;
    }
    edges[query[1]] = query[2];
  });

  var x = null;
  var y = null;
  if (isWest(handle)) {
    x = { guide: edges.west };
  } else if (isEast(handle)) {
    x = { guide: edges.east };
  }
  if (isNorth(handle)) {
    y = { guide: edges.north };
  } else if (isSouth(handle)) {
    y = { guide: edges.south };
  }  
  
  var update = {
    north: function () {
      var location = $(this).position();
      var size = { width: $(this).width(), height: $(this).height() };  
      $(this).css({ top: location.top + delta.y});
      $(this).height(size.height - delta.y);                            
    },
    south: function () {
      var location = $(this).position();
      var size = { width: $(this).width(), height: $(this).height() };  
      $(this).height(size.height + delta.y);
    },
    east: function () {
      var location = $(this).position();
      var size = { width: $(this).width(), height: $(this).height() };  
      $(this).width(size.width + delta.x);
    },
    west: function () {
      var location = $(this).position();
      var size = { width: $(this).width(), height: $(this).height() };  
      $(this).css({ left: location.left + delta.x});
      $(this).width(size.width - delta.x);                            
    },
  }
  
  if (x) {
    $('div.wiab_west'+x.guide).each(update.west);
    $('div.wiab_east'+x.guide).each(update.east);
  }
  if (y) {
    $('div.wiab_north'+y.guide).each(update.north);
    $('div.wiab_south'+y.guide).each(update.south);
  }
  

};
var mainMenu = function () {
  piMenu($('div.cell'), {
    primary: click,
    cancel: null,
    items: {
      s: item('Move', 'wiab_arrow', select.actions({moved: moveGuide})),
      se: item('Edit', 'wiab_arrow', null),
      sw: item('Select', 'wiab_button', null),
      w: item('Paste', 'wiab_button', null)
    }
  });
};

var insertTools = function () {
  insertPiMenu();
  insertSelectionTool();
};

$(function () {
  insertTools();
  mainMenu();
});
