#include "esp_camera.h"
#include <WiFi.h>

//
// WARNING!!! PSRAM IC required for UXGA resolution and high JPEG quality
//            Ensure ESP32 Wrover Module or other board with PSRAM is selected
//            Partial images will be transmitted if image exceeds buffer size
//
//            You must select partition scheme from the board menu that has at least 3MB APP space.
//            Face Recognition is DISABLED for ESP32 and ESP32-S2, because it takes up from 15
//            seconds to process single frame. Face Detection is ENABLED if PSRAM is enabled as well

// ===================
// Select camera model
// ===================

#define CAMERA_MODEL_ESP32S3_EYE // Has PSRAM


#include "camera_pins.h"

// ===========================
// Enter  WiFi credentials
// ===========================

const char *ssid = "wifidandiganteng";
const char *password = "11111111";

void startCameraServer();
void setupLedFlash(int pin);

void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(false); //disable debug for better performance
  Serial.println();

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  // config.xclk_freq_hz = 20000000;
  config.xclk_freq_hz = 24000000; // Experiment with 24 MHz
  // config.frame_size = FRAMESIZE_UXGA;
  config.frame_size = FRAMESIZE_XGA; // Lower resolution with good quality
  config.pixel_format = PIXFORMAT_JPEG;  // for streaming
  //config.pixel_format = PIXFORMAT_RGB565; // for face detection/recognition
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 8; // Lower value, better quality 
  config.fb_count = 3;

  // =======if PSRAM IC present, init with UXGA resolution and higher JPEG quality
  //========== for larger pre-allocated frame buffer.

  if (!psramFound()) {
    Serial.println("PSRAM not found. Switching to DRAM buffers.");
    config.fb_location = CAMERA_FB_IN_DRAM;
    config.frame_size = FRAMESIZE_VGA; // Lower resolution if PSRAM unavailable
    config.fb_count = 1;
  }

  //================== camera init =============================
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }


  // =============== Configure sensor settings for OV5640
  sensor_t *s = esp_camera_sensor_get();
    if (s->id.PID == OV5640_PID) {
    s->set_brightness(s, 1);        // Increase brightness slightly
    s->set_saturation(s, 1);       // Increase saturation for richer colors
    s->set_contrast(s, 1);         // Slightly increase contrast
    s->set_whitebal(s, 1);         // Enable auto white balance
    s->set_gain_ctrl(s, 1);        // Enable gain control
    s->set_exposure_ctrl(s, 1);    // Enable auto exposure control
    s->set_aec2(s, 1);             // Advanced auto exposure for low light
    s->set_sharpness(s, 1);        // Enable sharpness
    s->set_denoise(s, 1);          // Enable noise reduction
    s->set_vflip(s, 0);            // Adjust based on camera orientation
    s->set_hmirror(s, 0);          // Adjust based on camera orientation
    // s->set_lens_correction(s, 1);  // Enable lens correction for distortion
  }



  // WiFi connection
  WiFi.begin(ssid, password);
  WiFi.setSleep(false);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");

  startCameraServer();

  Serial.print("Camera Ready! Use 'http://");
  Serial.print(WiFi.localIP());
  Serial.println("' to connect");
}

void loop() {
  // Do nothing. Everything is done in another task by the web server
  delay(10000);
}
