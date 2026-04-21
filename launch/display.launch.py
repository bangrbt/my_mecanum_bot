import os
import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_name = 'my_mecanum_bot'
    urdf_file = 'URDF_MECANUM.urdf' 
    
    pkg_share = get_package_share_directory(pkg_name)
    urdf_path = os.path.join(pkg_share, 'urdf', urdf_file)

    doc = xacro.process_file(urdf_path)
    robot_desc = doc.toxml()

    workspace_share_dir = os.path.dirname(pkg_share)
    set_gazebo_model_path_cmd = SetEnvironmentVariable(
        'GAZEBO_MODEL_PATH', 
        os.path.join(pkg_share, 'models') + ':' + workspace_share_dir
    )
    
    world_file_path = os.path.join(pkg_share, 'world', 'my_map.world')
    
    # THÊM ĐƯỜNG DẪN TỚI FILE CONFIG CỦA RVIZ
    rviz_config_path = os.path.join(pkg_share, 'rviz', 'config.rviz')

    # Khởi chạy Gazebo và nạp file map
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')]),
        launch_arguments={'world': world_file_path}.items()
    )

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_desc,
            'use_sim_time': True
        }]
    )

    # CẬP NHẬT RVIZ NODE ĐỂ NHẬN FILE CONFIG
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_path], # Dòng quan trọng để load config
        parameters=[{'use_sim_time': True}]
    )

    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', 'mecanum_robot', '-z', '0.2'],
        output='screen'
    )

    # --- KHỞI TẠO CÁC SPAWNER (CHƯA CHẠY NGAY) ---
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
    )

    arm_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["arm_controller"],
    )

    wheel_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["wheel_controller"],
    )

    # Bước 1: Chờ Spawn Robot xong -> Mới chạy Joint State Broadcaster
    delay_joint_state_after_spawn = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_entity,
            on_exit=[joint_state_broadcaster_spawner],
        )
    )

    # Bước 2: Chờ Joint State Broadcaster chạy xong -> Mới chạy Controller cánh tay và bánh xe
    delay_controllers_after_joint_state = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[arm_controller_spawner, wheel_controller_spawner],
        )
    )

    return LaunchDescription([
        set_gazebo_model_path_cmd,
        gazebo,
        robot_state_publisher_node,
        rviz_node,
        spawn_entity,
        delay_joint_state_after_spawn,         
        delay_controllers_after_joint_state,   
    ])
