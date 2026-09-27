#include "HX711.h"

#define DT_PIN 5
#define SCK_PIN 4

HX711 scale;

float calibration_factor = 1.0;

void setup() {
    Serial.begin(115200);

    scale.begin(DT_PIN, SCK_PIN);
    scale.set_scale(calibration_factor);
    scale.tare();

    Serial.println("SIH26179 RACK SENSOR");
    Serial.println("HX711 READY");
}

void loop() {
    if (scale.is_ready()) {
        float weight = scale.get_units(5);

        if (weight < 0) {
            weight = 0;
        }

        Serial.print("RACK_WEIGHT:");
        Serial.println(weight, 2);
    } else {
        Serial.println("SENSOR_ERROR");
    }

    delay(1000);
}