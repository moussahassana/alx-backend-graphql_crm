import graphene
from crm.schema import Query as CRMQuery, Mutation as CRMMutation


class Query(CRMQuery, graphene.ObjectType):
    """Root query that inherits queries from crm."""
    pass


class Mutation(CRMMutation, graphene.ObjectType):
    """Root mutation that inherits mutations from crm."""
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
