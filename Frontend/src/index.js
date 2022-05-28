import { createTheme, ThemeProvider } from "@mui/material/styles";
import { ApolloProvider, ApolloClient, InMemoryCache } from "@apollo/client";
import React from "react";
import ReactDOM from "react-dom";
import App from "./App";

const theme = createTheme({
  palette: {
    primary: {
      main: "#91D4FA",
    },
  },
});

const client = new ApolloClient({
  uri: "https://kgs-project.ml/neo4j",
  //uri: "http://localhost:4000",
  cache: new InMemoryCache({ addTypename: false }),
});

ReactDOM.render(
  <ThemeProvider theme={theme}>
    <ApolloProvider client={client}>
      <App />
    </ApolloProvider>
  </ThemeProvider>,
  document.getElementById("root")
);

// const root = ReactDOM.createRoot(document.getElementById("root"));
// root.render(
//   <ThemeProvider theme={theme}>
//     <ApolloProvider client={client}>
//       <App />
//     </ApolloProvider>
//   </ThemeProvider>
// );
