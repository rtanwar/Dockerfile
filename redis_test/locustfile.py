from locust import HttpUser, between, task


class WebsiteUser(HttpUser):
    wait_time = between(5, 15)
    
    def on_start(self):
        self.client.get("/data")
    
    @task
    def index(self):        
        self.client.get("/data/1")
        
    @task
    def about(self):
        self.client.get("/data/2")
