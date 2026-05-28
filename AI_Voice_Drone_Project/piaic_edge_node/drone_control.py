#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from px4_msgs.msg import OffboardControlMode, TrajectorySetpoint, VehicleCommand, VehicleLocalPosition
from rclpy.qos import qos_profile_sensor_data, QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy
import re, math, time

class FlightDynamicsController(Node):
    def __init__(self):
        super().__init__('flight_dynamics_controller')
        self.subscription = self.create_subscription(String, '/voice_drone_command', self.command_callback, 10)
        
        qos_p = QoSProfile(reliability=ReliabilityPolicy.BEST_EFFORT, durability=DurabilityPolicy.VOLATILE, history=HistoryPolicy.KEEP_LAST, depth=1)
        self.pos_sub = self.create_subscription(VehicleLocalPosition, '/fmu/out/vehicle_local_position', self.pos_callback, qos_p)
        
        self.offboard_mode_publisher = self.create_publisher(OffboardControlMode, '/fmu/in/offboard_control_mode', qos_profile_sensor_data)
        self.trajectory_publisher = self.create_publisher(TrajectorySetpoint, '/fmu/in/trajectory_setpoint', qos_profile_sensor_data)
        self.vehicle_command_publisher = self.create_publisher(VehicleCommand, '/fmu/in/vehicle_command', QoSProfile(reliability=ReliabilityPolicy.RELIABLE, history=HistoryPolicy.KEEP_LAST, depth=10))

        self.timer = self.create_timer(0.1, self.control_loop)
        
        self.current_x = 0.0; self.current_y = 0.0; self.current_z = 0.0
        self.target_x = 0.0; self.target_y = 0.0; self.target_z = 0.0
        self.commanded_yaw = 0.0; self.commanded_pitch = 0.0
        self.px4_timestamp = 0 
        
        self.is_landing = False; self.command_queue = []
        self.current_command = None; self.command_start_time = 0.0; self.wait_duration = 0.0

        self.get_logger().info("🚀 [piaic MC] 절대 고도 앵커(Anchor) 장착 완료! 지면 추락 영구 방어!")

    def pos_callback(self, msg):
        self.current_x = msg.x; self.current_y = msg.y; self.current_z = msg.z
        self.px4_timestamp = msg.timestamp

    def publish_vehicle_command(self, command, **params):
        msg = VehicleCommand()
        msg.command = command
        msg.param1 = params.get("param1", 0.0); msg.param2 = params.get("param2", 0.0)
        msg.target_system = 1; msg.target_component = 1; msg.source_system = 1; msg.source_component = 1; msg.from_external = True
        msg.timestamp = self.px4_timestamp if self.px4_timestamp > 0 else int(self.get_clock().now().nanoseconds / 1000)
        self.vehicle_command_publisher.publish(msg)

    def command_callback(self, msg):
        self.command_queue.clear()
        self.current_command = None 
        
        for cmd in msg.data.split('\n'):
            if cmd.strip() and "IGNORE" not in cmd: 
                self.command_queue.append(cmd.strip())
                self.get_logger().info(f"📥 엑사원 타전 수신 (우선순위 덮어쓰기 완료!): {cmd.strip()}")

    def control_loop(self):
        current_time = time.time() 

        if self.current_command is None and len(self.command_queue) > 0:
            self.current_command = self.command_queue.pop(0)
            self.command_start_time = current_time
            self.publish_vehicle_command(VehicleCommand.VEHICLE_CMD_DO_SET_MODE, param1=1.0, param2=6.0)
            self.process_command(self.current_command)

        if self.current_command:
            if "TAKEOFF" in self.current_command or "LAND" in self.current_command:
                dist = abs(self.target_z - self.current_z)
                acceptance_radius = 0.3 
            else:
                dist = math.sqrt((self.target_x-self.current_x)**2 + (self.target_y-self.current_y)**2 + (self.target_z-self.current_z)**2)
                acceptance_radius = 1.5 # 🌟 바람 밀림 및 돌격 관성을 위한 여유 반경
                
            elapsed = current_time - self.command_start_time
            cmd_done = False
            
            if "WAIT" in self.current_command:
                if elapsed >= self.wait_duration: cmd_done = True
            elif "TURN" in self.current_command or "PITCH" in self.current_command:
                if elapsed >= 3.0: cmd_done = True
            else:
                if dist < acceptance_radius or elapsed > 20.0: cmd_done = True
                
            if cmd_done:
                self.current_command = None

        if not self.is_landing:
            now = self.px4_timestamp if self.px4_timestamp > 0 else int(self.get_clock().now().nanoseconds / 1000)
            off_msg = OffboardControlMode(); off_msg.position = True; off_msg.timestamp = now
            self.offboard_mode_publisher.publish(off_msg)
            
            set_msg = TrajectorySetpoint()
            set_msg.position = [float(self.target_x), float(self.target_y), float(self.target_z)]
            set_msg.velocity = [float('nan'), float('nan'), float('nan')]
            set_msg.acceleration = [float('nan'), float('nan'), float('nan')]
            set_msg.jerk = [float('nan'), float('nan'), float('nan')]
            set_msg.yaw = float(self.commanded_yaw)
            set_msg.yawspeed = float('nan')
            set_msg.timestamp = now
            self.trajectory_publisher.publish(set_msg)

    def process_command(self, cmd):
        nums = re.findall(r'\d+\.?\d*', cmd)
        val = float(nums[0]) if nums else 0.0
        
        if "TAKEOFF" in cmd:
            self.is_landing = False; val = val if val > 0 else 1.5
            self.publish_vehicle_command(VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM, param1=1.0)
            self.target_x = self.current_x; self.target_y = self.current_y 
            self.target_z = self.current_z - val # 이륙 시점에서 땅바닥을 기준으로 절대 고도 생성!
            self.commanded_yaw = 0.0; self.commanded_pitch = 0.0
            self.get_logger().info(f"🔥 {val}m 고도로 이륙 맹렬 개시!")
            
        elif "LAND" in cmd:
            self.is_landing = True; self.publish_vehicle_command(VehicleCommand.VEHICLE_CMD_NAV_LAND)
            self.get_logger().info("🛬 픽스호크 착륙 시퀀스 전개!")
            
        elif "WAIT" in cmd: 
            self.wait_duration = val
            self.get_logger().info(f"⏳ {val}초 대기 중...")
            
        elif "PITCH_UP" in cmd:
            self.commanded_pitch = math.radians(val)
        elif "PITCH_DOWN" in cmd:
            self.commanded_pitch = -math.radians(val)
            
        elif "GO_FORWARD" in cmd:
            xy_dist = val * math.cos(self.commanded_pitch)
            z_dist = val * math.sin(self.commanded_pitch)
            self.target_x = self.current_x + xy_dist * math.cos(self.commanded_yaw)
            self.target_y = self.current_y + xy_dist * math.sin(self.commanded_yaw)
            # 🌟 [위대한 혁명] 고도는 절대 현재 고도(current_z)를 참조하지 않고 이전 목표 고도(target_z)를 유지!
            self.target_z = self.target_z - z_dist 
            self.commanded_pitch = 0.0 
            self.get_logger().info(f"🚀 전진 {val}m 맹렬 돌격! (목표: X={self.target_x:.1f}, Y={self.target_y:.1f}, 고도 Z={self.target_z:.1f})")
            
        elif "TURN_LEFT" in cmd:
            self.commanded_yaw -= math.radians(val)
            self.get_logger().info(f"⬅️ 좌회전 {val}도 회전 개시!")
        elif "TURN_RIGHT" in cmd:
            self.commanded_yaw += math.radians(val)
            self.get_logger().info(f"➡️ 우회전 {val}도 회전 개시!")

def main(args=None):
    rclpy.init(args=args)
    node = FlightDynamicsController()
    try: rclpy.spin(node)
    except KeyboardInterrupt: pass
    finally: 
        node.destroy_node()
        if rclpy.ok(): rclpy.shutdown()

if __name__ == '__main__': main()

