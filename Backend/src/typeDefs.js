export default `
type NewsData{
  main: String
  sub: String
  title: String
  url: String
  uploadTime: String
}

type D3Node{
  id: String!
  type: String!
}

type D3Link{
  source: String!
  target: String!
  label: String!
}

type D3Return{
  nodes:[D3Node]!
  links:[D3Link]!
}

type MyNode {
  type: String!
  value: String!
  createdAt: DateTime! @timestamp(operations: [CREATE, UPDATE])
  relOut: [MyNode!]! @relationship(type: "REL", properties: "MyRel", direction: OUT)
  relIn: [MyNode!]! @relationship(type: "REL", properties: "MyRel", direction: IN)
}
interface MyRel @relationshipProperties {
  name: [String!]
}
type Query {
  search(
    limit: Int!
    words: String!
  ): D3Return!
  getMetaList(
    value: String!
  ): [NewsData]!
}
type Mutation {
  insertTwoNodes(
    E1_value: String!
    E1_type: String!
    E1_url: String
    E1_main: String
    E1_sub: String
    E1_title: String
    E1_uploadTime: String
    E1_uniqueId: Int
    E2_value: String!
    E2_type: String!
    E2_url: String
    E2_main: String
    E2_sub: String
    E2_title: String
    E2_uploadTime: String
    E2_uniqueId: Int
    REL: String!
  ): Boolean!
}
type Info {
  id: Int!
  countNode: Int!
  @cypher(
    statement: """
    MATCH (n)
    RETURN count(*)
    """
  )
  countRelation: Int!
  @cypher(
        statement: """
        MATCH (n)-[r]->(x)
        RETURN count(r)
        """
    )
  deleteTwoNodes: Boolean
  @cypher(
        statement: """
        MATCH (N) 
        WHERE N.value IS NOT NULL 
        WITH N 
        ORDER BY N.createdAt 
        LIMIT 2 
        DETACH DELETE N
        """
  )
}
`;
