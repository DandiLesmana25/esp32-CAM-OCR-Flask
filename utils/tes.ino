

static esp_err_t capture_handler(httpd_req_t *req) {
  camera_fb_t *fb = NULL;
  esp_err_t res = ESP_OK;
#if ARDUHAL_LOG_LEVEL >= ARDUHAL_LOG_LEVEL_INFO
  int64_t fr_start = esp_timer_get_time();
#endif

#if CONFIG_LED_ILLUMINATOR_ENABLED
  enable_led(true);
  vTaskDelay(150 / portTICK_PERIOD_MS);  // The LED needs to be turned on ~150ms before the call to esp_camera_fb_get()
  fb = esp_camera_fb_get();              // or it won't be visible in the frame. A better way to do this is needed.
  enable_led(false);
#else
  fb = esp_camera_fb_get();
#endif

  if (!fb) {
    log_e("Camera capture failed");
    httpd_resp_send_500(req);
    return ESP_FAIL;
  }

  httpd_resp_set_type(req, "image/jpeg");
  httpd_resp_set_hdr(req, "Content-Disposition", "inline; filename=capture.jpg");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");

  esp_http_client_handle_t http_client;
  esp_http_client_config_t config_client = {0};
  config_client.url = servername;

  // set time out 10 second
  config_client.timeout_ms = 60000; 
  config_client.event_handler = _http_event_handler;
  config_client.method = HTTP_METHOD_POST;

  http_client = esp_http_client_init(&config_client);
  esp_http_client_set_header(http_client, "Content-Type", "multipart/form-data");

  esp_http_client_set_post_field(http_client, postdata, strlen(postdata));

  http_client = esp_http_client_init(&config_client);
  
  esp_http_client_set_post_field(http_client, (const char *)fb->buf, fb->len);

// Tambahkan header untuk tipe konten
  // esp_http_client_set_header(http_client, "Content-Type", "image/jpg");
  esp_http_client_set_header(http_client, "Content-Type", "multipart/form-data");

  esp_err_t err = esp_http_client_perform(http_client);

  if (err == ESP_OK) {
    ESP_LOGI(TAG, "HTTP POST Status = %d, content_length = %d",
             esp_http_client_get_status_code(http_client),
             esp_http_client_get_content_length(http_client));
} else {
    ESP_LOGE(TAG, "HTTP POST request failed: %s", esp_err_to_name(err));
}

// Hapus HTTP client setelah selesai
esp_http_client_cleanup(http_client);

  // =============================