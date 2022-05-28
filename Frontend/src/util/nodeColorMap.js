const nodeColorMap = (data) => {
  if (!data) return undefined;
  let convertedNodes = data.search.nodes.map((node) => {
    let newNode = { ...node };
    var nodeType = newNode.type.substr(0, 2);
    if (nodeType === "PS") {
      newNode.color = "#f9aaa0";
      newNode.strokeColor = "#f9aaa033";
    } else if (nodeType === "LC") {
      newNode.color = "#f1935e";
      newNode.strokeColor = "#f1935e33";
    } else if (nodeType === "OG") {
      newNode.color = "#f4f839";
      newNode.strokeColor = "#f4f83933";
    } else if (nodeType === "DT") {
      newNode.color = "#39f87c";
      newNode.strokeColor = "#39f87c33";
    } else if (nodeType === "TI") {
      newNode.color = "#39f2f8";
      newNode.strokeColor = "#39f2f833";
    } else if (nodeType === "QT") {
      newNode.color = "#3996f8";
      newNode.strokeColor = "#3996f833";
    }
    return newNode;
  });
  let result = { search: { nodes: convertedNodes, links: data.search.links } };
  return result;
};
export default nodeColorMap;
