import graphene
from django.db import IntegrityError
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from task.schemas.task import TaskType
from task import models

class EpicType(DjangoObjectType):
    tasks = graphene.List(TaskType)
    task_count = graphene.Int()

    class Meta:
        model = models.Epic
        fields = (
            "id",
            "name",
            "is_completed",
            "created_at",
            "updated_at",
            "is_completed"
        )


    def resolve_tasks(self, info):
        return models.Task.objects.filter(epic=self)

    def resolve_task_count(self, info):
        return models.Task.objects.filter(epic=self).count()

class CreateEpic(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        user = graphene.ID(required=True)
        is_completed = graphene.Boolean()

    epic = graphene.Field(EpicType)
    success = graphene.Boolean(default_value=False)
    message = graphene.String(default_value="")

    def mutate(self, info, name, user, is_completed=False):
        try:
            user_instance = models.JiraUser.objects.get(id=user)
            epic = models.Epic.objects.create(
                name=name,
                user=user_instance,
                is_completed=is_completed
            )
            return CreateEpic(
                epic=epic,
                success=True,
                message="Epic created successfully"
            )

        except models.JiraUser.DoesNotExist:
            return CreateEpic(
                epic=None,
                success=False,
                message="User does not exist"
            )
        except IntegrityError:
            return CreateEpic(
                epic=None,
                success=False,
                message="Epic already exists"
            )


class UpdateEpic(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        is_completed = graphene.Boolean()

    epic = graphene.Field(EpicType)
    success = graphene.Boolean(default_value=False)
    message = graphene.String(default_value="")

    def mutate(self, info, id, name=None, is_completed=None):

        try:
            epic = models.Epic.objects.filter(id=id).first()

            if epic:
                if name:
                    epic.name = name
                if is_completed is not None:
                    epic.is_completed = is_completed
                epic.save()
                return UpdateEpic(
                    epic=epic,
                    success=True,
                    message="Epic updated successfully"
                )
            else:
                return UpdateEpic(
                    epic=None,
                    success=False,
                    message="Epic does not exist"
                )
        except IntegrityError:
            return UpdateEpic(
                epic=None,
                success=False,
                message="Epic already exists"
            )
        except Exception as e:
            return UpdateEpic(
                epic=None,
                success=False,
                message=f"An error occurred: {str(e)}"
            )



class Query(graphene.ObjectType):
    all_epics = graphene.List(EpicType)
    epic = graphene.Field(EpicType, id=graphene.ID(required=True))

    def resolve_all_epics(self, info):
        return models.Epic.objects.all()

    def resolve_epic(self, info, id):
        try:
            return models.Epic.objects.get(id=id)
        except models.Epic.DoesNotExist:
            raise GraphQLError("Epic with the given ID does not exist.")


class Mutation(graphene.ObjectType):
    create_epic = CreateEpic.Field()