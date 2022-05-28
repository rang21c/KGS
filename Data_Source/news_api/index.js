import { ApolloServer } from "apollo-server";
import pkg from "@prisma/client";

const { PrismaClient } = pkg;
const db = new PrismaClient();

const BUFFER_MAX = 300;

// 스키마
const typeDefs = `
    type News {
        id:Int!
        uniqueId:Int!
        title:String!
        content:String!
        url:String!
        uploadTime:String!
        main:String!
        sub:String!
    }
    type Query {
        checkNews(uniqueId:String!):Boolean!
    }
    type Mutation {
        readNews:News
        insertNews(uniqueId:String!, url:String!, urlOrigin:String!, title:String!, content:String!, uploadTime:String!, main:String!, sub:String!): Boolean!
        deleteAll:Boolean!
    }
`;

// 리졸버
const resolvers = {
  Query: {
    checkNews: async (_, { uniqueId }, ___) => {
      const result = await db.news.findUnique({
        where: {
          uniqueId,
        },
      });
      if (result == null) return false;
      else return true;
    },
  },
  Mutation: {
    readNews: async (_, __, ___) => {
      const result = await db.news.findFirst({
        orderBy: {
          id: "asc",
        },
      });
      await db.news.delete({
        where: {
          id: result.id,
        },
      });
      return result;
    },
    deleteAll: async () => {
      let result = true;
      try {
        await db.news.deleteMany({});
      } catch (e) {
        console.log(e);
        result = false;
      }
      return result;
    },
    insertNews: async (
      _,
      { uniqueId, url, urlOrigin, title, content, uploadTime, main, sub },
      ___
    ) => {
      let result = true;
      try {
        const newsNum = await db.news.count();
        if (newsNum >= BUFFER_MAX) {
          const newsLast = await db.news.findFirst({
            select: { id: true },
            orderBy: { id: "asc" },
          });
          await db.news.delete({
            where: { id: newsLast.id },
          });
        }

        await db.news.create({
          data: {
            uniqueId,
            url,
            urlOrigin,
            title,
            content,
            uploadTime: new Date(uploadTime),
            main,
            sub,
          },
        });
      } catch (e) {
        console.log(e);
        result = false;
      }
      return result;
    },
  },
};

// 서버 인스턴스 생성
const server = new ApolloServer({
  typeDefs,
  resolvers,
});

// 서버 구동
server
  .listen({
    port: 5000,
  })
  .then(({ url }) => console.log(`GraphQL Service running on ${url}`));
