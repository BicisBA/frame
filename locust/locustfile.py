import random

from locust import FastHttpUser, task


class StationsUser(FastHttpUser):
    @task
    def fetch_closest(self):
        response = self.client.get("/stations").json()
        stations = list(set(x.get("station_id") for x in response))
        for i in random.sample(stations, 5):
            self.client.get(f"/stations/{i}/status")
