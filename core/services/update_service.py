import requests

class UpdateService:

    API_URL = "https://api.github.com/repos/kholif18/school-bell/releases/latest"

    def check_latest(self):
        r = requests.get(self.API_URL, timeout=5)

        if r.status_code != 200:
            raise Exception("Cannot check update")

        data = r.json()

        return {
            "version": data["tag_name"],
            "url": data["html_url"]
        }