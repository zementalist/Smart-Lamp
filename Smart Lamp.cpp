// This file is the code within .ino file, just in case you couldn't open it

int red = 13;
int green = 12;
int blue = 11;
int leds[3] = {red, green, blue};

String msg;

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(10);
}

void loop() {
  while(!Serial.available());
  msg = Serial.readString();

  // No. of leds to control
  int n_leds = msg.substring(0).toInt();

  // distance between thumb & index
  String finger_dist_str = msg.substring(2);
  int finger_dist = finger_dist_str.toInt();

  // Map 0-25 to 0-255
  int sign = map(finger_dist, 0, 25, 0, 255);

  // Apply lumination to No. of leds to control
  for(int i = 0; i < n_leds; i++) {
    analogWrite(leds[i], sign);
  }
}