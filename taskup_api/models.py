import random
from django.db import models

def generate_random_issue_id():
    return str(random.randint(10**9, 10**10 - 1))

def generate_random_user_id():
    return str(random.randint(10**8, 10**9 - 1))

def generate_project_id():
    return str(random.randint(10**7, 10**8 - 1))
# Create your models here.
class MemberInfo(models.Model):
    memberId = models.CharField(max_length=20, null=False, default=generate_random_user_id)
    fullName = models.CharField(max_length=2000, null=False, blank=False)
    account = models.CharField(max_length=20, null=False, blank=False)
    email = models.CharField(max_length=2000, blank=True, null=False, default='')
    phoneNumber = models.CharField(max_length=10, blank=True, null=False, default='')
    address = models.CharField(max_length=2000, blank=True, null=False, default='')
    verified = models.BooleanField(blank=True, default=False)
    dateOfBirth = models.CharField(max_length=10, blank=True, null=False, default='')

    def __str__(self):
        return f"{self.fullName}"

class MemberRole(models.Model):
    role = models.CharField(max_length=20, blank=True, default='0')
    roleId = models.CharField(max_length=30, null=False, blank=False)
    description = models.CharField(max_length=200, blank=True, default='0')

    def __str__(self):
        return f"{self.role}"

class Project(models.Model):
    projectId = models.CharField(max_length=20, null=False, default=generate_project_id)
    name = models.CharField(max_length=2000, null=False, blank=False)
    description = models.CharField(max_length=500, blank=True, default='')
    parentId = models.CharField(max_length=2000, blank=True, default='')
    customerName = models.CharField(max_length=2000, blank=True, default='')
    endTime = models.CharField(max_length=20, blank=True, default='0')
    startTime = models.CharField(max_length=20, blank=True, default='0')
    status = models.IntegerField(null=False, blank=True, default=1)
    iconUrl = models.CharField(max_length=2000)
    config = models.CharField(max_length=2000, blank=True, default='')
    extend = models.CharField(max_length=2000, null=True, blank=True, default='')
    key = models.CharField(max_length=20, blank=True, default=0)

class Issue(models.Model):
    issueId = models.CharField(max_length=20, null=False, default=generate_random_user_id)
    start = models.CharField(max_length=20, blank=True, default='0')
    end = models.CharField(max_length=20, blank=True, default='0')
    parentId = models.CharField(max_length=20, null=False, blank=True, default='')
    creatorId = models.CharField(max_length=20, null=False, blank=False)
    assigneeId = models.CharField(max_length=20, null=False, blank=True, default='')
    reporterId = models.CharField(max_length=20, null=False, blank=False)
    summary = models.CharField(max_length=500, blank=False)
    summaryMd = models.CharField(max_length=500, blank=True, default='')
    description = models.CharField(max_length=500, blank=True, default='')
    descriptionMd = models.CharField(max_length=500, blank=True, default='')
    projectId = models.CharField(max_length=20, null=False, blank=True, default='')
    priorityId = models.CharField(max_length=20, null=False, blank=True, default='')
    projectKey = models.CharField(max_length=500, blank=True, default='')
    statusId = models.CharField(max_length=20, null=False, blank=True, default='')
    typeId = models.CharField(max_length=20, null=False, blank=True, default='')
    lastUpdateTime = models.CharField(max_length=20, blank=True, default='0')
    createdTime = models.CharField(max_length=20, blank=True, default='0')
    timeDone = models.CharField(max_length=20, blank=True, default='0')
    timeTodo = models.CharField(max_length=20, blank=True, default='0')
    extend = models.CharField(max_length=500, blank=True, default='')
    estimatePoint = models.DecimalField(blank=True, default=1.00, max_digits=5, decimal_places=2)

# each issue in each projects
class ProjectHasIssue(models.Model):
    issueId = models.CharField(max_length=20, null=False, blank=False)
    parentId = models.CharField(max_length=20, null=False, blank=False)

# Each user in projects
class UserHasProject(models.Model):
    userId = models.CharField(max_length=20, null=False, blank=False)
    projectId = models.CharField(max_length=20, null=False, blank=False)
    roles = models.CharField(max_length=2000, null=False, blank=False)

# Each user in issue with dataEdge
class IssueHasUser(models.Model):
    userId = models.CharField(max_length=20, null=False, blank=False)
    parentId = models.CharField(max_length=20, null=False, blank=False)
    roles = models.CharField(max_length=2000, null=False, blank=False)
    snoozedFromTime = models.CharField(max_length=20, blank=True, default='0')
    snoozedToTime = models.CharField(max_length=20, blank=True, default='0')
    isSnoozed = models.BooleanField(blank=True, default=False)
    isArchived = models.BooleanField(blank=True, default=False)
    inInbox = models.BooleanField(blank=True, default=False)
    inTodo = models.BooleanField(blank=True, default=False)
    inMyIssue = models.BooleanField(blank=True, default=False)
    lastseen = models.BooleanField(blank=True, default="0")

class Label(models.Model):
    labelId = models.CharField(max_length=20, null=False, blank=False)
    name = models.CharField(max_length=2000)
    parentId = models.CharField(max_length=20, null=False, blank=False)
    iconUrl = models.CharField(max_length=2000)

class HasLabel(models.Model):
    labelId = models.CharField(max_length=20, null=False, blank=False)
    parentId = models.CharField(max_length=20, null=False, blank=False)

class IssueStatus(models.Model):
    statusId = models.CharField(max_length=20, null=False, blank=False)
    type = models.CharField(max_length=20)
    name = models.CharField(max_length=200, null=False, blank=True, default="")
    description = models.CharField(max_length=500, null=False, blank=True, default="")
    flow = models.CharField(max_length=2000)
class Priority(models.Model):
    priorityId = models.CharField(max_length=20, null=False, blank=False)
    name = models.CharField(max_length=2000)
    description = models.CharField(max_length=500)
    color = models.CharField(max_length=2000)
    type = models.IntegerField(null=False)
    extends = models.CharField(max_length=500, blank=True, default='0')

class Attachment(models.Model):
    attachmentId = models.CharField(max_length=20, null=False, blank=False)
    name = models.CharField(max_length=2000)
    userId = models.CharField(max_length=20, null=False, blank=False)
    size = models.IntegerField(null=False)
    url = models.CharField(max_length=2000)
    mime = models.CharField(max_length=2000)
    createdTime = models.CharField(max_length=20, blank=True, default='0')
    width = models.IntegerField(null=False)
    height = models.IntegerField(null=False)

class Comment(models.Model):
    commentId = models.CharField(max_length=20, null=False, blank=False)
    comment = models.CharField(max_length=2000)
    userId = models.CharField(max_length=20, null=False, blank=False)
    issueId = models.CharField(max_length=20, null=False, blank=False)
    status = models.IntegerField(null=False)
    iconUrl = models.CharField(max_length=20, blank=True, default='0')
    createdTime = models.CharField(max_length=20, blank=True, default='0')
    parentId = models.CharField(max_length=20, null=False, blank=False)
    level = models.IntegerField(null=False)