export default async (MyNode, num) => {
  let findDeleteNode = await MyNode.find({
    options: {
      sort: [
        {
          createdAt: "ASC",
        },
      ],
      limit: num,
    },
  });
  findDeleteNode.map(async (node) => {
    await MyNode.delete({
      where: {
        value: node.value,
      },
    });
    await prisma.nodeMeta.delete({where: {
      value: node.value
    }})
  });
};
