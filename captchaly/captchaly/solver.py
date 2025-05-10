import logging
import time
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import requests
import urllib3

logging.basicConfig(level=logging.INFO)

RECAPTCHAV2_TYPE = "recaptchav2"
RECAPTCHAV2_ENTERPRISE_TYPE = "RecaptchaV2EnterpriseTaskProxyless"
RECAPTCHAV2HS_ENTERPRISE_TYPE = "RecaptchaV2HSEnterpriseTaskProxyless"
RECAPTCHAV3_PROXYLESS_TYPE = "RecaptchaV3TaskProxyless"
RECAPTCHAV3HS_PROXYLESS_TYPE = "RecaptchaV3HSTaskProxyless"
RECAPTCHAV3_TYPE = "RecaptchaV3Task"
RECAPTCHA_MOBILE_PROXYLESS_TYPE = "ReCaptchaMobileTaskProxyLess"
RECAPTCHA_MOBILE_TYPE = "ReCaptchaMobileTask"
HCAPTCHA_TYPE = "HCaptchaTask"
HCAPTCHA_PROXYLESS_TYPE = "HCaptchaTaskProxyless"
HCAPTCHA_ENTERPRISE_TYPE = "HCaptchaEnterpriseTask"

TIMEOUT = 45

PENDING_STATUS = "pending"
PROCESSING_STATUS = "processing"
READY_STATUS = "ready"
FAILED_STATUS = "failed"


class TaskBadParametersError(Exception):
    pass


class ApiClient:
    HOST = "https://v1.captchaly.com"

    def __init__(self, client_key: str, solft_id: str, callback_url: str, open_log: bool) -> None:
        self.client_key = client_key
        self.solft_id = solft_id
        self.callback_url = callback_url
        self.open_log = open_log
        self.session = requests.session()

        adapter = HTTPAdapter(pool_maxsize=1000)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        urllib3.disable_warnings()

    def _get_balance(self) -> str:
        resp = self.session.post(url=self.HOST + "/getBalance", json={"clientKey": self.client_key})
        if resp.status_code != 200:
            if self.open_log:
                logging.error(f"Error: {resp.status_code} {resp.text}")
            return resp.json()
        if self.open_log:
            logging.info(f"Balance: {resp.json().get('balance')}")
        return resp.json().get("balance")

    def _send(self, task_type: str, task: dict) -> str:
        response = self.session.post(url=self.HOST + f"/{task_type.lower()}", params=task)
        status_code = response.status_code

        if status_code != 200:
            if self.open_log:
                logging.error(f"Got status code {status_code} with error {response.text}")

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

        return str(response.json().get("token"))


class CaptchalyApi:
    def __init__(self, client_key: str, solft_id: str = "", callback_url: str = "", open_log: bool = True) -> None:
        self.api = ApiClient(client_key=client_key, solft_id=solft_id, callback_url=callback_url, open_log=open_log)

    def recaptchav2(self, website_url: str, website_key: str, recaptcha_data_s_value: str = "",
                    is_invisible: bool = False, api_domain: str = "", page_action: str = "",
                    website_info: str = "") -> dict:
        """
        Solve reCAPTCHA v2 challenge.

        :param website_url: The URL of the website where the reCAPTCHA is located.
        :param website_key: The sitekey of the reCAPTCHA.
        :param recaptcha_data_s_value: Optional. The value of the 'data-s' parameter if present.
        :param is_invisible: Optional. Whether the reCAPTCHA is invisible or not.
        :param api_domain: Optional. The domain of the reCAPTCHA API if different from the default.
        :return: A dictionary containing the solution of the reCAPTCHA.
        """
        task = {
            "sitekey": website_key,
            "url": website_url
        }
        return self.api._send(RECAPTCHAV2_TYPE, task)

    def recaptchav2enterprise(self, website_url: str, website_key: str, enterprise_payload: dict = {},
                              is_invisible: bool = False, api_domain: str = "", page_action: str = "",
                              website_info: str = "") -> dict:
        """
        Solve reCAPTCHA v2 Enterprise challenge.

        :param website_url: The URL of the website where the reCAPTCHA is located.
        :param website_key: The sitekey of the reCAPTCHA.
        :param enterprise_payload: Optional. Additional enterprise payload parameters.
        :param is_invisible: Optional. Whether the reCAPTCHA is invisible or not.
        :param api_domain: Optional. The domain of the reCAPTCHA API if different from the default.
        :return: A dictionary containing the solution of the reCAPTCHA.
        """
        task = {
            "type": RECAPTCHAV2_ENTERPRISE_TYPE,
            "websiteURL": website_url,
            "websiteKey": website_key,
            "enterprisePayload": enterprise_payload,
            "isInvisible": is_invisible,
            "apiDomain": api_domain,
            "pageAction": page_action,
            "websiteInfo": website_info

        }
        return self.api._send(task)

    def recaptchav2hs_enterprise(self, website_url: str, website_key: str, enterprise_payload: dict = {},
                                 is_invisible: bool = False, api_domain: str = "", page_action: str = "",
                                 website_info: str = "") -> dict:
        """
        Solve reCAPTCHA v2 Enterprise challenge.

        :param website_url: The URL of the website where the reCAPTCHA is located.
        :param website_key: The sitekey of the reCAPTCHA.
        :param enterprise_payload: Optional. Additional enterprise payload parameters.
        :param is_invisible: Optional. Whether the reCAPTCHA is invisible or not.
        :param api_domain: Optional. The domain of the reCAPTCHA API if different from the default.
        :return: A dictionary containing the solution of the reCAPTCHA.
        """
        task = {
            "type": RECAPTCHAV2HS_ENTERPRISE_TYPE,
            "websiteURL": website_url,
            "websiteKey": website_key,
            "enterprisePayload": enterprise_payload,
            "isInvisible": is_invisible,
            "apiDomain": api_domain,
            "pageAction": page_action,
            "websiteInfo": website_info

        }
        return self.api._send(task)

    def recaptchav3(self, website_url: str, website_key: str, page_action: str = "", api_domain: str = "",
                    proxy_type: str = "", proxy_address: str = "", proxy_port: int = 0, proxy_login: str = "",
                    proxy_password: str = "", website_info: str = "") -> dict:
        """
        Solve reCAPTCHA v3 challenge.

        :param website_url: The URL of the website where the reCAPTCHA is located.
        :param website_key: The sitekey of the reCAPTCHA.
        :param page_action: Optional. The action parameter to use for the reCAPTCHA.
        :param api_domain: Optional. The domain of the reCAPTCHA API if different from the default.
        :param proxy_type: Optional. The type of the proxy (HTTP, HTTPS, SOCKS4, SOCKS5).
        :param proxy_address: Optional. The address of the proxy.
        :param proxy_port: Optional. The port of the proxy.
        :param proxy_login: Optional. The login for the proxy.
        :param proxy_password: Optional. The password for the proxy.
        :return: A dictionary containing the solution of the reCAPTCHA.
        """
        task = {
            "type": RECAPTCHAV3_PROXYLESS_TYPE,
            "websiteURL": website_url,
            "websiteKey": website_key,
            "pageAction": page_action,
            "apiDomain": api_domain,
            "websiteInfo": website_info

        }
        if proxy_address:
            task["type"] = RECAPTCHAV3_TYPE
            task["proxyType"] = proxy_type
            task["proxyAddress"] = proxy_address
            task["proxyPort"] = proxy_port
            task["proxyLogin"] = proxy_login
            task["proxyPassword"] = proxy_password
        return self.api._send(task)

    def recaptchav3hs(self, website_url: str, website_key: str, page_action: str = "", api_domain: str = "",
                      website_info: str = "") -> dict:
        """
        Solve reCAPTCHA v3 challenge.

        :param website_url: The URL of the website where the reCAPTCHA is located.
        :param website_key: The sitekey of the reCAPTCHA.
        :param page_action: Optional. The action parameter to use for the reCAPTCHA.
        :param api_domain: Optional. The domain of the reCAPTCHA API if different from the default.
        :param proxy_type: Optional. The type of the proxy (HTTP, HTTPS, SOCKS4, SOCKS5).
        :param proxy_address: Optional. The address of the proxy.
        :param proxy_port: Optional. The port of the proxy.
        :param proxy_login: Optional. The login for the proxy.
        :param proxy_password: Optional. The password for the proxy.
        :return: A dictionary containing the solution of the reCAPTCHA.
        """
        task = {
            "type": RECAPTCHAV3HS_PROXYLESS_TYPE,
            "websiteURL": website_url,
            "websiteKey": website_key,
            "pageAction": page_action,
            "apiDomain": api_domain,
            "websiteInfo": website_info

        }
        return self.api._send(task)

    def recaptcha_mobile(self, app_key: str, app_package_name: str = "", app_action: str = "", proxy_type: str = "",
                         proxy_address: str = "", proxy_port: int = 0, proxy_login: str = "",
                         proxy_password: str = "", app_device: str = "ios") -> dict:
        """
        Solve Mobile reCAPTCHA challenge.

        :param app_key: The app key of the Mobile reCAPTCHA.
        :param app_package_name: Optional. The package name of the mobile app.
        :param app_action: Optional. The action parameter to use for the Mobile reCAPTCHA.
        :return: A dictionary containing the solution of the Mobile reCAPTCHA.
        """
        task = {
            "type": RECAPTCHA_MOBILE_PROXYLESS_TYPE,
            "appKey": app_key,
            "appPackageName": app_package_name,
            "appAction": app_action,
            "appDevice": app_device,
        }
        if proxy_address != "":
            task["type"] = RECAPTCHA_MOBILE_TYPE
            task["proxyType"] = proxy_type
            task["proxyAddress"] = proxy_address
            task["proxyPort"] = proxy_port
            task["proxyLogin"] = proxy_login
            task["proxyPassword"] = proxy_password
        return self.api._send(task)

    def hcaptcha(self, website_url: str, website_key: str, is_invisible: bool = False, enterprise_payload: dict = {},
                 proxy_type: str = "", proxy_address: str = "", proxy_port: int = 0, proxy_login: str = "",
                 proxy_password: str = "") -> dict:
        """
        Solve hCaptcha challenge.

        :param website_url: The URL of the website where the hCaptcha is located.
        :param website_key: The sitekey of the hCaptcha.
        :param is_invisible: Optional. Whether the hCaptcha is invisible or not.
        :param enterprise_payload: Optional. Additional enterprise payload parameters.
        :param proxy_type: Optional. The type of the proxy (HTTP, HTTPS, SOCKS4, SOCKS5).
        :param proxy_address: Optional. The address of the proxy.
        :param proxy_port: Optional. The port of the proxy.
        :param proxy_login: Optional. The login for the proxy.
        :param proxy_password: Optional. The password for the proxy.
        :return: A dictionary containing the solution of the hCaptcha.
        """
        task = {
            "type": HCAPTCHA_PROXYLESS_TYPE,
            "websiteURL": website_url,
            "websiteKey": website_key,
            "isInvisible": is_invisible,
            "enterprisePayload": enterprise_payload,
        }
        if proxy_address:
            task["type"] = HCAPTCHA_TYPE
            task["proxyType"] = proxy_type
            task["proxyAddress"] = proxy_address
            task["proxyPort"] = proxy_port
            task["proxyLogin"] = proxy_login
            task["proxyPassword"] = proxy_password
        return self.api._send(task)

    def hcaptcha_enterprise(self, website_url: str, website_key: str, enterprise_payload: dict = {},
                            is_invisible: bool = False, proxy_type: str = "", proxy_address: str = "",
                            proxy_port: int = 0, proxy_login: str = "", proxy_password: str = "") -> dict:
        """
        Solve hCaptcha Enterprise challenge.

        :param website_url: The URL of the website where the hCaptcha is located.
        :param website_key: The sitekey of the hCaptcha.
        :param enterprise_payload: Optional. Additional enterprise payload parameters.
        :param is_invisible: Optional. Whether the hCaptcha is invisible or not.
        :param proxy_type: Optional. The type of the proxy (HTTP, HTTPS, SOCKS4, SOCKS5).
        :param proxy_address: Optional. The address of the proxy.
        :param proxy_port: Optional. The port of the proxy.
        :param proxy_login: Optional. The login for the proxy.
        :param proxy_password: Optional. The password for the proxy.
        :return: A dictionary containing the solution of the hCaptcha.
        """
        task = {
            "type": HCAPTCHA_ENTERPRISE_TYPE,
            "websiteURL": website_url,
            "websiteKey": website_key,
            "enterprisePayload": enterprise_payload,
            "isInvisible": is_invisible,
            "proxyType": proxy_type,
            "proxyAddress": proxy_address,
            "proxyPort": proxy_port,
            "proxyLogin": proxy_login,
            "proxyPassword": proxy_password,
        }
        return self.api._send(task)

    def get_balance(self) -> str:
        """
        Get the account balance.

        :return: A string representing the account balance.
        """
        return self.api._get_balance()
