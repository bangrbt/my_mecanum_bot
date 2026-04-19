# 🤖 Mecanum Robot Simulation - ROS 2 Humble

Package `my_mecanum_bot` cung cấp môi trường mô phỏng toàn diện cho robot di chuyển đa hướng (Mecanum) trên nền tảng **ROS 2 Humble** và **Gazebo Classic**. Hệ thống tích hợp điều khiển động học (Kinematics), tay máy (Manipulator) 2 bậc tự do (Ở đây là 2 khâu tịnh tiến), cấu hình cảm biến (LiDAR, Camera, Encoder), và tính năng tự động sinh quỹ đạo trực quan trên RViz2.

Trong dự án có bao gồm cả bản báo cáo trình bày mô tả chi tiết, và video thử nghiệm mô hình.

## ✨ Tính năng Kỹ thuật
- **Động học Mecanum (Omnidirectional Kinematics):** Điều khiển 4 bánh xe độc lập cho phép robot di chuyển tịnh tiến 2D (tiến, lùi, trượt ngang) và xoay tại chỗ (yaw).
- **Cấu trúc Tay máy (Manipulator):** Tích hợp 2 khớp tịnh tiến (Prismatic joints) phục vụ tác vụ vươn và nâng hạ.
- **Hệ thống Cảm biến (Sensors):** Mô phỏng LiDAR quét 360 độ, Camera RGB, Encoder vấn tốc, góc bánh với luồng dữ liệu thời gian thực được map qua ROS topics.
- **Sinh quỹ đạo tự động (Auto-Trajectory & Marker):** Tự động chuyển đổi chuỗi ký tự đầu vào thành tín hiệu điều khiển vận tốc, đồng thời render quỹ đạo di chuyển trực quan thông qua `visualization_msgs/Marker` trên không gian RViz2.

---

## 🛠️ Yêu cầu Hệ thống (Prerequisites)

- **OS:** Ubuntu 22.04 LTS
- **Framework:** ROS 2 Humble Desktop
- **Simulator:** Gazebo Classic 11

### Cài đặt Thư viện phụ thuộc (Dependencies)
Thực thi tập lệnh sau để cài đặt các package cấu hình vật lý và bộ điều khiển (`ros2_control`):

```bash
sudo apt update
sudo apt install ros-humble-xacro ros-humble-gazebo-ros-pkgs \
ros-humble-gazebo-ros2-control ros-humble-ros2-control \
ros-humble-ros2-controllers ros-humble-velocity-controllers \
ros-humble-joint-trajectory-controller python3-pynput
``` 
## 🚀 Hướng dẫn Cài đặt & Khởi chạy (Installation & Launch)
Bước 1: Clone Repository

Tạo ROS 2 workspace và tải source code:
Mở Terminal và clone kho lưu trữ này vào thư mục src trong ROS 2 Workspace của bạn (ví dụ: `~/mecanum_ws`):
```
mkdir -p ~/mecanum_ws/src
cd ~/mecanum_ws/src
git clone [https://github.com/](https://github.com/)<TEN_GITHUB_CUA_BAN>/my_mecanum_bot.git
```
Bước 2: Biên dịch (Build Workspace)
```

cd ~/mecanum_ws
rm -rf build/ install/ log/
colcon build --packages-select my_mecanum_bot
source install/setup.bash
```
Bước 3: Khởi động Môi trường Mô phỏng

Lệnh khởi chạy sẽ tự động nạp cấu hình URDF, spawn model vào Gazebo và thiết lập giao diện RViz2:
```
ros2 launch my_mecanum_bot display.launch.py
```
Lệnh hiển thị dữ liệu Enocder:
```
python3 src/my_mecanum_bot/scripts/read_encoder.py
```
🎮 Vận hành & Điều khiển (Operation & Control)

Mở một Terminal mới, thực thi lệnh `source ~/mecanum_ws/install/setup.bash` trước khi gọi các script điều khiển.
Chế độ 1: Điều khiển Thủ công (Manual Teleop)

Kích hoạt node lắng nghe bàn phím để xuất lệnh vận tốc `cmd_vel` và lệnh vị trí tay máy.
```
python3 src/my_mecanum_bot/scripts/teleop_full.py
```
   W / S: Tiến / Lùi.

   A / D: Trượt ngang Trái / Phải (Strafe).

   Q / E: Xoay Trái / Phải (Yaw).

   R / F: Tịnh tiến trục Z (Nâng/Hạ tay 1).

   T / G: Tịnh tiến trục X (Thò/Thụt tay 2).

   ESC: Dừng khẩn cấp.
    
Chế độ 2: Sinh quỹ đạo tự động (Auto Trajectory)

Node tự động chuyển hóa văn bản thành tham số quỹ đạo hình học và vẽ Marker lên RViz2.
```
python3 src/my_mecanum_bot/scripts/auto_trajectory.py
```

   Cách sử dụng: Nhập chuỗi ký tự (VD: UET, ROS) và nhấn Enter. Robot sẽ tự động nội suy tín hiệu vận tốc để di chuyển theo hình chữ cái.

   Tính năng mở rộng: Nhập chuỗi mới và nhấn Enter trong lúc robot đang vận hành sẽ kích hoạt lệnh `DELETEALL` Marker, reset State Machine và bắt đầu vẽ lại từ đầu.

📁 Cấu trúc Thư mục (Directory Structure)

   `urdf/`: Chứa file mô tả vật lý robot (URDF_MECANUM.urdf) bao gồm thẻ inertial, collision và plugins.

   `meshes/`: Chứa các file mô hình 3D CAD (.STL) cho Visual rendering.

   `config/`: Định nghĩa tham số cho ros2_control (hardware interfaces, controllers).

   `launch/`: Script khởi tạo Gazebo, RViz2, robot_state_publisher và controller spawner.

   `scripts/`: Chứa các Node Python xử lý logic điều khiển và sinh quỹ đạo.

   `rviz/`: Tệp tin lưu trữ tham số hiển thị giao diện RViz2 (config.rviz).

👤 Tác giả

Anh Bằng - Sinh viên ngành Kỹ thuật Robot UET
