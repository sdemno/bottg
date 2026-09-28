import os
import random
import logging

# Caricamento sicuro di dotenv (non va in crash se la libreria non è installata)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto
)
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")

IMAGE_PATH = "menu.jpg"
SHIPPING_IMAGE_PATH = "spedizione.jpg"

# Dizionario completo in 5 lingue (nessun testo tagliato)
TEXTS = {
    "it": {
        "disclaimer": (
            "⚠️ <b>ATTENZIONE LEGGERE ATTENTAMENTE QUESTO MESSAGGIO!</b>\n\n"
            "Ciao, siamo venuti a conoscenza da diversi clienti che su Telegram e TikTok girano molti scammer! "
            "Chiediamo la massima attenzione e soprattutto chiediamo di segnalare il più possibile questi soggetti.\n\n"
            "Non siamo qui per giocare.\n"
            "Non siamo qui per ascoltare problemi.\n"
            "Non siamo qui per fare beneficenza.\n\n"
            "Siamo un team esperto in questo settore, mettiamo la nostra piena conoscenza e fiducia!\n\n"
            "Cerchiamo solo persone con la testa sulle spalle e che abbiano voglia di svoltare la propria vita!\n\n"
            "Da quando abbiamo iniziato a lavorare in questo settore abbiamo aiutato più di 300 persone, "
            "abbiamo riscontrato molti problemi tra ban e problemi con i clienti, "
            "ma non abbiamo mai mollato perché il successo è sempre dietro l’angolo!"
        ),
        "btn_read": "✅ HO LETTO!",
        "captcha_title": "🤖 <b>VERIFICA DI SICUREZZA</b>\n\nSeleziona l'icona corrispondente a: <b>{target_name}</b>",
        "captcha_wrong": "❌ Errato! Riprova con un nuovo captcha.",
        "welcome": "👋 Ciao <b>{name}</b>!\nBenvenuto nel nostro bot ufficiale.\nScegli un'opzione dal menu qui sotto:",
        "btn_banknotes": "💵 Banconote (10/20/50)",
        "btn_paypal": "💸 PayPal Transfer",
        "btn_shipping": "📦 Spedizioni",
        "btn_payments": "💳 Metodi di Pagamento",
        "btn_feedback": "⭐ Recensioni",
        "btn_white_cards": "🔴 CARTE BIANCHE",
        "btn_lang": "🌐 Cambia Lingua",
        "btn_back": "🔙 Menu Principale",
        "btn_back_banknotes": "🔙 Torna a Banconote",
        "btn_video_quality": "🎥 VIDEO QUALITÀ",
        "btn_video_paypal": "🎥 VIDEO",
        "banknotes_menu_title": "💵 <b>BANCONOTE DISPONIBILI</b>\n\nSeleziona il taglio desiderato per visualizzare il listino prezzi e i video di prova:",
        "banknotes_10_info": (
            "💵 <b>Listino Banconote da 10€</b>\n\n"
            "• 30 pezzi = 3,2 € al pezzo\n"
            "• 50 pezzi = 2,8 € al pezzo\n"
            "• 75 pezzi = 2,5 € al pezzo\n"
            "• 100 pezzi = 2,2 € al pezzo\n"
            "• 150 pezzi = 1,9 € al pezzo\n\n"
            "<b>Minimo ordine 30 pezzi.</b>\n"
            "<b>Accettiamo ordine misto</b>"
        ),
        "banknotes_20_info": (
            "💵 <b>Listino Banconote da 20€</b>\n\n"
            "• 30 pezzi = 8 € al pezzo\n"
            "• 50 pezzi = 7,5 € al pezzo\n"
            "• 75 pezzi = 7 € al pezzo\n"
            "• 100 pezzi = 6,5 € al pezzo\n"
            "• 150 pezzi = 5,8 € al pezzo\n"
            "• 200 pezzi = 5 € al pezzo\n\n"
            "<b>Minimo ordine 30 pezzi.</b>\n"
            "<b>Accettiamo ordine misto</b>"
        ),
        "banknotes_50_info": (
            "💵 <b>Listino Banconote da 50€</b>\n\n"
            "• 30 pezzi = 12 € al pezzo\n"
            "• 50 pezzi = 11 € al pezzo\n"
            "• 75 pezzi = 9,5 € al pezzo\n"
            "• 100 pezzi = 8,5 € al pezzo\n"
            "• 150 pezzi = 7,8 € al pezzo\n"
            "• 200 pezzi = 7 € al pezzo\n\n"
            "<b>Minimo ordine 30 pezzi.</b>\n"
            "<b>Accettiamo ordine misto</b>"
        ),
        "shipping_info": (
            "📦 <b>Spedizione tramite Locker InPost</b>\n\n"
            "💰 <b>Prezzo:</b> 5€\n\n"
            "⏱ <b>Tempi di consegna:</b>\n"
            "• 1/2 giorni lavorativi al Sud\n"
            "• 2/3 giorni lavorativi al Nord\n\n"
            "✅ Dopo la spedizione inviamo sempre il codice di tracciamento al cliente!"
        ),
        "paypal_info": (
            "💸 <b>PAYPAL TRANSFER</b>\n\n"
            "• €120 = Saldo 360\n"
            "• €150 = Saldo 680\n"
            "• €180 = Saldo 930\n"
            "• €220 = Saldo 1570\n"
            "• €280 = Saldo 2140\n"
            "• €320 = Saldo 3400\n"
            "• €380 = Saldo 4800\n"
            "• €470 = Saldo 5800\n\n"
            "Per info e ordini contattami @GustavoEuro"
        ),
        "payments_info": (
            "💳 <b>Gli unici pagamenti accettati sono:</b>\n\n"
            "(per maggiorenni) 🪙 <b>Crypto:</b> il metodo più sicuro e affidabile per tenere la propria identità nascosta e anonima!\n"
            "(Per chi non sa come acquistare le crypto, contattami e ti spiegherò passo passo come acquistarle e inviarle al venditore, senza documenti, tramite l’applicazione Phantom!)\n\n"
            "🏦 <b>Bonifico istantaneo:</b> pagamento rapido e sicuro tramite bonifico bancario istantaneo. L’accredito avviene generalmente in pochi secondi.\n\n"
            "(per minorenni) 🎁 <b>Buoni Amazon:</b> questo metodo di pagamento lo accettiamo solo ed esclusivamente per le persone che non hanno una carta di credito!\n"
            "(I buoni si possono comprare direttamente dal tabacchino oppure online.)"
        ),
        "white_cards_info": (
            "⚠️ <b>ATTENZIONE</b>\n\n"
            "Chiunque venda carte bianche nel 2026 in italia o in Europa e uno scammer, "
            "diffidate dalla gente che vende queste carte bianche in italia perché non hanno mai funzionato, "
            "è una minchiata che hanno creato gli americani nel 2023 ATTENZIONE!"
        )
    },
    "en": {
        "disclaimer": (
            "⚠️ <b>WARNING READ THIS MESSAGE CAREFULLY!</b>\n\n"
            "Hello, we have been informed by several clients that there are many scammers on Telegram and TikTok! "
            "We ask for maximum attention and above all we ask you to report these individuals as much as possible.\n\n"
            "We are not here to play.\n"
            "We are not here to listen to problems.\n"
            "We are not here to do charity.\n\n"
            "We are an experienced team in this field, offering our full knowledge and trust!\n\n"
            "We are only looking for responsible people who want to turn their lives around!\n\n"
            "Since we started working in this field, we have helped over 300 people. "
            "We faced many issues including bans and customer difficulties, but we never gave up because success is always around the corner!"
        ),
        "btn_read": "✅ I HAVE READ!",
        "captcha_title": "🤖 <b>SECURITY CHECK</b>\n\nSelect the icon matching: <b>{target_name}</b>",
        "captcha_wrong": "❌ Incorrect! Try again.",
        "welcome": "👋 Hello <b>{name}</b>!\nWelcome to our official bot.\nChoose an option below:",
        "btn_banknotes": "💵 Banknotes (10/20/50)",
        "btn_paypal": "💸 PayPal Transfer",
        "btn_shipping": "📦 Shipping",
        "btn_payments": "💳 Payment Methods",
        "btn_feedback": "⭐ Reviews",
        "btn_white_cards": "🔴 WHITE CARDS",
        "btn_lang": "🌐 Change Language",
        "btn_back": "🔙 Main Menu",
        "btn_back_banknotes": "🔙 Back to Banknotes",
        "btn_video_quality": "🎥 QUALITY VIDEO",
        "btn_video_paypal": "🎥 VIDEO",
        "banknotes_menu_title": "💵 <b>AVAILABLE BANKNOTES</b>\n\nSelect the denomination to see price lists and quality videos:",
        "banknotes_10_info": (
            "💵 <b>10€ Banknotes Price List</b>\n\n"
            "• 30 pcs = 3.2 € each\n"
            "• 50 pcs = 2.8 € each\n"
            "• 75 pcs = 2.5 € each\n"
            "• 100 pcs = 2.2 € each\n"
            "• 150 pcs = 1.9 € each\n\n"
            "<b>Minimum order 30 pcs.</b>\n"
            "<b>Mixed orders accepted</b>"
        ),
        "banknotes_20_info": (
            "💵 <b>20€ Banknotes Price List</b>\n\n"
            "• 30 pcs = 8 € each\n"
            "• 50 pcs = 7.5 € each\n"
            "• 75 pcs = 7 € each\n"
            "• 100 pcs = 6.5 € each\n"
            "• 150 pcs = 5.8 € each\n"
            "• 200 pcs = 5 € each\n\n"
            "<b>Minimum order 30 pcs.</b>\n"
            "<b>Mixed orders accepted</b>"
        ),
        "banknotes_50_info": (
            "💵 <b>50€ Banknotes Price List</b>\n\n"
            "• 30 pcs = 12 € each\n"
            "• 50 pcs = 11 € each\n"
            "• 75 pcs = 9.5 € each\n"
            "• 100 pcs = 8.5 € each\n"
            "• 150 pcs = 7.8 € each\n"
            "• 200 pcs = 7 € each\n\n"
            "<b>Minimum order 30 pcs.</b>\n"
            "<b>Mixed orders accepted</b>"
        ),
        "shipping_info": (
            "📦 <b>Shipping via InPost Locker</b>\n\n"
            "💰 <b>Price:</b> 5€\n\n"
            "⏱ <b>Delivery times:</b>\n"
            "• 1/2 business days South\n"
            "• 2/3 business days North\n\n"
            "✅ Tracking code is always sent right after shipping!"
        ),
        "paypal_info": (
            "💸 <b>PAYPAL TRANSFER</b>\n\n"
            "• €120 = Balance 360\n"
            "• €150 = Balance 680\n"
            "• €180 = Balance 930\n"
            "• €220 = Balance 1570\n"
            "• €280 = Balance 2140\n"
            "• €320 = Balance 3400\n"
            "• €380 = Balance 4800\n"
            "• €470 = Balance 5800\n\n"
            "For info and orders contact @GustavoEuro"
        ),
        "payments_info": (
            "💳 <b>Accepted payment methods:</b>\n\n"
            "🪙 <b>Crypto:</b> Safe and anonymous payment.\n"
            "🏦 <b>Instant Bank Transfer:</b> Fast and safe.\n"
            "🎁 <b>Amazon Gift Cards:</b> For users without credit cards."
        ),
        "white_cards_info": (
            "⚠️ <b>WARNING</b>\n\n"
            "Anyone selling white cards in 2026 in Italy or Europe is a scammer! "
            "Beware of people selling them, they have never worked. It is a scam created in 2023. BEWARE!"
        )
    },
    "es": {
        "disclaimer": (
            "⚠️ <b>¡ATENCIÓN LEA ESTE MENSAJE ATENTAMENTE!</b>\n\n"
            "¡Hola, varios clientes nos han informado de que en Telegram y TikTok hay muchos estafadores! "
            "Pedimos la máxima atención y, sobre todo, pedimos denunciar a estos sujetos lo máximo posible.\n\n"
            "No estamos aquí para jugar.\n"
            "No estamos aquí para escuchar problemas.\n"
            "No estamos aquí para hacer caridad.\n\n"
            "¡Somos un equipo experto en este sector, ponemos todo nuestro conocimiento y confianza!\n\n"
            "¡Buscamos únicamente a personas con la cabeza sobre los hombros y con ganas de cambiar su vida!\n\n"
            "Desde que empezamos a trabajar en este sector hemos ayudado a más de 300 personas, "
            "hemos tenido muchos problemas entre bloqueos y percances con clientes, "
            "¡pero nunca nos hemos rendido porque el éxito siempre está a la vuelta de la esquina!"
        ),
        "btn_read": "✅ ¡HE LEÍDO!",
        "captcha_title": "🤖 <b>CONTROL DE SEGURIDAD</b>\n\nSelecciona el icono: <b>{target_name}</b>",
        "captcha_wrong": "❌ ¡Incorrecto! Inténtalo de nuevo.",
        "welcome": "👋 ¡Hola <b>{name}</b>!\nBienvenido a nuestro bot oficial.\nSelecciona una opción:",
        "btn_banknotes": "💵 Billetes (10/20/50)",
        "btn_paypal": "💸 PayPal Transfer",
        "btn_shipping": "📦 Envíos",
        "btn_payments": "💳 Métodos de Pago",
        "btn_feedback": "⭐ Reseñas",
        "btn_white_cards": "🔴 TARJETAS BLANCAS",
        "btn_lang": "🌐 Cambiar Idioma",
        "btn_back": "🔙 Menú Principal",
        "btn_back_banknotes": "🔙 Volver a Billetes",
        "btn_video_quality": "🎥 VIDEO CALIDAD",
        "btn_video_paypal": "🎥 VIDEO",
        "banknotes_menu_title": "💵 <b>BILLETES DISPONIBLES</b>\n\nSelecciona el corte deseado para ver precios y videos:",
        "banknotes_10_info": (
            "💵 <b>Lista de Precios Billetes de 10€</b>\n\n"
            "• 30 unidades = 3,2 € por unidad\n"
            "• 50 unidades = 2,8 € por unidad\n"
            "• 75 unidades = 2,5 € por unidad\n"
            "• 100 unidades = 2,2 € por unidad\n"
            "• 150 unidades = 1,9 € por unidad\n\n"
            "<b>Pedido mínimo 30 unidades.</b>\n"
            "<b>Aceptamos pedidos mixtos</b>"
        ),
        "banknotes_20_info": (
            "💵 <b>Lista de Precios Billetes de 20€</b>\n\n"
            "• 30 unidades = 8 € por unidad\n"
            "• 50 unidades = 7,5 € por unidad\n"
            "• 75 unidades = 7 € por unidad\n"
            "• 100 unidades = 6,5 € por unidad\n"
            "• 150 unidades = 5,8 € por unidad\n"
            "• 200 unidades = 5 € por unidad\n\n"
            "<b>Pedido mínimo 30 unidades.</b>\n"
            "<b>Aceptamos pedidos mixtos</b>"
        ),
        "banknotes_50_info": (
            "💵 <b>Lista de Precios Billetes de 50€</b>\n\n"
            "• 30 unidades = 12 € por unidad\n"
            "• 50 unidades = 11 € por unidad\n"
            "• 75 unidades = 9,5 € por unidad\n"
            "• 100 unidades = 8,5 € por unidad\n"
            "• 150 unidades = 7,8 € por unidad\n"
            "• 200 unidades = 7 € por unidad\n\n"
            "<b>Pedido mínimo 30 unidades.</b>\n"
            "<b>Aceptamos pedidos mixtos</b>"
        ),
        "shipping_info": (
            "📦 <b>Envío por Locker InPost</b>\n\n"
            "💰 <b>Precio:</b> 5€\n\n"
            "⏱ <b>Tiempos de entrega:</b>\n"
            "• 1/2 días laborables al Sur\n"
            "• 2/3 días laborables al Norte\n\n"
            "✅ ¡Siempre enviamos el código de seguimiento tras el envío!"
        ),
        "paypal_info": (
            "💸 <b>PAYPAL TRANSFER</b>\n\n"
            "• €120 = Saldo 360\n"
            "• €150 = Saldo 680\n"
            "• €180 = Saldo 930\n"
            "• €220 = Saldo 1570\n"
            "• €280 = Saldo 2140\n"
            "• €320 = Saldo 3400\n"
            "• €380 = Saldo 4800\n"
            "• €470 = Saldo 5800\n\n"
            "Para info y pedidos contacta @GustavoEuro"
        ),
        "payments_info": (
            "💳 <b>Métodos de pago aceptados:</b>\n\n"
            "🪙 <b>Criptomonedas:</b> Pago seguro y anónimo.\n"
            "🏦 <b>Transferencia bancaria instantánea.</b>\n"
            "🎁 <b>Tarjetas regalo de Amazon.</b>"
        ),
        "white_cards_info": (
            "⚠️ <b>¡ATENCIÓN!</b>\n\n"
            "¡Cualquiera que venda tarjetas blancas en 2026 en Italia o Europa es un estafador! "
            "Desconfiad porque nunca han funcionado, es un timo creado en 2023. ¡ATENCIÓN!"
        )
    },
    "fr": {
        "disclaimer": (
            "⚠️ <b>ATTENTION LISEZ CE MESSAGE ATTENTIVEMENT !</b>\n\n"
            "Bonjour, plusieurs clients nous ont informés que de nombreux arnaqueurs circulent sur Telegram et TikTok ! "
            "Nous demandons la plus grande vigilance et surtout nous vous demandons de signaler ces individus le plus possible.\n\n"
            "Nous ne sommes pas là pour jouer.\n"
            "Nous ne sommes pas là pour écouter les problèmes.\n"
            "Nous ne sommes pas là pour faire de la charité.\n\n"
            "Nous sommes une équipe expérimentée dans ce secteur, nous mettons toutes nos connaissances et notre confiance à votre disposition !\n\n"
            "Nous recherchons uniquement des personnes sérieuses, qui ont la tête sur les épaules et qui veulent transformer leur vie !\n\n"
            "Depuis que nous avons commencé dans ce secteur, nous avons aidé plus de 300 personnes, "
            "nous avons rencontré de nombreux problèmes entre bannissements et soucis clients, "
            "mais nous n'avons jamais baissé les bras car le succès est toujours au coin de la rue !"
        ),
        "btn_read": "✅ J'AI LU !",
        "captcha_title": "🤖 <b>VÉRIFICATION DE SÉCURITÉ</b>\n\nSélectionnez l'icône : <b>{target_name}</b>",
        "captcha_wrong": "❌ Incorrect ! Réessayez.",
        "welcome": "👋 Bonjour <b>{name}</b> !\nBienvenue sur notre bot officiel.\nChoisissez une option :",
        "btn_banknotes": "💵 Billets (10/20/50)",
        "btn_paypal": "💸 PayPal Transfer",
        "btn_shipping": "📦 Livraisons",
        "btn_payments": "💳 Modes de Paiement",
        "btn_feedback": "⭐ Avis",
        "btn_white_cards": "🔴 CARTES BLANCHES",
        "btn_lang": "🌐 Changer de Langue",
        "btn_back": "🔙 Menu Principal",
        "btn_back_banknotes": "🔙 Retour aux Billets",
        "btn_video_quality": "🎥 VIDÉO QUALITÉ",
        "btn_video_paypal": "🎥 VIDÉO",
        "banknotes_menu_title": "💵 <b>BILLETS DISPONIBLES</b>\n\nChoisissez la coupure pour voir les prix et vidéos de démonstration :",
        "banknotes_10_info": (
            "💵 <b>Tarifs Billets de 10€</b>\n\n"
            "• 30 pièces = 3,2 € la pièce\n"
            "• 50 pièces = 2,8 € la pièce\n"
            "• 75 pièces = 2,5 € la pièce\n"
            "• 100 pièces = 2,2 € la pièce\n"
            "• 150 pièces = 1,9 € la pièce\n\n"
            "<b>Commande minimale 30 pièces.</b>\n"
            "<b>Commandes mixtes acceptées</b>"
        ),
        "banknotes_20_info": (
            "💵 <b>Tarifs Billets de 20€</b>\n\n"
            "• 30 pièces = 8 € la pièce\n"
            "• 50 pièces = 7,5 € la pièce\n"
            "• 75 pièces = 7 € la pièce\n"
            "• 100 pièces = 6,5 € la pièce\n"
            "• 150 pièces = 5,8 € la pièce\n"
            "• 200 pièces = 5 € la pièce\n\n"
            "<b>Commande minimale 30 pièces.</b>\n"
            "<b>Commandes mixtes acceptées</b>"
        ),
        "banknotes_50_info": (
            "💵 <b>Tarifs Billets de 50€</b>\n\n"
            "• 30 pièces = 12 € la pièce\n"
            "• 50 pièces = 11 € la pièce\n"
            "• 75 pièces = 9,5 € la pièce\n"
            "• 100 pièces = 8,5 € la pièce\n"
            "• 150 pièces = 7,8 € la pièce\n"
            "• 200 pièces = 7 € la pièce\n\n"
            "<b>Commande minimale 30 pièces.</b>\n"
            "<b>Commandes mixtes acceptées</b>"
        ),
        "shipping_info": (
            "📦 <b>Livraison via Locker InPost</b>\n\n"
            "💰 <b>Prix :</b> 5€\n\n"
            "⏱ <b>Délais de livraison :</b>\n"
            "• 1/2 jours ouvrés au Sud\n"
            "• 2/3 jours ouvrés au Nord\n\n"
            "✅ Numéro de suivi toujours fourni !"
        ),
        "paypal_info": (
            "💸 <b>PAYPAL TRANSFER</b>\n\n"
            "• €120 = Solde 360\n"
            "• €150 = Solde 680\n"
            "• €180 = Solde 930\n"
            "• €220 = Solde 1570\n"
            "• €280 = Solde 2140\n"
            "• €320 = Solde 3400\n"
            "• €380 = Solde 4800\n"
            "• €470 = Solde 5800\n\n"
            "Pour infos et commandes contactez @GustavoEuro"
        ),
        "payments_info": (
            "💳 <b>Paiements acceptés :</b>\n\n"
            "🪙 <b>Cryptomonnaies.</b>\n"
            "🏦 <b>Virement bancaire instantané.</b>\n"
            "🎁 <b>Cartes cadeaux Amazon.</b>"
        ),
        "white_cards_info": (
            "⚠️ <b>ATTENTION</b>\n\n"
            "Quiconque vend des cartes blanches en 2026 est un arnaqueur ! "
            "Elles n'ont jamais fonctionné, c'est une invention créée en 2023. ATTENTION !"
        )
    },
    "de": {
        "disclaimer": (
            "⚠️ <b>ACHTUNG LESEN SIE DIESE NACHRICHT AUFMERKSAM!</b>\n\n"
            "Hallo, wir wurden von mehreren Kunden darauf hingewiesen, dass auf Telegram und TikTok viele Scammer unterwegs sind! "
            "Wir bitten um höchste Wachsamkeit und vor allem darum, diese Profile so oft wie möglich zu melden.\n\n"
            "Wir sind nicht zum Spielen hier.\n"
            "Wir sind nicht hier, um Probleme anzuhören.\n"
            "Wir sind nicht für Wohltätigkeit hier.\n\n"
            "Wir sind ein erfahrenes Team in dieser Branche und setzen unser volles Wissen und Vertrauen ein!\n\n"
            "Wir suchen nur Personen mit Vernunft, die ihr Leben wirklich zum Besseren wenden wollen!\n\n"
            "Seit wir in dieser Branche tätig sind, haben wir mehr als 300 Personen geholfen. "
            "Wir hatten viele Schwierigkeiten mit Sperren und Kundenproblemen, "
            "aber wir haben nie aufgegeben, denn der Erfolg ist immer in greifbarer Nähe!"
        ),
        "btn_read": "✅ GELESEN!",
        "captcha_title": "🤖 <b>SICHERHEITSABFRAGE</b>\n\nWählen Sie das Symbol für: <b>{target_name}</b>",
        "captcha_wrong": "❌ Falsch! Bitte erneut versuchen.",
        "welcome": "👋 Hallo <b>{name}</b>!\nWillkommen bei unserem offiziellen Bot.\nWählen Sie eine Option:",
        "btn_banknotes": "💵 Banknoten (10/20/50)",
        "btn_paypal": "💸 PayPal Transfer",
        "btn_shipping": "📦 Versand",
        "btn_payments": "💳 Zahlungsmethoden",
        "btn_feedback": "⭐ Bewertungen",
        "btn_white_cards": "🔴 WEISSE KARTEN",
        "btn_lang": "🌐 Sprache ändern",
        "btn_back": "🔙 Hauptmenü",
        "btn_back_banknotes": "🔙 Zurück zu Banknoten",
        "btn_video_quality": "🎥 QUALITÄTSVIDEO",
        "btn_video_paypal": "🎥 VIDEO",
        "banknotes_menu_title": "💵 <b>VERFÜGBARE BANKNOTEN</b>\n\nWählen Sie die Stückelung aus, um Preise und Videos zu sehen:",
        "banknotes_10_info": (
            "💵 <b>Preisliste 10€ Banknoten</b>\n\n"
            "• 30 Stück = 3,2 € pro Stück\n"
            "• 50 Stück = 2,8 € pro Stück\n"
            "• 75 Stück = 2,5 € pro Stück\n"
            "• 100 Stück = 2,2 € pro Stück\n"
            "• 150 Stück = 1,9 € pro Stück\n\n"
            "<b>Mindestbestellmenge 30 Stück.</b>\n"
            "<b>Gemischte Bestellungen möglich</b>"
        ),
        "banknotes_20_info": (
            "💵 <b>Preisliste 20€ Banknoten</b>\n\n"
            "• 30 Stück = 8 € pro Stück\n"
            "• 50 Stück = 7,5 € pro Stück\n"
            "• 75 Stück = 7 € pro Stück\n"
            "• 100 Stück = 6,5 € pro Stück\n"
            "• 150 Stück = 5,8 € pro Stück\n"
            "• 200 Stück = 5 € pro Stück\n\n"
            "<b>Mindestbestellmenge 30 Stück.</b>\n"
            "<b>Gemischte Bestellungen möglich</b>"
        ),
        "banknotes_50_info": (
            "💵 <b>Preisliste 50€ Banknoten</b>\n\n"
            "• 30 Stück = 12 € pro Stück\n"
            "• 50 Stück = 11 € pro Stück\n"
            "• 75 Stück = 9,5 € pro Stück\n"
            "• 100 Stück = 8,5 € pro Stück\n"
            "• 150 Stück = 7,8 € pro Stück\n"
            "• 200 Stück = 7 € pro Stück\n\n"
            "<b>Mindestbestellmenge 30 Stück.</b>\n"
            "<b>Gemischte Bestellungen möglich</b>"
        ),
        "shipping_info": (
            "📦 <b>Versand per Locker InPost</b>\n\n"
            "💰 <b>Preis:</b> 5€\n\n"
            "⏱ <b>Lieferzeiten:</b>\n"
            "• 1/2 Werktage nach Süden\n"
            "• 2/3 Werktage nach Norden\n\n"
            "✅ Sendungsverfolgungsnummer wird immer bereitgestellt!"
        ),
        "paypal_info": (
            "💸 <b>PAYPAL TRANSFER</b>\n\n"
            "• €120 = Guthaben 360\n"
            "• €150 = Guthaben 680\n"
            "• €180 = Guthaben 930\n"
            "• €220 = Guthaben 1570\n"
            "• €280 = Guthaben 2140\n"
            "• €320 = Guthaben 3400\n"
            "• €380 = Guthaben 4800\n"
            "• €470 = Guthaben 5800\n\n"
            "Für Infos und Bestellungen kontaktieren Sie @GustavoEuro"
        ),
        "payments_info": (
            "💳 <b>Akzeptierte Zahlungsmethoden:</b>\n\n"
            "🪙 <b>Kryptowährungen.</b>\n"
            "🏦 <b>Echtzeit-Banküberweisung.</b>\n"
            "🎁 <b>Amazon-Gutscheine.</b>"
        ),
        "white_cards_info": (
            "⚠️ <b>ACHTUNG</b>\n\n"
            "Jeder, der 2026 weiße Karten verkauft, ist ein Betrüger! "
            "Diese Karten haben noch nie funktioniert, eine Erfindung aus 2023. ACHTUNG!"
        )
    }
}

CAPTCHA_ITEMS = [
    {"name": {"it": "Mela", "en": "Apple", "es": "Manzana", "fr": "Pomme", "de": "Apfel"}, "emoji": "🍎"},
    {"name": {"it": "Auto", "en": "Car", "es": "Coche", "fr": "Voiture", "de": "Auto"}, "emoji": "🚗"},
    {"name": {"it": "Fulmine", "en": "Lightning", "es": "Rayo", "fr": "Éclair", "de": "Blitz"}, "emoji": "⚡"},
    {"name": {"it": "Cane", "en": "Dog", "es": "Perro", "fr": "Chien", "de": "Hund"}, "emoji": "🐶"},
    {"name": {"it": "Pizza", "en": "Pizza", "es": "Pizza", "fr": "Pizza", "de": "Pizza"}, "emoji": "🍕"},
    {"name": {"it": "Aereo", "en": "Plane", "es": "Avión", "fr": "Avion", "de": "Flugzeug"}, "emoji": "✈️"}
]

def get_user_lang(context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.user_data.get("lang", "it")

def get_disclaimer_markup(lang: str) -> InlineKeyboardMarkup:
    t = TEXTS[lang]
    keyboard = [
        [
            InlineKeyboardButton("🇮🇹 IT", callback_data="setlang_it"),
            InlineKeyboardButton("🇬🇧 EN", callback_data="setlang_en"),
            InlineKeyboardButton("🇪🇸 ES", callback_data="setlang_es"),
            InlineKeyboardButton("🇫🇷 FR", callback_data="setlang_fr"),
            InlineKeyboardButton("🇩🇪 DE", callback_data="setlang_de"),
        ],
        [InlineKeyboardButton(t["btn_read"], callback_data="action_read_disclaimer")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_main_menu_markup(context: ContextTypes.DEFAULT_TYPE) -> InlineKeyboardMarkup:
    t = TEXTS[get_user_lang(context)]
    keyboard = [
        [
            InlineKeyboardButton(t["btn_banknotes"], callback_data="menu_banknotes"),
            InlineKeyboardButton(t["btn_paypal"], callback_data="menu_paypal")
        ],
        [
            InlineKeyboardButton(t["btn_shipping"], callback_data="menu_shipping"),
            InlineKeyboardButton(t["btn_payments"], callback_data="menu_payments")
        ],
        [
            InlineKeyboardButton(t["btn_feedback"], url="https://t.me/+gBf54xWnFapjMmRh")
        ],
        [
            InlineKeyboardButton(t["btn_white_cards"], callback_data="menu_white_cards")
        ],
        [
            InlineKeyboardButton(t["btn_lang"], callback_data="menu_changelang")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

async def update_view(query, photo_path: str, caption: str, reply_markup: InlineKeyboardMarkup, context: ContextTypes.DEFAULT_TYPE):
    current_photo = context.user_data.get("current_photo", IMAGE_PATH)

    if photo_path and os.path.exists(photo_path) and photo_path != current_photo:
        try:
            with open(photo_path, "rb") as photo:
                await query.edit_message_media(
                    media=InputMediaPhoto(media=photo, caption=caption, parse_mode=ParseMode.HTML),
                    reply_markup=reply_markup
                )
            context.user_data["current_photo"] = photo_path
            return
        except Exception as e:
            logger.warning(f"edit_message_media: {e}")

    try:
        await query.edit_message_caption(
            caption=caption,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        if "Message is not modified" not in str(e):
            try:
                await query.edit_message_text(
                    text=caption,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.HTML
                )
            except Exception:
                pass

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["lang"] = context.user_data.get("lang", "it")
    context.user_data["verified"] = False
    context.user_data["current_photo"] = IMAGE_PATH

    lang = get_user_lang(context)
    caption = TEXTS[lang]["disclaimer"]
    reply_markup = get_disclaimer_markup(lang)

    chat_id = update.effective_chat.id

    if os.path.exists(IMAGE_PATH):
        with open(IMAGE_PATH, "rb") as photo:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=caption,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=caption,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )

async def present_captcha(query, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_lang(context)
    selected = random.sample(CAPTCHA_ITEMS, 4)
    target = random.choice(selected)
    context.user_data["captcha_target"] = target["emoji"]

    target_name = target["name"].get(lang, target["name"]["it"])
    caption = TEXTS[lang]["captcha_title"].format(target_name=target_name)

    buttons = [
        InlineKeyboardButton(item["emoji"], callback_data=f"captcha_{item['emoji']}")
        for item in selected
    ]
    reply_markup = InlineKeyboardMarkup([buttons])

    await update_view(query, IMAGE_PATH, caption, reply_markup, context)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_lang = get_user_lang(context)

    await query.answer()

    if data.startswith("setlang_"):
        new_lang = data.split("_")[1]
        context.user_data["lang"] = new_lang
        await update_view(query, IMAGE_PATH, TEXTS[new_lang]["disclaimer"], get_disclaimer_markup(new_lang), context)
        return

    if data == "action_read_disclaimer":
        await present_captcha(query, context)
        return

    if data.startswith("captcha_"):
        chosen = data.split("_")[1]
        target = context.user_data.get("captcha_target")

        if chosen == target:
            context.user_data["verified"] = True
            name = update.effective_user.mention_html()
            text = TEXTS[user_lang]["welcome"].format(name=name)
            await update_view(query, IMAGE_PATH, text, get_main_menu_markup(context), context)
        else:
            await query.answer(TEXTS[user_lang]["captcha_wrong"], show_alert=True)
            await present_captcha(query, context)
        return

    if not context.user_data.get("verified", False):
        await update_view(query, IMAGE_PATH, TEXTS[user_lang]["disclaimer"], get_disclaimer_markup(user_lang), context)
        return

    # Menu Principale
    if data == "menu_main":
        name = update.effective_user.mention_html()
        text = TEXTS[user_lang]["welcome"].format(name=name)
        await update_view(query, IMAGE_PATH, text, get_main_menu_markup(context), context)

    # 1. Banconote (10, 20, 50)
    elif data == "menu_banknotes":
        markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("💶 10€", callback_data="banknotes_10"),
                InlineKeyboardButton("💶 20€", callback_data="banknotes_20"),
                InlineKeyboardButton("💶 50€", callback_data="banknotes_50")
            ],
            [InlineKeyboardButton(TEXTS[user_lang]["btn_back"], callback_data="menu_main")]
        ])
        await update_view(query, IMAGE_PATH, TEXTS[user_lang]["banknotes_menu_title"], markup, context)

    elif data == "banknotes_10":
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(TEXTS[user_lang]["btn_video_quality"], url="https://t.me/m/NdLioOk3OGEx")],
            [InlineKeyboardButton(TEXTS[user_lang]["btn_back_banknotes"], callback_data="menu_banknotes")]
        ])
        await update_view(query, IMAGE_PATH, TEXTS[user_lang]["banknotes_10_info"], markup, context)

    elif data == "banknotes_20":
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(TEXTS[user_lang]["btn_video_quality"], url="https://t.me/m/SfsSoalQZDVh")],
            [InlineKeyboardButton(TEXTS[user_lang]["btn_back_banknotes"], callback_data="menu_banknotes")]
        ])
        await update_view(query, IMAGE_PATH, TEXTS[user_lang]["banknotes_20_info"], markup, context)

    elif data == "banknotes_50":
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(TEXTS[user_lang]["btn_video_quality"], url="https://t.me/m/NmVyIZ7iMmFh")],
            [InlineKeyboardButton(TEXTS[user_lang]["btn_back_banknotes"], callback_data="menu_banknotes")]
        ])
        await update_view(query, IMAGE_PATH, TEXTS[user_lang]["banknotes_50_info"], markup, context)

    # 2. PayPal Transfer
    elif data == "menu_paypal":
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(TEXTS[user_lang]["btn_video_paypal"], url="https://t.me/m/c6FVwkszYmJh")],
            [InlineKeyboardButton(TEXTS[user_lang]["btn_back"], callback_data="menu_main")]
        ])
        await update_view(query, IMAGE_PATH, TEXTS[user_lang]["paypal_info"], markup, context)

    # 3. Spedizioni (Mostra Locker InPost)
    elif data == "menu_shipping":
        markup = InlineKeyboardMarkup([[InlineKeyboardButton(TEXTS[user_lang]["btn_back"], callback_data="menu_main")]])
        await update_view(query, SHIPPING_IMAGE_PATH, TEXTS[user_lang]["shipping_info"], markup, context)

    # 4. Metodi di Pagamento
    elif data == "menu_payments":
        markup = InlineKeyboardMarkup([[InlineKeyboardButton(TEXTS[user_lang]["btn_back"], callback_data="menu_main")]])
        await update_view(query, IMAGE_PATH, TEXTS[user_lang]["payments_info"], markup, context)

    # 5. Carte Bianche (Allerta)
    elif data == "menu_white_cards":
        markup = InlineKeyboardMarkup([[InlineKeyboardButton(TEXTS[user_lang]["btn_back"], callback_data="menu_main")]])
        await update_view(query, IMAGE_PATH, TEXTS[user_lang]["white_cards_info"], markup, context)

    # 6. Cambio Lingua
    elif data == "menu_changelang":
        buttons = [
            [
                InlineKeyboardButton("🇮🇹 IT", callback_data="menulang_it"),
                InlineKeyboardButton("🇬🇧 EN", callback_data="menulang_en"),
                InlineKeyboardButton("🇪🇸 ES", callback_data="menulang_es"),
                InlineKeyboardButton("🇫🇷 FR", callback_data="menulang_fr"),
                InlineKeyboardButton("🇩🇪 DE", callback_data="menulang_de"),
            ],
            [InlineKeyboardButton(TEXTS[user_lang]["btn_back"], callback_data="menu_main")]
        ]
        await update_view(query, IMAGE_PATH, "🌐 <b>Seleziona la tua lingua / Select language:</b>", InlineKeyboardMarkup(buttons), context)

    elif data.startswith("menulang_"):
        new_lang = data.split("_")[1]
        context.user_data["lang"] = new_lang
        name = update.effective_user.mention_html()
        text = TEXTS[new_lang]["welcome"].format(name=name)
        await update_view(query, IMAGE_PATH, text, get_main_menu_markup(context), context)

def main():
    if not BOT_TOKEN:
        print("ERRORE: Inserisci il BOT_TOKEN nelle variabili d'ambiente!")
        return

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(handle_callback))

    print("🤖 Bot avviato con successo...")
    application.run_polling()

if __name__ == "__main__":
    main()
