var mainMenu = function () {
  $("body").prepend('' +
    '<div id="wiab_editor" class="wiab">' +
    '  <form>' +
    '    <textarea name="data">' +
    '    </textarea>' +
    '  </form>' +
    '</div>');

  $.fn.dimensions = function () {
    var dimensions = $(this).offset();
    dimensions.width = $(this).width();
    dimensions.height = $(this).height();
    return dimensions;
  };

  var edit = function (target) {
    var html = target.html();
    var editor = $('#wiab_editor');
    target.fadeOut(200, function () {
      editor.css("z-index", "20");
    });
    editor.css(target.dimensions());
    editor.css("z-index", "0");
    
    $('#wiab_editor textarea').text(html);
    
    editor.show();
  };

  guides.cells = $('div.cell');
  piMenu(guides.cells, {
    primary: click,
    cancel: null,
    items: {
      s: item('Move', 'wiab_arrow', select.actions({ 
        edgeMoved: moveGuide, 
        objectMoved: moveObject, 
        objectMoving: updateAnchorIndicators
      }, guides.cells)),
      se: item('Edit', 'wiab_arrow', edit),
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
