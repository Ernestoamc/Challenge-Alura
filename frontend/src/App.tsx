import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import ReactMarkdown from "react-markdown";
import {
  Send,
  ShoppingBag,
  Bot,
  User,
  MoreHorizontal,
  Paperclip,
} from "lucide-react";

interface Fuente {
  archivo: string;
  pagina: string | number;
}
interface Message {
  id: string;
  text: string;
  sender: "user" | "bot";
  timestamp: Date;
  fuentes?: Fuente[];
}

export default function App() {
  const API_URL = import.meta.env.VITE_API_URL;

  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      text: "¡Hola! Bienvenido a BIMBAM BUY. ¿En qué puedo ayudarte hoy?",
      sender: "bot",
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
    }
  };

  useEffect(() => {
    adjustTextareaHeight();
  }, [inputValue]);

  const handleSendMessage = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!inputValue.trim()) return;

    const newUserMessage: Message = {
      id: Date.now().toString(),
      text: inputValue.trim(),
      sender: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, newUserMessage]);
    setInputValue("");
    setIsTyping(true);

    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pregunta: newUserMessage.text }),
      });

      if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);

      const data = await response.json();

      const newBotMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: data.respuesta,
        sender: "bot",
        timestamp: new Date(),
        fuentes: data.fuentes,
      };
      setMessages((prev) => [...prev, newBotMessage]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          text: "Error de conexión. El servidor RAG no responde o hay un bloqueo de CORS.",
          sender: "bot",
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-neutral-950 flex items-center justify-center p-4 sm:p-6 relative overflow-hidden font-sans selection:bg-white/20">
      {/* Elementos decorativos de fondo */}
      <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-emerald-500/20 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-blue-500/20 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute top-[40%] left-[60%] w-72 h-72 bg-purple-500/10 rounded-full blur-[100px] pointer-events-none" />

      {/* Contenedor del Chat */}
      <div className="w-full max-w-3xl h-[85vh] sm:h-[750px] max-h-full bg-neutral-900/40 backdrop-blur-2xl border border-white/10 rounded-3xl shadow-2xl flex flex-col relative z-10 overflow-hidden">
        {/* Cabecera */}
        <header className="px-6 py-5 border-b border-white/10 bg-white/5 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-4">
            <div className="w-11 h-11 rounded-full bg-white/10 border border-white/10 flex items-center justify-center shadow-inner">
              <ShoppingBag className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="font-semibold text-lg text-white tracking-tight">
                BIMBAM BUY
              </h1>
              <div className="flex items-center gap-2 mt-0.5">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
                <span className="text-xs text-white/60 font-medium">
                  Asistente de Inferencia Activo
                </span>
              </div>
            </div>
          </div>
          <button className="p-2.5 rounded-full hover:bg-white/10 transition-colors text-white/60 hover:text-white">
            <MoreHorizontal className="w-5 h-5" />
          </button>
        </header>

        {/* Área de Mensajes */}
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6 scroll-smooth">
          <AnimatePresence initial={false}>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 15, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                transition={{ duration: 0.4, ease: [0.23, 1, 0.32, 1] }}
                className={`flex gap-3 max-w-[85%] ${
                  message.sender === "user" ? "ml-auto flex-row-reverse" : ""
                }`}
              >
                <div
                  className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center mt-1 shadow-sm border ${
                    message.sender === "user"
                      ? "bg-white/10 border-white/10 text-white"
                      : "bg-white/20 border-white/20 text-white"
                  }`}
                >
                  {message.sender === "user" ? (
                    <User className="w-4 h-4" />
                  ) : (
                    <Bot className="w-4 h-4" />
                  )}
                </div>
                <div
                  className={`flex flex-col ${
                    message.sender === "user" ? "items-end" : "items-start"
                  }`}
                >
                  <div
                    className={`px-4 py-3 rounded-2xl text-[15px] leading-relaxed backdrop-blur-md shadow-sm border ${
                      message.sender === "user"
                        ? "bg-white/10 border-white/10 text-white rounded-tr-sm font-medium"
                        : "bg-black/30 border-white/5 text-white/90 rounded-tl-sm"
                    }`}
                  >
                    {message.sender === "user" ? (
                      <div className="whitespace-pre-wrap">{message.text}</div>
                    ) : (
                      <div className="space-y-3">
                        <ReactMarkdown
                          components={{
                            p: (props) => (
                              <p className="text-white/90 leading-relaxed">
                                {props.children}
                              </p>
                            ),
                            ul: (props) => (
                              <ul className="list-disc pl-5 space-y-1 text-white/80">
                                {props.children}
                              </ul>
                            ),
                            ol: (props) => (
                              <ol className="list-decimal pl-5 space-y-1 text-white/80">
                                {props.children}
                              </ol>
                            ),
                            li: (props) => (
                              <li className="pl-1">{props.children}</li>
                            ),
                            strong: (props) => (
                              <strong className="font-semibold text-emerald-400">
                                {props.children}
                              </strong>
                            ),
                          }}
                        >
                          {message.text}
                        </ReactMarkdown>
                        {message.fuentes && message.fuentes.length > 0 && (
                          <div className="mt-3 pt-3 border-t border-white/10 flex flex-wrap gap-1.5">
                            {message.fuentes.map((f, i) => (
                              <span
                                key={i}
                                className="text-[11px] px-2 py-1 rounded-full bg-white/5 border border-white/10 text-white/50 font-medium"
                                title={`${f.archivo}, página ${f.pagina}`}
                              >
                                📄 {f.archivo} · p.{f.pagina}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                  <span className="text-[11px] text-white/40 mt-1.5 px-1 font-medium">
                    {message.timestamp.toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </span>
                </div>
              </motion.div>
            ))}
            {isTyping && (
              <motion.div
                initial={{ opacity: 0, y: 15, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{
                  opacity: 0,
                  scale: 0.95,
                  transition: { duration: 0.2 },
                }}
                transition={{ duration: 0.4, ease: [0.23, 1, 0.32, 1] }}
                className="flex gap-3 max-w-[85%]"
              >
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-white/20 border border-white/20 text-white flex items-center justify-center mt-1 shadow-sm">
                  <Bot className="w-4 h-4" />
                </div>
                <div className="bg-black/30 border border-white/5 backdrop-blur-md rounded-2xl rounded-tl-sm px-4 py-4 flex items-center gap-1.5 shadow-sm">
                  <motion.div
                    className="w-1.5 h-1.5 bg-white/60 rounded-full"
                    animate={{ y: [0, -4, 0] }}
                    transition={{
                      duration: 0.6,
                      repeat: Infinity,
                      ease: "easeInOut",
                      delay: 0,
                    }}
                  />
                  <motion.div
                    className="w-1.5 h-1.5 bg-white/60 rounded-full"
                    animate={{ y: [0, -4, 0] }}
                    transition={{
                      duration: 0.6,
                      repeat: Infinity,
                      ease: "easeInOut",
                      delay: 0.15,
                    }}
                  />
                  <motion.div
                    className="w-1.5 h-1.5 bg-white/60 rounded-full"
                    animate={{ y: [0, -4, 0] }}
                    transition={{
                      duration: 0.6,
                      repeat: Infinity,
                      ease: "easeInOut",
                      delay: 0.3,
                    }}
                  />
                </div>
              </motion.div>
            )}
          </AnimatePresence>
          <div ref={messagesEndRef} className="h-2" />
        </main>

        {/* Área de Entrada */}
        <div className="p-4 sm:p-5 border-t border-white/10 bg-white/5 shrink-0">
          <form
            onSubmit={handleSendMessage}
            className="relative flex items-end gap-2 bg-black/20 backdrop-blur-md border border-white/10 rounded-3xl p-1.5 focus-within:border-white/30 focus-within:bg-black/30 transition-all shadow-inner"
          >
            <button
              type="button"
              className="p-3 text-white/50 hover:text-white hover:bg-white/10 rounded-full transition-colors flex-shrink-0 m-0.5"
            >
              <Paperclip className="w-5 h-5" />
            </button>
            <textarea
              ref={textareaRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Escribe tu mensaje al motor RAG..."
              className="w-full bg-transparent border-none focus:ring-0 resize-none py-3.5 px-2 max-h-32 text-white placeholder:text-white/40 text-[15px] outline-none"
              rows={1}
              style={{ minHeight: "52px" }}
            />
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              type="submit"
              disabled={!inputValue.trim()}
              className="p-3 bg-white hover:bg-neutral-200 text-black rounded-full disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex-shrink-0 flex items-center justify-center m-0.5"
            >
              <Send className="w-5 h-5 ml-0.5" />
            </motion.button>
          </form>
          <div className="text-center mt-3"></div>
        </div>
      </div>
    </div>
  );
}
