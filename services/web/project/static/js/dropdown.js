$(function() {
  var dropdown = {
    area: $('#select_area'),
    pref: $('#select_pref')
  };
  updateLocations();

  function updateLocations() {
    var send = {
      area: dropdown.area.val()
    };
    dropdown.pref.attr('disabled', 'disabled');
    dropdown.pref.empty();
    $.getJSON(dd_location_url, send, function(data) {
      data.forEach(function(item) {
        dropdown.pref.append(
          $('<option>', {
            value: item[0],
            text: item[1]
          })
        );
      });
      dropdown.pref.removeAttr('disabled');
    });
  }
  dropdown.area.on('change', function() {
    updateLocations();
  });
});

$(function() {
  var dropdown = {
    parent: $('#select_parent'),
    child: $('#select_child')
  };
  updateCategories();

  function updateCategories() {
    var send = {
      parent: dropdown.parent.val()
    };
    dropdown.child.attr('disabled', 'disabled');
    dropdown.child.empty();
    $.getJSON(dd_category_url, send, function(data) {
      data.forEach(function(item) {
        dropdown.child.append(
          $('<option>', {
            value: item[0],
            text: item[1]
          })
        );
      });
      dropdown.child.removeAttr('disabled');
    });
  }
  dropdown.parent.on('change', function() {
    updateCategories();
  });
});
