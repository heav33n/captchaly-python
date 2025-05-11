# Captchaly Python Module
Captchaly is a fast, reliable, and affordable CAPTCHA solving with a powerful API. Ensure seamless automation and efficiency while we handle the challenges.

This SDK is made by myself, expect bugs.

## Installation
You can install the Captchaly Python Module with Pip:

```shell
pip install captchaly
```

## Usage
First, obtain the API Key from the dashboard in the [Captchaly Official Website](https://captchaly.com/dashboard) dashboard. Then, create a Captchaly instance:

```python3
from captchaly import CaptchalyAPI

api = CaptchalyAPI(client_api="YOUR_API_KEY")
# You can also disable the logs:
# api = CaptchalyAPI(client_api="YOUR_API_KEY", open_log=False)
```

# Solve captcha
### reCAPTCHA v2

```python3
token = api.recaptchav2(website_url="...", website_key="...")
```

### reCAPTCHA v3

```python3
token = api.recaptchav3(website_url="...", website_key="...", page_action="...", fast="OPTIONAL")
```

### Turnstile

```python3
token = api.turnstile(website_url="...", website_key="...", page_action="...", website_cdata="OPTIONAL")
```

### hCaptcha

```python3
token = api.hcaptcha(website_url="...", website_key="...", proxy_type="OPTIONAL", proxy_address="OPTIONAL", proxy_port="OPTIONAL", proxy_login="OPTIONAL", proxy_password="OPTIONAL")
```

### hCaptcha Enterprise

```python3
token = api.hcaptcha_enterprise(website_url="...", website_key="...", proxy_type="OPTIONAL", proxy_address="OPTIONAL", proxy_port="OPTIONAL", proxy_login="OPTIONAL", proxy_password="OPTIONAL")
```

### GeeTest v4

```python3
token = api.geetestv4(website_url="...", website_captcha_id="...")
```

# Error Handling
When any error happens, it will return the description of the error as an string.

# Contributing
If you find any bugs or have suggestions for improvement, please feel free to submit an issue or send a pull request. I welcome all contributions!

# License
This project is licensed under the MIT License. For more information, please see the LICENSE file.
