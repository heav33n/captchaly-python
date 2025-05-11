from captchaly import CaptchalyAPI

api = CaptchalyAPI("CP_FKwPA4KHJheq3s5ZZW58UDTPn8CPSYmjfQDJn4VYAHm")

token = api.recaptchav2(
    "https://recaptcha-demo.appspot.com/recaptcha-v2-checkbox.php",
    "6LfW6wATAAAAAHLqO2pb8bDBahxlMxNdo9g947u9",
)

print(token)
