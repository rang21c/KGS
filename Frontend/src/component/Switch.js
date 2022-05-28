import React from "react";
import Typography from "@mui/material/Typography";
import { Stack, Switch } from "@mui/material";

const CustomSwitch = ({ design, setDesign }) => {
  return (
    <Stack sx={{ width: "100%" }}>
      <Stack
        direction="row"
        sx={{ width: "100%", justifyContent: "space-between" }}
      >
        <Typography sx={{ color: "white" }}>디자인 모드</Typography>
        <Typography sx={{ color: "white" }}>{design ? "ON" : "OFF"}</Typography>
      </Stack>
      <Switch
        defaultChecked
        color="default"
        sx={{ ml: -2 }}
        onChange={(e) => setDesign(e.target.checked)}
      />
    </Stack>
  );
};

export default CustomSwitch;
