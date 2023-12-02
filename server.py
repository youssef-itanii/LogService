from concurrent import futures
import time
import grpc
from demo_pb2 import (OrderLog , AddLogRequest, GetLogRequest , Empty)
import demo_pb2_grpc
import threading
import json
import health_pb2
import health_pb2_grpc

class OrderLogService(demo_pb2_grpc.LogServiceServicer):
    
    def __init__(self):
        print("Generated Service...")
        self.logs = {}

        self.id = 0

    
    def AddLog(self, request, context):
        try:
            user_id = request.user_id
            order_id = request.order_id
            items = request.items
            new_order_log = OrderLog(user_id = user_id, order_id = order_id,items = items)
           
            self.logs[self.id] = new_order_log
            self.id+=1
            new_req = {self.id : new_order_log}
            print(f"LOG #{self.id}: User {user_id} has placed an order:\n - Order ID: {order_id} \n - Items: {items}")

            return Empty()
        except Exception as e:
            context.set_code(grpc.StatusCode.UNKNOWN)
            context.set_details(f"Exception calling application: {str(e)}")
            return Empty()
    
    def GetLog(self, request, context):
        # Implement your GetLog logic here
        log_id = request.log_id

        # Retrieve the log from the dictionary
        log_entry = self.logs.get(log_id)

        if log_entry:
            return log_entry
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Log entry not found')
            return "Not Found"
    
    def Check(self, request, context):
        return health_pb2.HealthCheckResponse(
            status=health_pb2.HealthCheckResponse.SERVING)

    def Watch(self, request, context):
        return health_pb2.HealthCheckResponse(
            status=health_pb2.HealthCheckResponse.UNIMPLEMENTED)
        
def serve():
    try:
        print("Version 2.0")
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        service = OrderLogService()
        demo_pb2_grpc.add_LogServiceServicer_to_server(service, server)
        health_pb2_grpc.add_HealthServicer_to_server(service, server)
        
        server.add_insecure_port('[::]:3138')
        server.start()
        
        print("Log Server started. Listening on port 3138.")
        try:
            while True:
                time.sleep(10000)
        except KeyboardInterrupt:
                server.stop(0)
    except Exception as e:
        print(f"An error occurred: {e} ")

if __name__ == '__main__':
    serve()
    