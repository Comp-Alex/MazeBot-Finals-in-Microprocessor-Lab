<div align="center">
  <img src="dashboard/assets/maze-bot.svg" alt="MazeBot line-art icon" width="96">
  <h1>{{project_name}} Engineering Dashboard</h1>
  <p>{{subtitle}}</p>
  <p><strong>Last updated:</strong> {{updated_at}}</p>
</div>

> A living project snapshot generated from `dashboard/config.json` and repository history. Progress percentages are engineering estimates based on checked-in evidence, not automated hardware test results.

## Robot specifications

| Subsystem | Specification |
|---|---|
{{specifications}}

### Motor and sensor pinout

| Signal | Arduino pin(s) |
|---|---:|
{{pinout}}

## Engineering milestones

{{overall_progress}}

| Workstream | Status | Progress | Repository evidence |
|---|---|---:|---|
{{milestones}}

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
{{tuning}}

`getDistance()` uses a 25 ms `pulseIn()` timeout and maps a missing/invalid echo to 999 cm. Treat that sentinel carefully when validating sensor health; it can otherwise resemble an open path.

## Future improvements

{{future_improvements}}

## Repository statistics

{{statistics}}

## Recent commits

{{recent_commits}}

## Maze and run footage

{{media}}

## Team

{{contributors}}

**Laboratory advisor:** {{advisor}}

## Safe testing notes

- Test on a clear, controlled surface and start with low motor PWM.
- Disconnect power before changing wiring.
- Battery voltage and motor load change turn behavior; recalibrate after changing either.
- Verify the XL6009 output and motor-driver supply against component ratings before connecting the motors.

---

Generated daily by [`.github/workflows/dashboard.yml`](.github/workflows/dashboard.yml). To refresh locally, run `python dashboard/dashboard.py --offline` from the repository root. The script uses only the Python standard library.
