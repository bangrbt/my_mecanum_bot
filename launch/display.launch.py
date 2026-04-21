import os
import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_name = 'my_mecanum_bot'
    urdf_file = 'URDF_MECANUM.urdf' 
    
    pkg_share = get_package_share_directory(pkg_name)
    urdf_path = os.path.join(pkg_share, 'urdf', urdf_file)

    doc = xacro.process_file(urdf_path)
    robot_desc = doc.toxml()

    set_gazebo_model_path_cmd = SetEnvironmentVariable('GAZEBO_MODEL_PATH', os.path.join(pkg_share, '..'))
    
    world_file_path = os.path.join(pkg_share, 'world', 'house.world')

    # Khởi chạy Gazebo VÀ nạp file map
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

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        parameters=[{'use_sim_time': True}]
    )

    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', 'mecanum_robot', '-z', '0.2'],
        output='screen'
    )

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

    return LaunchDescription([
        set_gazebo_model_path_cmd,
        gazebo, # Chỉ gọi Gazebo 1 lần ở đây thôi
        robot_state_publisher_node,
        rviz_node,
        spawn_entity,
        joint_state_broadcaster_spawner,
        arm_controller_spawner,
        wheel_controller_spawner,
    ])