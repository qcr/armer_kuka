# Armer KUKA

*To be used with the [Armer Driver](https://github.com/qcr/armer)*

``WIP``

This package launches the Kuka drivers for use with the [Armer Driver](https://github.com/qcr/armer).

It interfaces with the [ROS Industrial Kuka drivers](https://github.com/ros-industrial/kuka_experimental) so they must be installed and built as well.

This hardware package is semi implemented. The sim will work, but the launch file for the real kuka does not launch the hardware drivers yet.

## Usage
 By default this will launch to control a physical Kuka. To run a Swift simulation the sim parameter can be set to true. For example:

```sh
roslaunch armer_kuka robot_bringup.launch sim:=true
```

To run on a real robot:


```sh
roslaunch armer_kuka robot_bringup.launch config:=path_to_/armer_kuka/cfg/kuka_real.yaml

```

