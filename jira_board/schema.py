import graphene
from task.schema import Query as TaskQuery, Mutation as TaskMutation


class Query(TaskQuery, graphene.ObjectType):
    pass


class Mutation(TaskMutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
