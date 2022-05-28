import relTag from "../../util/relTag.js";
export default (MyNode) => {
  return async (_, { limit, words }, ___) => {
    const selectionSet = `
      {
        value
        type
        relOutConnection {
          edges {
            name
          }
        }
        relOut {
          value
          type
        }
        relInConnection {
          edges {
            name
          }
        }
        relIn {
          value
          type
        }
      }
    `;

    var nodes = [];
    var links = [];

    if (words === "") {
      var findedNodes = await MyNode.find({
        selectionSet: selectionSet,
        options: {
          limit: limit,
        },
      });
      findedNodes.map((source) => {
        nodes.push({
          id: source.value,
          type: source.type,
        });
        source.relOut.map((target, index) => {
          links.push({
            source: source.value,
            target: target.value,
            label: source.relOutConnection.edges[index].name[0],
          });
        });
      });
    } else {
      var wordsList = words.split(" ");
      for (var i = 0; i < wordsList.length; i++) {
        var findedNodes = await MyNode.find({
          selectionSet: selectionSet,
          where: {
            value: wordsList[i],
          },
        });
        findedNodes.map((source) => {
          //if (nodes.length >= limit) return;
          nodes.push({
            id: source.value,
            type: source.type,
          });
          source.relOut.map((target, index) => {
            //if (nodes.length >= limit) return;
            nodes.push({
              id: target.value,
              type: target.type,
            });
            links.push({
              source: source.value,
              target: target.value,
              label: source.relOutConnection.edges[index].name[0],
            });
          });
          source.relIn.map((target, index) => {
            //if (nodes.length >= limit) return;
            nodes.push({
              id: target.value,
              type: target.type,
            });
            links.push({
              source: target.value,
              target: source.value,
              label: source.relInConnection.edges[index].name[0],
            });
          });
        });
      }
    }
    // 중복제거
    nodes = nodes.filter((node, idx, arr) => {
      return (
        arr.findIndex((item) => item.id === node.id && item.id === node.id) ===
        idx
      );
    });
    links = links.filter((link, idx, arr) => {
      return (
        arr.findIndex(
          (item) =>
            item.source === link.source &&
            item.target === link.target &&
            item.label === link.label
        ) === idx
      );
    });
    for (var i = limit; i < nodes.length; i++) {
      for (var j = 0; j < links.length; j++) {
        if (
          links[j].source === nodes[i].id ||
          links[j].target === nodes[i].id
        ) {
          links.splice(j, 1);
          j--;
        }
      }
      nodes.splice(i, 1);
      i--;
    }
    for (var i = 0; i < links.length; i++) {
      let checkSource = false;
      let checkTarget = false;
      for (var j = 0; j < nodes.length; j++) {
        if (links[i].source === nodes[j].id) {
          checkSource = true;
        }
        if (links[i].target === nodes[j].id) {
          checkTarget = true;
        }
      }
      if (!checkSource || !checkTarget) {
        links.splice(i, 1);
        i--;
      }
    }
    for (var i = 0; i < links.length; i++) {
      links[i].label = relTag[links[i].label];
    }
    console.log({ nodes, links });
    return { nodes, links };
  };
};
