import requests
import json


class GitHubAPI:
    def __init__(self, token=None):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if token:
            self.headers["Authorization"] = f"token {token}"

    def search_user(self, username):
        """Поиск пользователей по имени"""
        try:
            url = f"{self.base_url}/search/users"
            params = {
                "q": username,
                "per_page": 30
            }

            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            data = response.json()
            users = []
            for user in data.get("items", []):
                users.append({
                    "login": user["login"],
                    "id": user["id"],
                    "type": user["type"],
                    "avatar_url": user["avatar_url"],
                    "html_url": user["html_url"]
                })

            return {
                "success": True,
                "data": users
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Ошибка API: {str(e)}"
            }

    def get_user_info(self, username):
        """Получение подробной информации о пользователе"""
        try:
            url = f"{self.base_url}/users/{username}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            data = response.json()
            return {
                "success": True,
                "data": data
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Ошибка API: {str(e)}"
            }

    def get_user_repos(self, username):
        """Получение списка репозиториев пользователя"""
        try:
            url = f"{self.base_url}/users/{username}/repos"
            params = {
                "sort": "updated",
                "per_page": 10
            }

            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            repos = response.json()
            return {
                "success": True,
                "data": repos
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Ошибка API: {str(e)}"
            }