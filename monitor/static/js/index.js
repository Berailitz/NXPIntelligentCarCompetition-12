'use strict;'

import { showToast } from '/static/js/base.js';

function connect() {
  if ("WebSocket" in window) {
    var ws_path = 'ws://' + window.location.host + window.location.pathname + 'ws/video';
    //alert(ws_path);
    var ws = new WebSocket(ws_path);
    //alert(ws);
    ws.onopen = function () {
      ws.send(1);
      showToast("正在连接服务器");
    };
    ws.onmessage = function (msg) {
      let data = JSON.parse(msg.data);
      let table_html = '';
      Object.entries(data['status']).forEach(item => {
        table_html +=
          `<tr><td>${item[0]}</td><td>${item[1]}</tr>`;
      });
      $('#status-table tbody').html(table_html);
      $("#webcamera").attr('src', 'data:image/jpg;base64,' + data['picture']);
      ws.send(1);
    };
    ws.onerror = function (e) {
      console.log(e);
      showToast("正在重新连接服务器");
      ws.send(1);
    };
  } else {
    alert("WebSocket not supported");
  }
}

export { connect };