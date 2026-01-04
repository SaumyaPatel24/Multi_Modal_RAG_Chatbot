import React, { useState } from "react";

export default function RAGChat() {
  const [question, setQuestion] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [fileLoading, setFileLoading] = useState(false);

  // Send question to backend
  const handleSend = async () => {
    if (!question.trim()) return;

    // Exit if user types 'exit'
    if (question.trim().toLowerCase() === "exit") {
      setChatHistory((prev) => [
        ...prev,
        { type: "system", text: "Chat ended by user." },
      ]);
      setQuestion("");
      return;
    }

    const currentQuestion = question;
    setChatHistory((prev) => [...prev, { type: "user", text: currentQuestion }]);
    setQuestion(""); // clear input
    setLoading(true);

    try {
      const res = await fetch("http://localhost:5000/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: currentQuestion,
          chat_history: chatHistory,
        }),
      });

      const data = await res.json();
      setChatHistory((prev) => [...prev, { type: "bot", text: data.answer }]);
    } catch (err) {
      console.error(err);
      setChatHistory((prev) => [
        ...prev,
        { type: "bot", text: "Failed to fetch answer." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Handle file upload for ingestion
  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setFileLoading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:5000/ingest", {
        method: "POST",
        body: formData,
      });

      if (res.ok) alert("Document ingested successfully!");
      else alert("Failed to ingest document.");
    } catch (err) {
      console.error(err);
      alert("Error uploading document.");
    } finally {
      setFileLoading(false);
      e.target.value = null; // reset input
    }
  };

  return (
    <div className="h-screen w-screen bg-gradient-to-r from-gray-900 via-black to-gray-900 flex justify-center items-start p-4">
      <div className="flex flex-col w-full max-w-md">
        {/* Welcome Box */}
        <div className="w-full mb-6 text-center">
          <div className="text-4xl font-black text-purple-800">
            🤖 RAG Chatbot
          </div>
          <div className="text-sm font-semibold text-purple-600 mt-1">
            Ask questions. Get grounded answers.
          </div>
        </div>


        {/* Document Upload */}
        <div className="flex flex-col mb-4">
          <label className="mb-2 font-semibold text-purple-700">
            Upload Document for Ingestion:
          </label>
          {/* <label className="bg-purple-700 text-white px-4 py-2 rounded-lg cursor-pointer font-bold"> */}
          <input
            type="file"
            onChange={handleFileUpload}
            className="border bg-purple-700 p-2 rounded-lg"
            disabled={fileLoading}
          />
          {fileLoading && <span className="text-purple-800 mt-1">Uploading...</span>}
          {/* </label> */}
        </div>
        

        {/* Chat History */}
        <div className="flex flex-col space-y-3 overflow-y-auto h-[60vh] mb-4 p-2 bg-purple-300 rounded-lg">
          {chatHistory.map((msg, idx) => (
            <div
              key={idx}
              className={`p-3 rounded-xl max-w-[80%] ${
                msg.type === "user"
                  ? "bg-purple-700 text-white self-end"
                  : msg.type === "bot"
                  ? "bg-white text-black self-start"
                  : "bg-gray-300 text-gray-800 self-center"
              }`}
            >
              {msg.text}
            </div>
          ))}
        </div>

        {/* Input Box */}
        <div className="flex">
          <input
            type="text"
            placeholder="Type your question..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            className="border rounded-l-lg p-2 flex-grow focus:outline-none"
            onKeyDown={(e) => {
              if (e.key === "Enter") handleSend();
            }}
          />
          <button
            onClick={handleSend}
            className="bg-purple-700 text-white p-2 rounded-r-lg hover:bg-purple-800"
            disabled={loading}
          >
            {loading ? "..." : "→"}
          </button>
        </div>
      </div>
        <footer className="absolute bottom-3 w-full text-center text-xs font-medium text-purple-100">
          © 2026 RAG Chatbot · Powered by LLMs  
          <span className="mx-1">·</span>
          Built by <span className="font-semibold">Saumya Patel</span>
        </footer>
    </div>
    
  );

}
