import { prisma } from "../../../util/prisma.js";

const upsertData = async ({ node }) => {
  await prisma.nodeMeta.upsert({
    where: {
      uniqueId_value: {
        uniqueId: node.meta.uniqueId,
        value: node.value,
      },
    },
    create: {
      ...node.meta,
      value: node.value,
    },
    update: {
      ...node.meta,
      value: node.value,
    },
  });
};

export const createTwoNode = async ({ MyNode, create1, create2, REL }) => {
  MyNode.create({
    input: [
      {
        value: create1.value,
        type: create1.type,
        relOut: {
          create: {
            node: {
              value: create2.value,
              type: create2.type,
            },
            edge: {
              name: REL,
            },
          },
        },
      },
    ],
  });
  await upsertData({ node: create1 });
  await upsertData({ node: create2 });
};

export const IN = "IN";
export const OUT = "OUT";
export const createOneNode = async ({
  MyNode,
  create,
  where,
  REL,
  direction,
}) => {
  if (direction === IN) {
    MyNode.create({
      input: [
        {
          value: create.value,
          type: create.type,
          relIn: {
            connect: {
              where: {
                node: {
                  value: where.value,
                  //type: E1_type
                },
              },
              edge: {
                name: REL,
              },
            },
          },
        },
      ],
    });
  } else {
    MyNode.create({
      input: [
        {
          value: create.value,
          type: create.type,
          relOut: {
            connect: {
              where: {
                node: {
                  value: where.value,
                  //type: E1_type
                },
              },
              edge: {
                name: REL,
              },
            },
          },
        },
      ],
    });
  }
  await upsertData({ node: create });
  await upsertData({ node: where });
};

export const updateRelation = async ({ MyNode, where1, where2, REL }) => {
  MyNode.update({
    where: {
      value: where1.value,
      //type: E1_type,
    },
    update: {
      relOut: {
        connect: {
          where: {
            node: {
              value: where2.value,
              //type: E2_type
            },
          },
          edge: {
            name: REL,
          },
        },
      },
    },
  });
  await upsertData({ node: where1 });
  await upsertData({ node: where2 });
};
