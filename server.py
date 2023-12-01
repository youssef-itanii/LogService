from concurrent import futures
import grpc
from demo_pb2 import (OrderLog , AddLogRequest, GetLogRequest , Empty)
import demo_pb2_grpc
import threading
import json


class OrderLogService(demo_pb2_grpc.LogServiceServicer):
    
    def __init__(self):
        self.logs = {}
        self.log_lock = threading.Lock() 
        self.id = 0
        self.id_lock = threading.Lock()
    
    def AddLog(self, request, context):
        try:
            user_id = request.user_id
            order_id = request.order_id
            items = request.items
            new_order_log = OrderLog(user_id = user_id, order_id = order_id,items = items)
            with self.log_lock and self.id_lock:
                self.logs[self.id] = new_order_log
                self.id+=1
                new_req = {self.id : new_order_log}
                with open("data.log", 'a') as file:
                    file.write(f"New log #{self.id}: User #{user_id} of order #{order_id} ordered: {items}" + '\n')

                print(f"Added new log entry {new_order_log}")
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

        
def serve():
    try:
        print("V 1.0")
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        demo_pb2_grpc.add_LogServiceServicer_to_server(OrderLogService(), server)
        server.add_insecure_port('[::]:3138')
        server.start()
        print("Log Server started. Listening on port 3138.")
        server.wait_for_termination()
    except Exception as e:
        print(f"An error occurred: {e} ")

if __name__ == '__main__':
    serve()
    