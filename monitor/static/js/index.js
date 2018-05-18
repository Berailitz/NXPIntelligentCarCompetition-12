'use strict;'

import { showToast } from '/static/js/base.js';

class LiveStream {
  constructor(wsPath) {
    this.wsPath = wsPath;
    this.ws = null;
    this.autoReconnectInterval = 1500;
  }

  connect() {
    if ("WebSocket" in window) {
      let that = this;
      this.ws = new WebSocket(this.wsPath);
      this.ws.onmessage = this.onmessage();
      this.ws.onerror = this.onerror();
      this.ws.onclose = this.onclose();
      this.ws.onopen = this.onopen();
      window.onbeforeunload = function () {
        that.ws.close();
      }
    } else {
      alert("请使用Chrome浏览器打开本网页");
    }
  }

  onclose() {
    let that = this;
    return function (e) {
      if (e.code != 1000) {
        that.reconnect();
      }
    }
  }

  onopen() {
    let that = this;
    return function () {
      that.ws.send(1);
      showToast("正在连接服务器");
    }
  };

  onmessage() {
    let that = this;
    return function (msg) {
      let data = JSON.parse(msg.data);
      that.ws.send(data['index'] + 1);
      that.update(data);
    }
  };

  onerror() {
    let that = this;
    return function (e) {
      console.log(e);
    }
  };

  doReconnect() {
    let that = this;
    return function (e) {
      showToast("重新连接服务器");
      that.connect();
    }
  }

  reconnect() {
    setTimeout(this.doReconnect(), this.autoReconnectInterval);
  }

  update(data) {
    let table_html = '';
    if (data['warning']) {
      showToast(data['warning']);
    }
    Object.entries(data['status']).forEach(item => {
      table_html +=
        `<tr><td>${item[0]}</td><td>${item[1]}</tr>`;
    });
    $('#status-table tbody').html(table_html);
    $("#webcamera").attr('src', 'data:image/jpg;base64,' + data['picture']);
  }
}

function createStream(streamPath) {
  let liveStream = new LiveStream('wss://' + window.location.host + streamPath);
  liveStream.connect();
}

export { createStream };
