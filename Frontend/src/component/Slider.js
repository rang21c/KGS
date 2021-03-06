import React from "react";
import Typography from "@mui/material/Typography";
import Slider from "@mui/material/Slider";
import { Stack } from "@mui/material";

const CustomSlider = ({ limit, setLimit, maxLimit }) => {
  const handleSliderChange = (event, newlimit) => {
    setLimit(newlimit);
  };

  return (
    <Stack sx={{ width: "100%" }}>
      <Stack
        direction="row"
        sx={{ width: "100%", justifyContent: "space-between" }}
      >
        <Typography sx={{ color: "white" }}>λΈλ κ°μ</Typography>
        <Typography sx={{ color: "white" }}>{limit}</Typography>
      </Stack>
      <Slider
        sx={{ color: "white" }}
        value={limit}
        onChange={handleSliderChange}
        onChangeCommitted={(e, newlimit) => setLimit(newlimit)}
        aria-labelledby="input-slider"
        step={1}
        min={0}
        max={maxLimit}
      />
    </Stack>
  );
};

export default CustomSlider;
