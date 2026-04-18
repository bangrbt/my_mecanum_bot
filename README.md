#  ROS 2 Mecanum Robot Simulation (`my_mecanum_bot`)

Chào mừng bạn đến với dự án mô phỏng Robot Mecanum đa hướng trên nền tảng **ROS 2 Humble** và **Gazebo Classic**. 

Package này cung cấp một hệ thống robot hoàn chỉnh bao gồm bệ lăn Mecanum, cánh tay robot (Robot Arm) 2 bậc tự do, các cảm biến (Lidar, Camera) và đặc biệt là hệ thống **Động học (Kinematics)** tự động tính toán nét vẽ quỹ đạo (Robot Pen) trực tiếp trên RViz2.

## ✨ Tính năng nổi bật
* **Di chuyển Đa hướng (Omnidirectional):** 4 bánh xe Mecanum xoay đan chéo đồng bộ giúp robot có thể tiến, lùi, trượt ngang và xoay tại chỗ mượt mà.
* **Tích hợp Cảm biến:** Camera góc rộng và Lidar quét 360 độ (hiển thị trực quan trên RViz2).
* **Điều khiển Tay máy:** Cánh tay robot có thể nâng/hạ và thò/thụt linh hoạt.
* **Robot di chuyển tự động vẽ ra quỹ đạo là chữ cái:** Robot tự động chạy và nhả mực đỏ trên giao diện RViz2 để vẽ các chữ cái (U, E, T, I, H, O...) với tỷ lệ siêu to khổng lồ. Tự động xóa bảng khi nhập chữ mới.

---

## Yêu cầu Hệ thống (Prerequisites)

Dự án này được phát triển và kiểm thử trên:
* **OS:** Ubuntu 22.04 LTS
* **ROS Version:** ROS 2 Humble
* **Simulator:** Gazebo Classic (thường đi kèm khi cài ROS 2 Desktop)

### Cài đặt Thư viện phụ thuộc (Dependencies)
Trước khi Build package, bạn cần cài đặt các gói điều khiển và mô phỏng bắt buộc. Mở Terminal và chạy các lệnh sau:

```bash
sudo apt update
sudo apt install ros-humble-xacro ros-humble-gazebo-ros-pkgs
sudo apt install ros-humble-gazebo-ros2-control ros-humble-ros2-control ros-humble-ros2-controllers
sudo apt install ros-humble-velocity-controllers ros-humble-joint-trajectory-controller
sudo apt install python3-pynput


Hướng dẫn Cài đặt & Khởi chạy (Installation & Launch)

Bước 1: Clone dự án về Workspace
Mở Terminal và clone kho lưu trữ này vào thư mục src trong ROS 2 Workspace của bạn (ví dụ: ~/mecanum_ws):
mkdir -p ~/mecanum_ws/src
cd ~/mecanum_ws/src
git clone [https://github.com/](https://github.com/)<TEN_GITHUB_CUA_BAN>/my_mecanum_bot.git
(Lưu ý: Thay <TEN_GITHUB_CUA_BAN> bằng đường link GitHub thực tế của bạn).

Bước 2: Build Package
Di chuyển ra thư mục gốc của workspace và tiến hành biên dịch (Build):
cd ~/mecanum_ws
rm -rf build/ install/ log/
colcon build --packages-select my_mecanum_bot
source install/setup.bash

Bước 3: Khởi động Mô phỏng
Sau khi build thành công, hãy khởi động môi trường Gazebo và RViz2:
ros2 launch my_mecanum_bot display.launch.py


Hướng dẫn Điều khiển (How to Control)
Sau khi đã chạy file launch ở trên, hãy mở một Terminal mới, thực hiện source install/setup.bash và chọn một trong hai chế độ:

1. Điều khiển bằng bàn phím (Manual Teleop)
Sử dụng bàn phím để lái xe và điều khiển tay máy một cách linh hoạt (Nhấn giữ để chạy, nhả để dừng).
python3 src/my_mecanum_bot/scripts/teleop_full.py

W/S: Tiến / Lùi.

A/D: Trượt ngang Trái / Phải.

Q/E: Xoay Trái / Phải.

R/F: Nâng / Hạ cánh tay 1.

T/G: Thò / Thụt cánh tay 2.

2. Robot tự động vẽ chữ (Auto Printing)
Dưới đây là nội dung đầy đủ và chi tiết nhất cho file README.md. Mình đã trình bày theo chuẩn GitHub với các định dạng bảng, khối code và biểu tượng (emoji) để trông chuyên nghiệp nhất.

Bạn chỉ cần mở file README.md trong thư mục my_mecanum_bot, xóa hết nội dung cũ và dán toàn bộ đoạn dưới đây vào là xong:
Markdown

# 🤖 Mecanum Robot Simulation - ROS 2 Humble

Dự án mô phỏng Robot đa hướng sử dụng bánh xe **Mecanum**, tích hợp cánh tay robot (Robot Arm), cảm biến Lidar và Camera. Package này được phát triển trên nền tảng **ROS 2 Humble** và **Gazebo Classic**, hỗ trợ điều khiển động học thời gian thực và tự động vẽ quỹ đạo (Robot Pen).

## ✨ Tính năng nổi bật
- **Động học Mecanum:** Điều khiển đa hướng (Omnidirectional) cho phép robot tiến, lùi, xoay và trượt ngang (Strafing).
- **Cánh tay Robot:** 2 bậc tự do (Prismatic joints) hỗ trợ các tác vụ nâng hạ và vươn dài.
- **Hệ thống "Bút vẽ" (Robot Pen):** Tự động nhả mực đỏ trên Rviz2 để theo dõi quỹ đạo di chuyển dưới dạng nét bút đậm.
- **Chế độ in chữ tự động:** Robot tự động di chuyển để viết các từ được nhập từ bàn phím (Mặc định: `UET`).
- **Cảm biến:** Camera và Lidar 360 độ hiển thị dữ liệu thời gian thực.

---

## 🛠️ Yêu cầu hệ thống (Prerequisites)

Dự án yêu cầu máy tính đã cài đặt **Ubuntu 22.04** và **ROS 2 Humble Desktop**.

### 1. Cài đặt thư viện phụ thuộc
Mở Terminal và chạy lệnh sau để cài đặt các plugin và bộ điều khiển cần thiết:

```bash
sudo apt update
sudo apt install ros-humble-xacro ros-humble-gazebo-ros-pkgs \
ros-humble-gazebo-ros2-control ros-humble-ros2-control \
ros-humble-ros2-controllers ros-humble-velocity-controllers \
ros-humble-joint-trajectory-controller python3-pynput

🚀 Hướng dẫn Cài đặt & Khởi chạy
Bước 1: Clone dự án

Tạo workspace và clone package này vào thư mục src:
Bash

mkdir -p ~/mecanum_ws/src
cd ~/mecanum_ws/src
git clone <LINK_GITHUB_CỦA_BẠN_Ở_ĐÂY>

Bước 2: Biên dịch (Build)
Bash

cd ~/mecanum_ws
colcon build --packages-select my_mecanum_bot
source install/setup.bash

Bước 3: Chạy mô phỏng
Bash

ros2 launch my_mecanum_bot display.launch.py

    Lưu ý: Rviz2 sẽ tự động mở lên kèm theo cấu hình Robot Model và hệ quy chiếu odom.

🎮 Các chế độ điều khiển

Sau khi đã chạy file launch ở trên, hãy mở một Terminal mới, thực hiện source install/setup.bash và chọn một trong hai chế độ:

1. Điều khiển bằng bàn phím (Manual Teleop)
Sử dụng bàn phím để lái xe và điều khiển tay máy một cách linh hoạt (Nhấn giữ để chạy, nhả để dừng).
Bash

python3 src/my_mecanum_bot/scripts/teleop_full.py

    W/S: Tiến / Lùi.

    A/D: Trượt ngang Trái / Phải.

    Q/E: Xoay Trái / Phải.

    R/F: Nâng / Hạ cánh tay 1.

    T/G: Thò / Thụt cánh tay 2.

2. Robot tự động vẽ chữ (Auto Printing)
Robot sẽ tự động xóa quỹ đạo cũ và thực hiện kịch bản vẽ chữ cái theo yêu cầu.

python3 src/my_mecanum_bot/scripts/auto_trajectory.py

Cách dùng: Nhập chữ muốn vẽ (VD: UET, IOT, HUI) rồi nhấn Enter.
Tính năng: Trong khi robot đang vẽ, bạn có thể gõ chữ mới và Enter, robot sẽ xóa bảng ngay lập tức và bắt đầu vẽ chữ mới từ vị trí hiện tại.

Cấu trúc Package

    urdf/: Chứa file mô tả robot URDF_MECANUM.urdf và cấu hình vật lý.

    meshes/: Chứa các file 3D (.STL) của robot.

    config/: Cấu hình các bộ điều khiển ros2_control (Wheel & Arm).

    launch/: File khởi động tích hợp Gazebo và Rviz2.

    scripts/: Các mã nguồn Python điều khiển động học và xử lý quỹ đạo.

    rviz/: Lưu trữ cấu hình giao diện Rviz2 (config.rviz).


Tác giả
    Anh Bang - Sinh viên Kỹ thuật Robot

***

### Một số lưu ý nhỏ:
1. **Link GitHub:** Đừng quên thay đoạn `<LINK_GITHUB_CỦA_BẠN_Ở_ĐÂY>` bằng link thực tế sau khi bạn tạo repo nhé.
2. **File .gitignore:** Hãy đảm bảo bạn đã tạo file `.gitignore` như mình hướng dẫn ở tin nhắn trước để người khác không bị tải về các file rác trong thư mục `build/` hay `install/`.