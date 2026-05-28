#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket, threading, time, struct, rclpy
from flask import Flask, Response
from rclpy.node import Node
from std_msgs.msg import String

AICAR_IP = "192.168.3.38"
app = Flask(__name__)
global_frame_bytes = None
lock = threading.Lock()

class CommandPublisher(Node):
    def __init__(self):
        super().__init__('bn_command_publisher')
        self.publisher_ = self.create_publisher(String, '/voice_drone_command', 10)
    def publish_command(self, cmd):
        msg = String()
        msg.data = cmd
        self.publisher_.publish(msg)

def voice_hub_thread(ros_node):
    s_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s_server.bind(('0.0.0.0', 9998))
    s_server.listen(5)
    while True:
        conn, addr = s_server.accept()
        try:
            text = conn.recv(1024).decode('utf-8')
            if text:
                aicar_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                aicar_sock.settimeout(20.0)
                aicar_sock.connect((AICAR_IP, 9999))
                aicar_sock.send(text.encode('utf-8'))
                cmd_result = aicar_sock.recv(4096).decode('utf-8')
                aicar_sock.close()
                ros_node.publish_command(cmd_result)
        except Exception: pass
        finally: conn.close()

def video_receiver_thread():
    global global_frame_bytes
    v_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    v_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    v_server.bind(('0.0.0.0', 8899))
    v_server.listen(5)
    while True:
        conn, addr = v_server.accept()
        data = b""
        payload_size = struct.calcsize("Q")
        while True:
            try:
                while len(data) < payload_size:
                    packet = conn.recv(4096)
                    if not packet: break
                    data += packet
                if len(data) < payload_size: break
                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("Q", packed_msg_size)[0]
                while len(data) < msg_size:
                    packet = conn.recv(4096)
                    if not packet: break
                    data += packet
                if len(data) < msg_size: break
                with lock: global_frame_bytes = data[:msg_size]
                data = data[msg_size:]
            except: break
        conn.close()

def generate_video():
    global global_frame_bytes
    while True:
        if global_frame_bytes is None: 
            time.sleep(0.01)
            continue
        with lock: frame_data = global_frame_bytes
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')

@app.route('/')
def video_feed(): return Response(generate_video(), mimetype='multipart/x-mixed-replace; boundary=frame')

def main():
    rclpy.init(); ros_node = CommandPublisher()
    threading.Thread(target=voice_hub_thread, args=(ros_node,), daemon=True).start()
    threading.Thread(target=video_receiver_thread, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

if __name__ == '__main__': main()

