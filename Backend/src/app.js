import { ApolloServer } from "apollo-server";
import { Neo4jGraphQL } from "@neo4j/graphql";
import pkg from "@neo4j/graphql-ogm";
const { OGM } = pkg;
import neo4j from "neo4j-driver";
import typeDefs from "./typeDefs.js";
import { AURA_ENDPOINT, USERNAME, PASSWORD } from "./util/neo4jInfo.js";
import search from "./resolvers/search/search.js";
import getMetaList from "./resolvers/getMetaList/getMetaList.js";
import insertTwoNodes from "./resolvers/insertTwoNodes/insertTwoNodes.js";

const driver = neo4j.driver(
  AURA_ENDPOINT,
  neo4j.auth.basic(USERNAME, PASSWORD)
);

//OGM 정의
const ogm = new OGM({ typeDefs, driver });
const MyNode = ogm.model("MyNode");
const Info = ogm.model("Info");

//Resolver 정의
const resolvers = {
  Query: {
    search: search(MyNode),
    getMetaList
  },

  Mutation: {
    insertTwoNodes: insertTwoNodes(MyNode, Info),
  },
};

const neo4jSchema = new Neo4jGraphQL({ typeDefs, driver, resolvers });

//DB 최초 초기화
const init = async () => {
  let isInfoExist = await Info.find({
    where: { id: 0 },
  });
  if (isInfoExist.length === 0) {
    await Info.create({
      input: [
        {
          id: 0,
        },
      ],
    });
  }
};

// 서버 시작
Promise.all([neo4jSchema.getSchema(), ogm.init()]).then(([schema]) => {
  const server = new ApolloServer({
    schema,
    context: async ({ req }) => {
      return { req };
    },
  });

  server.listen({ port: 4000 }).then(async ({ url }) => {
    await init();
    console.log(`🚀 Server ready at ${url}`);
  });
});
