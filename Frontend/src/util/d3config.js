const withDesign = ({ width, height }) => {
  return {
    automaticRearrangeAfterDropNode: true,
    collapsible: false,
    directed: true,
    focusAnimationDuration: 0.75,
    focusZoom: 1,
    freezeAllDragEvents: false,
    height: height,
    width: width,
    highlightDegree: 1,
    highlightOpacity: 0.2,
    linkHighlightBehavior: true,
    maxZoom: 30,
    minZoom: 0.5,
    nodeHighlightBehavior: true,
    panAndZoom: false,
    staticGraph: false,
    staticGraphWithDragAndDrop: false,
    d3: {
      alphaTarget: 0.05,
      gravity: -100,
      linkLength: 300,
      linkStrength: 1,
      disableLinkForce: false,
    },
    node: {
      fontColor: "white",
      fontSize: 14,
      fontWeight: "normal",
      highlightFontSize: 20,
      highlightFontWeight: "bold",
      highlightStrokeColor: "SAME",
      highlightStrokeWidth: 1.5,
      labelProperty: "name",
      mouseCursor: "pointer",
      opacity: 1,
      renderLabel: true,
      size: 400,
      strokeWidth: 12,
      svg: "",
      symbolType: "circle",
      labelPosition: "top",
    },
    link: {
      type: "CURVE_SMOOTH",
      color: "#a6a6a6",
      fontColor: "#a6a6a6",
      fontSize: 8,
      fontWeight: "bold",
      highlightColor: "SAME",
      highlightFontSize: 8,
      highlightFontWeight: "bold",
      mouseCursor: "pointer",
      opacity: 0.8,
      renderLabel: true,
      semanticStrokeWidth: false,
      strokeWidth: 2,
      markerHeight: 4,
      markerWidth: 4,
      strokeDasharray: 0,
      strokeDashoffset: 0,
      strokeLinecap: "butt",
    },
  };
};
const withoutDesign = ({ width, height }) => {
  return {
    height: height,
    width: width,
    node: {
      fontColor: "white",
    },
    link: {
      color: "#a6a6a6",
      fontColor: "#a6a6a6",
      renderLabel: true,
    },
  };
};

const d3config = ({ width, height, isDesignOn }) => {
  return isDesignOn
    ? withDesign({ width, height })
    : withoutDesign({ width, height });
};
export default d3config;
