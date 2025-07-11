async function enviarMensagem() {
  const input = document.getElementById("mensagem");
  const texto = input.value.trim();
  if (!texto) return;

  adicionarMensagem("user", texto);
  input.value = "";

  try {
    const resposta = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mensagem: texto }),
    });

    const data = await resposta.json();
    adicionarMensagem("bot", data.resposta || data.erro || "Erro na resposta.");
  } catch (erro) {
    adicionarMensagem("bot", "Erro ao se comunicar com o servidor.");
  }
}

function adicionarMensagem(origem, texto) {
  const chatBox = document.getElementById("chat-box");
  const msg = document.createElement("div");
  msg.classList.add("msg", origem);
  msg.textContent = texto;
  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}
