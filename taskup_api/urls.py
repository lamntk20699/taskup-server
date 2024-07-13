from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework_simplejwt import views as jwt_views
from .views import (UserView, IssueView, IssueListView, ProjectListView,
                    ProjectView, LabelView, Project, UndefinedView, IssueArchiveView, IssueSnoozeView,
                    IssueMoveView, LabelListView, MemberListView, MemberIssueView, IssueStatusView,
                    IssuePriorityView, UserSearchView, IssueTodoView)

urlpatterns = [
    # issue
    path('issue/<str:issueId>/', IssueView.as_view(), name="issue-update-delete"), # get, updatee, delete issue()
    path('<str:objectId>/issues/', IssueListView.as_view(), name="create-issue-and-get-list-issue-in-project"), # getListIssue()
    path('snooze_issue/<str:issueId>/', IssueSnoozeView.as_view(), name="snooze_issue"),
    path('archive_issue/<str:issueId>/', IssueArchiveView.as_view(), name="archive_issue"),
    path('<str:objectId>/move_issue/<str:issueId>/', IssueMoveView.as_view(), name="archive_issue"),
    path('<str:userMeId>/todo_issues/', IssueTodoView.as_view(), name="archive_issue"),

    # project
    path('<str:objectId>/projects/', ProjectListView.as_view()), # tạo dự án mới hoặc lấy danh sách project của user
    path('project/<str:projectId>/', ProjectView.as_view()), # xem chi tiết, cập nhật, xóa dự án

    # member
    path('<str:objectId>/members/', MemberListView.as_view()),
    path('<str:objectId>/member/<str:memberId>/', MemberListView.as_view(), name="delete-member"),
    path('leave_issue/<str:issueId>/', MemberIssueView.as_view()),

    # # label
    path('<str:objectId>/labels/', LabelListView.as_view()),
    path('<str:issueId>/label/<str:labelId>/', LabelView.as_view()),

    # search
    path('<str:companyId>/search_user/', UserSearchView.as_view()),

    # otherwise
    path('default_issue_status/', IssueStatusView.as_view()),
    path('default_issue_priorities/', IssuePriorityView.as_view()),
    path('test/', UndefinedView.as_view())
]