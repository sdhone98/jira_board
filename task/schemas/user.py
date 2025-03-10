import graphene
from django.db import IntegrityError
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from task import models
from resources.all_purpose import common
from task.schemas.epic import EpicType


class JiraUserType(DjangoObjectType):
    epics = graphene.List(EpicType)
    epicsCount = graphene.Int()

    class Meta:
        model = models.JiraUser
        fields = (
            "id",
            "first_name",
            "last_name",
            "user_name",
            "email",
            "mobile_number",
            "role",
            "created_at",
            "updated_at"
        )

    def resolve_epics(self, info):
        return models.Epic.objects.filter(epic=self)

    def resolve_epics_counts(self, info):
        return models.Epic.objects.filter(epic=self).count()


class CreateUser(graphene.Mutation):
    class Arguments:
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)
        user_name = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        mobile_number = graphene.String(required=True)
        role = graphene.String(required=True)

    user = graphene.Field(JiraUserType)
    success = graphene.Boolean(default_value=False)
    message = graphene.String(default_value="")

    def mutate(self, info, first_name, last_name, user_name, email, password, mobile_number, role):
        try:
            hashed_password = common.convert_raw_password_to_hash(password)
            user = models.JiraUser.objects.create(
                first_name=first_name,
                last_name=last_name,
                user_name=user_name,
                email=email,
                password=hashed_password,
                mobile_number=mobile_number,
                role=role
            )
            return CreateUser(
                user=user,
                success=True,
                message="User created successfully"
            )
        except IntegrityError:
            return CreateUser(
                user=None,
                success=False,
                message="User already exists"
            )


class UpdateUser(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        first_name = graphene.String()
        last_name = graphene.String()
        user_name = graphene.String()
        email = graphene.String()
        mobile_number = graphene.String()
        role = graphene.String()

    user = graphene.Field(JiraUserType)
    success = graphene.Boolean(default_value=False)
    message = graphene.String(default_value="")

    def mutate(self, info, id, first_name=None, last_name=None, user_name=None, email=None, mobile_number=None,
               role=None):
        try:
            user = models.JiraUser.objects.get(id=id)

            if user:
                if first_name:
                    user.first_name = first_name
                if last_name:
                    user.last_name = last_name
                if user_name:
                    user.user_name = user_name
                if email:
                    user.email = email
                if mobile_number:
                    user.mobile_number = mobile_number
                if role:
                    user.role = role

                user.save()

                return UpdateUser(
                    user=user,
                    success=True,
                    message="User updated successfully"
                )
            else:
                return UpdateUser(
                    user=None,
                    success=False,
                    message="User not found"
                )

        except models.JiraUser.DoesNotExist:
            return UpdateUser(
                user=None,
                success=False,
                message="User not found"
            )
        except IntegrityError:
            return UpdateUser(
                user=None,
                success=False,
                message="Failed to update user"
            )
        except Exception as e:
            return UpdateUser(
                epic=None,
                success=False,
                message=f"An error occurred: {str(e)}"
            )


class Query(graphene.ObjectType):
    all_users = graphene.List(JiraUserType)
    user = graphene.Field(JiraUserType, id=graphene.ID(required=True))

    def resolve_all_users(self, info):
        return models.JiraUser.objects.all()

    def resolve_user(self, info, id):
        try:
            return models.JiraUser.objects.get(id=id)
        except models.JiraUser.DoesNotExist:
            raise GraphQLError("User with the given ID does not exist.")


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
