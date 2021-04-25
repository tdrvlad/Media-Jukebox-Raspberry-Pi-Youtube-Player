

// constants won't change. They're used here to set pin numbers:
int input_pins[] = {2, 3, 4, 5, 6, 7, 8, A2, A1, A0};
int output_pins[] = {9, 10, 11, 12};

// variables will change:
int buttonState = 0;         // variable for reading the pushbutton status

void setup() {
  for (int i = 0; i < 10; i++)
    pinMode(input_pins[i], INPUT);
  // initialize the pushbutton pin as an input:
  
  for (int i = 0; i < 3; i++)
    pinMode(output_pins[i], OUTPUT);

  pinMode(13, OUTPUT);
  Serial.begin(9600);
}

int get_button() {
  for (int i = 0; i < 10; i++) {
    int state = digitalRead(input_pins[i]);
    if(state == 1) 
      return i + 1;
  }
  return 0; 
}

void loop() {

  int pressed = get_button();
  Serial.println(pressed);
  
  if (pressed != 0) {
    
    if (pressed == 1) {
      digitalWrite(output_pins[0], LOW);
      digitalWrite(output_pins[1], LOW);
      digitalWrite(output_pins[2], LOW);
      digitalWrite(output_pins[3], HIGH);
    }
    if (pressed == 2) {
      digitalWrite(output_pins[0], LOW);
      digitalWrite(output_pins[1], LOW);
      digitalWrite(output_pins[2], HIGH);
      digitalWrite(output_pins[3], LOW);
    }
    if (pressed == 3) {
      digitalWrite(output_pins[0], LOW);
      digitalWrite(output_pins[2], LOW);
      digitalWrite(output_pins[2], HIGH);
      digitalWrite(output_pins[3], HIGH);
    }
    if (pressed == 4) {
      digitalWrite(output_pins[0], LOW);
      digitalWrite(output_pins[1], HIGH);
      digitalWrite(output_pins[2], LOW);
      digitalWrite(output_pins[3], LOW);
    }
    if (pressed == 5) {
      digitalWrite(output_pins[0], LOW);
      digitalWrite(output_pins[1], HIGH);
      digitalWrite(output_pins[2], LOW);
      digitalWrite(output_pins[3], HIGH);
    }
    if (pressed == 6) {
      digitalWrite(output_pins[0], LOW);
      digitalWrite(output_pins[1], HIGH);
      digitalWrite(output_pins[2], HIGH);
      digitalWrite(output_pins[3], LOW);
    }
    if (pressed == 7) {
      digitalWrite(output_pins[0], LOW);
      digitalWrite(output_pins[1], HIGH);
      digitalWrite(output_pins[2], HIGH);
      digitalWrite(output_pins[3], HIGH);
    }
    if (pressed == 8) {
      digitalWrite(output_pins[0], HIGH);
      digitalWrite(output_pins[1], LOW);
      digitalWrite(output_pins[2], LOW);
      digitalWrite(output_pins[3], LOW);
    }
    if (pressed == 9) {
      digitalWrite(output_pins[0], HIGH);
      digitalWrite(output_pins[1], LOW);
      digitalWrite(output_pins[2], LOW);
      digitalWrite(output_pins[3], HIGH);
    }
    if (pressed == 10) {
      digitalWrite(output_pins[0], HIGH);
      digitalWrite(output_pins[1], LOW);
      digitalWrite(output_pins[2], HIGH);
      digitalWrite(output_pins[3], LOW);
    }
  }
  else {
    digitalWrite(output_pins[0], LOW);
    digitalWrite(output_pins[1], LOW);
    digitalWrite(output_pins[2], LOW);
    digitalWrite(output_pins[3], LOW);
 }
  delay(100);
}
