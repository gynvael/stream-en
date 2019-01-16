#include <stdint.h>
#define PIN_SER 8
#define PIN_SRCLK 9
#define PIN_RCLK 10

short data_pins[] = {
  11, 12, 2, 3, 4, 5, 6, 7
};

void setup() {
  for (int i = 0; i < 8; i++) 
    pinMode(data_pins[i], INPUT);

  pinMode(PIN_SER, OUTPUT);
  pinMode(PIN_SRCLK, OUTPUT);
  pinMode(PIN_RCLK, OUTPUT);

  Serial.begin(115200); 
}

void sr_send_addr(uint32_t addr) {
  digitalWrite(PIN_RCLK, 0);
  
  for (int i = 0; i < 20; i++) {
    digitalWrite(PIN_SRCLK, 0);
    digitalWrite(PIN_SER, (addr >> (19 - i)) & 1);
    digitalWrite(PIN_SRCLK, 1);
  }

  digitalWrite(PIN_RCLK, 1);  
}

uint8_t sr_get_byte() {
  uint8_t b = 0;
  for (int i = 0; i < 8; i++) {
    b |= digitalRead(data_pins[i]) << i;
  }
  
  return b;
}

void print_hex(uint8_t x) {
  if (x < 0x10) {
    Serial.print('0');
    Serial.print(x, HEX);
  } else {
    Serial.print(x, HEX);
  }
}

void loop() {
  Serial.print("Start---\n");
  for (uint32_t addr = 0; addr < (1UL << 20); addr++) {
    sr_send_addr(addr);
    uint8_t b = sr_get_byte();
    print_hex(b);

    if ((addr + 1) % 16 == 0) {
      Serial.print("\n");
    }
  }

  Serial.print("Done!\n");
  for(;;);
}
