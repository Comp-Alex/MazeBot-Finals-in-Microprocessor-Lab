<div align="center">
  <img src="dashboard/assets/maze-bot.svg" alt="MazeBot line-art icon" width="96">
  <h1>MazeBot Engineering Dashboard</h1>
  <p>Maze-solving robot · Microprocessor Lab Finals · A.Y. 2025–2026</p>
  <p><strong>Last updated:</strong> 2026-10-31 UTC</p>
</div>

> A living project snapshot generated from `dashboard/config.json` and repository history. Progress percentages are engineering estimates based on checked-in evidence, not automated hardware test results.

## Robot specifications

| Subsystem | Specification |
|---|---|
| Controller | Arduino Uno (or compatible) |
| Motor driver | L298N dual H-bridge |
| Drive | 2 × 9 V DC motors · differential drive |
| Distance sensors | 2 × HC-SR04 ultrasonic (left and front) |
| Power | 5,000 mAh power bank · TP4056 charging module · XL6009 motor supply boost |
| Chassis | Acrylic, 22 × 16 cm |

### Motor and sensor pinout

| Signal | Arduino pin(s) |
|---|---:|
| Left motor PWM (ENA) | 5 |
| Left motor direction (IN1 / IN2) | 4 / 3 |
| Right motor PWM (ENB) | 6 |
| Right motor direction (IN3 / IN4) | 7 / 8 |
| Left ultrasonic (TRIG / ECHO) | A0 / A1 |
| Front ultrasonic (TRIG / ECHO) | A2 / A3 |

## Engineering milestones

**Estimated engineering milestone completion: 56%**  
` 56%` `███████████░░░░░░░░░`  
Average of 8 configured milestone estimates.

| Workstream | Status | Progress | Repository evidence |
|---|---|---:|---|
| Embedded firmware and I/O bring-up | Implemented | `100%` `████████████████████` | Arduino setup, GPIO initialization, and 9600-baud serial diagnostics. |
| Ultrasonic sensor integration | Implemented | `100%` `████████████████████` | Left and front HC-SR04 readings with a bounded pulse measurement. |
| Differential-drive motor control | Implemented | `100%` `████████████████████` | L298N direction/PWM control, forward motion, stopping, and timed turns. |
| Reactive maze navigation | Implemented | `100%` `████████████████████` | Left-wall following, open-left turns, dead-end turns, and emergency reverse. |
| Repeatable hardware calibration | In progress | ` 45%` `█████████░░░░░░░░░░░` | Tunable thresholds and turn durations are documented; repeatability still needs measured test results. |
| Closed-loop PID motion control | Planned | `  0%` `░░░░░░░░░░░░░░░░░░░░` | Current firmware uses fixed PWM values and timed turns; no PID loop is present. |
| Wheel encoder odometry | Planned | `  0%` `░░░░░░░░░░░░░░░░░░░░` | No wheel encoders or position feedback are currently documented. |
| Non-blocking control and fault handling | Planned | `  0%` `░░░░░░░░░░░░░░░░░░░░` | The current control loop uses delay(); scheduling and sensor-fault handling can be improved. |

## Embedded systems and control

The Arduino sketch initializes the motor-driver and ultrasonic I/O, reports left/front distances over Serial at **9600 baud**, and runs a prioritized reactive controller:

1. Read left and front HC-SR04 distances.
2. Attempt an emergency reverse if readings are dangerously close or appear unchanged for the stuck timeout.
3. Turn right at a front dead end; take a left turn when the left side is open.
4. Otherwise, adjust the two motor PWM values to follow the left wall.

Motor commands are open-loop: the sketch uses fixed PWM values and timed turns. **PID control and wheel encoder feedback are not implemented yet.**

### Current tuning reference

| Parameter | Current value | Purpose |
|---|---:|---|
| Left / right base PWM | 110 / 110 | 0–255 PWM; tune at low speed on a clear test surface. |
| Emergency proximity | 6 cm | Reverse if a valid front or left reading is closer. |
| Left-wall correction window | 15–25 cm | Steering corrections are based on the left sensor. |
| Open-left threshold | 35 cm | Advance, then execute a timed left turn. |
| Front dead-end threshold | 15 cm | Execute a timed 180° right turn. |
| 90° / 180° turn duration | 120 / 220 ms | Open-loop timing; recalibrate when battery or load changes. |
| Stuck timeout | 5 s | Triggers a timed emergency reverse when readings appear unchanged. |

`getDistance()` uses a 25 ms `pulseIn()` timeout and maps a missing/invalid echo to 999 cm. Treat that sentinel carefully when validating sensor health; it can otherwise resemble an open path.

## Future improvements

- Add wheel encoders and use closed-loop PID to balance wheel speed and improve turn accuracy.
- Replace blocking delays with a millis()-based state machine so sensing and safety checks remain responsive.
- Validate ultrasonic readings (timeouts, outliers, and cross-talk) and expose sensor faults in diagnostics.
- Log repeatable course runs, calibration values, and success rate so navigation changes can be compared objectively.
- Re-test motor thresholds and battery behavior under load; document safe voltage limits for the motor supply.

## Repository statistics

| Stars | 0 |
| Forks | 0 |
| Open issues | 0 |
| GitHub repository size | 6,498 KB |
| Tracked files | 9 |
| Git commits | 16 |
| Contributors in local history | 3 |

## Recent commits

| Date | Commit |
|---|---|
| 2026-10-30 | [`e5a3e8f` chore: refresh robotics dashboard [skip ci]](https://github.com/Comp-Alex/MazeBot-Finals-in-Microprocessor-Lab/commit/e5a3e8f9e01d7a0c1cfce3d8e1eb137209f26334) |
| 2026-10-29 | [`06c31cf` chore: refresh robotics dashboard [skip ci]](https://github.com/Comp-Alex/MazeBot-Finals-in-Microprocessor-Lab/commit/06c31cfcc90f2985ab73a44dac9bf063db59c413) |
| 2026-10-28 | [`dbaf756` chore: refresh robotics dashboard [skip ci]](https://github.com/Comp-Alex/MazeBot-Finals-in-Microprocessor-Lab/commit/dbaf756f96210774d9a7926fcf39fac9d5245843) |
| 2026-10-27 | [`df76ec3` chore: refresh robotics dashboard [skip ci]](https://github.com/Comp-Alex/MazeBot-Finals-in-Microprocessor-Lab/commit/df76ec33ae9e7aad36454d70b5bce3f75340dc1f) |
| 2026-10-26 | [`2daf16d` chore: refresh robotics dashboard [skip ci]](https://github.com/Comp-Alex/MazeBot-Finals-in-Microprocessor-Lab/commit/2daf16d0ae01aa196ab870ee27127a962f0f69ab) |

## Maze and run footage

![Maze course](<Maze-CPE2026.jpg>)

[View the MazeBot run video](<Speedup run of Mazebot.mp4>)

## Team

- Aaron Ludwig Altar — code debugging, video documentation
- Alexander John Balagso — code debugging, code documentation
- Carl Jayson Eli Bonaobra — code debugging, hardware debugging
- Ronald William Geron — hardware debugging, MazeBot design

**Laboratory advisor:** Engr. Charles Ray B. Juanillas

## Safe testing notes

- Test on a clear, controlled surface and start with low motor PWM.
- Disconnect power before changing wiring.
- Battery voltage and motor load change turn behavior; recalibrate after changing either.
- Verify the XL6009 output and motor-driver supply against component ratings before connecting the motors.

---

Generated daily by [`.github/workflows/dashboard.yml`](.github/workflows/dashboard.yml). To refresh locally, run `python dashboard/dashboard.py --offline` from the repository root. The script uses only the Python standard library.
