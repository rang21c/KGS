import { prisma } from "../../util/prisma.js";

export default async (_, { value }, ___) => {
  const result = prisma.nodeMeta.findMany({
    where: {
      value,
    },
    orderBy: {
      uploadTime: "desc",
    },
    take: 50,
  });
  return result;
};
