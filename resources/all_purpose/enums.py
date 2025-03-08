from enum import Enum


class UserRoleTypes(Enum):
    ADMIN = 'admin'
    MANAGER = 'manager'
    DEVELOPER = 'developer'
    TESTER = 'tester'
    USER = 'user'

    @classmethod
    def choices(cls):
        return [(choice.value, choice.name.replace("_", " ").title()) for choice in cls]


class TaskTypeEnum(Enum):
    MAIN_TASK = "main_task"
    SUB_TASK = "sub_task"

    @classmethod
    def choices(cls):
        return [(choice.value, choice.name.replace("_", " ").title()) for choice in cls]
