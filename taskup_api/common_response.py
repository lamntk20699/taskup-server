from rest_framework import status
from rest_framework.response import Response

def response_success():
    return Response({"success": True}, status=status.HTTP_200_OK)

def response_create_object_success(client_created_id, server_created_id, created_time):
    dataResponse = {
        "offlineId": client_created_id,
        "createdTime": created_time,
        "id": server_created_id
    }
    return Response(dataResponse, status=status.HTTP_201_CREATED)

def response_invalidate_data():
    return Response({"message": "Invalid input"}, status=status.HTTP_400_BAD_REQUEST)

def response_not_permit():
    return Response({"message": "Not permit"}, status=status.HTTP_403_FORBIDDEN)

def response_conflict():
    return Response({"message": "Object already exists!"}, status=status.HTTP_403_FORBIDDEN)

