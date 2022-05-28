import { NODE_LIMIT, RELATION_LIMIT } from "../../util/neo4jInfo.js";
import getDBInfo from "./util/getDBInfo.js";
import deleteNode from "./util/deleteNode.js";
import deleteRelation from "./util/deleteRelation.js";
import {
  ALL_EXIST,
  isNodeExist,
  NODE1_ONLY,
  NODE2_ONLY,
  NOT_EXIST,
} from "./util/isNodeExist.js";
import { isRelationExist } from "./util/isRelationExist.js";
import {
  createOneNode,
  createTwoNode,
  IN,
  OUT,
  updateRelation,
} from "./util/createNode.js";

export default (MyNode, Info) => {
  return async (
    _,
    {
      E1_value,
      E1_type,
      E1_url,
      E1_main,
      E1_sub,
      E1_title,
      E1_uploadTime,
      E1_uniqueId,
      E2_value,
      E2_type,
      E2_url,
      E2_main,
      E2_sub,
      E2_title,
      E2_uploadTime,
      E2_uniqueId,
      REL,
    },
    ___
  ) => {
    const { nodeNum, relationNum } = await getDBInfo(Info);

    //node1 정의, node2 정의
    const myNode1 = {
      value: E1_value,
      type: E1_type,
      meta: {
        uniqueId: E1_uniqueId,
        main: E1_main,
        sub: E1_sub,
        url: E1_url,
        title: E1_title,
        uploadTime: E1_uploadTime,
      },
    };
    const myNode2 = {
      value: E2_value,
      type: E2_type,
      meta: {
        uniqueId: E2_uniqueId,
        main: E2_main,
        sub: E2_sub,
        url: E2_url,
        title: E2_title,
        uploadTime: E2_uploadTime,
      },
    };

    //node 존재여부
    let nodeExist = await isNodeExist({
      MyNode,
      where1: myNode1,
      where2: myNode2,
    });

    //node 삭제
    if (nodeExist === NOT_EXIST && nodeNum + 2 > NODE_LIMIT) {
      await deleteNode(MyNode, 2);
    } else if (
      (nodeExist === NODE1_ONLY || nodeExist === NODE2_ONLY) &&
      nodeNum + 1 > NODE_LIMIT
    ) {
      await deleteNode(MyNode, 1);
    }

    //rel 존재여부
    let relExist = await isRelationExist({
      MyNode,
      where1: myNode1,
      where2: myNode2,
    });

    //relation삭제
    if (
      !(nodeExist === ALL_EXIST && relExist) &&
      relationNum + 1 > RELATION_LIMIT
    ) {
      deleteRelation(MyNode);
    }

    //둘다 존재하지 않을때
    if (nodeExist === NOT_EXIST) {
      createTwoNode({
        MyNode,
        create1: myNode1,
        create2: myNode2,
        REL,
      });
    }
    //node2만 존재할때
    else if (nodeExist === NODE2_ONLY) {
      createOneNode({
        MyNode,
        create: myNode1,
        where: myNode2,
        REL,
        direction: "OUT",
      });
    }
    //node1만 존재할때
    else if (nodeExist === NODE1_ONLY) {
      createOneNode({
        MyNode,
        create: myNode2,
        where: myNode1,
        REL,
        direction: "IN",
      });
    }
    //둘다 존재할때
    else {
      updateRelation({
        MyNode,
        where1: myNode1,
        where2: myNode2,
        REL,
      });
    }
    return true;
  };
};
