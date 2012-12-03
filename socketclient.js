function SocketClient(ip,port,query) {
    var _this = this;
    this.socket = '';
    this.uid = 0;
    this.sign = '';
    this.connect = function() {
        this.socket = new WebSocket('ws://'+ip+':'+port+'/'+query);
        this.socket.onopen = function() {
            _this.onOpen()
        }
        this.socket.onmessage = function(event) {
           
            data = event.data;
            eval("var data="+data);
            _this.uid = data['uid'];
            _this.sign = data['sign'];
            if(data['text']!='SETUID') {
                _this.onData(data['text']);
            } else {
                
                _this.onRegist()
            }
        }        
        this.socket.onclose = function(event) { 
            _this.onClose();
        }; 
    }
    this.onRegist = function() {

    }
    this.onClose = function() {

    }

    this.onOpen = function() {

    }

    this.onData = function(text) {

    }
    
    this.sendData = function (text) {
        var data = '{"uid":'+this.uid+',"sign":"'+this.sign+'","data":"'+text+'"}'
        console.log(data);
        this.socket.send(data);
    }
    
    this.close = function() {
        this.socket.close();
    }
}