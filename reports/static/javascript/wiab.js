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
      $('#wiab_guide_box').height(target.height()).width(target.width()).show();
      updateAnchorIndicators(element, currentLocation, currentDropTarget);

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
var toClassLine = function (edges) {
  var line = [];
  for (d in edges) {
    line.push('wiab_' + d + edges[d]);
  }
  return line.join(' ');
};
var getFarEdge = function() {
  var cells = moveGuide.cells;
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

var snapToSide = function (target, location) {
  var diff = (target.width() - target.height()) / 4;
  var outright = {
    x: diff > 0 ? diff : 0,
    y: diff < 0 ? -diff : 0
  };
  var from = { 
    west: Math.abs(location.x - target.offset().left),
    north: Math.abs(location.y - target.offset().top),
    east: Math.abs(-location.x + (target.offset().left + target.width())),
    south: Math.abs(-location.y + (target.offset().top + target.height()))
  };
  var minHorizontal = Math.min(from.west, from.east);
  var minVertical = Math.min(from.north, from.south);

  var edge;
  if (minHorizontal < outright.x) {
    edge = 'x';
  } else if (minVertical < outright.y) {
    edge = 'y'; 
  } else if (Math.abs(from.north - from.south) < outright.y*2){
    edge = 'x';
  } else if (Math.abs(from.west - from.east) < outright.x*2){
    edge = 'y';
  } else if (minHorizontal - outright.x < minVertical) {
    edge = 'x';
  } else {
    edge = 'y';
  } 
  switch(edge){
  case 'x':
    if (from.west < from.east) {
      console.log('west');
      return 'west';
    } else {
      console.log('east');
      return 'east';
    }
  case 'y':
    if (from.north < from.south) {
      console.log('north');
      return 'north';
    } else {
      console.log('south');
      return 'south';
    }
  }
};

var divideCell = function (cell, edge, offsets) {
  if (!offsets) {
    offsets = { top: 0, left: 0 };
  }
  var offset = {
    left: cell.offset().left + offsets.left,
    top: cell.offset().top + offsets.top
  };
  box = [
    {top: null, left: null, width: null, height: null},
    {top: null, left: null, width: null, height: null},
  ];
  switch (edge) {
  case "west":
    box[0].left = (offset.left) + "px";
    box[0].top = (offset.top) + "px";
    box[0].width = (cell.width() / 3) + "px";
    box[0].height = (cell.height()) + "px";

    box[1].left = (offset.left + cell.width()/3) + "px";
    box[1].top = (offset.top) + "px";
    box[1].width = (cell.width()*2/3) + "px";
    box[1].height = (cell.height()) + "px";
    break;
  case "east":
    box[0].left = (offset.left + cell.width()*2/3) + "px";
    box[0].top = (offset.top) + "px";
    box[0].width = (cell.width() / 3) + "px";
    box[0].height = (cell.height()) + "px";

    box[1].left = (offset.left) + "px";
    box[1].top = (offset.top) + "px";
    box[1].width = (cell.width()*2/3) + "px";
    box[1].height = (cell.height()) + "px";
    break;
  case "north":
    box[0].left = (offset.left) + "px";
    box[0].top = (offset.top) + "px";
    box[0].width = (cell.width()) + "px";
    box[0].height = (cell.height()/3) + "px";

    box[1].left = (offset.left) + "px";
    box[1].top = (offset.top + cell.height()/3) + "px";
    box[1].width = (cell.width()) + "px";
    box[1].height = (cell.height()*2/3) + "px";
    break;
  case "south":
    box[0].left = (offset.left) + "px";
    box[0].top = (offset.top + cell.height()*2/3) + "px";
    box[0].width = (cell.width()) + "px";
    box[0].height = (cell.height()/3) + "px";

    box[1].left = (offset.left) + "px";
    box[1].top = (offset.top) + "px";
    box[1].width = (cell.width()) + "px";
    box[1].height = (cell.height()*2/3) + "px";
    break;
  }
  return box;
};

var updateAnchorIndicators = function (selection, location, hover, move) {
  var target = updateAnchorIndicators.cells.whichParent($(hover));
  var edge = snapToSide(target, location);

  var box = move ? selection : $('#wiab_guide_box');
  var offset = {
    left: box.position().left - box.offset().left + target.offset().left,
    top: box.position().top - box.offset().top + target.offset().top
  }
  
  box = box[0].style;

  if (target[0] === selection[0]) {
    box.left = (offset.left) + "px";
    box.top = (offset.top) + "px";
    box.width = (target.width()) + "px";
    box.height = (target.height()) + "px";
    return;
  }
  
  sizes = divideCell(target, edge);
  
  box.left = sizes[0].left;
  box.top = sizes[0].top;
  box.width = sizes[0].width;
  box.height = sizes[0].height;
};

var moveGuide = function (selection, handle, delta) {
  var farEdge = getFarEdge();
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
  var target = updateAnchorIndicators.cells.whichParent($(hover));
  if (target[0] === selection[0]) {
    return;
  }

  var edge = snapToSide(target, location);

  var offset = {
    left: selection.position().left - selection.offset().left,
    top: selection.position().top - selection.offset().top
  }
  sizes = divideCell(target, edge, offset);


  console.log('selection ', selection.attr('class'));
  console.log('target ', target.attr('class'));
  
  var box = selection[0].style;
  box.left = sizes[0].left;
  box.top = sizes[0].top;
  box.width = sizes[0].width;
  box.height = sizes[0].height;

  var shoved = target[0].style;
  shoved.left = sizes[1].left;
  shoved.top = sizes[1].top;
  shoved.width = sizes[1].width;
  shoved.height = sizes[1].height;
  
  oldEdges = getEdges(selection[0]);
  
  edges = getEdges(target[0]);
  var farEdge = getFarEdge();

  var bumpGuides = function (index) {
    moveGuide.cells.each(function () {
      var edges = getEdges(this);
      var classes = {};
      if (edges.west >= index) {
        classes.west = index;
      }
      if (edges.east >= index) {
        classes.east = index;
      }
      $(this).removeClass(toClassLine(classes));
      for (var edge in classes) {
        classes[edge] += 1;
      }
      $(this).addClass(toClassLine(classes));
    });
  }

  var insertGuide = function (offset) {
    var farEdge = getFarEdge();
    var guides = []
    var currentOffset = 0;
    
    var checkGuide = function (index) {
      var west = $('wiab_west' + index);
      var east = $('wiab_east' + index);
      if (west.length > 0){
        currentOffset = west.offset().left;
      } else if (east.length > 0) {
        currentOffset = west.offset().left + west.width();
      } else {
        alert('Undefined guide '+index+' (last guide was '+currentOffset+')');
      }
      return offset < currentOffset
    }
    
    for (var i = 0; i <= farEdge.x; i++) {
      if (checkGuide(i))
        break;
      guides.push(currentOffset);
    }        
    guides.push(offset);
    bumpGuides(i);
    for (; i <= farEdge.x; i++) {
      checkGuide(i);
      guides.push(currentOffset);
    } 
  } 
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
