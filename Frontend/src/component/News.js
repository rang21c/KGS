import {
  Paper,
  IconButton,
  Typography,
  CircularProgress,
  Stack,
  Divider,
} from "@mui/material";
import ClearOutlinedIcon from "@mui/icons-material/ClearOutlined";
import { useQuery } from "@apollo/client";
import { GET_METALIST } from "../queries";

const News = ({ node, setNode }) => {
  const { data, error, loading } = useQuery(GET_METALIST, {
    variables: { value: node ? node.id : "" },
  });
  const myData = data
    ? data.getMetaList.map((item) => {
        return {
          ...item,
          uploadTime: new Date(item.uploadTime * 1).toLocaleDateString(),
        };
      })
    : [];

  return (
    <Paper
      sx={{
        position: "relative",
        overflow: "scroll",
        pt: 4,
        px: 4,
        pb: 4,
        height: "100%",
        bgcolor: "#121212",
        minWidth: 300,
      }}
    >
      <Stack direction="row" justifyContent="space-between" sx={{ mb: 2 }}>
        <Typography variant="h6" sx={{ color: "#909090" }}>
          관련 뉴스 - {node ? node.id : undefined}
        </Typography>
        <IconButton
          onClick={() => {
            setNode(undefined);
          }}
          sx={{ color: "white" }}
        >
          <ClearOutlinedIcon />
        </IconButton>
      </Stack>

      {loading ? (
        <Stack
          sx={{
            width: "100%",
            height: "100%",
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          <CircularProgress size={50} />
        </Stack>
      ) : error ? (
        <Stack
          sx={{
            width: "100%",
            height: "100%",
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          <Typography variant="h4" sx={{ color: "white" }}>
            에러가 났어요 {":("}
          </Typography>
        </Stack>
      ) : data && data.getMetaList.length === 0 ? (
        <Stack
          sx={{
            width: "100%",
            height: "100%",
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          <Typography variant="h4" sx={{ color: "white" }}>
            데이터가 없어요 {":("}
          </Typography>
        </Stack>
      ) : (
        myData.map((item, index) => (
          <Stack
            key={index}
            sx={{ cursor: "pointer" }}
            onClick={() => {
              window.open(item.url, "_blank");
            }}
          >
            <Typography
              variant="body2"
              sx={{
                color: "white",
                height: "1.4em",
                overflow: "hidden",
                textOverflow: "ellipsis",
              }}
            >
              {item.title}
            </Typography>
            <Stack direction="row" justifyContent="space-between">
              <Typography
                variant="body2"
                sx={{
                  color: "#9d9d9d",
                  height: "1.4em",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                }}
              >
                {item.main} / {item.sub}
              </Typography>
              <Typography
                variant="body2"
                sx={{
                  color: "#9d9d9d",
                  height: "1.4em",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                }}
              >
                {item.uploadTime}
              </Typography>
            </Stack>
            {index !== myData.length - 1 && (
              <Divider width="100%" color="#303030" sx={{ my: 2 }} />
            )}
          </Stack>
        ))
      )}
    </Paper>
  );
};

export default News;
