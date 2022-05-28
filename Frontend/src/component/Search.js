import * as React from "react";
import Paper from "@mui/material/Paper";
import InputBase from "@mui/material/InputBase";
import IconButton from "@mui/material/IconButton";
import SearchIcon from "@mui/icons-material/Search";
import { Stack } from "@mui/material";

export default function Search({ setWords }) {
  return (
    <Stack sx={{ width: "100%", zIndex: 1 }}>
      <Paper
        component="form"
        sx={{
          bgcolor: "#121212",
          px: 3,
          py: 0.5,
          mx: 3,
          mt: 2,
          display: "flex",
          alignItems: "center",
        }}
      >
        <InputBase
          sx={{ ml: 1, flex: 1, color: "white" }}
          placeholder="검색 단어 입력"
          onChange={(e) => setWords(e.target.value)}
        />
        <IconButton
          type="submit"
          sx={{ p: "10px", color: "white" }}
          aria-label="search"
        >
          <SearchIcon />
        </IconButton>
      </Paper>
    </Stack>
  );
}
