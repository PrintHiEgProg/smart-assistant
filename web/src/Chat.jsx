import React, { useState, useEffect, useRef } from "react";
import {
  Box,
  TextField,
  Button,
  List,
  ListItem,
  ListItemText,
  Paper,
  Typography,
  Avatar,
  useTheme,
  AppBar,
  Toolbar,
} from "@mui/material";
import { FaPaperPlane } from "react-icons/fa";
import { styled, keyframes } from "@mui/system";
import Linkify from "react-linkify"; // Импортируем Linkify

// Кастомные стили для сообщений
const UserMessage = styled(Paper)(({ theme }) => ({
  backgroundColor: theme.palette.primary.light,
  color: theme.palette.primary.contrastText,
  borderRadius: "20px 20px 0 20px",
  padding: "10px 15px",
  maxWidth: "70%",
  marginLeft: "auto",
  marginBottom: "10px",
  boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
}));

const BotMessage = styled(Paper)(({ theme }) => ({
  backgroundColor: theme.palette.grey[200],
  color: theme.palette.text.primary,
  borderRadius: "20px 20px 20px 0",
  padding: "10px 15px",
  maxWidth: "70%",
  marginRight: "auto",
  marginBottom: "10px",
  boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
}));

// Анимация для текста "печатает..."
const typingAnimation = keyframes`
  0% { content: ''; }
  25% { content: '.'; }
  50% { content: '..'; }
  75% { content: '...'; }
  100% { content: ''; }
`;

const TypingIndicator = styled(Typography)(({ theme }) => ({
  color: theme.palette.text.secondary,
  "&::after": {
    content: '""',
    animation: `${typingAnimation} 1.5s infinite`,
  },
}));

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const theme = useTheme();

  // Прокрутка к последнему сообщению
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Отправка сообщения
  const handleSend = async () => {
    if (input.trim() === "") return;

    const userMessage = { text: input, sender: "user" };
    setMessages([...messages, userMessage]);
    setInput("");
    setIsTyping(true);

    try {
      const response = await fetch("http://127.0.0.1:7270/generate-response", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: 1, // Замените на реальный user_id
          message: input,
        }),
      });

      const data = await response.json();
      const botMessage = { text: data.response, sender: "bot" };
      setMessages([...messages, userMessage, botMessage]);
    } catch (error) {
      console.error("Ошибка при отправке сообщения:", error);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        width: "100vw",
        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      }}
    >
      {/* Шапка (Header) */}
      <AppBar
        position="static"
        sx={{
          backgroundColor: "rgba(255, 255, 255, 0.1)",
          backdropFilter: "blur(10px)",
          boxShadow: "none",
        }}
      >
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1, color: "white" }}>
            Умный ассистент ЮФУ
          </Typography>
        </Toolbar>
      </AppBar>

      {/* Основное содержимое чата */}
      <Box
        sx={{
          flexGrow: 1,
          display: "flex",
          flexDirection: "column",
          padding: 3,
          overflow: "hidden",
        }}
      >
        <Paper
          sx={{
            flexGrow: 1,
            overflow: "auto",
            marginBottom: 2,
            padding: 2,
            backgroundColor: "rgba(255, 255, 255, 0.9)",
            borderRadius: "15px",
            boxShadow: "0 8px 32px rgba(0, 0, 0, 0.2)",
          }}
        >
          <List>
            {messages.map((msg, index) => (
              <ListItem
                key={index}
                sx={{ display: "flex", alignItems: "center" }}
              >
                {msg.sender === "bot" && (
                  <Avatar
                    sx={{
                      bgcolor: theme.palette.secondary.main,
                      mr: 2,
                      boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
                    }}
                  >
                    🤖
                  </Avatar>
                )}
                {msg.sender === "user" ? (
                  <UserMessage>
                    <Linkify
                      componentDecorator={(
                        decoratedHref,
                        decoratedText,
                        key
                      ) => (
                        <a
                          href={decoratedHref}
                          key={key}
                          style={{ color: "#2196F3", textDecoration: "none" }}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          {decoratedText}
                        </a>
                      )}
                    >
                      <ListItemText primary={msg.text} />
                    </Linkify>
                  </UserMessage>
                ) : (
                  <BotMessage>
                    <Linkify
                      componentDecorator={(
                        decoratedHref,
                        decoratedText,
                        key
                      ) => (
                        <a
                          href={decoratedHref}
                          key={key}
                          style={{ color: "#2196F3", textDecoration: "none" }}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          {decoratedText}
                        </a>
                      )}
                    >
                      <ListItemText primary={msg.text} />
                    </Linkify>
                  </BotMessage>
                )}
                {msg.sender === "user" && (
                  <Avatar
                    sx={{
                      bgcolor: theme.palette.primary.main,
                      ml: 2,
                      boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
                    }}
                  >
                    👤
                  </Avatar>
                )}
              </ListItem>
            ))}
            {isTyping && (
              <ListItem sx={{ display: "flex", alignItems: "center" }}>
                <Avatar
                  sx={{
                    bgcolor: theme.palette.secondary.main,
                    mr: 2,
                    boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
                  }}
                >
                  🤖
                </Avatar>
                <BotMessage>
                  <TypingIndicator>печатает</TypingIndicator>
                </BotMessage>
              </ListItem>
            )}
            <div ref={messagesEndRef} />
          </List>
        </Paper>
        <Box sx={{ display: "flex", gap: 1 }}>
          <TextField
            fullWidth
            variant="outlined"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleSend()}
            sx={{
              backgroundColor: "rgba(255, 255, 255, 0.9)",
              borderRadius: "15px",
              "& .MuiOutlinedInput-root": {
                borderRadius: "15px",
              },
            }}
          />
          <Button
            variant="contained"
            color="primary"
            onClick={handleSend}
            sx={{
              borderRadius: "15px",
              boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
              minWidth: "56px", // Фиксированная ширина для кнопки
              height: "56px", // Фиксированная высота для кнопки
            }}
          >
            <FaPaperPlane style={{ fontSize: "24px" }} />{" "}
            {/* Увеличиваем иконку */}
          </Button>
        </Box>
      </Box>
    </Box>
  );
};

export default Chat;
