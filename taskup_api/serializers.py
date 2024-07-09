from rest_framework import serializers

from .models import MemberInfo, Project, Issue, IssueHasUser, Label, HasLabel, IssueStatus, Priority, Attachment, Comment, UserHasProject


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberInfo
        fields = ('memberId', 'fullName', 'account', 'email', 'phoneNumber', 'address', 'verified', 'dateOfBirth' )

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = (
            'projectId',
            'name',
            'description',
            'parentId',
            'endTime',
            'startTime',
            'status',
            'iconUrl',
            'config',
            'extend',
            'key',
            'customerName',
            )

class UserHasProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserHasProject
        fields = (
            'userId', 'projectId', 'roles'
        )

class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = (
            'issueId',
            'start',
            'end',
            'parentId',
            'creatorId',
            'assigneeId',
            'reporterId',
            'summary',
            'summaryMd',
            'description',
            'descriptionMd',
            'projectId',
            'priorityId',
            'projectKey',
            'statusId',
            'typeId',
            'lastUpdateTime',
            'createdTime',
            'timeDone',
            'timeTodo',
            'extend',
        )

class HasUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueHasUser
        fields = ('userId', 'parentId')

class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = (
            'labelId', 'name', 'parentId', 'iconUrl'
        )

class HasLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = HasLabel
        fields = ('labelId', 'parentId')

class StatusSerializer(serializers.ModelSerializer):
  class Meta:
      model = IssueStatus
      fields = (
          'statusId', 'type', 'description', 'flow',
        )

class PrioritySerializer(serializers.ModelSerializer):
  class Meta:
      model = Priority
      fields = (
          'priorityId','name','description','color','type','extends',
        )

class AttachmentSerializer(serializers.ModelSerializer):
  class Meta:
      model = Attachment
      fields = (
          'attachmentId',
          'name',
          'userId',
          'size',
          'url',
          'mime',
          'createdTime',
          'width',
          'height',
        )

class CommentSerializer(serializers.ModelSerializer):
  class Meta:
      model = Comment
      fields = (
          'commentId',
          'comment',
          'userId',
          'issueId',
          'status',
          'iconUrl',
          'createdTime',
          'parentId',
          'level',
        )
