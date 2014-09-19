$(document).ready(function () {
  $('#models').on('click', 'a', on_load);
  $('#values').on('click focus', 'td:not(.edt)', on_edit);
  $('#values').on('focusout', 'td.edt input:not(.date)', on_edited);
});

function on_load() {
  var li = $(this).parent();
  // Makes the model active
  $('#models li.active').removeClass('active');
  li.addClass('active');
  // Loads data from the model
  load_data(li.attr('id'));
}

function on_edit() {
  var td = $(this);
  var fld = get_field(td);
  var id = fld.data('id');
  var tp = fld.data('type');
  //
  var val = td.html();
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
  var val = $(this).val();
  var org = $(this).data('orig'); // original value
  var td = $(this).parent();
  // Completes editing
  td.html(val);
  td.toggleClass('edt');
  // Updating data
  if (val != org) { // => value changed
    var fld = get_field(td);
    var type = fld.data('type');
    var mdl_id = $('#models li.active').attr('id');
    //
    if (is_valid(type, val)) {
      var vals = {};
      vals[fld.data('id')] = val;
      update_data(mdl_id, vals);
      //
      $(this).attr('data-orig', val);
    }
    else {
      alert('Value "' + val + '" must be of type ' + type);
      td.html(org);
    }
  }
  // Otherwise => no change, do nothing
}

function load_data(mdl_id) {
  $.ajax({
    url: '/data/' + mdl_id,
    type: 'GET',
    dataType: 'json',
    cache: false,
    success: _on_success,
    failure: _on_failure
  });

  function _on_success(data) {
    if ('fields' in data) {
      // Adds table head
      add_fields(data.fields);
      //
      if ('values' in data) {
        // Adds table rows
        add_values(data.values);
      }
      //
      add_blank(data.fields);
    }
  }

  function _on_failure(data) { 
    alert('Data loading failed');
  }
}

function is_valid(type, val) {
  console.log(val + ': ' + type);
  if (type === 'int') {
    return !isNaN(Number(val));
  }
  if (type === 'date') {
    return (val.match(/^\d{4}-\d{2}-\d{2}$/) !== null);
  }
  // Otherwise => char
  return true;
}

function update_data(mdl_id, vals) {
  $.ajax({
    url: '/update/' + mdl_id + '/1/',
    type: 'POST',
    data: vals,
    dataType: 'json',
    cache: false,
    success: _on_success,
    failure: _on_failure
  });

  function _on_success(data) {
    console.log(data);
  }

  function _on_failure(data) { 
    alert('Data updating failed');
  }
}

function get_field(td) {
  return $($('#fields').find('th').get(td.index()));
}

function add_fields(flds) {
  var tr = $('#fields');
  var i, fld;
  // Removes all header items
  tr.empty();
  // Adds new header items
  for (i in flds) {
    fld = flds[i];
    tr.append('<th data-id="' + fld.id + '" data-type="' + fld.type + '">' +
              (('title' in fld) ? fld.title : fld.id) + '</th>');
  }
}

function add_values(vals) {
  var tr, tbody = $('#values');
  var i, row;
  // Removes all data items
  tbody.empty();
  // Adds new data items
  for (i in vals) {
    tr = $('<tr></tr>');
    tbody.append(tr);
    //
    row = vals[i];
    for (j in row) {
      tr.append('<td>' + row[j] + '</td>');
    }
  }
}

function add_blank(flds) {
  var tbody = $('#blank');
  // Removes all data items
  tbody.empty();
  // Adds a blank row for new data
  var tr = $('<tr></tr>');
  tbody.append(tr);
  //
  var i, fld;
  for (i in flds) {
    fld = flds[i];
    tr.append('<td data-id="' + fld.id + '" data-type="' + fld.type +
              '"><input id="' + fld.id + '" class="' + fld.type +
              ' blk" type="text" name="' + fld.id + '" size="10" /></td>');
  }
}
