#include <Arduino.h>
// CONFIGURATION: Pins and calibrated values

// --- Motor Pins (L298N) ---
#define ENA  5  // PWM pin for left motor speed
#define IN1  4  // left motor direction
#define IN2  3  // left motor direction
#define ENB  6  // PWM pin for right motor speed
#define IN3  7  // right motor direction
#define IN4  8  // right motor direction

// --- Ultrasonic Sensor Pins ---
#define trigLeft  A0
#define echoLeft  A1
#define trigFront A2
#define echoFront A3

// --- Motor speed calibration ---
const int BASE_SPEED_LEFT  = 110;  // Base PWM for left motor
const int BASE_SPEED_RIGHT = 110;  // Base PWM for right motor

// --- Distance thresholds (in centimeters) ---
const int STUCK_DIST      = 6;     // Distance considered "stuck" (emergency reverse)
const int MIN_WALL_DIST   = 15;    // Too close to left wall
const int MAX_WALL_DIST   = 25;    // Comfortable distance from left wall
const int OPEN_WALL_DIST  = 35;    // Considered open space on the left
const int FRONT_WALL_DIST = 15;    // Distance to front wall to trigger 180 turn

// --- Turn timing (milliseconds) ---
const int TURN_90_TIME  = 120;    // Milliseconds to approximate 90 degrees
const int TURN_180_TIME = 220;    // Milliseconds to approximate 180 degrees

// --- Anti-idle / stuck detection variables ---
unsigned long lastMoveTime = 0;
long lastDistSum = 0;
const long STUCK_TIMEOUT = 5000;   // 5 seconds

void setup() {
  Serial.begin(9600);

  // Setup Ultrasonic Pins
  pinMode(trigLeft, OUTPUT);  pinMode(echoLeft, INPUT);
  pinMode(trigFront, OUTPUT); pinMode(echoFront, INPUT);

  // Setup Motor Driver Pins
  pinMode(ENA, OUTPUT); pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(ENB, OUTPUT); pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT);
  
  lastMoveTime = millis(); 
}

void loop() {
  // 1. Read distances from sensors
  long distLeft  = getDistance(trigLeft, echoLeft);
  long distFront = getDistance(trigFront, echoFront);

  // Debug output to Serial Monitor
  Serial.print("Left: "); Serial.print(distLeft);
  Serial.print("cm | Front: "); Serial.println(distFront);

  // --- Anti-stuck logic (movement detector) ---
  if (abs((distLeft + distFront) - lastDistSum) > 1) {
    lastMoveTime = millis(); 
    lastDistSum = distLeft + distFront;
  }
  if (millis() - lastMoveTime > STUCK_TIMEOUT) {
    stopMotors();
    delay(200);
    // Emergency reverse to free the robot
    analogWrite(ENA, BASE_SPEED_LEFT);
    digitalWrite(IN1, LOW); digitalWrite(IN2, HIGH);
    analogWrite(ENB, BASE_SPEED_RIGHT - 40);
    digitalWrite(IN3, LOW); digitalWrite(IN4, HIGH);
    delay(600);
    stopMotors();
    lastMoveTime = millis();
    return;
  }

  // 2. Left-wall follower behavior

  // Case A: Emergency backup (front obstacle)
  if (distFront < STUCK_DIST && distFront > 0) {
    stopMotors();
    delay(100);
    analogWrite(ENA, BASE_SPEED_LEFT);
    digitalWrite(IN1, LOW); digitalWrite(IN2, HIGH); 
    analogWrite(ENB, BASE_SPEED_RIGHT - 20); 
    digitalWrite(IN3, LOW); digitalWrite(IN4, HIGH); 
    delay(500); 
    stopMotors();
    delay(100);
    return; 
  }

  // Case A.1: Emergency backup (too close to left wall)
  if (distLeft < STUCK_DIST && distLeft > 0) {
    stopMotors();
    delay(100);
    analogWrite(ENA, BASE_SPEED_LEFT - 30); 
    digitalWrite(IN1, LOW); digitalWrite(IN2, HIGH); 
    analogWrite(ENB, BASE_SPEED_RIGHT);     
    digitalWrite(IN3, LOW); digitalWrite(IN4, HIGH); 
    delay(450); 
    stopMotors();
    delay(100);
    return;
  }

  // Case B: Dead end (front is close) -> 180 turn to the right
  if (distFront < FRONT_WALL_DIST && distFront > 0) {
    stopMotors();
    delay(200);
    turn180Right();
    return; 
  }

  // Case C: Left side is open -> move and turn left
  if (distLeft > OPEN_WALL_DIST) {
    moveForward(BASE_SPEED_LEFT, BASE_SPEED_RIGHT); 
    delay(250); 
    turn90Left();
    moveForward(BASE_SPEED_LEFT, BASE_SPEED_RIGHT); 
    delay(400);
    return;
  }

  // Case D: Normal wall-following corrections
  if (distLeft < MIN_WALL_DIST && distLeft > 0) {
    moveForward(BASE_SPEED_LEFT, BASE_SPEED_RIGHT - 35);
  } 
  else if (distLeft > MAX_WALL_DIST) {
    moveForward(BASE_SPEED_LEFT - 35, BASE_SPEED_RIGHT);
  } 
  else {
    moveForward(BASE_SPEED_LEFT, BASE_SPEED_RIGHT);
  }

  delay(30); 
}

// ====================================================================
// FUNCTIONS: sensors and motor movement (no logic changes)
// ====================================================================

long getDistance(int trigPin, int echoPin) {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  long duration = pulseIn(echoPin, HIGH, 25000); 
  long distance = duration * 0.034 / 2;
  if (distance <= 0) return 999; 
  return distance;
}

void moveForward(int speedLeft, int speedRight) {
  analogWrite(ENA, speedLeft);
  digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);
  analogWrite(ENB, speedRight);
  digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
}

void turn90Left() {
  analogWrite(ENA, BASE_SPEED_LEFT);
  digitalWrite(IN1, LOW); digitalWrite(IN2, HIGH); 
  analogWrite(ENB, BASE_SPEED_RIGHT);
  digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);  
  delay(TURN_90_TIME);
  stopMotors();
}

void turn180Right() {
  analogWrite(ENA, BASE_SPEED_LEFT);
  digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);  
  analogWrite(ENB, BASE_SPEED_RIGHT);
  digitalWrite(IN3, LOW); digitalWrite(IN4, HIGH); 
  delay(TURN_180_TIME);
  stopMotors();
}

void stopMotors() {
  digitalWrite(IN1, LOW);   digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);   digitalWrite(IN4, LOW);
  analogWrite(ENA, 0);      analogWrite(ENB, 0);
}