from django.db import models
from django.core.exceptions import ValidationError
from resources.all_purpose.enums import UserRoleTypes, TaskTypeEnum
from resources.all_purpose.common import email_validator


class JiraUser(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    role = models.CharField(max_length=20, choices=UserRoleTypes.choices(), default=UserRoleTypes.USER.value)
    user_name = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'jira_users'
        managed = True
        constraints = [
            models.UniqueConstraint(fields=["user_name", "email"], name="unique_user_name_email")
        ]

    def clean(self):
        """Custom validation before saving"""
        if not self.first_name or not self.last_name:
            raise ValidationError("First name and last name cannot be empty.")

        valid_roles = [choice[0] for choice in UserRoleTypes.choices()]
        if self.role not in valid_roles:
            raise ValidationError(f"Invalid role: {self.role}. Choose from {valid_roles}.")

        if JiraUser.objects.exclude(pk=self.pk).filter(user_name=self.user_name).exists():
            raise ValidationError("A user with this username already exists.")

        if not email_validator(self.email):
            raise ValidationError(f"{self.email} is not a valid email address")

        if JiraUser.objects.exclude(pk=self.pk).filter(email=self.email).exists():
            raise ValidationError("A user with this email already exists.")

        if len(self.mobile_number) < 10:
            raise ValidationError("Mobile number must be at least 10 digits long.")

        if JiraUser.objects.exclude(pk=self.pk).filter(mobile_number=self.mobile_number).exists():
            raise ValidationError("A user with this mobile number already exists.")

    def save(self, *args, **kwargs):
        """ Calls clean before saving """
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.role}"


class Epic(models.Model):
    name = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(JiraUser, on_delete=models.CASCADE, related_name="epics")
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'epics'
        managed = True

    def clean(self):
        """Custom validation before saving"""
        if not self.name:
            raise ValidationError("Epic name cannot be empty.")

        if not self.user:
            raise ValidationError("User must be specified.")

    def save(self, *args, **kwargs):
        """ Calls clean before saving """
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.name}"


class Task(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    epic = models.ForeignKey(Epic, on_delete=models.CASCADE, related_name="tasks")
    owner = models.ForeignKey(JiraUser, on_delete=models.CASCADE, related_name="tasks")
    assignee = models.ForeignKey(
        JiraUser,
        on_delete=models.CASCADE,
        related_name="assigned_tasks",
        null=True,
        blank=True
    )
    task_type = models.CharField(max_length=20, choices=TaskTypeEnum.choices(), default=TaskTypeEnum.MAIN_TASK.value)
    parent_task = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="subtasks")
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tasks'
        managed = True
        constraints = [
            models.UniqueConstraint(fields=["name", "epic"], name="unique_task_name_epic")
        ]

    def clean(self):
        """Custom validation before saving"""
        if not self.name:
            raise ValidationError("Task name cannot be empty.")

        if not self.epic:
            raise ValidationError("Epic must be specified.")

        if not self.owner:
            raise ValidationError("Owner must be specified.")

        if not self.assignee:
            raise ValidationError("Assignee must be specified.")

        valid_task_type = [choice[0] for choice in TaskTypeEnum.choices()]
        if self.task_type not in valid_task_type:
            raise ValidationError(f"Invalid task type: {self.task_type}. Choose from {valid_task_type}.")

    def save(self, *args, **kwargs):
        """ Calls clean before saving """
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Task: {self.name} (Parent: {self.parent_task.name if self.parent_task else 'None'})"


class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField()
    user = models.ForeignKey(JiraUser, on_delete=models.CASCADE, related_name="user_comment")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'comments'
        managed = True

    def clean(self):
        """Custom validation before saving"""
        if not self.task:
            raise ValidationError("Task must be specified.")

        if not self.user:
            raise ValidationError("User must be specified.")

    def save(self, *args, **kwargs):
        """ Calls clean before saving """
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.comment
