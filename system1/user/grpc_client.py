import grpc
import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
# import django
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'system1.settings')
# django.setup()

from user import user_pb2_grpc
from user import user_pb2

class UserClient:
    def __init__(self):
        self.channel = grpc.insecure_channel('localhost:50051')
        self.stub = user_pb2_grpc.UserServiceStub(self.channel)
    
    def create_user(self, email, password, first_name, middle_name, last_name):
        request = user_pb2.CreateUserRequest(
            email=email,
            password=password,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name
        )
        try:
            response = self.stub.CreateUser(request)
            return response
        except grpc.RpcError as e:
            print(f"Error creating user: {e.code().name} - {e.details()}")
            return None
    
    def get_user(self, email):
        request = user_pb2.GetUserRequest(email=email)
        try:
            response = self.stub.GetUser(request)
            return response
        except grpc.RpcError as e:
            print(f"Error fetching user: {e.code().name} - {e.details()}")
            return None
    
    def get_all_users(self):
        request = user_pb2.GetAllUserRequest()
        try:
            response = self.stub.GetAllUser(request)
            return response
        except grpc.RpcError as e:
            print(f"Error fetching all user: {e.code().name} - {e.details()}")
            return None
    
    def update_user(self, id, email, first_name, middle_name, last_name, is_staff, is_superuser):
        request = user_pb2.UpdateUserRequest(
            id=id,
            email=email,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            is_staff=is_staff,
            is_superuser=is_superuser
        )
        try:
            response = self.stub.UpdateUser(request)
            return response
        except grpc.RpcError as e:
            print(f"Error updating user: {e.code().name} - {e.details()}")
            return None
    

if __name__ == '__main__':
    client = UserClient()
    
    user1 = client.create_user(
        email="saileshghimire@gmail.com",
        password="123456",
        first_name="Sailesh",
        middle_name="Kumar",
        last_name="Ghimire",
    )

    print("All User:")
    response = client.get_all_users()
    if response:
        for user in response.users:
            print(user)