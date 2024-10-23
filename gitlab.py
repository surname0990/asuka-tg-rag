import requests

class GitLabAPI:
    def __init__(self, private_token, base_url='https://gitlab.com/api/v4'):
        self.private_token = private_token
        self.base_url = base_url
        self.headers = {'PRIVATE-TOKEN': self.private_token}

    def get_projects(self):
        """Получение списка проектов."""
        response = requests.get(f'{self.base_url}/projects', headers=self.headers)
        return response.json()