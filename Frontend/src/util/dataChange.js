import getRandomInt from "./getRandomInt";
import nodeColorMap from "./nodeColorMap";

const dataChange = (data, width, height) => {
  if (!data) return undefined;
  let convertedNodes = data.search.nodes.map((node) => {
    let newNode = { ...node };
    var check = false;
    for (var i = 0; i < data.search.links.length; i++) {
      if (
        node.id === data.search.links[i].source ||
        node.id === data.search.links[i].target
      ) {
        check = true;
        break;
      }
    }
    if (!check) {
      newNode.fx = String(getRandomInt(40, width - 40));
      newNode.fy = String(getRandomInt(40, height - 40));
    }
    return newNode;
  });

  let result = { search: { nodes: convertedNodes, links: data.search.links } };
  result = nodeColorMap(result);
  return result;
};
export default dataChange;
