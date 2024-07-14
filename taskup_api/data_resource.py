import json
import random
import datetime
from .models import (MemberInfo, Project, Issue, IssueHasUser, Label,
                     HasLabel, IssueStatus, Priority, Attachment, Comment,
                     ProjectHasIssue, UserHasProject)

from .serializers import (IssueSerializer)

companyId = "71124658431777"
dateTimeField = ["start", "end", "timeDone", "timeTodo",
                 "lastUpdateTime", "createdTime", "lastseen",
                 "snoozedFromTime", "snoozedToTime"]

def get_label_and_hasLabel_response(objectId):
    listLabelData = {}
    hasLabelData = {}
    hasLabelIds = []
    hasLabelItem = {}

    listLabelIds = HasLabel.objects.filter(parentId=objectId)
    if listLabelIds.exists():
        for hasLabelQueryset in listLabelIds:
                labelId = hasLabelQueryset.labelId
                hasLabelIds.append(labelId)
                labelQueryset = Label.objects.get(labelId=labelId)
                # labelData = LabelSerializer(data=labelQueryset)
                # if labelData.is_valid():
                listLabelData[labelId] = {
                    "data": {
                        "id": labelQueryset.labelId,
                        "name": labelQueryset.name,
                        "parentId": labelQueryset.parentId,
                        "iconUrl": labelQueryset.iconUrl,
                    }
                }
                    # listLabelData[labelId]["data"]["id"] = labelData.data.get("labelId")
    hasLabelData[objectId] = {
        "itemIds": hasLabelIds,
        # "items": hasLabelItem,
    }
    result = {
        "Label": listLabelData,
        "HasLabel": hasLabelData,
    }

    return result

def get_user_data(userId):
    userItemQuerySet = MemberInfo.objects.filter(memberId=userId)
    userData = {}
    if userItemQuerySet.exists():
        userItemInfo = userItemQuerySet[0]
        userData = {
            "version": 1,
            "href": "",
            "data": {
                "lastName": '',
                "userMail": '',
                "verified": True, # userItemInfo.verified
                "profile": '',
                "account": userItemInfo.account,
                "phone": userItemInfo.phoneNumber,
                "avatar": "",
                "dateOfBirth": userItemInfo.dateOfBirth,
                "fullName": userItemInfo.fullName,
                "id": userId,
                "firstName": '',
                "email": userItemInfo.email
            }
        }
    return userData

def get_user_and_hasUser_response(objectId, parentType, getType="all"):
    userData = {}
    userItemData = {}
    hasUserData = {}
    hasUserIds = []
    hasUserItem = {}
    queryset = None
    # parentFieldName = ""

    if parentType == 'project':
        queryset = UserHasProject.objects.filter(projectId__exact=objectId)
        # parentFieldName
    if parentType == 'issue':
        queryset = IssueHasUser.objects.filter(parentId__exact=objectId)

    if ((queryset is not None) and (queryset.exists())):
        for userHasPrj in queryset:
            userId = userHasPrj.userId
            roles = userHasPrj.roles
            hasUserIds.append(userId)
            hasUserItem[userId] = {
                "data": {
                    "roles": json.loads(roles)
                    }
            }

            if getType == "all":
                userData[userId] = get_user_data(userId)

        hasUserData[objectId] = {
            "itemIds": hasUserIds,
            "items": hasUserItem
        }

    result = {
        "User": userData,
        "HasUser": hasUserData,
    }

    return result

def get_issue_and_hasIssue_response(listIssueIds, requestUserId):
    issueDetailData = {}
    hasIssueData = {}

    for issueId in listIssueIds:
        issueQueryItem = Issue.objects.filter(issueId=issueId)
        if issueQueryItem.exists():
            issueData = IssueSerializer(issueQueryItem[0]).data
            issueDetailData[issueId] = {"data": issueData}
            projectId = issueData.get("projectId")

            issueParentId = ""
            if projectId != "":
                issueParentId = projectId
            elif requestUserId:
                issueParentId = requestUserId

            hasIssueQueryset = IssueHasUser.objects.filter(parentId=issueId, userId=requestUserId)

            if hasIssueQueryset.exists():
                hasIssueInfo = hasIssueQueryset[0]
                currentHasIssueIds = []
                currentHasIssueItems = {}
                if issueParentId in hasIssueData.keys() :
                    currentHasIssueIds = hasIssueData[issueParentId]["itemIds"]
                    currentHasIssueItems = hasIssueData[issueParentId]["items"]

                currentHasIssueIds.append(issueId)
                currentHasIssueItems[issueId] = {
                    "data": {
                        "snoozedFromTime": hasIssueInfo.snoozedFromTime,
                        "snoozedToTime": hasIssueInfo.snoozedToTime,
                        "isSnoozed": hasIssueInfo.isSnoozed,
                        "isArchived": hasIssueInfo.isArchived,
                        "inInbox": hasIssueInfo.inInbox,
                        "inTodo": hasIssueInfo.inTodo,
                        "inMyIssue": hasIssueInfo.inMyIssue,
                        "lastseen": hasIssueInfo.lastseen,
                    }
                }
                hasIssueData = {
                    issueParentId: {
                        "itemIds": currentHasIssueIds,
                        "total": len(currentHasIssueIds),
                        "items": currentHasIssueItems,
                    }
                }

    result = {
        "Issue": issueDetailData,
        "HasIssue": hasIssueData,
        # "HasIssue": listIssueIds,
    }
    return result

def get_search_data_by_type(type, id, data):
    result = {}
    if type == "user":
        result = {
            "id": id,
            "fullName": data.fullName,
            "account": data.account,
            # "avatar": "",
            "email": data.email,
        }
    elif type == "issue":
        result = {
            "id": id,
            "summary": data.summary,
            "description": data.description,
            "issueKey": data.projectKey,
            "statusId": data.statusId,
            # "statusType": data.typeId,
            # "statusCategory": "",
        }

    return result

def get_user_search_response(listQuery):
    searchItems = {}
    searchIds = []
    type = "user"

    for userItem in listQuery:
        id = userItem.memberId
        searchIds.append(id)
        searchItems[id] = {
            "type": type,
            "data": get_search_data_by_type(type, id, userItem)
        }

    result = {
        "Search": searchItems,
        "HasSearch": {
            companyId: {"itemIds": searchIds}
        }
    }
    return result

def get_issue_search_response(listQuery):
    searchItems = {}
    searchIds = []
    type = "issue"

    for issueItem in listQuery:
        id = issueItem.issueId
        searchIds.append(id)
        searchItems[id] = {
            "type": type,
            "data": get_search_data_by_type(type, id, issueItem)
        }

    result = {
        "Search": searchItems,
        "HasSearch": {
            companyId: {
                "itemIds": searchIds,
                "total": len(searchIds),
                "count": len(searchIds),
            }
        }
    }
    return result