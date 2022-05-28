export const isRelationExist = async ({MyNode, where1, where2}) => {
  const relExist = await MyNode.find({
    where: {
      value: where1.value,
      type: where1.type,
      relOutConnection_SINGLE: {
        node: {
          value: where2.value,
          type: where2.type,
        },
      },
    },
  });
  return relExist.length > 0;
};
