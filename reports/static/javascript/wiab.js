var fadeOutTime = 300;

jQuery.scope = function () {      
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
        cancels.pop().call(this);
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
jQuery.False = function () {
  return false;
};
jQuery.fn.whichParent = function (node) {
  var parents = node.parents().andSelf().get();
  var target = [];
  while (parents.length > 0) {
    var parent = parents.pop();
    target = this.filter(function (index) { 
      return this === parent; 
    });
    if (target.length > 0) {
      break;
    }
  }
  return target;
};

//////////////////////////////////////////////////

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
    children.css({ display: 'none' });
    
    var whileMenuShown = $.scope();
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
        child = children.filter(class_)
        child.addClass(menu.items[direction].style);
        child.html("<br/>" + menu.items[direction].label);
        
        if (menu.items[direction].action) {
          var action = menu.items[direction].action;                  
          whileMenuShown.bind(child, { 
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
      target = selector.whichParent($(e.target));

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



/////////////////////////////////////////////////////




var insertSelectionTool = function () {
  $("body").prepend('<div id="wiab_guide_horizontal" /><div id="wiab_guide_vertical" /><div id="wiab_guide_box" />');
  $("body").prepend('' +
    '<div id="wiab_selection">' +
    '  <div class="wiab_ne" />' +
    '  <div class="wiab_nw" />' +
    '  <div class="wiab_se" />' +
    '  <div class="wiab_sw" />' +
    '  <div class="wiab_n" />' +
    '  <div class="wiab_s" />' +
    '  <div class="wiab_e" />' +
    '  <div class="wiab_w" />' +
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
    $('#wiab_selection div').hover(function () {
      $(this).addClass('wiab_active');
    }, function () {
      $(this).removeClass('wiab_active');
    });
    $('#wiab_selection').show();
  };      
      
  var whileSelected = $.scope();      
  select = function (element, actions, selector) {
    whileSelected.stop();
    var selection = element;
    var initialClick = { x: null, y: null };
    var initialDelta = { x: null, y: null };
    var currentLocation = { x: null, y: null };
    var x = null, y = null;
    var target = null;
    var whileDragging = $.scope();
    if (!element) {
      setTimeout(function () { 
        $('#wiab_selection').fadeOut(fadeOutTime); 
      }, 0);
      return false;
    }

    updateSelectionBox(element);
    var currentDropTarget = null;
    var drag = function (e) {
      currentLocation = { x: e.pageX, y: e.pageY, scrollX: e.pageX - e.clientX, scrollY: e.pageY - e.clientY };
      currentDropTarget = e.target;
    };
    var vertical = $('#wiab_guide_vertical')[0].style;
    var horizontal = $('#wiab_guide_horizontal')[0].style;    
    var action = null;
    
    var updateGuideLocation = function () {
      vertical.left = currentLocation.x + initialDelta.x + "px";
      vertical.top = currentLocation.scrollY + "px";
      horizontal.left = currentLocation.scrollX + "px";
      horizontal.top = currentLocation.y + initialDelta.y + "px";  
    };
    var stopGuideDrag = function (e) {
      $('#wiab_guide_horizontal,#wiab_guide_vertical,#wiab_guide_box').fadeOut(fadeOutTime);
      whileDragging.stop();
      var delta = { x: currentLocation.x - initialClick.x, y: currentLocation.y - initialClick.y }; 
      action(selection, target, delta);
      updateSelectionBox(selection);
    };  
    var startGuideDrag = function (e) {
      if (e.button < 0) {
        return;    
      }
      e.stopPropagation();
      e.preventDefault();
      
      action = actions.edgeMoved;
      target = $(e.target);
      initialClick = { x: e.pageX, y: e.pageY };
      initialDelta = { x: null, y: null }; 
      
      if (isWest(target)) {
        initialDelta.x = selection.offset().left - e.pageX;
        $('#wiab_guide_vertical').show();
      } else if (isEast(target)) {
        initialDelta.x = 1 + selection.offset().left + selection.width() - e.pageX ;
        $('#wiab_guide_vertical').show();
      }
      if (isNorth(target)) {
        initialDelta.y = selection.offset().top - e.pageY;
        $('#wiab_guide_horizontal').show();
      } else if (isSouth(target)) {
        initialDelta.y = 1 + selection.offset().top + selection.height() - e.pageY;
        $('#wiab_guide_horizontal').show();
      }  
      
      drag(e);
      updateGuideLocation();      

      whileDragging.interval(updateGuideLocation, 15);
      whileDragging.bind($(document), {
        mousemove: drag,
        mouseup: stopGuideDrag
      });
    };    
    var stopCellDrag = function (e) {
      $('#wiab_guide_horizontal,#wiab_guide_vertical,#wiab_guide_box').fadeOut(fadeOutTime);
      whileDragging.stop();
      actions.objectMoved(element, currentLocation, currentDropTarget);
      //actions.objectMoved(selection, target, edge);
      updateSelectionBox(selection);
    };
    var startCellDrag = function (e) {
      if (e.button < 0) {
        return;    
      }
      e.stopPropagation();
      e.preventDefault();
      
      $('div.cell').addClass('wiab_front');
      
      action = actions.objectMoved;
      target = element;
      initialClick = { x: e.pageX, y: e.pageY };
      initialDelta = { x: target.offset().left - e.pageX, y: target.offset().top - e.pageY };      

      drag(e);
      updateAnchorIndicators(element, currentLocation, currentDropTarget);
      $('#wiab_guide_box').height(target.height()).width(target.width()).show();

      whileDragging.interval(function () { actions.objectMoving(selection, currentLocation, currentDropTarget); }, 200);
      whileDragging.after(function () {
        $('div.cell').removeClass('wiab_front');
      });
      whileDragging.bind($(document.body), {
        mousemove: drag,
        mouseup: stopCellDrag
      });
    };    

    whileSelected.bind($('#wiab_selection>div'), { mousedown: startGuideDrag });
    whileSelected.bind(element, { mousedown: startCellDrag });
    whileSelected.bind($('body'), { mousedown: function () { 
      return select(null); 
    } });          
  };
  select.actions = function (actions, selector) {
    return function (element) {
      select(element, actions, selector);
    };
  };

};


////////////////////////////////////////////


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

var ifEdge = function (then) {
  return function () {
    var query = this.match(/wiab_(\D+)(\d+)/);
    if (!query || !query[1].match(/north|south|east|west/)) {
      return;
    }
    edge = query[1];
    index = parseInt(query[2], 10);
    
    then.call(this, edge, index); 
  }
};
var getEdges = function (cell) {
  var edges = {};
  $.each(cell.className.split(' '), ifEdge(function (edge, index) {
    edges[edge] = index;
  }));
  return edges;
};
var getFarEdge = function(cells) {
  var farEdge = { x: 0, y: 0 }
  var cellClasses = [];
  cells.each(function () { 
    cellClasses = cellClasses.concat(this.className.split(' '));
  }) 
  $.each(cellClasses, ifEdge(function (edge, index) {
    if (farEdge.y < index && (edge === 'north' || edge === 'south')) {
      farEdge.y = index;
    } else if (farEdge.x < index && (edge === 'west' || edge === 'east')) {
      farEdge.x = index;
    }
  }));
  return farEdge;
};

var updateAnchorIndicators = function (selection, location, hover, move) {
  var target = updateAnchorIndicators.cells.whichParent($(hover));
  var box = move ? selection : $('#wiab_guide_box');
  var offset = move ? target.position() : target.offset(); //KILL THIS 
  
  box = box[0].style;
  
  if (target[0] === selection[0]) {
    box.left = (offset.left) + "px";
    box.top = (offset.top) + "px";
    box.width = (target.width()) + "px";
    box.height = (target.height()) + "px";      
    return;
  }
  var side = { 
    west: Math.abs(location.x - target.offset().left),
    north: Math.abs(location.y - target.offset().top),
    east: Math.abs(location.x - (target.offset().left + target.width())),
    south: Math.abs(location.y - (target.offset().top + target.height()))
  };
  var edge;
  if (Math.min(side.west, side.east) < Math.min(side.north, side.south)) {
    edge = side.west < side.east ? 'west' : 'east';
  } else {
    edge = side.north < side.south ? 'north' : 'south';
  } 

  switch(edge){
  case "west":
    box.left = (offset.left) + "px";
    box.top = (offset.top) + "px";
    box.width = (target.width() / 3) + "px";
    box.height = (target.height()) + "px";
    break;
  case "east":
    box.left = (offset.left + target.width()*2/3) + "px";
    box.top = (offset.top) + "px";
    box.width = (target.width() / 3) + "px";
    box.height = (target.height()) + "px";
    break;
  case "north":
    box.left = (offset.left) + "px";
    box.top = (offset.top) + "px";
    box.width = (target.width()) + "px";
    box.height = (target.height()/3) + "px";
    break;
  case "south":
    box.left = (offset.left) + "px";
    box.top = (offset.top + target.height()*2/3) + "px";
    box.width = (target.width()) + "px";
    box.height = (target.height()/3) + "px";
    break;
  }
};

var moveGuide = function (selection, handle, delta) {
  var farEdge = getFarEdge(moveGuide.cells);
  var edges = getEdges(selection[0]);
  
  var x = null;
  var y = null;
  if (isWest(handle)) {
    x = { guide: edges.west, edge: 'west' };

    moveGuide.cells.each(function () {  
      var cell = getEdges(this);
      var location = $(this).position();
      if (x.guide !== 0 && cell.west === 0 && cell.east > x.guide) {
        return;
      } else if (x.guide !== 0 && cell.west === 0 && cell.east <= x.guide) {
        $(this).width($(this).width() + delta.x);
      } else if (cell.west <= x.guide && cell.east > x.guide) {
        $(this).width($(this).width() - delta.x);
        $(this).css({ left: location.left + delta.x});
      } else if (cell.west <= x.guide && cell.east <= x.guide) {
        $(this).css({ left: location.left + delta.x});
      }
    });
  } else if (isEast(handle)) {
    x = { guide: edges.east, edge: 'east' };
    
    moveGuide.cells.each(function () {  
      var cell = getEdges(this);
      var location = $(this).position();
      if (x.guide !== farEdge.x && cell.east === farEdge.x && cell.west < x.guide) {
        return;
      } else if (x.guide !== farEdge.x && cell.east === farEdge.x && cell.west >= x.guide) {
        $(this).css({ left: location.left + delta.x});
        $(this).width($(this).width() - delta.x);
      } else if (cell.east >= x.guide && cell.west < x.guide) {
        $(this).width($(this).width() + delta.x);
      } else if (cell.east >= x.guide && cell.west >= x.guide) {
        $(this).css({ left: location.left + delta.x});
      }
    });
  }
  
  if (isNorth(handle)) {
    y = { guide: edges.north, edge: 'north' };

    moveGuide.cells.each(function () {  
      var cell = getEdges(this);
      var location = $(this).position();
      if (y.guide !== 0 && cell.north === 0 && cell.south > y.guide) {
        return;
      } else if (y.guide !== 0 && cell.north === 0 && cell.south <= y.guide) {
        $(this).height($(this).height() + delta.y);
      } else if (cell.north <= y.guide && cell.south > y.guide) {
        $(this).height($(this).height() - delta.y);
        $(this).css({ top: location.top + delta.y});
      } else if (cell.north <= y.guide && cell.south <= y.guide) {
        $(this).css({ top: location.top + delta.y});
      }
    });
  } else if (isSouth(handle)) {
    y = { guide: edges.south, edge: 'south' };
    
    moveGuide.cells.each(function () {  
      var cell = getEdges(this);
      var location = $(this).position();
      if (cell.south >= y.guide && cell.north < y.guide) {
        $(this).height($(this).height() + delta.y);
      } else if (cell.south >= y.guide && cell.north >= y.guide) {
        $(this).css({ top: location.top + delta.y});
      }
    });
  }
};
var moveObject = function (selection, location, hover) { 
  //(selection, handle, delta) {
  updateAnchorIndicators(selection, location, hover, true);
//  return; 
//  var farEdge = getFarEdge(moveGuide.cells);
//  var edges = getEdges(selection[0]);
//  
//  var pos = selection.position()
//  selection.css({ left: pos.left + delta.x, top: pos.top + delta.y }); 

//  return;
//  var uses = { north: 0, south: 0, east: 0, west: 0 };
//  uses.west += $('div.cell.wiab_west' + edges.west).length;
//  uses.west += $('div.cell.wiab_east' + edges.west).length;
//  uses.east += $('div.cell.wiab_west' + edges.east).length;
//  uses.east += $('div.cell.wiab_east' + edges.east).length;  
//  uses.north += $('div.cell.wiab_north' + edges.north).length;
//  uses.north += $('div.cell.wiab_south' + edges.north).length;
//  uses.south += $('div.cell.wiab_north' + edges.south).length;
//  uses.south += $('div.cell.wiab_south' + edges.south).length;
//  
//  if (uses.west > 1) {
//    $('div.wiab_')
//    selection.removeClass('wiab_west' + edges.west);
//    selection.removeClass('wiab_west' + edges.west);
//  }
//  $.each(selection[0].className.split(' '), function () {
//    var query = this.match(/wiab_(\D+)(\d+)/);
//    if (!query || !query[1].match(/north|south|east|west/)) {
//      return;
//    }
//    
//    edge = query[1]
//    index = query[2]
//    edges[edge] = index;
//  });
}

var mainMenu = function () {
  cells = $('div.cell');
  moveGuide.cells = cells;
  moveObject.cells = cells;
  updateAnchorIndicators.cells = cells;
  piMenu(cells, {
    primary: click,
    cancel: null,
    items: {
      s: item('Move', 'wiab_arrow', select.actions( { 
        edgeMoved: moveGuide, 
        objectMoved: moveObject, 
        objectMoving: updateAnchorIndicators
      }, cells )),
      se: item('Edit', 'wiab_arrow', null),
      sw: item('Style', 'wiab_arrow', null),
      w: item('Current', 'wiab_button', null)
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
