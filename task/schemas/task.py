import graphene
from django.db import IntegrityError
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from task import models

class TaskType(DjangoObjectType):
    class Meta:
        model = models.Task
        fields = (
            "id",
            "name",
            "description",
            "epic",
            "owner",
            "assignee",
            "task_type",
            "parent_task",
            "created_at",
            "updated_at",
            "is_completed"
        )

class CreateTask(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String(required=True)
        epic = graphene.ID(required=True)
        owner = graphene.ID(required=True)
        assignee = graphene.ID(required=True)
        task_type = graphene.String()
        parent_task = graphene.String()
        is_completed = graphene.String()

    task = graphene.Field(TaskType)
    success = graphene.Boolean(default_value=False)
    message = graphene.String(default_value="")

    def mutate(self, info, name, description, epic, owner, assignee):
        try:
            epic_instance = models.Epic.objects.get(id=epic)
            owner_instance = models.JiraUser.objects.get(id=owner)
            assignee_instance = models.JiraUser.objects.get(id=assignee)
            task = models.Task.objects.create(
                name=name,
                description=description,
                epic=epic_instance,
                owner=owner_instance,
                assignee=assignee_instance
            )
            return CreateTask(
                task=task,
                success=True,
                message="Task created successfully"
            )

        except models.Epic.DoesNotExist:
            return CreateTask(
                task=None,
                success=False,
                message="Epic does not exist"
            )

        except models.JiraUser.DoesNotExist:
            return CreateTask(
                task=None,
                success=False,
                message="User does not exist"
            )
        except IntegrityError:
            return CreateTask(
                task=None,
                success=False,
                message="Epic already exists"
            )

class UpdateTask(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        description = graphene.String()
        assignee = graphene.ID()
        parent_task = graphene.String()
        is_completed = graphene.String()

    task = graphene.Field(TaskType)
    success = graphene.Boolean(default_value=False)
    message = graphene.String(default_value="")


    def mutate(self, info, id, name=None, description=None, assignee=None, parent_task=None, is_completed=False):
        try:
            task_instance = models.Task.objects.get(id=id)

            if task_instance:
                if name:
                    task_instance.name = name
                if description:
                    task_instance.description = description
                if assignee:
                    task_instance.assignee = models.JiraUser.objects.get(id=assignee)
                if parent_task:
                    task_instance.parent_task = models.Task.objects.get(id=parent_task)
                if is_completed:
                    task_instance.is_completed = is_completed == True
                task_instance.save()

                return UpdateTask(
                    task=task_instance,
                    success=True,
                    message="Task updated successfully"
                )
            else:
                return UpdateTask(
                    task=None,
                    success=False,
                    message="Task does not exist"
                )
        except models.JiraUser.DoesNotExist:
            return UpdateTask(
                task=None,
                success=False,
                message="User does not exist"
            )
        except models.Task.DoesNotExist:
            return UpdateTask(
                task=None,
                success=False,
                message="Parent Task does not exist"
            )


class Query(graphene.ObjectType):
    all_tasks = graphene.List(TaskType)
    task = graphene.Field(TaskType, id=graphene.ID(required=True))


    def resolve_all_tasks(self, info):
        return models.Task.objects.all()

    def resolve_task(self, info, id):
        try:
            return models.Task.objects.get(id=id)
        except models.Task.DoesNotExist:
            raise GraphQLError("Task with the given ID does not exist.")


class Mutation(graphene.ObjectType):
    create_task = CreateTask.Field()
    update_task = UpdateTask.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)