import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, Point
from std_msgs.msg import Float64MultiArray
from visualization_msgs.msg import Marker
from nav_msgs.msg import Odometry
from std_msgs.msg import ColorRGBA
import threading
import sys

class AutoTrajectory(Node):
    def __init__(self, initial_text):
        super().__init__('auto_trajectory')
        
        # --- 1. PUBLISHERS & SUBSCRIBERS ---
        self.pub_base = self.create_publisher(Twist, 'cmd_vel', 10)
        self.pub_wheels = self.create_publisher(Float64MultiArray, '/wheel_controller/commands', 10)
        self.pub_marker = self.create_publisher(Marker, '/robot_ink_trail', 10) # Bút vẽ RViz
        self.sub_odom = self.create_subscription(Odometry, '/odom', self.odom_callback, 10) # Đọc vị trí xe
        
        # --- 2. THÔNG SỐ XE MECANUM ---
        self.R = 0.045
        self.LX = 0.14
        self.LY = 0.19

        # --- 3. CẤU HÌNH NGÒI BÚT ĐỎ ---
        self.pen = Marker()
        self.pen.header.frame_id = 'odom'
        self.pen.ns = 'robot_pen'
        self.pen.id = 0
        self.pen.type = Marker.LINE_STRIP
        self.pen.action = Marker.ADD
        self.pen.scale.x = 0.005 # Nét dày 6cm
        self.pen.color = ColorRGBA(r=1.0, g=0.0, b=0.0, a=1.0)
        self.last_pos = None

        # --- 4. TRẠNG THÁI HOẠT ĐỘNG ---
        self.sequence = []
        self.state = 0
        self.timer = self.create_timer(0.05, self.timer_callback)
        
        # Khởi động lần đầu với chữ mặc định
        self.update_text(initial_text)

        # --- 5. BẬT LUỒNG NGẦM ĐỂ NGHE BÀN PHÍM LIÊN TỤC ---
        self.input_thread = threading.Thread(target=self.wait_for_input)
        self.input_thread.daemon = True
        self.input_thread.start()

    def wait_for_input(self):
        """Luồng chạy ngầm để chờ bạn gõ chữ mới bất cứ lúc nào"""
        while rclpy.ok():
            try:
                # Dừng lại chờ bạn gõ chữ trên Terminal
                new_text = input("").strip().upper()
                if new_text:
                    self.update_text(new_text)
            except (EOFError, KeyboardInterrupt):
                break

    def update_text(self, text):
        """Tự động xóa hình cũ, nạp chữ mới và vẽ lại từ đầu"""
        # 1. Xóa sạch bộ nhớ của cây bút
        self.pen.points.clear()
        self.last_pos = None
        
        # 2. Bắn tín hiệu xóa sạch màn hình RViz2
        clear_msg = Marker()
        clear_msg.header.frame_id = 'odom'
        clear_msg.ns = 'robot_pen'
        clear_msg.action = Marker.DELETEALL
        self.pub_marker.publish(clear_msg)
        
        # 3. Tạo kịch bản cho từ mới
        self.text = text
        self.sequence = self.generate_sequence(self.text)
        self.state = 0
        self.state_start_time = self.get_clock().now()
        
        print(f"\n[HỆ THỐNG] Đã xóa bảng! Đang bắt đầu vẽ chữ: '{self.text}'")
        print("Gõ chữ mới rồi nhấn ENTER bất cứ lúc nào để đổi chữ!")
        if len(self.sequence) > 0:
            print(f"-> {self.sequence[0][3]}")

    def odom_callback(self, msg):
        """Mỗi khi xe chạy, hàm này tự động lấy tọa độ để nhả mực"""
        curr_pos = msg.pose.pose.position
        
        # Chỉ nhả mực nếu xe vẫn đang trong quá trình vẽ
        if self.state < len(self.sequence) - 1:
            if self.last_pos is not None:
                dist = ((curr_pos.x - self.last_pos.x)**2 + (curr_pos.y - self.last_pos.y)**2)**0.5
                if dist < 0.01:
                    return # Xe đứng im thì không nhả mực
            
            self.last_pos = curr_pos
            p = Point(x=curr_pos.x, y=curr_pos.y, z=0.01)
            self.pen.points.append(p)
            
            if len(self.pen.points) > 10000:
                self.pen.points.pop(0)
                
            self.pen.header.stamp = self.get_clock().now().to_msg()
            self.pub_marker.publish(self.pen)

    def generate_sequence(self, text):
        """Dịch từng chữ cái thành chuỗi các lệnh điều hướng"""
        seq = []
        for char in text:
            strokes = self.get_strokes(char)
            for (vx, vy, t, desc) in strokes:
                seq.append((vx, vy, t, f"Vẽ '{char}': {desc}"))
                seq.append((0.0, 0.0, 0.2, "Dừng nét")) 
            
            # Sang chữ tiếp theo
            seq.append((0.0, -0.3, 0.5, f"Chuyển sang chữ tiếp theo"))
            seq.append((0.0, 0.0, 0.2, "Chuẩn bị"))
            
        seq.append((0.0, 0.0, 9999.0, "Đã vẽ xong toàn bộ!"))
        return seq

    def get_strokes(self, char):
        """Từ điển chữ cái (Tốc độ X, Tốc độ Y, Thời gian, Mô tả)"""
        if char == 'U':
            return [
                (-0.3, 0.0, 2.0, "Nét trái (Xuống)"),
                (0.0, -0.3, 1.0, "Đáy (Sang phải)"),
                (0.3, 0.0, 2.0, "Nét phải (Lên)")
            ]
        elif char == 'E':
            return [
                (0.0, -0.3, 1.0, "Ngang trên"), (0.0, 0.3, 1.0, "Trở lại"),
                (-0.3, 0.0, 1.0, "Xuống giữa"),
                (0.0, -0.3, 1.0, "Ngang giữa"), (0.0, 0.3, 1.0, "Trở lại"),
                (-0.3, 0.0, 1.0, "Xuống đáy"),
                (0.0, -0.3, 1.0, "Ngang đáy"),
                (0.3, 0.0, 2.0, "Trở về góc phải trên")
            ]
        elif char == 'T':
            return [
                (0.0, -0.3, 1.0, "Ngang trên"), (0.0, 0.15, 0.5, "Lùi vào giữa"),
                (-0.3, 0.0, 2.0, "Dọc giữa"), (0.3, 0.0, 2.0, "Lên đỉnh"),
                (0.0, -0.15, 0.5, "Ra góc phải")
            ]
        elif char == 'I':
            return [
                (0.0, -0.3, 1.0, "Ngang trên"), (0.0, 0.15, 0.5, "Vào giữa"),
                (-0.3, 0.0, 2.0, "Dọc"), (0.0, 0.15, 0.5, "Sang trái đáy"),
                (0.0, -0.3, 1.0, "Ngang đáy"), (0.0, 0.15, 0.5, "Vào giữa đáy"),
                (0.3, 0.0, 2.0, "Lên đỉnh"), (0.0, -0.15, 0.5, "Góc phải")
            ]
        else:
            # Vẽ hình vuông nếu chữ chưa có trong bộ font
            return [
                (0.0, -0.3, 1.0, "Nét ngang"), (-0.3, 0.0, 2.0, "Nét dọc"),
                (0.0, 0.3, 1.0, "Nét ngang đáy"), (0.3, 0.0, 2.0, "Nét dọc lên"),
                (0.0, -0.3, 1.0, "Thoát nét")
            ]

    def timer_callback(self):
        """Vòng lặp gửi vận tốc xuống bánh xe"""
        if self.state >= len(self.sequence):
            return

        vx, vy, duration, desc = self.sequence[self.state]
        
        elapsed = (self.get_clock().now() - self.state_start_time).nanoseconds / 1e9

        if elapsed > duration:
            self.state += 1
            if self.state < len(self.sequence):
                self.state_start_time = self.get_clock().now()
                if "Dừng" not in self.sequence[self.state][3]:
                    print(f"-> {self.sequence[self.state][3]}")
            return

        # Ra lệnh thân xe
        twist = Twist()
        twist.linear.x, twist.linear.y = vx, vy
        self.pub_base.publish(twist)

        # Tính toán Động học 4 bánh
        w_tt = (vx - vy) / self.R
        w_tp = (vx + vy) / self.R
        w_dt = (vx + vy) / self.R
        w_dp = (vx - vy) / self.R

        wheel_msg = Float64MultiArray()
        wheel_msg.data = [w_tt, w_tp, w_dt, w_dp]
        self.pub_wheels.publish(wheel_msg)

def main(args=None):
    print("\n" + "="*50)
    print("🤖 MÁY IN CHỮ MECANUM (TÍCH HỢP BÚT VẼ)")
    text = input("Nhập chữ cái bạn muốn robot vẽ (Enter = UET): ").strip().upper()
    if not text:
        text = "UET"
    print("="*50 + "\n")

    rclpy.init(args=args)
    node = AutoTrajectory(text)
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.pub_base.publish(Twist())
        node.pub_wheels.publish(Float64MultiArray(data=[0.0, 0.0, 0.0, 0.0]))
        node.destroy_node()
        if rclpy.ok(): rclpy.shutdown()

if __name__ == '__main__':
    main()