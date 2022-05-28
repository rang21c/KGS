export default async (Info) => {
  const selectionSet = `
          {
            countNode
            countRelation
          }
      `;
  let desc;
  await Info.find({ selectionSet: selectionSet }).then((nodes) => {
    //관계 개수
    desc = nodes[0];
  });

  let nodeNum = desc.countNode; //노드 개수
  let relationNum = desc.countRelation;
  return { nodeNum, relationNum };
};
