$(document).ready(function () {
  $('#models').on('click', 'a', on_load);
  //
  $('#values').on('click', 'td:not(.edt,.pk)', on_edit);
  $('#values').on('focusout', 'td.edt input:not(.date)', on_edited);
});

function on_load() {
  var li = $(this).parent();
  // Makes the model active
  $('#models li.active').removeClass('active');
  li.addClass('active');
  // Loads data from the model
  load_data(li.attr('id'), function on_loaded(data) {
    if ('fields' in data) {
      // Adds table head
      add_fields(data.fields);
      // Adds table rows
      if ('values' in data) {
        add_values(data.values);
      }
      // Adds inputs for new data
      add_blanks(data.fields);
    }
  });
}

function on_edit() {
  var td = $(this);
  var val = td.html();
  //
  var fld = field_by_cell(td);
  var id = fld.data('id');
  var tp = fld.data('type');
  //
  td.html('<input id="' + id + '" class="' + tp + '" type="text" name="' + id +
          '" value="' + val + '" size="10" data-orig="' + val + '" />');
  //
  if (tp === 'date') {
    $('#' + id).datepicker({dateFormat: 'yy-mm-dd', onClose: on_edited});
  }
  //
  td.toggleClass('edt');
  $('#' + id).focus();
}

function on_edited() {
  var td = $(this).parent();
  var val = $(this).val();
  // Completes editing
  td.html(val);
  td.toggleClass('edt');
  // Updating data
  var org = $(this).data('orig'); // original value
  if (val != org) { // => value changed
    var fld = field_by_cell(td);
    var type = fld.data('type');
    //
    if (is_valid(type, val)) {
      var vals = {};
      vals[fld.data('id')] = val;
      //
      var mdl_id = $('#models li.active').attr('id');
      var pk = td.parent('tr').data('pk');
      send_data('update', mdl_id + '/' + pk, vals, function on_sent(data) {
        //console.log(data);
      });
    }
    else {
      alert('Value "' + val + '" must be of type ' + type);
      td.html(org);
    }
  }
  // Otherwise => no change, do nothing
}

function load_data(prms, on_loaded) {
  $.ajax({
    url: '/data/' + prms + '/',
    type: 'GET',
    dataType: 'json',
    cache: false,
    success: on_loaded,
    failure: _on_fail
  });

  function _on_fail(data) { 
    alert('Data loading failed');
  }
}

function is_valid(type, val) {
  if (type === 'int') {
    return !isNaN(Number(val));
  }
  if (type === 'date') {
    return (val.match(/^\d{4}-\d{2}-\d{2}$/) !== null);
  }
  // Otherwise => char
  return true;
}

function send_data(act, prms, data, on_sent) {
  $.ajax({
    url: '/' + act + '/' + prms + '/',
    type: 'POST',
    data: data,
    dataType: 'json',
    cache: false,
    success: on_sent,
    failure: _on_fail
  });

  function _on_fail(data) { 
    alert('Data updating failed');
  }
}

function field_by_index(i) {
  return $($('#fields').find('th').get(i));
}

function field_by_cell(td) {
  return field_by_index(td.index());
}

function add_fields(flds) {
  var tr = $('#fields');
  // Removes all header items
  tr.empty();
  // Adds the header
  tr.append('<th class="pk">#</th>');
  var fld;
  var n = flds.length;
  for (var i = 0; i < n; i++) {
    fld = flds[i];
    tr.append('<th data-id="' + fld.id + '" data-type="' + fld.type + '">' +
              (('title' in fld) ? fld.title : fld.id) + '</th>');
  }
  tr.append('<th class="ctrl"></th>');
}

function add_values(vals) {
  // Removes all data cells
  $('#values').empty();
  // Adds rows of data
  var n = vals.length;
  for (var i = 0; i < n; i++) {
    add_values_row(vals[i]);
  }
}

function add_values_row(vals) {
  var n = vals.length;
  if (n > 0) {
    var pk = vals[0];
    var tr = $('<tr data-pk="' + pk + '"></tr>');
    $('#values').append(tr);
    // Adds one row of data
    tr.append('<td class="pk">' + pk + '</td>');
    for (var i = 1; i < n; i++) {
      tr.append('<td>' + vals[i] + '</td>');
    }
    tr.append('<td></td>');
  }
}

function add_blanks(flds) {
  var tbody = $('#blanks');
  // Removes all elements
  tbody.empty();
  // Adds a row for new data
  var tr = $('<tr><td></td></tr>');
  tbody.append(tr);
  // Adds inputs for new data
  var fld;
  var n = flds.length;
  if (n > 0) {
    for (var i = 0; i < n; i++) {
      fld = flds[i];
      tr.append('<td><input class="' + fld.type + '" type="text" name="' +
                fld.id + '" size="10" /></td>');
    }
    //
    $('#blanks input.date').datepicker({dateFormat: 'yy-mm-dd'});
    //
    tr.append('<td><input type="button" id="create" value="Добавить" /></td>');
    $('#create').on('click', on_create);
  }
}

function on_create() {
  var fld, type, val, vals = {};
  //
  var ctrls = $('#blanks input[type=text]');
  ctrls.each(function (i) {
    fld = field_by_index(i + 1);
    type = fld.data('type');
    val = $(this).val();
    //
    if (!is_valid(fld.data('type'), val)) {
      alert('Value "' + val + '" must be of type ' + type);
      $(this).select();
      vals = {};
      return false; // break each
    }
    //
    vals[fld.data('id')] = val;
  });
  //
  if (!$.isEmptyObject(vals)) {
    var mdl_id = $('#models li.active').attr('id');
    send_data('create', mdl_id, vals, function on_sent(data) {
      ctrls.val(''); // clear inputs
      if ('values' in data) {
        add_values_row(data.values);
      }
    });
  }
}
