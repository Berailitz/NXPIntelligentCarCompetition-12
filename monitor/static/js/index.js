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
      $("#webcamera").attr('src', 'data:image/jpg;base64,' + msg.data);
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