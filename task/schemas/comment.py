import graphene
from graphql import GraphQLError
from task import models
from graphene_django import DjangoObjectType
from task.schemas.task import TaskType


class CommentType(DjangoObjectType):
    class Meta:
        model = models.Comment
        fields = (
            "id",
            "task",
            "comment",
            "user",
            "created_at",
            "updated_at",
            "is_deleted"
        )


class CreateComment(graphene.Mutation):
    class Arguments:
        task = graphene.ID(required=True)
        msg = graphene.String(required=True)
        user = graphene.ID(required=True)


    comment = graphene.Field(CommentType)
    success = graphene.Boolean(default_value=False)
    message = graphene.String(default_value="")


    def mutate(self, info, task, msg, user):
        try:
            task_instance = models.Task.objects.get(id=task)
            user_instance = models.JiraUser.objects.get(id=user)

            comment = models.Comment(
                task=task_instance,
                comment=msg,
                user=user_instance
            )
            comment.save()

            return CreateComment(
                comment=comment,
                success=True,
                message="Comment created successfully."
            )

        except Exception as e:
            return CreateComment(
                comment=None,
                success=False,
                message=str(e)
            )
        except models.Task.DoesNotExist:
            return CreateComment(
                comment=None,
                success=False,
                message="Task not found."
            )
        except models.User.DoesNotExist:
            return CreateComment(
                comment=None,
                success=False,
                message="User not found."
            )

class UpdateComment(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        msg = graphene.String()
        is_deleted = graphene.Boolean()

    comment = graphene.Field(CommentType)
    success = graphene.Boolean(default_value=False)
    message = graphene.String(default_value="")

    def mutate(self, info, id, msg=None, is_deleted=None):
        try:
            comment_instance = models.Comment.objects.get(id=id)

            if comment_instance:

                if msg:
                    comment_instance.comment = msg
                if is_deleted:
                    comment_instance.is_deleted = is_deleted == True

                comment_instance.save()

                return UpdateComment(
                    comment=comment_instance,
                    success=True,
                    message="Comment deleted successfully."
                )
            else:
                return UpdateComment(
                    comment=None,
                    success=False,
                    message="Comment not found."
                )
        except Exception as e:
            return UpdateComment(
                comment=None,
                success=False,
                message=str(e)
            )
        except models.Comment.DoesNotExist:
            return UpdateComment(
                comment=None,
                success=False,
                message="Comment not found."
            )
class Query(graphene.ObjectType):
    all_comments = graphene.List(CommentType)
    comment = graphene.Field(CommentType, id=graphene.ID())

    def resolve_all_comments(self, info):
        return models.Comment.objects.all()

    def resolve_comment(self, info, id):
        try:
            return models.Comment.objects.get(id=id)
        except models.Comment.DoesNotExist:
            return GraphQLError("Comment not found.")

class Mutation(graphene.ObjectType):
    create_comment = CreateComment.Field()
    update_comment = UpdateComment.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)