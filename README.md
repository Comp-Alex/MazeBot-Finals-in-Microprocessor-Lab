# University of Batangas — Lipa Campus

## Microprocessor Lab Finals — MazeBot

This repository contains the MazeBot Arduino sketch and detailed documentation for the maze-solving robot developed for the Microprocessor Lab. The project implements a reactive left-wall-following strategy using two ultrasonic sensors and a simple anti-stuck routine. The goal is to provide a reliable, easy-to-tune system for navigating standard rectangular mazes.

**Contents**
- `Maze-CPE2026.png` — Top-view image of the maze.
- `MazeBotFinals.ino` — Main Arduino sketch for the maze-solving robot. Contains the left-wall-following control loop, ultrasonic sensor reading, emergency and dead-end recovery logic, and motion functions for forward movement and turns.
- `README.md` — Project documentation: hardware summary, pin mapping, configuration and tuning guidance, behavior details, and contributor credits.
- `Speedup run of Mazebot.mp4` — Time-lapse (sped-up) video of the MazeBot running through the maze.

### Hardware
- Microcontroller: Arduino Uno (or compatible)
- Motor driver: L298N dual H-bridge
- Drive: 2 × 9V DC motors (differential drive)
- Sensors: 2 × HC-SR04 ultrasonic sensors (left and front)
- TP4056 charging module
- XL6009 step-up booster (adjustable voltage to power the motors)
- Power: 5000 mAh power bank
- Chassis: acrylic (22 × 16 cm)
- Wheels and motor brackets
- Breadboard
- Jumper wires (male–male, male–female)

### Pinout
Refer to the top of `MazeBotFinals.ino` for exact defines. Summary below:
- ENA (left motor PWM): pin 5
- IN1/IN2 (left motor direction): pins 4, 3
- ENB (right motor PWM): pin 6
- IN3/IN4 (right motor direction): pins 7, 8
- Left ultrasonic: trig A0, echo A1
- Front ultrasonic: trig A2, echo A3

### Configuration & Tuning
This section explains the key constants, what they control, and a recommended procedure to tune them safely.

Key parameters (defined at top of `MazeBotFinals.ino`):
- `BASE_SPEED_LEFT`, `BASE_SPEED_RIGHT` — Base PWM values (0–255) controlling motor speed. Start low and increase until the motors move reliably without stalling.
- `STUCK_DIST` — Distance (cm) that counts as "too close" and triggers an emergency reverse.
- `MIN_WALL_DIST` / `MAX_WALL_DIST` — Target window for left-wall following. The robot adjusts wheel speeds when the left distance falls outside this range.
- `OPEN_WALL_DIST` — Threshold to detect when the left side is open (room to turn left).
- `FRONT_WALL_DIST` — Threshold for considering the front blocked (dead end) and triggering a 180° turn.
- `TURN_90_TIME`, `TURN_180_TIME` — Milliseconds the robot applies differential wheel actions to perform approximate turns. These values depend on motor speed, wheel diameter, and battery voltage.

Recommended tuning steps:
1. Power the robot off and verify wiring matches the `Pinout` section.
2. With no obstacles, upload the sketch and open the Serial Monitor at `9600` baud.
3. Start with `BASE_SPEED_*` around `100–120` and test forward motion in short bursts. If motors stall, raise the speed; if motors are too fast or unstable, lower the speed.
4. Tune turning constants:
	- Place the robot in an open area and run a test to perform a 90° command (use `turn90Left()` by temporarily calling it or by observing behavior during a normal run when the left side is detected as open).
	- Adjust `TURN_90_TIME` until the physical rotation matches ~90°. Repeat for `TURN_180_TIME`.
5. Wall-follow thresholds:
	- Stand alongside a wall and watch `Left:` readings in the Serial Monitor. Set `MIN_WALL_DIST` and `MAX_WALL_DIST` around the typical measured distance ±5 cm to produce gentle corrections.
6. Stuck detection:
	- If the robot tends to get wedged, consider increasing `STUCK_TIMEOUT` or tweaking the emergency reverse durations in the code.

Safety & notes:
- Always keep the robot on a test mat or other controlled surface while tuning.
- Disconnect the motors when adjusting wiring or changing the mounting.
- Battery voltage affects motor speed; retune `TURN_*_TIME` and `BASE_SPEED_*` after changing the battery or motor load.

### Behavior Summary
The control logic is organized as a prioritized reactive sequence evaluated in `loop()`:

1. Anti-stuck monitor
	- Tracks changes in combined sensor readings. If the readings remain static for the duration of `STUCK_TIMEOUT`, the robot performs an emergency reverse to free itself.

2. Emergency front/backups
	- If the front distance is below `STUCK_DIST`: perform a short reverse.
	- If the left distance is below `STUCK_DIST`: perform a short reverse biased to the right to avoid the wall.

3. Dead-end handling
	- If `distFront < FRONT_WALL_DIST`: stop and execute `turn180Right()` to escape the dead end.

4. Left-open detection
	- If `distLeft > OPEN_WALL_DIST`: the robot moves slightly forward, executes `turn90Left()`, and proceeds — effectively taking the left turn when available.

5. Normal wall-follow corrections
	- If left distance < `MIN_WALL_DIST`: the robot steers right by slowing the right motor.
	- If left distance > `MAX_WALL_DIST`: the robot steers left by slowing the left motor.
	- Otherwise, drive straight using `BASE_SPEED_*`.

### Serial Debugging
Open the Serial Monitor at `9600` baud. Typical output:

Left: 18 cm | Front: 40 cm

Use these readings to verify sensor health, tune thresholds, and diagnose odd behavior.

### Contributors
- Aaron Ludwig Altar — Code debugging, Video documentation
- Alexander John Balagso — Code debugging, Code documentation
- Carl Jayson Eli Bonaobra — Code debugging, Hardware debugging
- Ronald William Geron — Hardware debugging, MazeBot design

### Laboratory Advisor
- Engr. Charles Ray B. Juanillas

### License
Use and modify this code for lab and learning purposes. Please credit your team when sharing.
