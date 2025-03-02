import React from "react";
import Chat from "./Chat";
import { CssBaseline, ThemeProvider, createTheme } from "@mui/material";

// Кастомная тема
const theme = createTheme({
  palette: {
    primary: {
      main: "#667eea",
      light: "#a3b4f5",
      contrastText: "#fff",
    },
    secondary: {
      main: "#764ba2",
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Chat />
    </ThemeProvider>
  );
}

export default App;
