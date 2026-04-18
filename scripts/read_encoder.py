import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import sys

class EncoderReader(Node):
    def __init__(self):
        super().__init__('encoder_reader')
        
        # 1. Lắng nghe dữ liệu và lưu vào biến ngầm
        self.subscription = self.create_subscription(
            JointState,
            '/joint_states',
            self.listener_callback,
            10)
        
        # Biến dạng từ điển (dictionary) để lưu trữ thông số mới nhất
        self.encoder_data = {}
        
        # 2. Tạo một bộ đếm nhịp (timer) để in ra màn hình 10 lần/giây (0.1s)
        self.timer = self.create_timer(0.1, self.timer_callback)
        
        # Xóa màn hình 1 lần duy nhất khi vừa bật script
        sys.stdout.write('\033[2J\033[H')

    def listener_callback(self, msg):
        # Cập nhật thông số mới nhất vào biến nhưng KHÔNG in ra
        for i in range(len(msg.name)):
            if "Wheel" in msg.name[i]:
                name = msg.name[i].replace("_joint", "")
                self.encoder_data[name] = {
                    'pos': msg.position[i],
                    'vel': msg.velocity[i]
                }

    def timer_callback(self):
        # Đợi cho đến khi có dữ liệu mới bắt đầu in
        if not self.encoder_data:
            return

        # Mã \033[H: Đưa con trỏ chuột về góc trên cùng bên trái (Không xóa màn hình)
        sys.stdout.write('\033[H')
        
        # Gom tất cả nội dung vào 1 biến text rồi in ra cùng lúc
        output = "=========================================\n"
        output += "       DU LIEU ENCODER BANH XE           \n"
        output += "=========================================\n"
        
        # Duyệt qua 4 bánh xe và định dạng số cho thẳng cột (chiếm 8 khoảng trắng, 2 số thập phân)
        for name in sorted(self.encoder_data.keys()):
            pos = self.encoder_data[name]['pos']
            vel = self.encoder_data[name]['vel']
            output += f"[{name}] \t Goc: {pos:>8.2f} rad \t Van toc: {vel:>8.2f} rad/s \n"
            
        output += "=========================================\n"
        output += "Nhấn CTRL+C để thoát.\n"
        
        # Đẩy dữ liệu ra Terminal
        sys.stdout.write(output)
        sys.stdout.flush()

def main(args=None):
    rclpy.init(args=args)
    node = EncoderReader()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Xóa màn hình cho sạch sẽ khi thoát
        sys.stdout.write('\033[2J\033[H')
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()