import grpc
# from user.user_pb2_grpc import UserServiceStub
from user import user_pb2_grpc
from user import user_pb2
# from user.user_pb2 import CreateUserRequest, GetUserRequest, UpdateUserRequest

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
        response = self.stub.CreateUser(request)
        return response
    
    def get_user(self, email):
        request = user_pb2.GetUserRequest(email=email)
        response = self.stub.GetUser(request)
        return response
    
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
        response = self.stub.UpdateUser(request)
        return response
    

if __name__ == '__main__':
    client = UserClient()
    
    user1 = client.create_user(
        email="saileshghimire@gmail.com",
        password="123456",
        first_name="Sailesh",
        last_name="Ghimire",
        is_staff=False,
        is_superuser=False
    )

    print("All User:")
    for user in client.get_user():
        print(user)