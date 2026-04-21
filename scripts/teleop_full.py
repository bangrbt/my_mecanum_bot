import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from std_msgs.msg import Float64MultiArray
from pynput import keyboard

msg = """
========================================
ĐIỀU KHIỂN ROBOT (KINEMATICS MECANUM)
========================================
Di chuyển Xe (Có thể bấm 2 phím cùng lúc):
    W : Tiến            Q : Xoay trái
    S : Lùi             E : Xoay phải
    A : Trượt ngang trái      
    D : Trượt ngang phải      
    
    W + A : Tiến chéo trái    W + D : Tiến chéo phải
    S + A : Lùi chéo trái     S + D : Lùi chéo phải

Điều khiển Tay máy: 
    R : Nâng Tay 1 Lên  F : Hạ Tay 1 Xuống
    T : Tay 2 Thò ra    G : Tay 2 Thụt vào
========================================
Nhấn phím ESC để thoát.
"""

class TeleopFull(Node):
    def __init__(self):
        super().__init__('teleop_full')
        self.pub_base = self.create_publisher(Twist, 'cmd_vel', 10)
        self.pub_wheels = self.create_publisher(Float64MultiArray, '/wheel_controller/commands', 10)
        self.pub_arm = self.create_publisher(JointTrajectory, '/arm_controller/joint_trajectory', 10)
        
        # Thông số cấu hình Robot (Lấy từ URDF)
        self.R = 0.045   # Bán kính bánh xe
        self.LX = 0.14   # Khoảng cách từ tâm đến trục bánh xe theo chiều X
        self.LY = 0.19   # Khoảng cách từ tâm đến trục bánh xe theo chiều Y

        self.t1, self.t2 = 0.0, 0.0
        self.cmd_x, self.cmd_y, self.cmd_z = 0.0, 0.0, 0.0
        self.arm1_dir, self.arm2_dir = 0.0, 0.0

        # Tập hợp chứa các phím đang được giữ
        self.pressed_keys = set()

        self.timer = self.create_timer(0.05, self.timer_callback)
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()
        print(msg)

    def update_commands(self):
        # Đặt lại 0 trước khi tính toán
        self.cmd_x, self.cmd_y, self.cmd_z = 0.0, 0.0, 0.0
        self.arm1_dir, self.arm2_dir = 0.0, 0.0

        # Kiểm tra các phím đang được bấm và cộng dồn vận tốc
        if 'w' in self.pressed_keys: self.cmd_x += 0.2
        if 's' in self.pressed_keys: self.cmd_x -= 0.2
        if 'a' in self.pressed_keys: self.cmd_y += 0.5
        if 'd' in self.pressed_keys: self.cmd_y -= 0.5
        if 'q' in self.pressed_keys: self.cmd_z += 1.0
        if 'e' in self.pressed_keys: self.cmd_z -= 1.0
        
        if 'r' in self.pressed_keys: self.arm1_dir = 1.0
        if 'f' in self.pressed_keys: self.arm1_dir = -1.0
        if 't' in self.pressed_keys: self.arm2_dir = 1.0
        if 'g' in self.pressed_keys: self.arm2_dir = -1.0

    def on_press(self, key):
        try:
            char = key.char.lower()
            self.pressed_keys.add(char)
            self.update_commands()
        except AttributeError:
            pass 

    def on_release(self, key):
        if key == keyboard.Key.esc:
            rclpy.shutdown()
            return False 
        try:
            char = key.char.lower()
            if char in self.pressed_keys:
                self.pressed_keys.remove(char)
            self.update_commands()
        except AttributeError:
            pass

    def timer_callback(self):
        # 1. Gửi lệnh Lái Xe cho plugin trượt
        twist = Twist()
        twist.linear.x = self.cmd_x
        twist.linear.y = self.cmd_y
        twist.angular.z = self.cmd_z
        self.pub_base.publish(twist)

        # 2. TÍNH TOÁN ĐỘNG HỌC (KINEMATICS) CHO 4 BÁNH XE
        w_tt = (self.cmd_x - self.cmd_y - (self.LX + self.LY) * self.cmd_z) / self.R
        w_tp = (self.cmd_x + self.cmd_y + (self.LX + self.LY) * self.cmd_z) / self.R
        w_dt = (self.cmd_x + self.cmd_y - (self.LX + self.LY) * self.cmd_z) / self.R
        w_dp = (self.cmd_x - self.cmd_y + (self.LX + self.LY) * self.cmd_z) / self.R

        # Đóng gói và gửi lệnh cho 4 bánh
        wheel_msg = Float64MultiArray()
        wheel_msg.data = [w_tt, w_tp, w_dt, w_dp] 
        self.pub_wheels.publish(wheel_msg)

        # 3. Cập nhật vị trí Tay máy
        if self.arm1_dir != 0 or self.arm2_dir != 0:
            self.t1 += self.arm1_dir * 0.005 
            self.t2 += self.arm2_dir * 0.005
            self.t1 = max(-0.12, min(0.055, self.t1))
            self.t2 = max(0.0, min(0.2, self.t2))

            traj = JointTrajectory()
            traj.joint_names = ['Tay1_joint', 'Tay2_joint']
            point = JointTrajectoryPoint()
            point.positions = [float(self.t1), float(self.t2)]
            point.time_from_start.sec = 0
            point.time_from_start.nanosec = 50000000 
            traj.points.append(point)
            self.pub_arm.publish(traj)

def main(args=None):
    rclpy.init(args=args)
    node = TeleopFull()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        twist = Twist()
        node.pub_base.publish(twist)
        wheel_msg = Float64MultiArray()
        wheel_msg.data = [0.0, 0.0, 0.0, 0.0]
        node.pub_wheels.publish(wheel_msg)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from std_msgs.msg import Float64MultiArray
from pynput import keyboard

msg = """
========================================
ĐIỀU KHIỂN ROBOT (KINEMATICS MECANUM)
========================================
Di chuyển Xe:
    W : Tiến            Q : Xoay trái
    S : Lùi             E : Xoay phải
    A : Trượt ngang trái      
    D : Trượt ngang phải      
    
Điều khiển Tay máy: 
    R : Nâng Tay 1 Lên  F : Hạ Tay 1 Xuống
    T : Tay 2 Thò ra    G : Tay 2 Thụt vào
========================================
Nhấn phím ESC để thoát.
"""

class TeleopFull(Node):
    def __init__(self):
        super().__init__('teleop_full')
        self.pub_base = self.create_publisher(Twist, 'cmd_vel', 10)
        self.pub_wheels = self.create_publisher(Float64MultiArray, '/wheel_controller/commands', 10)
        self.pub_arm = self.create_publisher(JointTrajectory, '/arm_controller/joint_trajectory', 10)
        
        # Thông số cấu hình Robot (Lấy từ URDF)
        self.R = 0.045   # Bán kính bánh xe
        self.LX = 0.14   # Khoảng cách từ tâm đến trục bánh xe theo chiều X
        self.LY = 0.19   # Khoảng cách từ tâm đến trục bánh xe theo chiều Y

        self.t1, self.t2 = 0.0, 0.0
        self.cmd_x, self.cmd_y, self.cmd_z = 0.0, 0.0, 0.0
        self.arm1_dir, self.arm2_dir = 0.0, 0.0

        self.timer = self.create_timer(0.05, self.timer_callback)
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()
        print(msg)

    def on_press(self, key):
        try:
            char = key.char.lower()
            if char == 'w': self.cmd_x = 0.2
            elif char == 's': self.cmd_x = -0.2
            elif char == 'a': self.cmd_y = 0.5
            elif char == 'd': self.cmd_y = -0.5
            elif char == 'q': self.cmd_z = 1.0
            elif char == 'e': self.cmd_z = -1.0
            
            elif char == 'r': self.arm1_dir = 1.0
            elif char == 'f': self.arm1_dir = -1.0
            elif char == 't': self.arm2_dir = 1.0
            elif char == 'g': self.arm2_dir = -1.0
        except AttributeError:
            pass 

    def on_release(self, key):
        if key == keyboard.Key.esc:
            rclpy.shutdown()
            return False 
        try:
            char = key.char.lower()
            if char in ['w', 's']: self.cmd_x = 0.0
            if char in ['a', 'd']: self.cmd_y = 0.0
            if char in ['q', 'e']: self.cmd_z = 0.0
            if char in ['r', 'f']: self.arm1_dir = 0.0
            if char in ['t', 'g']: self.arm2_dir = 0.0
        except AttributeError:
            pass

    def timer_callback(self):
        # 1. Gửi lệnh Lái Xe cho plugin trượt
        twist = Twist()
        twist.linear.x = self.cmd_x
        twist.linear.y = self.cmd_y
        twist.angular.z = self.cmd_z
        self.pub_base.publish(twist)

        # 2. TÍNH TOÁN ĐỘNG HỌC (KINEMATICS) CHO 4 BÁNH XE
        # Công thức Vận tốc góc bánh xe = (V_x +/- V_y +/- (LX+LY)*W_z) / R
        w_tt = (self.cmd_x - self.cmd_y - (self.LX + self.LY) * self.cmd_z) / self.R
        w_tp = (self.cmd_x + self.cmd_y + (self.LX + self.LY) * self.cmd_z) / self.R
        w_dt = (self.cmd_x + self.cmd_y - (self.LX + self.LY) * self.cmd_z) / self.R
        w_dp = (self.cmd_x - self.cmd_y + (self.LX + self.LY) * self.cmd_z) / self.R

        # Đóng gói và gửi lệnh cho 4 bánh
        wheel_msg = Float64MultiArray()
        # Lưu ý: Thứ tự các bánh phải khớp chuẩn với thứ tự trong file controllers.yaml
        wheel_msg.data = [w_tt, w_tp, w_dt, w_dp] 
        self.pub_wheels.publish(wheel_msg)

        # 3. Cập nhật vị trí Tay máy
        if self.arm1_dir != 0 or self.arm2_dir != 0:
            self.t1 += self.arm1_dir * 0.005 
            self.t2 += self.arm2_dir * 0.005
            self.t1 = max(-0.12, min(0.055, self.t1))
            self.t2 = max(0.0, min(0.2, self.t2))

            traj = JointTrajectory()
            traj.joint_names = ['Tay1_joint', 'Tay2_joint']
            point = JointTrajectoryPoint()
            point.positions = [float(self.t1), float(self.t2)]
            point.time_from_start.sec = 0
            point.time_from_start.nanosec = 50000000 
            traj.points.append(point)
            self.pub_arm.publish(traj)

def main(args=None):
    rclpy.init(args=args)
    node = TeleopFull()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        twist = Twist()
        node.pub_base.publish(twist)
        wheel_msg = Float64MultiArray()
        wheel_msg.data = [0.0, 0.0, 0.0, 0.0]
        node.pub_wheels.publish(wheel_msg)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
