import grpc
from grpc_reflection.v1alpha import reflection_pb2_grpc, reflection_pb2
import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
# import django
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'system1.settings')
# django.setup()

# from user import user_pb2_grpc
# from user import user_pb2
from google.protobuf.json_format import MessageToDict, ParseDict
from google.protobuf.descriptor_pb2 import FileDescriptorProto
from google.protobuf.descriptor_pb2 import FileDescriptorSet
from google.protobuf import descriptor_pool, message_factory

class UserClient:
    def __init__(self):
        self.channel = grpc.insecure_channel('localhost:50051')
        self.stub = reflection_pb2_grpc.ServerReflectionStub(self.channel)
    
    def list_services(self):
        """Lists available gRPC services on the server"""
        request = reflection_pb2.ServerReflectionRequest(list_services='')
        response = self.stub.ServerReflectionInfo(iter([request]))

        for service in response:
            print(f"Available service:{service.list_services_response.service}")

    
    def get_service_descriptor(self, service_name):
        """Get the descriptor of a service"""
        request = reflection_pb2.ServerReflectionRequest(file_containing_symbol=service_name)
        response = self.stub.ServerReflectionInfo(iter([request]))
        
        for file_descriptor in response:
            for file_descriptor_proto in file_descriptor.file_descriptor_response.file_descriptor_proto:
                file_descriptor_parsed = FileDescriptorProto()
                file_descriptor_parsed.ParseFromString(file_descriptor_proto)
                if file_descriptor_parsed.service:
                    for service in file_descriptor_parsed.service:
                        return service
                        # print(f"Found service: {service.name}")
                        # if service.name == service_name:
                        #     return service

        print(f"Service {service_name} not found")
        return None
    def _get_file_descriptors(self, service_name):
        """Retrieve FileDescriptorProtos for the given service using reflection."""
        request = reflection_pb2.ServerReflectionRequest(file_containing_symbol=service_name)
        alt_responses = self.stub.ServerReflectionInfo(iter([request]))
        file_descriptions = []
        for resposne in alt_responses:
            if resposne.HasField('file_descriptor_response'):
                file_descriptions.extend(resposne.file_descriptor_response.file_descriptor_proto)
        return file_descriptions
    
    def call_method(self, service_name, method_name, request_dict):
        # Get FileDescriptorProtos for the service
        fd_protos = self._get_file_descriptors(service_name)
        
        # Create a descriptor pool and add descriptors
        pool = descriptor_pool.DescriptorPool()
        for fd_proto_bytes in fd_protos:
            fd_proto = FileDescriptorProto()
            fd_proto.ParseFromString(fd_proto_bytes)
            pool.Add(fd_proto)
        
        try:
            # Get service and method descriptors
            service_desc = pool.FindServiceByName(service_name)
            method_desc = next(m for m in service_desc.methods if m.name == method_name)
        except (KeyError, StopIteration):
            print(f"Service/Method not found: {service_name}/{method_name}")
            return None

        # Create message factories
        request_class = message_factory.MessageFactory(pool).GetPrototype(method_desc.input_type)
        response_class = message_factory.MessageFactory(pool).GetPrototype(method_desc.output_type)

        # Create request message from dictionary
        request = ParseDict(request_dict, request_class())

        # Create method full name
        method_full_name = f'/{service_name}/{method_name}'

        # Create RPC method
        if method_desc.client_streaming or method_desc.server_streaming:
            print("Streaming methods not supported")
            return None

        rpc_method = self.channel.unary_unary(
            method_full_name,
            request_serializer=request_class.SerializeToString,
            response_deserializer=response_class.FromString
        )

        # Execute RPC call
        try:
            response = rpc_method(request)
            return MessageToDict(response, preserving_proto_field_name=True)
        except grpc.RpcError as e:
            print(f"RPC failed: {e.code()}: {e.details()}")
            return None

    # def call_method(self, service_name, method_name, request_dict):
    #     """Dynamically calls a method with JSON input"""
    #     service_descriptor = self.get_service_descriptor(service_name)
    #     if not service_descriptor:
    #         print(f"Service {service_name} not found")
    #         return None  
    #     for method in service_descriptor.method:
    #         if method.name == method_name:
    #             print("hi")
    #             method_name = f".user.{method_name}"
    #             request = grpc.dynamic_stub.DynamicStub(self.channel).Invoke(service_name,method_name,request_dict)
    #             return MessageToDict(request)  
    #     print(f"Method {method_name} not found in service {service_name}.")
    #     return None
                
    
    # def create_user(self, email, password, first_name, middle_name, last_name):
    #     request = user_pb2.CreateUserRequest(
    #         email=email,
    #         password=password,
    #         first_name=first_name,
    #         middle_name=middle_name,
    #         last_name=last_name
    #     )
    #     try:
    #         response = self.stub.CreateUser(request)
    #         return response
    #     except grpc.RpcError as e:
    #         print(f"Error creating user: {e.code().name} - {e.details()}")
    #         return None
    
    # def get_user(self, email):
    #     request = user_pb2.GetUserRequest(email=email)
    #     try:
    #         response = self.stub.GetUser(request)
    #         return response
    #     except grpc.RpcError as e:
    #         print(f"Error fetching user: {e.code().name} - {e.details()}")
    #         return None
    
    # def get_all_users(self):
    #     request = user_pb2.GetAllUserRequest()
    #     try:
    #         response = self.stub.GetAllUser(request)
    #         return response
    #     except grpc.RpcError as e:
    #         print(f"Error fetching all user: {e.code().name} - {e.details()}")
    #         return None
    
    # def update_user(self, id, email, first_name, middle_name, last_name, is_staff, is_superuser):
    #     request = user_pb2.UpdateUserRequest(
    #         id=id,
    #         email=email,
    #         first_name=first_name,
    #         middle_name=middle_name,
    #         last_name=last_name,
    #         is_staff=is_staff,
    #         is_superuser=is_superuser
    #     )
    #     try:
    #         response = self.stub.UpdateUser(request)
    #         return response
    #     except grpc.RpcError as e:
    #         print(f"Error updating user: {e.code().name} - {e.details()}")
    #         return None
    

if __name__ == '__main__':
    client = UserClient()
    
    # client.list_services()
    # data = client.get_service_descriptor("user.UserService")
    # print(data)
    # user1 = client.create_user(
    #     email="saileshghimire@gmail.com",
    #     password="123456",
    #     first_name="Sailesh",
    #     middle_name="Kumar",
    #     last_name="Ghimire",
    # )

    user1_data = {
        "email":"saileshghimire@gmail.com",
        "password":"123456",
        "first_name":"Sailesh",
        "middle_name":"Kumar",
        "last_name":"Ghimire",
    }
    response = client.call_method("user.UserService", "CreateUser", user1_data)
    print("CreateUser Response:", response)


    # print("All User:")
    # response = client.get_all_users()
    # if response:
    #     for user in response.users:
    #         print(user)