#include "Wire.h"

#include "I2Cdev.h"
#include "MPU9250.h"
#include "BMP180.h"

MPU9250 accelgyro;
I2Cdev   I2C_M;

uint8_t buffer_m[6];

int16_t ax, ay, az;
int16_t gx, gy, gz;
int16_t   mx, my, mz;

float heading;
float tiltheading;

float Axyz[3];
float Gxyz[3];
float Mxyz[3];

#define sample_num_mdate  5000

volatile float mx_sample[3];
volatile float my_sample[3];
volatile float mz_sample[3];

static float mx_centre = 0;
static float my_centre = 0;
static float mz_centre = 0;

volatile int mx_max = 0;
volatile int my_max = 0;
volatile int mz_max = 0;

volatile int mx_min = 0;
volatile int my_min = 0;
volatile int mz_min = 0;

float temperature;
float pressure;
float atm;
float altitude;
BMP180 Barometer;

void setup() {
// join I2C bus (I2Cdev library doesn't do this automatically)
    Wire.begin();

    // initialize serial communication
    // (38400 chosen because it works as well at 8MHz as it does at 16MHz, but
    // it's really up to you depending on your project)
    Serial.begin(38400);

    // initialize device
    accelgyro.initialize();
    Barometer.init();

    delay(1000);
}

// Prints the data as a form:
// Acceleration data x,y,z, Gyroscope data x,y,z, HearthRate
// float,float,float,float,float,float,int
void loop() {
  getAccel_Data();
  getGyro_Data();
  Serial.print(Axyz[0]);
  Serial.print(",");
  Serial.print(Axyz[1]);
  Serial.print(",");
  Serial.print(Axyz[2]);
  Serial.print(",");
  Serial.print(Gxyz[0]);
  Serial.print(",");
  Serial.print(Gxyz[1]);
  Serial.print(",");
  Serial.print(Gxyz[2]);
  Serial.print(",");

  // Hearth rate as (beats/min)
  Wire.requestFrom(0xA0 >> 1, 1);
  if (Wire.available()) {
    int hr = Wire.read();
    Serial.print(hr);
  }
  Serial.println();
  delay(5000);
}

void getAccel_Data(void)
{
  // The acceleration data as (g)
    accelgyro.getMotion9(&ax, &ay, &az, &gx, &gy, &gz, &mx, &my, &mz);
    Axyz[0] = (double) ax / 16384;
    Axyz[1] = (double) ay / 16384;
    Axyz[2] = (double) az / 16384;
}
void getGyro_Data(void)
{
  // The gyro data as (degrees/s)
    accelgyro.getMotion9(&ax, &ay, &az, &gx, &gy, &gz, &mx, &my, &mz);
    Gxyz[0] = (double) gx * 250 / 32768;
    Gxyz[1] = (double) gy * 250 / 32768;
    Gxyz[2] = (double) gz * 250 / 32768;
}
