import graphene
import task.schemas.user as user
import task.schemas.epic as epic
import task.schemas.task as task
import task.schemas.comment as comment


class Query(
    user.Query,
    epic.Query,
    task.Query,
    comment.Query,
    graphene.ObjectType
):
    pass


class Mutation(
    user.Mutation,
    epic.Mutation,
    task.Mutation,
    comment.Mutation,
    graphene.ObjectType
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
