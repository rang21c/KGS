export const ALL_EXIST = "ALL_EXIST";
export const NODE1_ONLY = "NODE1_ONLY";
export const NODE2_ONLY = "NODE2_ONLY";
export const NOT_EXIST = "NOT_EXIST";
export const isNodeExist = async ({ MyNode, where1, where2 }) => {
  //Node 존재여부 체크필요
  let node1 = await MyNode.find({
    where: { value: where1.value },
  });
  let node2 = await MyNode.find({
    where: { value: where2.value },
  });
  let isNode1Exist = node1.length >= 1;
  let isNode2Exist = node2.length >= 1;

  if (isNode1Exist && isNode2Exist) return ALL_EXIST;
  else if (isNode1Exist && !isNode2Exist) return NODE1_ONLY;
  else if (!isNode1Exist && isNode2Exist) return NODE2_ONLY;
  else return NOT_EXIST;
};
