export default async (MyNode) => {
  const selectionSet2 = `
          {
            type
            value
            relOut {
              type
              value
            }
          }
        `;

  let a = await MyNode.find({
    selectionSet: selectionSet2,
    where: {
      relOutAggregate: {
        count_GT: 0,
      },
    },
    options: {
      sort: [
        {
          createdAt: "ASC",
        },
      ],
      limit: 1,
    },
  });
  let nodeType1 = a[0].type;
  let nodeValue1 = a[0].value;
  let nodeType2 = a[0].relOut[a[0].relOut.length - 1].type;
  let nodeValue2 = a[0].relOut[a[0].relOut.length - 1].value;

  await MyNode.update({
    where: {
      type: nodeType1,
      value: nodeValue1,
    },
    update: {
      relOut: [
        {
          disconnect: [
            {
              where: {
                node: {
                  type: nodeType2,
                  value: nodeValue2,
                },
              },
            },
          ],
        },
      ],
    },
  });
};
