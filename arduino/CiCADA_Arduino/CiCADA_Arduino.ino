
// Initiate buttons to I/O pins, initiate ShiftPWM latch pin, invert for common anode LEDs
const int buttons [9] = {4, 19, 3, 14, 20, 16, 17, 15, 18};
const int ShiftPWM_latchPin=53;
const bool ShiftPWM_invertOutputs = true; 
const bool ShiftPWM_balanceLoad = false;

// Define speed and target multipliers in order to translate incoming bytes (0-255) to proper ranges
const int SPD_MULT = 2;
const int TARGET_MULT = 323;

// 
int buf[5] = { 0, 0, 0, 0, 0 };
int buf_ptr = 0;

// Set boolean active, include ShiftPWM and AccelStepper libraries
boolean active = true;
#include <ShiftPWM.h>
#include <AccelStepper.h>

// Set maxBrightness to 2 (allows LEDs to actually turn mostly off), pwmFrequency (maximum refresh before noticeable lag), set the number of shift registers to 18
unsigned char maxBrightness = 2;
unsigned char pwmFrequency = 120;
int numRegisters = 18;

// Define the number of stepper motors, initiate data storage array (H = height, S = speed)
AccelStepper steppers[9];
//                Hs1  Ss1  Hs2  Ss2  Hs3  Ss3  Hs4  Ss4  Hs5  Ss5  Hs6  Ss6  Hs7  Ss7  Hs8  Ss8  Hs9  Ss9   
long data[18] = {   0, 410,   0, 410,   0, 410,   0, 410,   0, 410,   0, 410,   0, 410,   0, 410,   0, 410};

// Initiate button state storage array
int buttonState[9] = { LOW, LOW, LOW, LOW, LOW, LOW, LOW, LOW, LOW};

// Define led, stepper, zero objects
void led(byte idx, byte r, byte g, byte b);
void stepper(byte idx, long target, long spd);
void zero();

void setup(){
  
  for( int i =0; i<9; i++)
  {
  pinMode(buttons[i],INPUT_PULLUP);
  }
  
steppers[0] = AccelStepper(AccelStepper::FULL4WIRE, 22, 24, 23, 25);
steppers[1] = AccelStepper(AccelStepper::FULL4WIRE, 26, 28, 27, 29);
steppers[2] = AccelStepper(AccelStepper::FULL4WIRE, 30, 32, 31, 33);
steppers[3] = AccelStepper(AccelStepper::FULL4WIRE, 34, 36, 35, 37);
steppers[4] = AccelStepper(AccelStepper::FULL4WIRE, 38, 40, 39, 41);
steppers[5] = AccelStepper(AccelStepper::FULL4WIRE, 42, 44, 43, 45);
steppers[6] = AccelStepper(AccelStepper::FULL4WIRE, 12, 10, 11, 9);
steppers[7] = AccelStepper(AccelStepper::FULL4WIRE, 8, 6, 7, 5);
steppers[8] = AccelStepper(AccelStepper::FULL4WIRE, 46, 48, 47, 49);

for( int i = 0; i < 9; i++ )
{
steppers[i].setMaxSpeed(410);
steppers[i].setAcceleration(0);
}    
    
  Serial.begin(9600);
  ShiftPWM.SetAmountOfRegisters(numRegisters);
  ShiftPWM.SetPinGrouping(1);
  ShiftPWM.Start(pwmFrequency,maxBrightness);
       
}

void serialEvent()
{
  byte b = 0;
  while(Serial.available())
  {
    b = Serial.read();
    if(255 == b)
    {
      switch( buf[0] )
      {
        case 0: led(buf[1],buf[2],buf[3],buf[4]);break;
        case 1: stepper(buf[1],buf[2],buf[3]);break;
        case 2: stepper(buf[1],-buf[2],buf[3]);break;
        case 3: zero(); break;
        default: break;
      }
      buf_ptr = 0;
    }
    else
    {
      buf[buf_ptr] = b;
      buf_ptr = (buf_ptr + 1)%5;
    }
  }
}

void loop()
{    
  boolean done = true;
  int currentState;
  for(int i=0; i<9; i++)
  {
    currentState = digitalRead(buttons[i]);
    if( currentState != buttonState[i])
    {
      if( currentState == HIGH)
      {
        Serial.write(255-i);
      }
      else
      {
        Serial.write(i);
      }
    }
    buttonState[i] = currentState;
if( buttonState[i] == HIGH )
{
steppers[i].moveTo(data[i*2]);
steppers[i].setSpeed(data[i*2+1]);
if( steppers[i].distanceToGo()==0)
{
steppers[i].disableOutputs();
}
else
{
steppers[i].enableOutputs();
steppers[i].runSpeedToPosition();
done = false;
active = true;
}
}
  }
if( done == true && active==true)
{
Serial.write(128);
active = false;
}
}

void led(byte idx, byte r, byte g, byte b)
{
  int offset = idx*3+2*((idx*3)/6);
  ShiftPWM.SetOne (offset, r);
  ShiftPWM.SetOne (offset+1, g);
  ShiftPWM.SetOne (offset+2, b);
}
void stepper(byte idx, long target, long spd)
{
  data[idx*2] = target*TARGET_MULT;
  data[idx*2+1] = spd*SPD_MULT;
}
void zero()
{
  for(int i=0; i<9; i++)
  {
    steppers[i].setCurrentPosition(0);
  }
}
