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
                          HasIssueSerializer, LabelSerializer, HasLabelSerializer,
                          StatusSerializer, PrioritySerializer, AttachmentSerializer,
                          CommentSerializer, UserHasProjectSerializer)

from .common_response import (response_success, response_create_object_success,
                              response_invalidate_data, response_not_permit, response_conflict)

from .data_resource import (get_label_and_hasLabel_response, get_user_and_hasUser_response,
                             get_issue_and_hasIssue_response, get_user_search_response,
                             get_user_data)

def generate_random_issue_id():
    return str(random.randint(10**9, 10**10 - 1))

def generate_random_user_id():
    return str(random.randint(10**8, 10**9 - 1))

def generate_project_id():
    return str(random.randint(10**7, 10**8 - 1))

def generate_comment_id():
    return str(random.randint(10**10, 10**11 - 1))

def generate_label_id():
    return str(random.randint(10**6, 10**7 - 1))

def get_int_timestamp_now():
    dataTimeNow = datetime.datetime.now()
    timeNow = round(dataTimeNow.timestamp() * 1000)
    return timeNow

MAX_DATE_TIMESTAMP = 3256272578000
COMPANY_ID = "71124658431777"
DATA_TIME_FIELDS = ["start", "end", "timeDone", "timeTodo",
                 "lastUpdateTime", "createdTime", "lastseen",
                 "snoozedFromTime", "snoozedToTime"]

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
    assignee_ids = "assigneeIds"
    reporter_ids = "reporterIds"
    priority_ids = "priorityIds"
    label_ids = "labelIds"
    has_deadline = "hasDeadline"
    sort_by = "sortBy"
    limit = "limit"
    maxscore = "maxscore"
    minscore = "minscore"
    filter_list = ["statusTypes", "parentIds"]

    # Láy danh sách công việc và lọc, sáp xếp?
    def get(self, request, objectId):
        filterParams = {}
        meId = request.headers['CurrentUser-Id']
        # unquote
        parentId = request.GET.get(self.parent_id)
        statusType = request.GET.get(self.status_type)
        assigneeIds = request.GET.get(self.assignee_ids)
        reporterIds = request.GET.get(self.reporter_ids)
        labelIds = request.GET.get(self.label_ids)
        priorityIds = request.GET.get(self.priority_ids)
        hasDeadline = request.GET.get(self.has_deadline)
        sortBy = request.GET.get(self.sort_by)

        # limit = request.GET.get(self.limit)
        # minscore = request.GET.get(self.minscore)
        # maxscore = request.GET.get(self.maxscore)

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

        if assigneeIds:
            issueAssigneeIds = assigneeIds.split(",")
            filterParams['assigneeId__in'] = issueAssigneeIds

        if reporterIds:
            issueReporterIds = reporterIds.split(",")
            # listReporterIds = []
            # for memId in issueReporterIds:
            #     listReporterIds.append(memId)
            filterParams['reporterId__in'] = issueReporterIds

        listHasLabelIssueIds = []
        if labelIds:
            issueLabelFilterTypes = [int(x) for x in labelIds.split(",")]
            hasLabelQueryset = HasLabel.objects.filter(labelId__in=issueLabelFilterTypes)
            if hasLabelQueryset.exists():
                for hasLabelData in hasLabelQueryset:
                    listHasLabelIssueIds.append(hasLabelData.parentId)

            # filterParams['issueId__in'] = listHasLabelIssueIds

        if priorityIds:
            issuePriorityFilterIds = priorityIds.split(",")
            # listPriorityIds = []
            # for priorityId in issuePriorityFilterIds:
            #     listPriorityIds.append(priorityId)
            filterParams['priorityId__in'] = issuePriorityFilterIds

        if hasDeadline:
            filterParams['end__gt'] = "0"

        # Sort with: order_by
        # user = self.year
        objectHasIssue = None

        if meId == objectId:
            objectHasIssue = IssueHasUser.objects.filter(userId=objectId)
        else:
            objectHasIssue = ProjectHasIssue.objects.filter(parentId=objectId)

        # dataResponse = {}
        hasIssueData = {}
        hasIssueItems = {}
        hasIssueIds = []

        userData = {}
        hasUserData = {}
        hasLabelData = {}
        labelData = {}
        issueData = {}

        if objectHasIssue.exists():
            listIds = []

            for item in objectHasIssue:
                issueId = item.issueId
                if len(listHasLabelIssueIds) > 0:
                    if (issueId in listHasLabelIssueIds):
                        listIds.append(item.issueId)
                else:
                    listIds.append(item.issueId)
            # Lọc issue trong project hoặc chứa meId
            filterParams['issueId__in'] = listIds

            sortData = {}
            listIssue = Issue.objects.filter(**filterParams)
            if listIssue.exists():
                for issueItems in listIssue:

                    hasUserIds = []
                    hasUserItem = {}

                    hasLabelIds = []

                    data = IssueSerializer(issueItems).data
                    issueId = issueItems.issueId
                    hasIssueIds.append(issueId)
                    issueData[issueId] = {
                        "data": data
                    }
                    issueData[issueId]['data']['id'] = issueId
                    for item in DATA_TIME_FIELDS:
                        if item in data.keys():
                            issueData[issueId]['data'][item] = int(data.get(item))
                            if sortBy == "end":
                                issueDeadline = int(issueItems.end)
                                if issueDeadline == 0:
                                    sortData[issueId] = MAX_DATE_TIMESTAMP
                                else:
                                    sortData[issueId] = int(issueItems.end)
                            elif sortBy == "priority":
                                sortData[issueId] = int(issueItems.priorityId)
                            else:
                                sortData[issueId] = int(issueItems.lastUpdateTime)

                    ## user included in issue
                    userRoleQueryset = IssueHasUser.objects.filter(parentId=issueId)
                    if userRoleQueryset.exists():
                        for userRoleData in userRoleQueryset:
                            roles = json.loads(userRoleData.roles)
                            userId = userRoleData.userId
                            hasUserIds.append(userId)
                            hasUserItem[issueId] = {
                                "data": {
                                    "roles": roles
                                    }
                            }
                            userData[userId] = get_user_data(userId)

                    userData[userId] = get_user_data(issueItems.reporterId)
                    if issueItems.assigneeId != "" and int(issueItems.assigneeId) > 0:
                        userData[userId] = get_user_data(issueItems.assigneeId)

                    hasUserData[issueId] = {
                        "itemIds": hasUserIds,
                        "items": hasUserItem
                    }

                    # Label in issue
                    hasLabelQueryset = HasLabel.objects.filter(parentId=issueId)
                    if hasLabelQueryset.exists():
                        for hasLabel in hasLabelQueryset:
                            labelId= hasLabel.labelId
                            labelItem = Label.objects.filter(labelId=labelId)
                            if labelItem.exists():
                                hasLabelIds.append(labelId)
                                if labelData.get(labelId) is None:
                                    labelData[labelId] = LabelSerializer(labelItem[0]).data

                    hasLabelData[issueId] = {
                        "itemIds": hasLabelIds,
                        "items": {}
                    }

            isReversed = False
            if sortBy is None:
                isReversed = True
            sortedHasIssue = sorted(hasIssueIds, key=lambda x: sortData[x], reverse=isReversed)

            hasIssueData[objectId] = {
                "itemIds": sortedHasIssue,
                "total": len(hasIssueIds),
                "items": {},
                "older204": True
            }
            dataResponse = {
                "Issue": issueData,
                "HasIssue": hasIssueData,
                "User": userData,
                "HasUser": hasUserData,
                "HasLabel": hasLabelData,
                "Label": labelData
            }
            return Response(dataResponse, status=status.HTTP_200_OK)
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    # Tạo việc mới
    def post(self, request, objectId):
        try:
            requestData = request.data
            listIssueId = requestData.get('HasIssue').get(objectId).get('itemIds')
            hasUserData = requestData.get('HasUser')
            hasLabelData = requestData.get('HasLabel')
            dataResponse = {}
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
                    dataResponse[issueId] = {"offlineId": item, "createdTime": createdTime, "id": issueId}

                    # Edge: creator
                    # userIds = requestData.get('HasIssue').get(objectId).get('itemIds')
                    # userData = ["user.type.creator"]
                    # if objectId == reporterId: userData.append("user.type.reporter")
                    # if objectId == assigneeId: userData.append("user.type.assignee")

                    # newUserData = IssueHasUser(userId=objectId, parentId=issueId, roles=json.dumps(userData))
                    # newUserData.save()

                    # Edge: HasIssue
                    if projectId != "" and int(projectId) > 0:
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
                    if hasLabelData is not None:
                        labelIds = hasLabelData.get(item).get('itemIds')
                        temp = []
                        for labelId in labelIds:
                            temp.append({"labelId": labelId, "issueId": issueId})
                            labelData = HasLabel(labelId=labelId, parentId=issueId)
                            labelData.save()

                    return Response(
                        # {"success2": dataSerializer.data},
                        dataResponse.values(),
                        status=status.HTTP_200_OK)

                return Response(
                    # {"success": postedData},
                    {"message": "Lack of data"},
                    status=status.HTTP_200_OK)

        except:
            return Response({"message": "Invalid input"}, status=status.HTTP_400_BAD_REQUEST)

class IssueTodoView(generics.CreateAPIView):
    serializer_class = IssueSerializer
    status_type = "statusTypes"
    parent_id ="parentIds"
    assignee_ids = "assigneeIds"
    reporter_ids = "reporterIds"
    limit = "limit"
    maxscore = "maxscore"
    minscore = "minscore"
    filter_list = ["statusTypes", "parentIds"]

    # GetList Todolist
    # Chú ý logic phân biệt chi tiết issue và danh sách issue
    def get(self, request, userMeId):
        filterParams = {}
        meId = "70506187193630"
        # unquote
        parentId = request.GET.get(self.parent_id)
        statusType = request.GET.get(self.status_type)
        assigneeIds = request.GET.get(self.assignee_ids)
        reporterIds = request.GET.get(self.reporter_ids)
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

        if assigneeIds:
            issueAssigneeIds = [int(x) for x in assigneeIds.split(",")]
            listAssigneeIds = []
            for memId in issueAssigneeIds:
                listAssigneeIds.append(memId)
            filterParams['assigneeId__in'] = listAssigneeIds

        if reporterIds:
            issuereporterIds = [int(x) for x in reporterIds.split(",")]
            listreporterIds = []
            for memId in issuereporterIds:
                listreporterIds.append(memId)
            filterParams['reporterId__in'] = listreporterIds
        # Sort with: order_by
        # user = self.year

        objectHasIssue = IssueHasUser.objects.filter(userId=userMeId)

        # dataResponse = {}
        hasIssueData = {}
        hasIssueItems = {}
        hasIssueIds = []

        hasUserData = {}
        hasLabelData = {}
        labelData = {}
        issueData = {}

        if objectHasIssue.exists():
            listIds = []

            for item in objectHasIssue:
                listIds.append(item.parentId)\
            # Lọc issue trong project hoặc chứa meId
            filterParams['issueId__in'] = listIds

            listIssue = Issue.objects.filter(**filterParams)
            if listIssue.exists():
                for issueItems in listIssue:

                    hasUserIds = []
                    hasUserItem = {}

                    hasLabelIds = []

                    data = IssueSerializer(issueItems).data
                    issueId = issueItems.issueId
                    hasIssueIds.append(issueId)
                    issueData[issueId] = {
                        "data": data
                    }
                    issueData[issueId]['data']['id'] = issueId
                    for item in DATA_TIME_FIELDS:
                        issueData[issueId]['data'][item] = int(data.get(item))

                    ## user included in issue
                    meRoleQueryset = IssueHasUser.objects.filter(userId=meId, parentId=issueId)
                    if meRoleQueryset.exists():
                        roles = json.loads(meRoleQueryset[0].roles)

                    hasUserIds.append(meId)
                    hasUserItem[issueId] = {
                        "data": {
                            "roles": roles
                            }
                    }

                    hasUserData[issueId] = {
                        "itemIds": hasUserIds,
                        "items": hasUserItem
                    }

                    # Label in issue
                    hasLabelQueryset = HasLabel.objects.filter(parentId=issueId)
                    if hasLabelQueryset.exists():
                        for hasLabel in hasLabelQueryset:
                            labelId= hasLabel.labelId
                            labelItem = Label.objects.filter(labelId=labelId)
                            if labelItem.exists():
                                hasLabelIds.append(labelId)
                                if labelData.get(labelId) is None:
                                    labelData[labelId] = LabelSerializer(labelItem[0]).data

                    hasLabelData[issueId] = {
                        "itemIds": hasLabelIds,
                        "items": {}
                    }

            hasIssueData[userMeId] = {
                "itemIds": hasIssueIds,
                "total": len(hasIssueIds),
                "items": {},
                "older204": True
            }
            dataResponse = {
                "Issue": issueData,
                "HasTodo": hasIssueData,
                "HasUser": hasUserData,
                "HasLabel": hasLabelData,
                "Label": labelData
            }
            return Response(dataResponse, status=status.HTTP_200_OK)
        return Response({}, status=status.HTTP_204_NO_CONTENT)

class IssueView(generics.CreateAPIView):
    serializer_class = IssueSerializer
    # Get issueDetail
    def get(self, request, issueId):
        try:
            meId = request.headers['CurrentUser-Id']
            # meId = request.COOKIES['meId']

            # hasIssueQueryItem = IssueHasUser.objects.filter(userId=meId, parentId=issueId)
            # if hasIssueQueryItem.exists():
            #     hasIssueInfo = HasIssueSerializer(hasIssueQueryItem[0])
            #     hasIssueData[]

            issueDataResponse = get_issue_and_hasIssue_response([issueId], meId)
            labelDataResponse = get_label_and_hasLabel_response(issueId)
            userDataResponse = get_user_and_hasUser_response(issueId, "issue")
            dataResponse = {
                "Issue": issueDataResponse["Issue"],
                "HasIssue": issueDataResponse["HasIssue"],
                "Label": labelDataResponse["Label"],
                "HasLabel": labelDataResponse["HasLabel"],
                # "Attachment": {},
                # "HasAttachment": {},
                # "Comment": {},
                # "HasComment": {},
                "User": userDataResponse["User"],
                "HasUser": userDataResponse["HasUser"],
            }
            return Response(dataResponse, status=status.HTTP_200_OK)
        except:
            return Response({"error": "not found"}, status=status.HTTP_404_NOT_FOUND)

    # Thay đổi thông tin việc
    def patch(self, request, issueId):
        try:
            requestData = request.data
            issuePostData = requestData.get('Issue').get(issueId).get('data')
            postedData = dict(issuePostData)
            updatedField = issuePostData.keys()
            postedData['issueId'] = issueId
            if issuePostData.get('summary') is None:
                postedData['summary'] = issueId
            if issuePostData.get('reporterId') is None:
                postedData['reporterId'] = issueId
            if issuePostData.get('creatorId') is None:
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
                    temp = []
                    for key in updatedField:
                        updatedValue = dataSerializer.data.get(key)
                        if updatedValue != None:
                            temp.append(updatedValue)
                            setattr(issue, key, updatedValue)

                    setattr(issue, 'lastUpdateTime', str(timeNow))
                    issue.save()
                    return Response(
                        # {"success2": temp},
                        {"response": "success"},
                        status=status.HTTP_200_OK)

            return  Response({"error": "not found"}, status=status.HTTP_404_NOT_FOUND)
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
        issueStatusData = {}
        hasIssueStatusData = {}
        hasIssueStatusIds = []
        hasIssueStatusItems = {}

        issueStatusList = IssueStatus.objects.all()
        if issueStatusList.exists():
            for issueStatusItem in issueStatusList:
                statusData = StatusSerializer(issueStatusItem).data
                statusId = statusData.get('statusId')
                issueStatusData[statusId] = { "data": statusData }
                issueStatusData[statusId]["data"]["id"] = statusId
                issueStatusData[statusId]["data"]["iconUrl"] = ""
                hasIssueStatusIds.append(statusId)
                hasIssueStatusItems[statusId] = {
                    "data": {}
                }

            hasIssueStatusData[COMPANY_ID] = {
                "itemIds": hasIssueStatusIds,
                "items": hasIssueStatusItems,
                "total": len(hasIssueStatusIds),
            }

            dataResponse = {
                "IssueStatus": issueStatusData,
                "HasIssueStatus": hasIssueStatusData
            }
            return Response(dataResponse, status=status.HTTP_200_OK)
        return Response({}, status=status.HTTP_204_NO_CONTENT)

class IssuePriorityView(generics.CreateAPIView):
    def get(self, request):
        # Xử lý database
        issuePriorityData = {}
        hasIssuePriorityData = {}
        hasIssuePriorityIds = []
        hasIssuePriorityItems = {}

        issuePriorityList = Priority.objects.all()
        if issuePriorityList.exists():
            for issuePriorityItem in issuePriorityList:
                priorityData = PrioritySerializer(issuePriorityItem).data
                priorityId = priorityData.get('priorityId')
                issuePriorityData[priorityId] = { "data": priorityData }
                issuePriorityData[priorityId]["data"]["id"] = priorityId
                hasIssuePriorityIds.append(priorityId)
                hasIssuePriorityItems[priorityId] = {
                    "data": {}
                }

            hasIssuePriorityData[COMPANY_ID] = {
                "itemIds": hasIssuePriorityIds,
                "items": hasIssuePriorityItems,
                "total": len(hasIssuePriorityIds),
            }

            dataResponse = {
                "IssuePriority": issuePriorityData,
                "HasIssuePriority": hasIssuePriorityData
            }
            return Response(dataResponse, status=status.HTTP_200_OK)
        return Response({}, status=status.HTTP_204_NO_CONTENT)


class ProjectListView(generics.CreateAPIView):
    serializer_class = ProjectSerializer
    # permission_classes = (IsAuthenticated,)

    # Lấy danh sách project của người dùng, công ty
    def get(self, request, objectId):
        # try:
            requestData = request.data
            # xử lý database
            queryset = UserHasProject.objects.filter(userId__exact=objectId)
            hasProjectData = {}
            hasProjectIds = []
            hasProjectItem = {}

            projectData = {}

            allProjectUsers = {}
            allProjectLabels = {}
            allProjectHasUsers = {}
            allProjectHasLabels = {}

            if queryset.exists():
                for userHasProject in queryset:
                    result = UserHasProjectSerializer(userHasProject)
                    projectId = result.data.get('projectId')
                    userId = result.data.get('userId')
                    roles = json.loads(result.data.get('roles'))

                    projectInfoQueryset = Project.objects.filter(projectId__exact=projectId)

                    if projectInfoQueryset.exists():
                        project = self.serializer_class(projectInfoQueryset[0]).data

                        projectData[projectId] = {
                            "data": project
                        }
                        projectData[projectId]['data']['id'] = projectId

                        hasProjectIds.append(projectId)
                        hasProjectItem[projectId] = {
                            "data": {}
                        }

                        userResponse = get_user_and_hasUser_response(projectId, "project")
                        allProjectUsers.update(userResponse["User"])
                        allProjectHasUsers.update(userResponse["HasUser"])
                        labelResponse = get_label_and_hasLabel_response(projectId)
                        allProjectLabels.update(labelResponse["Label"])
                        allProjectLabels.update(labelResponse["HasLabel"])

                    # else:
                    #     return Response({"message": "Lack of data"}, status=status.HTTP_400_BAD_REQUEST)

                hasProjectData[objectId] = {
                    "itemIds": hasProjectIds,
                    "items": hasProjectItem
                }
                # projectData = {}

                dataResponse = {
                    "Project": projectData,
                    "HasProject": hasProjectData,
                    "User": allProjectUsers,
                    "HasUser": allProjectHasUsers,
                    "Label": allProjectLabels,
                    "HasLabel": allProjectHasLabels,
                }
                return Response(dataResponse, status=status.HTTP_200_OK)
            # return Response("Kiem tra", status=status.HTTP_200_OK)
        # except:
        #     return response_invalidate_data()

    # Tạo project mới
    def post(self, request, objectId):
        # try:
            requestData = request.data
            listProjectId = requestData.get('HasProject').get(objectId).get('itemIds')

            for item in listProjectId:
                projectPostData = requestData.get('Project').get(item).get('data')
                postedData = dict(projectPostData)
                # postedData['projectId'] = generate_project_id()
                projectName = projectPostData.get('name')
                # Kiểm tra tên dự án
                if not projectName:
                    return response_invalidate_data()
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
                createdTime = get_int_timestamp_now()
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

                return response_create_object_success(item, postedData['projectId'], createdTime)

        # except:
        #     return response_invalidate_data()

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
                temp = []
                if dataSerializer.is_valid():
                    for key in updatedField:
                        updatedValue = dataSerializer.data.get(key)
                        if updatedValue != None:
                            temp.append(key)
                            setattr(project, key, updatedValue)
                    project.save()

                return Response(
                    # {"success2": temp},
                    {"response": True},
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
        try:
            labelDataResponse = get_label_and_hasLabel_response(objectId)
            dataResponse = {
                "Label": labelDataResponse["Label"],
                "HasLabel": labelDataResponse["HasLabel"],
            }
            return Response(dataResponse, status=status.HTTP_200_OK)
        except:
            return Response({"error": "invalid input"}, status=status.HTTP_400_BAD_REQUEST)

    # Tạo mới label ~ Thêm label vào project
    def post(self, request, objectId):
        try:
            requestData = request.data
            meId = request.headers['CurrentUser-Id']
            listLabelId = requestData.get('HasLabel').get(objectId).get('itemIds')
            for item in listLabelId:
                labelPostData = requestData.get('Label').get(item).get('data')
                postedData = dict(labelPostData)
                newLabelId = ''
                flag = False
                while not flag:
                    tempId = generate_label_id()
                    queryset = Label.objects.filter(labelId__exact=tempId)
                    if not queryset.exists():
                        newLabelId = tempId
                        flag = True

                postedData['labelId'] = newLabelId
                # postedData['parentId'] = objectId
                # postedData['extend'] = json.dumps(labelPostData.get('extend') or {})
                dataSerializer = self.serializer_class(data=postedData)
                if dataSerializer.is_valid():
                    dataTimeNow = datetime.datetime.now()
                    timeNow = round(dataTimeNow.timestamp() * 1000)
                    labelId = dataSerializer.data.get('labelId')
                    name = dataSerializer.data.get('name')
                    parentId = dataSerializer.data.get('parentId')
                    iconUrl = dataSerializer.data.get('iconUrl')
                    # Xử lý database
                    newLabel = Label(
                        labelId = labelId,
                        name = name,
                        iconUrl = iconUrl,
                        parentId = parentId,
                        )
                    newLabel.save()
                    newHasLabel = HasLabel(labelId = labelId, parentId = objectId)
                    newHasLabel.save()

                    dataResponse = {
                        "offlineId": item,
                        "createdTime": str(timeNow),
                        "id": labelId,
                    }
                    return Response(dataResponse, status=status.HTTP_200_OK)

            return Response({"error": "conflict"}, status=status.HTTP_409_CONFLICT)

        except:
            return Response({"message": "Invalid input"}, status=status.HTTP_400_BAD_REQUEST)

class LabelView(generics.CreateAPIView):
    serializer_class = LabelSerializer
    # Thêm label vào công việc
    def post(self, request, issueId, labelId):
        labelQueryset = Label.objects.filter(labelId=labelId)
        hasLabelQueryset = HasLabel.objects.filter(labelId = labelId, parentId = issueId)
        if labelQueryset.exists() and (not hasLabelQueryset.exists()):
            newHasLabel = HasLabel(labelId = labelId, parentId = issueId)
            newHasLabel.save()
            return Response({"success": True}, status=status.HTTP_200_OK)
        return Response({"message": "Invalid input"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, issueId, labelId):
        hasLabelQueryset = HasLabel.objects.filter(labelId = labelId, parentId = issueId)
        if hasLabelQueryset.exists():
            newHasLabel = hasLabelQueryset[0]
            newHasLabel.delete()
            # newHasLabel.save()
            return Response({"success": True}, status=status.HTTP_200_OK)
        return Response({"message": "Invalid input"}, status=status.HTTP_400_BAD_REQUEST)

class MemberListView(generics.CreateAPIView):
    serializer_class = LabelSerializer
    # Add member to issue, project
    def post(self, request, objectId):
        try:
            requestData = request.data
            listMemberId = requestData.get(objectId).get('itemIds')

            for memberId in listMemberId:
                roles = requestData.get(memberId).get("data").get('roles')
                project = Project.objects.filter(projectId=objectId)
                if project.exists():
                    hasMemberData = UserHasProject(projectId=objectId, userId=memberId, roles=json.dumps(roles))
                    hasMemberData.save()
                else:
                    issue = Project.objects.get(issueId=objectId)
                    if issue.exists():
                        hasMemberData = IssueHasUser(parentId=objectId, userId=memberId, roles=json.dumps(roles))
                        hasMemberData.save()
                # return Response({"success": {"objectId": objectId}}, status=status.HTTP_200_OK)
            return response_success()
        except:
            return response_invalidate_data()

    def get(self, request, objectId):
        try:
            userDataResponse = {}
            project = Project.objects.filter(projectId=objectId)
            if project.exists():
                userDataResponse = get_user_and_hasUser_response(objectId, "project", "HasUser")
            else:
                issue = Project.objects.get(issueId=objectId)
                if issue.exists():
                    userDataResponse = get_user_and_hasUser_response(objectId, "issue", "HasUser")
            dataResponse = {
                "HasUser": userDataResponse["HasUser"],
            }
            return Response(dataResponse, status=status.HTTP_200_OK)
        except:
            return response_invalidate_data()

    def put(self, request, objectId):
        try:
            requestData = request.data
            listMemberId = requestData.get(objectId).get('itemIds')

            for memberId in listMemberId:
                roles = requestData.get(memberId).get("data").get('roles')
                project = Project.objects.filter(projectId=objectId)
                if project.exists():
                        hasMemberQueryset = UserHasProject.objects.filter(projectId=objectId, userId=memberId)
                        if hasMemberQueryset.exists():
                            hasMemberData = hasMemberQueryset[0]
                            hasMemberData.roles = json.dumps(roles)
                            hasMemberData.save()
                else:
                    issue = Project.objects.get(issueId=objectId)
                    if issue.exists():
                        hasMemberQueryset = IssueHasUser.objects.filter(parentId=objectId, userId=memberId)
                        if hasMemberQueryset.exists():
                            hasMemberData = hasMemberQueryset[0]
                            hasMemberData.roles = json.dumps(roles)
                            hasMemberData.save()
            return response_success()
        except:
            return response_invalidate_data()

    def patch(self, request, objectId):
        try:
            requestData = request.data
            listMemberId = requestData.get(objectId).get('itemIds')
            listMemberDeleteIds = requestData.get(objectId).get('deleteIds')

            for memberId in listMemberDeleteIds:
                hasProjectQueryset = UserHasProject.objects.filter(projectId=objectId, userId=memberId)
                if hasProjectQueryset.exists():
                    for member in hasProjectQueryset:
                        member.delete()
                hasIssueQueryset = IssueHasUser.objects.filter(parentId=objectId, userId=memberId)
                if hasIssueQueryset.exists():
                    for member in hasIssueQueryset:
                            member.delete()

            for memberId in listMemberId:
                roles = requestData.get(memberId).get("data").get('roles')
                project = Project.objects.filter(projectId=objectId)
                if project.exists():
                        hasMemberQueryset = UserHasProject.objects.filter(projectId=objectId, userId=memberId)
                        if hasMemberQueryset.exists():
                            hasMemberData = hasMemberQueryset[0]
                            hasMemberData.roles = json.dumps(roles)
                            hasMemberData.save()
                else:
                    issue = Project.objects.get(issueId=objectId)
                    if issue.exists():
                        hasMemberQueryset = IssueHasUser.objects.filter(parentId=objectId, userId=memberId)
                        if hasMemberQueryset.exists():
                            hasMemberData = hasMemberQueryset[0]
                            hasMemberData.roles = json.dumps(roles)
                            hasMemberData.save()
            return response_success()
        except:
            return response_invalidate_data()

    # Delete member
    def delete(self, request, objectId, memberId):
        try:
            hasProjectQueryset = UserHasProject.objects.filter(projectId=objectId, userId=memberId)
            if hasProjectQueryset.exists():
                hasProjectData = hasProjectQueryset[0]
                hasProjectData.delete()
            else:
                hasIssueQueryset = IssueHasUser.objects.filter(parentId=objectId, userId=memberId)
                if hasIssueQueryset.exists():
                    hasIssueData = hasIssueQueryset[0]
                    # roles = json.loads(hasIssueData.roles)
                    hasIssueData.delete()

            return response_success()
        except:
            return response_invalidate_data()

class MemberIssueView(generics.CreateAPIView):
    serializer_class = LabelSerializer
    # Rời khỏi công việc
    def delete(self, request, issueId):
        try:
            meId = request.headers['CurrentUser-Id']

            issueQueryset = Issue.objects.get(issueId=issueId)
            reportId = issueQueryset.reporterId
            if reportId != meId:
                hasIssueQueryset = IssueHasUser.objects.filter(parentId=issueId, userId=meId)
                if hasIssueQueryset.exists():
                    hasIssueQueryset[0].delete()
            return response_success()
        except:
            return response_invalidate_data()

class UserSearchView(generics.CreateAPIView):
    serializer_class = LabelSerializer
    key_search = "key"
    # Rời khỏi công việc
    def get(self, request, companyId):
        searchKey = request.GET.get(self.key_search)
        if not searchKey:
            userQuery = MemberInfo.objects.all()
        else:
            userQuery = MemberInfo.objects.filter(fullName__icontains=searchKey)
        if userQuery.exists():
            dataResponse = get_user_search_response(userQuery)
            return Response(dataResponse, status=status.HTTP_200_OK)

        return Response({"error": "not found"}, status=status.HTTP_404_NOT_FOUND)

class UndefinedView(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        return Response({'Product Not Found': 'Invalid Product Code.'}, status=status.HTTP_400_BAD_REQUEST)