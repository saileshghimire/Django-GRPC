import os
import sys
import django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'system1.settings')
django.setup()

import grpc
from concurrent import futures
import uuid
from user import user_pb2_grpc
from user import user_pb2
from django.db.utils import IntegrityError

from django.contrib.auth import get_user_model
User = get_user_model()

class UserService(user_pb2_grpc.UserServiceServicer):
    def CreateUser(self, request, context):
        try:
            user = User.objects.create_user(
                email=request.email,
                password=request.password,
                first_name=request.first_name,
                middle_name=request.middle_name,
                last_name=request.last_name,
                is_active=True,
                is_superuser=False,
                is_staff=False
            )
            return user_pb2.CreateUserResponse(success=True, message='User created', user=user)
        except IntegrityError:
            # return CreateUserResponse(success=False, message='Error creating user')
            context.abort(grpc.StatusCode.ALREADY_EXISTS, 'User already exists')
    
    def GetUser(self, request, context):
        try:
            user = User.objects.get(email=request.email)
            return user_pb2.GetUserResponse(user=User())
        except User.DoesNotExist:
            context.abort(grpc.StatusCode.NOT_FOUND, 'User not found')
    
    def UpdateUser(self, request, context):
        try:
            user = User.objects.get(id=request.id)
            user.email = request.email
            user.first_name = request.first_name
            user.middle_name = request.middle_name
            user.last_name = request.last_name
            user.is_staff = request.is_staff
            user.is_superuser = request.is_superuser
            user.save()
            return user_pb2.UpdateUserResponse(success=True, message='User updated', user=user)
        except User.DoesNotExist:
            context.abort(grpc.StatusCode.NOT_FOUND, 'User not found')





def serve():
    try:
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        user_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
        server.add_insecure_port('[::]:50051')
        server.start()
        print('Server started at 50051')
        server.wait_for_termination()
    except Exception as e:
        print(f"Error:${e}")

    
if __name__ == '__main__':
    serve()