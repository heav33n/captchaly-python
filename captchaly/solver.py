import logging
from requests.adapters import HTTPAdapter
import requests
import urllib3
import json

logging.basicConfig(level=logging.INFO)

RECAPTCHAV2_TYPE = "recaptchav2"
RECAPTCHAV3_TYPE = "recaptchav3"
CLOUDFLARE_TURNSTILE_TYPE = "turnstile"
HCAPTCHA_TYPE = "hcaptcha"
HCAPTCHA_ENTERPRISE_TYPE = "hcaptcha-enterprise"
GEETESTV4_TYPE = "geetest"


class TaskBadParametersError(Exception):
    pass


class APIClient:
    HOST = "https://v1.captchaly.com"

    def __init__(self, api_key: str, open_log: bool) -> None:
        self.api_key = api_key
        self.open_log = open_log
        self.session = requests.session()

        adapter = HTTPAdapter(pool_maxsize=1000)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        urllib3.disable_warnings()

    def _get_balance(self) -> str:
        response = self.session.get(
            url=self.HOST + "/account", params={"apikey": self.api_key}
        )
        status_code = response.status_code

        if status_code != 200:
            if self.open_log:
                logging.error(f"Error: {status_code} {response.text}")

            return response.json()

        if self.open_log:
            logging.info(f"Balance: {response.json().get('balance')}")

        return response.json().get("balance")

    def _send(self, task_type: str, task: dict) -> str:
        response = self.session.get(
            url=self.HOST + f"/{task_type.lower()}",
            params=task,
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
        status_code = response.status_code

        if status_code != 200:
            if self.open_log:
                logging.error(
                    f"Got status code {status_code} with error {response.text}"
                )

            if status_code == 401:
                return "Invalid API key."
            elif status_code == 402:
                return "Your account doesn't have enough funds. Please recharge your account!"
            elif status_code == 403:
                return "Your account subscription has expired. Please renew your subscription or use the Pay-Per-Token service!"
            elif status_code == 422:
                # This error is unparseable without replication
                return str(response.json().get("detail")[0].get("msg"))
            elif status_code == 429:
                return "Concurrency limit reached! Please wait until your other requests finish!"
            elif status_code == 503:
                return "Failed to solve the captcha. Please try again."
            else:
                return "Unknown error."

        token = str(response.json().get("token"))

        if self.open_log:
            logging.info(f"Token retrieved: {token}")

        return str(token)


class CaptchalyAPI:
    def __init__(self, api_key: str, open_log: bool = True) -> None:
        self.api = APIClient(api_key=api_key, open_log=open_log)

    def recaptchav2(self, website_url: str, website_key: str) -> str:
        """
        Solve reCAPTCHA v2 challenge.

        :param website_url: The URL of the website where the reCAPTCHA is located.
        :param website_key: The sitekey of the reCAPTCHA.
        :return: A dictionary containing the solution of the reCAPTCHA or the error generated.
        """
        task = {"sitekey": website_key, "url": website_url}
        return self.api._send(RECAPTCHAV2_TYPE, task)

    def recaptchav3(
        self,
        website_url: str,
        website_key: str,
        page_action: str = "",
        fast: bool = False,
    ) -> str:
        """
        Solve reCAPTCHA v3 challenge.

        :param website_url: The URL of the website where the reCAPTCHA is located.
        :param website_key: The sitekey of the reCAPTCHA.
        :param page_action: The action parameter to use for the reCAPTCHA.
        :param fast: Optional. If it should pioritize speed over quality.
        :return: A dictionary containing the solution of the reCAPTCHA or the error generated.
        """
        task = {
            "sitekey": website_key,
            "action": page_action,
            "fast": fast,
            "url": website_url,
        }
        return self.api._send(RECAPTCHAV3_TYPE, task)

    def turnstile(
        self,
        website_url: str,
        website_key: str,
        page_action: str = "",
        website_cdata: str = "",
    ) -> str:
        """
        Solve Turnstile challenge.

        :param website_url: The URL of the website where the Turnstile is located.
        :param website_key: The sitekey of the Turnstile.
        :param page_action: Optional. The action parameter to use for the Turnstile.
        :param website_cdata: Optional. The value of `the data-cdata` property of the captcha element.
        :return: A dictionary containing the solution of the Turnstile or the error generated.
        """
        task = {
            "sitekey": website_key,
            "url": website_url,
        }
        if website_cdata:
            task["cdata"] = website_cdata

        if page_action:
            task["action"] = page_action

        return self.api._send(CLOUDFLARE_TURNSTILE_TYPE, task)

    def hcaptcha(
        self,
        website_url: str,
        website_key: str,
        proxy_type: str = "",
        proxy_address: str = "",
        proxy_port: int = 0,
        proxy_login: str = "",
        proxy_password: str = "",
    ) -> str:
        """
        Solve hCaptcha challenge.

        :param website_url: The URL of the website where the hCaptcha is located.
        :param website_key: The sitekey of the hCaptcha.
        :param proxy_type: Optional. The type of the proxy (HTTP, HTTPS, SOCKS4, SOCKS5).
        :param proxy_address: Optional. The address of the proxy.
        :param proxy_port: Optional. The port of the proxy.
        :param proxy_login: Optional. The login for the proxy.
        :param proxy_password: Optional. The password for the proxy.
        :return: A dictionary containing the solution of the hCaptcha or the error generated.
        """
        task = {
            "sitekey": website_key,
            "url": website_url,
        }
        if proxy_address and proxy_port:
            if proxy_login and proxy_password:
                task["proxy"] = (
                    f"{proxy_type}://{proxy_login}:{proxy_password}@{proxy_address}:{proxy_port}"
                )
            else:
                task["proxy"] = f"{proxy_type}://{proxy_address}:{proxy_port}"

        return self.api._send(HCAPTCHA_TYPE, task)

    def hcaptcha_enterprise(
        self,
        website_url: str,
        website_key: str,
        proxy_type: str = "",
        proxy_address: str = "",
        proxy_port: int = 0,
        proxy_login: str = "",
        proxy_password: str = "",
    ) -> str:
        """
        Solve hCaptcha Enterprise challenge.

        :param website_url: The URL of the website where the hCaptcha is located.
        :param website_key: The sitekey of the hCaptcha.
        :param proxy_type: Optional. Recommended.The type of the proxy (HTTP, HTTPS, SOCKS4, SOCKS5).
        :param proxy_address: Optional. Recommended. The address of the proxy.
        :param proxy_port: Optional. Recommended. The port of the proxy.
        :param proxy_login: Optional. Recommended. The login for the proxy.
        :param proxy_password: Optional. Recommended. The password for the proxy.
        :return: A dictionary containing the solution of the hCaptcha or the error generated.
        """
        task = {
            "sitekey": website_key,
            "url": website_url,
        }
        if proxy_address and proxy_port:
            if proxy_login and proxy_password:
                task["proxy"] = (
                    f"{proxy_type}://{proxy_login}:{proxy_password}@{proxy_address}:{proxy_port}"
                )
            else:
                task["proxy"] = f"{proxy_type}://{proxy_address}:{proxy_port}"

        return self.api._send(HCAPTCHA_ENTERPRISE_TYPE, task)

    def geetestv4(
        self,
        website_url: str,
        website_captcha_id: str,
    ) -> dict:
        """
        Solve GeeTest v4 challenge.

        :param website_url: The URL of the website where the GeeTest is located.
        :param website_captcha_id: The captcha_id of the GeeTest.
        :return: A dictionary containing the solution of the GeeTest or the error generated.
        """
        task = {
            "captchaId": website_captcha_id,
            "url": website_url,
        }

        # ts pmo "magic"
        return json.loads(self.api._send(GEETESTV4_TYPE, task).replace("'", '"'))

    def get_balance(self) -> str:
        """
        Get the account balance.

        :return: A string representing the account balance.
        """
        return self.api._get_balance()
