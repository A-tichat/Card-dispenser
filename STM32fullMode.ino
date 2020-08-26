#include <Servo.h>
#include <Wire_slave.h>

#define DIR PB3
#define STP PB5
#define SERVO PB7
#define LIMIT_SWITCH PA3
#define SDA PB11
#define SCL PB10
#define SET_ADDRESS PA0
#define stepper 800

int address = 0;
int box;
int stepping;
int readLimitSwitch;
Servo myservo;

void setup() {
  Serial.begin(115200);
  pinMode(SET_ADDRESS, INPUT);
  pinMode(DIR, OUTPUT);
  pinMode(STP, OUTPUT);
  pinMode(LIMIT_SWITCH, INPUT);
  digitalWrite(DIR, LOW);
  myservo.attach(SERVO);
  myservo.write(0);
  setAddress(SET_ADDRESS);
  Wire.begin(address); // join i2c bus with address
  Wire.onReceive(receiveEvent); // register event
}

void loop() {
    delay(100);
    if(box > -1){
      stepping = box * stepper;
      stepMoter(false, stepping);
      servoHit();
      int i = 0;
      while(readLimitSwitch < 500) {
        delay(50);
        readLimitSwitch = analogRead(LIMIT_SWITCH);
        i++;
        stepMoter(true, i);
      }
    }
}

void receiveEvent(int howMany){
  box = Wire.read();
}

void servoHit() {
    myservo.write(90);
    delay(1000);
    myservo.write(0);
    delay(1000);
}

void stepMoter (boolean dir, uint steps) {
  digitalWrite (DIR, dir);
  delay (50);
  for (int i = 0; i < steps; i++) {
    digitalWrite (STP, HIGH);
    delayMicroseconds (800);
    digitalWrite (STP, LOW);
    delayMicroseconds (800);
  }

}

void setAddress (int set) {
      if (set < 1400) {
        address = 70;
      }else if (set > 1400 && set < 1500) {
          address = 71;
        }else if (set > 2300 && set < 2400) {
            address = 72;
          }else if (set > 2900 && set < 3000) {
              address = 73;
            }else if (set > 3400 && set < 3500) {
                address = 74;
              }else if (set > 3700 && set < 3800) {
                  address = 75;
                }else if (set > 4000 && set < 4100) {
                    address = 76;
                  }else {Serial.println("Unknow analog raed PIN PA0 or Apart from defined");}
}
