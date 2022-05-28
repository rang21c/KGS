import { Stack, Typography, CircularProgress } from "@mui/material";
import { Graph } from "react-d3-graph";
import { useQuery } from "@apollo/client";
import { SEARCH } from "./queries";
import Search from "./component/Search";
import CustomSlider from "./component/Slider";
import { useEffect, useState } from "react";
import d3config from "./util/d3config";
import dataChange from "./util/dataChange";
import useWindowSize from "./util/useWindowSize";
import CustomSwitch from "./component/Switch";
import { motion } from "framer-motion";
import News from "./component/News";

const MAX_LIMIT = 400;

function App() {
  const { width, height } = useWindowSize();

  const [words, setWords] = useState("");
  const [limit, setLimit] = useState(10);
  const [design, setDesign] = useState(true);
  const [node, setNode] = useState();

  const [renderData, setRenderData] = useState();

  const { loading, error, data } = useQuery(SEARCH, {
    variables: { limit: limit, words: words },
  });

  useEffect(() => {
    setRenderData(dataChange(data, width, height));
  }, [data, width, height]);

  // the graph configuration, just override the ones you need
  const onClickNode = function (nodeId, node) {
    setNode(node);
  };

  const onClickLink = function (source, target) {
    window.alert(`Clicked link between ${source} and ${target}`);
  };

  const onZoomChange = (prevZoom, newZoom) => {
    this.setState({ currentZoom: newZoom });
  };

  return (
    <Stack alignItems="center" sx={{ bgcolor: "#292c33" }}>
      <Search setWords={setWords} />

      <motion.div
        animate={{
          position: "absolute",
          top: 0,
          left: 0,
          opacity: node ? 1 : 0,
          x: node ? 0 : -200,
          height: "89%",
        }}
        transition={{
          x: { type: "spring", stiffness: 120 },
          opacity: { duration: 0.1 },
        }}
      >
        <Stack
          sx={{
            width: 300,
            position: "absolute",
            left: 0,
            top: 0,
            pl: 3,
            pt: 10,
            height: "100%",
          }}
        >
          <News node={node} setNode={setNode} />
        </Stack>
      </motion.div>

      <Stack
        sx={{
          alignItems: "flex-end",
          minWidth: 300,
          position: "absolute",
          right: 0,
          bottom: 0,
          pb: 2,
          pr: 5,
        }}
      >
        <CustomSwitch design={design} setDesign={setDesign} />
        <CustomSlider limit={limit} setLimit={setLimit} maxLimit={MAX_LIMIT} />
      </Stack>

      <Stack sx={{ height, justifyContent: "center", alignItems: "center" }}>
        {error ? (
          <Typography variant="h3" sx={{ color: "white", mt: -20 }}>
            에러가 났어요 {":("}
          </Typography>
        ) : !loading && renderData ? (
          renderData.search.nodes.length !== 0 ? (
            <Graph
              id="graph-id" // id is mandatory
              data={renderData.search}
              config={d3config({ width, height, isDesignOn: design })}
              onClickNode={onClickNode}
              onClickLink={onClickLink}
              onZoomChange={onZoomChange}
            />
          ) : (
            <Typography variant="h3" sx={{ color: "white", mt: -20 }}>
              데이터가 없어요 {":("}
            </Typography>
          )
        ) : (
          <CircularProgress size={100} />
        )}
      </Stack>
    </Stack>
  );
}

export default App;
