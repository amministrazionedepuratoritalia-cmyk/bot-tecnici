import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

SYSTEM_PROMPT = """Sei un assistente tecnico per purificatori d'acqua. REGOLE ASSOLUTE:
- Rispondi SOLO basandoti sulle procedure qui sotto
- Se il problema non e nelle procedure rispondi SOLO con: Non ho informazioni su questo problema, contatta l'ufficio
- VIETATO fare domande
- VIETATO aggiungere informazioni extra
- Sii breve e diretto

FALSA PARTENZA - macchina si avvia da sola:
1. Controlla se il rubinetto gocciola, se si riparalo
2. Apri la macchina e cerca perdite interne
3. Sostituisci la valvola di non ritorno sull acqua permeata
4. Se persiste, sostituisci il pressostato di minima

ALLARME BIP solo aprendo il rubinetto:
E allarme filtri. Sostituisci i filtri e resetta dalla centralina.

ALLARME BIP anche a rubinetto chiuso e macchina bloccata:
E la sonda anti-allagamento bagnata. Apri la macchina, ripara la perdita, asciuga la sonda, spegni e riaccendi.

MACCHINA IN BLOCCO allarme volumetrico:
Controlla che il rubinetto di alimentazione sia aperto. Se e aperto sostituisci l elettrovalvola. Elettrovalvola difettosa causa anche: macchina che non eroga, o che continua a girare a rubinetto chiuso."""


def chiedi_groq(messaggio):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": messaggio}
        ]
    }
    risposta = requests.post(url, headers=headers, json=body, timeout=30)
    dati = risposta.json()
    return dati["choices"][0]["message"]["content"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Ciao! Sono l'assistente tecnico.\nDescrivimi il problema e ti guido nella soluzione."
    )


async def gestisci_messaggio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )
    testo = update.message.text
    risposta = chiedi_groq(testo)
    await update.message.reply_text(risposta)


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, gestisci_messaggio))
    print("Bot avviato...")
    app.run_polling()


if __name__ == "__main__":
    main()
