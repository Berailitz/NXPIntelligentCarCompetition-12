'use strict;'

import {showToast} from '/static/js/base.js';

function update_status() {
  let loading_notice = '更新中';
  $('#status-table-title')[0].innerHTML = loading_notice;
  showToast(loading_notice, 1200);
  $.get(
      '/api/status',
      function(rawData) {
        console.log(rawData);
        if (rawData['status'] == 0) {
          let table_html = '';
          Object.entries(rawData['data']).forEach(item => {
            console.log(item);
            table_html +=
                `<tr><td>${item[0]}</td><td>${item[1]}</tr>`;
          });
          $('#status-table tbody').html(table_html);
          $('#status-table-title')[0].innerHTML = '当前状态';
          showToast('状态已更新', 800);
        } else {
          showToast(rawData['message'], 1200);
        }
      })
}

export {update_status};
