import json
import random
import datetime
from urllib.parse import unquote
from django.contrib.auth import authenticate, login
from django.contrib.sessions.models import Session
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .models import (MemberInfo, Project, Issue, IssueHasUser, Label,
                     HasLabel, IssueStatus, Priority, Attachment, Comment,
                     ProjectHasIssue, UserHasProject)
from .serializers import (MemberSerializer, ProjectSerializer, IssueSerializer,
                          HasUserSerializer, LabelSerializer, HasLabelSerializer,
                          StatusSerializer, PrioritySerializer, AttachmentSerializer,
                          CommentSerializer, UserHasProjectSerializer)

def generate_random_issue_id():
    return str(random.randint(10**9, 10**10 - 1))

def generate_random_user_id():
    return str(random.randint(10**8, 10**9 - 1))

def generate_project_id():
    return str(random.randint(10**7, 10**8 - 1))

# Create your views here.
class UserView(generics.CreateAPIView):
    serializer_class = MemberSerializer
    def post(self, request):
        user = "game la de"
        return Response({"game la de"}, status=status.HTTP_200_OK)

# class CreateIssueView(generics.CreateAPIView):
#     serializer_class = IssueSerializer
#     def post(self, request):
#         user = "game la de"
#         return Response({"game la de"}, status=status.HTTP_200_OK)

class IssueListView(generics.CreateAPIView):
    serializer_class = IssueSerializer
    status_type = "statusTypes"
    parent_id ="parentIds"
    limit = "limit"
    maxscore = "maxscore"
    minscore = "minscore"
    filter_list = ["statusTypes", "parentIds"]

    # Láy danh sách công việc và lọc, sáp xếp?
    # Chú ý logic phân biệt chi tiết issue và danh sách issue
    def get(self, request, objectId):
        filterParams = {}
        meId = "70506187193630"
        # unquote
        parentId = request.GET.get(self.parent_id)
        statusType = request.GET.get(self.status_type)
        # limit = request.GET.get(self.limit)
        # minscore = request.GET.get(self.minscore)
        # maxscore = request.GET.get(self.maxscore)
        # temp = statusType.split(',')
        # filterParams = {statusType}

        if parentId:
            filterParams['parentId__exact'] = parentId
        if statusType:
            issueStatusTypes = [int(x) for x in statusType.split(",")]
            statusInfo = IssueStatus.objects.filter(type__in=issueStatusTypes)
            if statusInfo.exists():
                listStatusIds=[]
                for statusItem in statusInfo:
                    listStatusIds.append(statusItem.statusId)
                filterParams['statusId__in'] = listStatusIds
        # Sort with: order_by
        # user = self.year
        objectHasIssue = None

        if meId == objectId:
            objectHasIssue = IssueHasUser.objects.filter(parentId=objectId)
        else:
            objectHasIssue = ProjectHasIssue.objects.filter(parentId=objectId)

        # dataResponse = {}
        hasIssueData = {}
        # hasIssueItems = {}
        hasIssueIds = []

        hasUserData = {}
        hasUserIds = []
        hasUserItem = {}

        issueData = {}

        # if objectHasIssue.exists():
            # listIds = []
            # for item in objectHasIssue:
            #     listIds.append(item.issueId)\

            # filterParams['issueId__in'] = listIds
            # filterParams[]

            # listIssue = Issue.objects.filter(**filterParams)
            # if listIssue.exists():
            #     for issueItems in listIssue:
            #         data = IssueSerializer(issueItems).data
            #         issueId = issueItems.issueId
            #         hasIssueIds.append(issueId)
            #         issueData[issueId] = {
            #             "data": data
            #         }
            #         issueData[issueId]['data']['id'] = issueId
            #         # hasUserIds.append(objectId)
            #         # hasUserItem[objectId] = {
            #         #     "data": {
            #         #         "roles": roles
            #         #         }
            #         # }
            #         # hasUserData[projectId] = {
            #         #     "itemIds": hasUserIds,
            #         #     "item": hasUserItem

            # hasIssueData[objectId] = {
            #     "itemIds": hasIssueIds,
            #     "total": len(hasIssueIds),
            #     "items": {},
            #     "older204": True
            # }
            # dataResponse = {
            #     "Issue": issueData,
            #     "HasIssue": hasIssueData,
            #     # "HasUser": hasUserData,
            # }
            # return Response(dataResponse, status=status.HTTP_200_OK)
        return Response({"data": filterParams}, status=status.HTTP_204_NO_CONTENT)

    # Tạo việc mới
    def post(self, request, objectId):
        try:
            requestData = request.data
            listIssueId = requestData.get('HasIssue').get(objectId).get('itemIds')
            hasUserData = requestData.get('HasUser')
            hasLabelData = requestData.get('HasLabel')
            for item in listIssueId:
                issuePostData = requestData.get('Issue').get(item).get('data')
                postedData = dict(issuePostData)

                # postedData['issueId'] = '123456'
                newIssueId = ''
                flag = False
                while not flag:
                    tempId = generate_random_issue_id()
                    queryset = Issue.objects.filter(issueId__exact=tempId)
                    if not queryset.exists():
                        newIssueId = tempId
                        flag = True

                dataTimeNow = datetime.datetime.now()
                timeNow = round(dataTimeNow.timestamp() * 1000)

                postedData['issueId'] = newIssueId or generate_random_issue_id()
                postedData['creatorId'] = objectId

                postedData['start'] = issuePostData.get('start') or '0'
                postedData['end'] = issuePostData.get('end') or '0'
                postedData['parentId'] = issuePostData.get('parentId') or '-1'
                postedData['assigneeId'] = issuePostData.get('assigneeId') or '0'
                postedData['summaryMd'] = issuePostData.get('summaryMd') or ''
                postedData['description'] = issuePostData.get('description') or ''
                postedData['descriptionMd'] = issuePostData.get('descriptionMd') or ''
                postedData['projectId'] = issuePostData.get('projectId') or ''
                postedData['priorityId'] = issuePostData.get('priorityId') or ''
                postedData['projectKey'] = issuePostData.get('projectKey') or ''
                postedData['statusId'] = issuePostData.get('statusId') or '78271484576083'
                postedData['typeId'] = issuePostData.get('typeId') or '570783974620601'
                postedData['lastUpdateTime'] = issuePostData.get('lastUpdateTime') or '0'
                postedData['createdTime'] = issuePostData.get('createdTime') or str(timeNow)
                postedData['timeDone'] = issuePostData.get('timeDone') or '0'
                postedData['timeTodo'] = issuePostData.get('timeTodo') or '0'
                postedData['extend'] = issuePostData.get('extend') or ''

                dataSerializer = self.serializer_class(data=postedData)
                if dataSerializer.is_valid():
                    issueId = dataSerializer.data.get('issueId')
                    start = dataSerializer.data.get('start')
                    end = dataSerializer.data.get('end')
                    parentId = dataSerializer.data.get('parentId')
                    creatorId = dataSerializer.data.get('creatorId')
                    assigneeId = dataSerializer.data.get('assigneeId')
                    reporterId = dataSerializer.data.get('reporterId')
                    summary = dataSerializer.data.get('summary')
                    summaryMd = dataSerializer.data.get('summaryMd')
                    description = dataSerializer.data.get('description')
                    descriptionMd = dataSerializer.data.get('descriptionMd')
                    projectId = dataSerializer.data.get('projectId')
                    priorityId = dataSerializer.data.get('priorityId')
                    projectKey = dataSerializer.data.get('projectKey')
                    statusId = dataSerializer.data.get('statusId')
                    typeId = dataSerializer.data.get('typeId')
                    lastUpdateTime = dataSerializer.data.get('lastUpdateTime')
                    createdTime = dataSerializer.data.get('createdTime')
                    timeDone = dataSerializer.data.get('timeDone')
                    timeTodo = dataSerializer.data.get('timeTodo')
                    extend = dataSerializer.data.get('extend')
                    # Xử lý database
                    issue = Issue(
                        issueId=issueId,
                        start=start,
                        end=end,
                        parentId=parentId,
                        creatorId=creatorId,
                        assigneeId=assigneeId,
                        reporterId=reporterId,
                        summary=summary,
                        summaryMd=summaryMd,
                        description=description,
                        descriptionMd=descriptionMd,
                        projectId=projectId,
                        priorityId=priorityId,
                        projectKey=projectKey,
                        statusId=statusId,
                        typeId=typeId,
                        lastUpdateTime=lastUpdateTime,
                        createdTime=createdTime,
                        timeDone=timeDone,
                        timeTodo=timeTodo,
                        extend=extend,
                    )
                    issue.save()

                    # Edge: HasUser
                    userIds = requestData.get('HasIssue').get(objectId).get('itemIds')
                    userData = []
                    if objectId == reporterId: userData.append("user.type.reporter")
                    else:
                        if objectId == assigneeId: userData.append("user.type.assignee")
                    if len(userData) < 1: userData.append("user.type.watcher")

                    hasUserData = IssueHasUser(userId=objectId, parentId=issueId, roles=json.dumps(userData))
                    hasUserData.save()

                    # Edge: HasIssue
                    if projectId and int(projectId) > 0:
                        hasIssueData = ProjectHasIssue(issueId=issueId, parentId=projectId)
                        hasIssueData.save()

                    # # Edge: User
                    # userIds = requestData.get('HasUser').get(item).get('itemIds')
                    # userData = requestData.get('HasUser').get(item).get('items')

                    # # Thêm quan hệ
                    # if len(userIds) > 0:
                    #     for userId in userIds:
                    #         roles = userData.get(userId).get('data').get('roles')
                    #         userRole = UserHasProject(userId=userId, projectId=postedData['projectId'], roles=json.dumps(roles))
                    #         userRole.save()

                    # Edge: Label
                    labelIds = requestData.get('HasLabel').get(item).get('itemIds')
                    temp = []
                    for labelId in labelIds:
                        temp.append({"labelId": labelId, "issueId": issueId})
                        labelData = HasLabel(labelId=labelId, parentId=issueId)
                        labelData.save()

                    return Response(
                        # {"success2": dataSerializer.data},
                        {"response": "success"},
                        status=status.HTTP_200_OK)

                return Response(
                    # {"success": postedData},
                    {"message": "Lack of data"},
                    status=status.HTTP_200_OK)

        except:
            return Response({"message": "Invalid input"}, status=status.HTTP_400_BAD_REQUEST)

class IssueView(generics.CreateAPIView):
    serializer_class = IssueSerializer
    # Thay đổi thông tin việc
    def patch(self, request, issueId):
        try:
            requestData = request.data
            issuePostData = requestData.get('Issue').get(issueId).get('data')
            postedData = dict(issuePostData)
            updatedField = issuePostData.keys()
            postedData['issueId'] = issueId
            postedData['summary'] = issueId
            postedData['reporterId'] = issueId
            postedData['creatorId'] = issueId
            # postedData['extend'] = json.dumps(projectPostData.get('extend') or {})

            dataTimeNow = datetime.datetime.now()
            timeNow = round(dataTimeNow.timestamp() * 1000)

            queryset = Issue.objects.filter(issueId__exact=issueId)
            if queryset.exists():
                issue = queryset[0]
                dataSerializer = self.serializer_class(data=postedData)
                # Xử lý database
                if dataSerializer.is_valid():
                    # temp = []
                    for key in updatedField:
                        updatedValue = dataSerializer.data.get(key)
                        if updatedValue != None:
                            # temp.append(updatedValue)
                            setattr(issue, key, updatedValue)

                    setattr(issue, 'lastUpdateTime', str(timeNow))
                    issue.save()
                    return Response(
                        # {"success2": temp},
                        {"response": "success"},
                        status=status.HTTP_200_OK)
                return  Response({"message s": dataSerializer.data}, status=status.HTTP_400_BAD_REQUEST)
            return  Response({"message": postedData}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"message": "Invalid input"}, status=status.HTTP_400_BAD_REQUEST)

    # Xóa công việc
    def delete(self, request, issueId):
        # Lấy meId từ token !?
        meId = "70506187193630"
        # Xử lý database
        queryset = Issue.objects.filter(issueId__exact=issueId)
        if queryset.exists():
            issue = queryset[0];
            if issue.reporterId == meId:
                issue.delete();
                # issue.save()
                return Response({"success": issueId}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "not permit"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "not found"}, status=status.HTTP_404_NOT_FOUND)

class IssueMoveView(generics.CreateAPIView):
    def post(self, request, objectId, issueId):
        # Xử lý database
        return Response({"success": {"projectId": objectId, "issueId": issueId}}, status=status.HTTP_200_OK)
class IssueArchiveView(generics.CreateAPIView):
    def post(self, request, issueId):
        # Xử lý database
        return Response({"success": issueId}, status=status.HTTP_200_OK)

class IssueSnoozeView(generics.CreateAPIView):
    def post(self, request, issueId):
        # Xử lý database
        return Response({"success": issueId}, status=status.HTTP_200_OK)

class IssueStatusView(generics.CreateAPIView):
    def get(self, request):
        # Xử lý database
        return Response({"success": "ok"}, status=status.HTTP_200_OK)

class IssuePriorityView(generics.CreateAPIView):
    def get(self, request):
        # Xử lý database
        return Response({"success": "ok"}, status=status.HTTP_200_OK)

class ProjectListView(generics.CreateAPIView):
    serializer_class = ProjectSerializer
    # permission_classes = (IsAuthenticated,)

    # Lấy danh sách project của người dùng, công ty
    def get(self, request, objectId):
        try:
            requestData = request.data
            # xử lý database
            queryset = UserHasProject.objects.filter(userId__exact=objectId)
            hasProjectData = {}
            hasProjectIds = []
            hasProjectItem = {}

            hasUserData = {}
            hasUserIds = []
            hasUserItem = {}

            projectData = {}

            if queryset.exists():
                for userHasProject in queryset:
                    result = UserHasProjectSerializer(userHasProject)
                    projectId = result.data.get('projectId')
                    userId = result.data.get('userId')
                    roles = json.loads(result.data.get('roles'))

                    projectQueryset = Project.objects.filter(projectId__exact=projectId)

                    if projectQueryset.exists():
                        project = self.serializer_class(projectQueryset[0]).data

                        projectData[projectId] = {
                            "data": project
                        }
                        projectData[projectId]['data']['id'] = projectId

                        hasProjectIds.append(projectId)
                        hasProjectItem[projectId] = {
                            "data": {}
                        }

                        hasUserIds.append(objectId)
                        hasUserItem[objectId] = {
                            "data": {
                                "roles": roles
                                }
                        }
                        hasUserData[projectId] = {
                            "itemIds": hasUserIds,
                            "item": hasUserItem
                        }
                    # else:
                    #     return Response({"message": "Lack of data"}, status=status.HTTP_400_BAD_REQUEST)

                hasProjectData[objectId] = {
                    "itemIds": hasProjectIds,
                    "item": hasProjectItem
                }
                # projectData = {}

                response = {
                    "Project": projectData,
                    "HasProject": hasProjectData,
                    "HasUser": hasUserData,
                }
                return Response(response, status=status.HTTP_200_OK)
            return Response("Kiem tra", status=status.HTTP_200_OK)
        except:
            return Response({"message": "Invalid input"}, status=status.HTTP_400_BAD_REQUEST)

    # Tạo project mới
    def post(self, request, objectId):
        try:
            requestData = request.data
            listProjectId = requestData.get('HasProject').get(objectId).get('itemIds')

            for item in listProjectId:
                projectPostData = requestData.get('Project').get(item).get('data')
                postedData = dict(projectPostData)
                # postedData['projectId'] = generate_project_id()
                projectName = projectPostData.get('name')
                # Kiểm tra tên dự án
                if not projectName:
                    return Response({"message": "Invalid input"}, status=status.HTTP_400_BAD_REQUEST)
                # Kiểm tra trùng tên dự án
                queryset = Project.objects.filter(name__exact=projectName)
                if queryset.exists():
                    return Response({"error": "Duplicate project name"}, status=status.HTTP_200_OK)

                newProjectId = ''
                flag = False
                while not flag:
                    tempId = generate_project_id()
                    queryset = Project.objects.filter(projectId__exact=tempId)
                    if not queryset.exists():
                        newProjectId = tempId
                        flag = True

                postedData['projectId'] = newProjectId or generate_project_id()
                postedData['parentId'] = objectId
                postedData['extend'] = json.dumps(projectPostData.get('extend') or {})

                postedData['description'] = projectPostData.get('description') or ''
                postedData['customerName'] = projectPostData.get('customerName') or ''
                postedData['endTime'] = projectPostData.get('endTime') or '0'
                postedData['startTime'] = projectPostData.get('startTime') or '0'
                postedData['statusPj'] = projectPostData.get('status') or ''
                postedData['iconUrl'] = projectPostData.get('iconUrl') or ''
                postedData['config'] = projectPostData.get('config') or ''
                postedData['extend'] = projectPostData.get('extend') or ''
                postedData['key'] = projectPostData.get('key') or ''

                dataSerializer = self.serializer_class(data=postedData)
                if dataSerializer.is_valid():
                    projectId = dataSerializer.data.get('projectId')
                    name = dataSerializer.data.get('name')
                    description = dataSerializer.data.get('description')
                    parentId = dataSerializer.data.get('parentId')
                    customerName = dataSerializer.data.get('customerName')
                    endTime = dataSerializer.data.get('endTime')
                    startTime = dataSerializer.data.get('startTime')
                    statusPj = dataSerializer.data.get('status')
                    iconUrl = dataSerializer.data.get('iconUrl')
                    config = dataSerializer.data.get('config')
                    extend = dataSerializer.data.get('extend')
                    key = dataSerializer.data.get('key')
                    # # Xử lý database
                    projectRecord = Project(
                        projectId = projectId,
                        name = name,
                        description = description,
                        parentId = parentId,
                        customerName = customerName,
                        endTime = endTime,
                        startTime = startTime,
                        status = statusPj,
                        iconUrl = iconUrl,
                        config = config,
                        extend = extend,
                        key = key,
                        )
                    projectRecord.save()

                # Edge: User
                userIds = requestData.get('HasUser').get(item).get('itemIds')
                userData = requestData.get('HasUser').get(item).get('items')
                # Thêm quan hệ
                if len(userIds) > 0:
                    for userId in userIds:
                        roles = userData.get(userId).get('data').get('roles')
                        userRole = UserHasProject(userId=userId, projectId=postedData['projectId'], roles=json.dumps(roles))
                        userRole.save()

                # Edge: Label

                return Response({"success": dataSerializer.data, "response": "success"}, status=status.HTTP_200_OK)

        except:
            return Response({"message": "Invalid input"}, status=status.HTTP_400_BAD_REQUEST)

class ProjectView(generics.CreateAPIView):
    serializer_class = ProjectSerializer
    # Cập nhật thông tin project
    def put(self, request, projectId):
        try:
            requestData = request.data
            projectPostData = requestData.get('Project').get(projectId).get('data')
            updatedField = projectPostData.keys()
            postedData = dict(projectPostData)
            postedData['projectId'] = projectId
            postedData['test'] = projectId
            postedData['extend'] = json.dumps(projectPostData.get('extend') or {})

            # Xử lý database
            queryset = Project.objects.filter(projectId__exact=projectId)
            if queryset.exists():
                project = queryset[0]
                dataSerializer = self.serializer_class(data=postedData)
                # temp = []
                if dataSerializer.is_valid():
                    for key in updatedField:
                        updatedValue = dataSerializer.data.get(key)
                        if updatedValue != None:
                            # temp.append(key)
                            setattr(project, key, updatedValue)
                    project.save()

                return Response(
                    # {"success2": temp},
                    {"response": "success"},
                    status=status.HTTP_200_OK
                    )
            else:
                return Response({"message": "Invalid input"}, status=status.HTTP_400_BAD_REQUEST)

        except:
            return Response({"message": "Invalid input"}, status=status.HTTP_400_BAD_REQUEST)

        # return Response({"success": postedData}, status=status.HTTP_200_OK)

class LabelListView(generics.CreateAPIView):
    serializer_class = LabelSerializer
    # Lấy danh sách label project
    def get(self, request, objectId):
        return Response({"success": objectId}, status=status.HTTP_200_OK)

    # Tạo mới label ~ Thêm label vào project
    def post(self, request, objectId):
        try:
            requestData = request.data
            listLabelId = requestData.get('HasLabel').get(objectId).get('itemIds')
            for item in listLabelId:
                labelPostData = requestData.get('Label').get(item).get('data')
                postedData = dict(labelPostData)
                postedData['labelId'] = '123456'
                # postedData['parentId'] = objectId
                # postedData['extend'] = json.dumps(labelPostData.get('extend') or {})
                dataSerializer = self.serializer_class(data=postedData)
                if dataSerializer.is_valid():
                    data2 = dataSerializer.data.get('name')
                    # Xử lý database
                    return Response({"success2": dataSerializer.data}, status=status.HTTP_200_OK)

                return Response({"success": postedData}, status=status.HTTP_200_OK)

        except:
            return Response({"message": "Invalid input"}, status=status.HTTP_400_BAD_REQUEST)

class LabelView(generics.CreateAPIView):
    serializer_class = LabelSerializer
    # Thêm label vào công việc
    def post(self, request, objectId, issueId):
        user = "game la de"
        return Response({"success": {"objectId": objectId, "issueId": issueId}}, status=status.HTTP_200_OK)

class MemberListView(generics.CreateAPIView):
    serializer_class = LabelSerializer
    #
    def post(self, request, objectId):
        user = "game la de"
        return Response({"success": {"objectId": objectId}}, status=status.HTTP_200_OK)

    def get(self, request, objectId):
        user = "game la de"
        return Response({"success": {"objectId": objectId}}, status=status.HTTP_200_OK)

    def put(self, request, objectId):
        user = "game la de"
        return Response({"success": {"objectId": objectId}}, status=status.HTTP_200_OK)

    def patch(self, request, objectId):
        user = "game la de"
        return Response({"success": {"objectId": objectId}}, status=status.HTTP_200_OK)

    def delete(self, request, objectId, memberId):
        user = "game la de"
        return Response({"success": {"objectId": objectId, "memberId": memberId}}, status=status.HTTP_200_OK)

class MemberIssueView(generics.CreateAPIView):
    serializer_class = LabelSerializer
    # Rời khỏi công việc
    def delete(self, request, objectId, issueId):
        user = "game la de"
        return Response({"success": {"objectId": objectId, "issueId": issueId}}, status=status.HTTP_200_OK)

class UndefinedView(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        return Response({'Product Not Found': 'Invalid Product Code.'}, status=status.HTTP_400_BAD_REQUEST)