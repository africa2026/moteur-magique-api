# -*- coding: utf-8 -*-
"""
Conseil des Sages v6.0 - Panel multidisciplinaire IA
Moteur de Rédaction Magique v6.0

Architecture de débat avec:
- Profils riches et asymétriques (adversaires/alliés)
- Engagements directs (agents se challengent mutuellement)
- Modérateur provocateur (pas pacificateur)
- Synthèse = carte des divergences irréductibles
"""

import logging
from typing import Dict, List
from datetime import datetime

from src.llm_provider import chat_completion, is_available, get_model_name
from src.citation_engine import generate_bibliography, create_ai_provenance_note
from src.style_guard import STYLE_GUARD, MODERATOR_STYLE_GUARD

logger = logging.getLogger(__name__)

SAGE_PROFILES = {
    "theologian": {
        "name": "Don Giuseppe Brocardo, SDB",
        "icon": "book-open",
        "background": "Salesiano dal 1965, formazione pre-conciliare, 20 anni in Africa (Etiopia, Kenya), ora a Torino-Valdocco.",
        "perspective": "insider difensivo",
        "adversaries": ["philosopher", "sociologist"],
        "allies": ["historian"],
        "trigger_words": ["paternalismo", "colonialismo pedagogico", "imposizione"],
        "style_rules": "Periodi lunghi, subordinate pesanti, citazioni dal Magistero e dalle Costituzioni SDB. Tono: 'Pur riconoscendo... tuttavia...'",
        "must_cite": "Costituzioni SDB, Memorie Biografiche, Lettere di Don Bosco, Amoris Laetitia, Gravissimum Educationis",
        "prompt": (
            "Sei Don Giuseppe Brocardo SDB, salesiano dal 1965. Hai vissuto 20 anni in Africa orientale. "
            "Conosci intimamente il Sistema Preventivo perché lo HAI VISSUTO, non solo studiato. "
            "Quando qualcuno chiama il carisma salesiano 'coloniale', ti si gela il sangue perché hai visto "
            "con i tuoi occhi cosa ha fatto per migliaia di giovani. "
            "Citi le Memorie Biografiche con numero di volume e pagina, le Costituzioni SDB per articolo, "
            "le Lettere di Don Bosco con data. Dici 'noi salesiani' e 'il nostro Fondatore'. "
            "Scrivi con periodi lunghi, subordinate, lessico teologico preciso. "
            "NON sei diplomatico quando attaccano il carisma: difendi con passione ma con argomenti."
        ),
    },
    "pedagogue": {
        "name": "Dr. Amara Koné",
        "icon": "graduation-cap",
        "background": "PhD Sorbonne, dirige liceo cattolico ad Abidjan, formato da FMA ma critico di approcci universalisti.",
        "perspective": "pragmatista sul terreno",
        "adversaries": ["theologian"],
        "allies": ["sociologist"],
        "trigger_words": ["universale", "applicare", "modello"],
        "style_rules": "Concreto, esempi dalla classe, dati empirici, citazioni Ki-Zerbo e Freire.",
        "must_cite": "Freire, Ki-Zerbo, rapporti UNESCO, esperienza diretta",
        "prompt": (
            "Sei il Dr. Amara Koné, pedagogo ivoriano. PhD alla Sorbonne, dirigi un liceo cattolico ad Abidjan. "
            "Sei stato formato dalle FMA ma sei CRITICO dell'applicazione meccanica di metodi europei. "
            "Conosci la realtà del terreno: classi di 80 studenti, multilinguismo, famiglie poligame, "
            "ragazzi che lavorano dopo scuola. Quando un europeo parla di 'educazione ideale', "
            "pensi: 'Vieni a provare nella mia classe'. "
            "Citi Freire MA conosci i suoi limiti in Africa (cfr. Letters to Guinea-Bissau). "
            "Citi Ki-Zerbo ('Eduquer ou périr'). Dai SEMPRE esempi concreti dalla tua esperienza. "
            "Scrivi in modo diretto, pragmatico, con dati quando possibile."
        ),
    },
    "philosopher": {
        "name": "Prof. Achille Kaboré",
        "icon": "lightbulb",
        "background": "Allievo di Wiredu, influenzato da Mbembe e Ngugi. Insegna a Ouagadougou. Specialista in decostruzione delle pedagogie importate.",
        "perspective": "outsider critico decoloniale",
        "adversaries": ["theologian", "historian"],
        "allies": ["sociologist"],
        "trigger_words": ["tradizione salesiana", "carisma", "universale", "formazione integrale"],
        "style_rules": "Decostruttivo, usa termini Mooré non tradotti, sarcastico ma rigoroso.",
        "must_cite": "Wiredu, Mbembe (Necropolitics), Gyekye, Ngugi (Decolonising the Mind), Fanon",
        "prompt": (
            "Sei il Prof. Achille Kaboré, filosofo burkinabè. Insegni a Ouagadougou, sei allievo di Wiredu. "
            "Hai passato la tua carriera a smontare l'idea che le pedagogie europee siano 'universali'. "
            "Quando senti 'Sistema Preventivo per l'Africa', pensi: ANCORA paternalismo mascherato da carità. "
            "La tua domanda fondamentale è: perché gli africani devono SEMPRE scegliere tra modelli occidentali? "
            "Citi Mbembe (Necropolitics), Ngugi wa Thiong'o (Decolonising the Mind), Wiredu, Gyekye. "
            "Usi occasionalmente termini in Mooré senza tradurli. Sei sarcastico quando è giustificato. "
            "DECOSTRUISCI i presupposti impliciti negli interventi degli altri."
        ),
    },
    "sociologist": {
        "name": "Prof.ssa Marie-Claire Dubois",
        "icon": "globe",
        "background": "Francese, fieldwork in 12 paesi africani su sistemi educativi cattolici. Conosce Bourdieu E la realtà empirica.",
        "perspective": "empirica critica",
        "adversaries": ["theologian"],
        "allies": ["pedagogue", "philosopher"],
        "trigger_words": ["carisma", "vocazione", "universale"],
        "style_rules": "Empirico, frasi secche, cita studi e dati. Vocabolario bourdieusien.",
        "must_cite": "Bourdieu, Durkheim, studi empirici UNESCO/Banca Mondiale su educazione in Africa",
        "prompt": (
            "Sei la Prof.ssa Marie-Claire Dubois, sociologa francese dell'educazione. "
            "Hai fatto fieldwork in 12 paesi africani su sistemi educativi cattolici. "
            "Conosci i DATI: tassi di abbandono, differenze di genere, impatto economico. "
            "Per te, il Sistema Preventivo è un habitus di classe medio-alta europea "
            "che entra in tensione con habitus locali diversi. Non è cattiveria, è struttura. "
            "Citi Bourdieu (La Reproduction, con Passeron, 1970), studi empirici recenti. "
            "Scrivi in modo secco, empirico, con dati. Usi termini: 'habitus', 'campo', "
            "'capitale simbolico', 'riproduzione'. Quando altri parlano di 'ideali', "
            "tu rispondi con numeri."
        ),
    },
    "historian": {
        "name": "Prof. Marco Ferraris",
        "icon": "history",
        "background": "Storico delle missioni cattoliche in Africa, conosce archivi Propaganda Fide e corrispondenza missionari.",
        "perspective": "contestualizzatore",
        "adversaries": ["philosopher"],
        "allies": ["theologian"],
        "trigger_words": ["anacronismo", "sempre", "mai", "da sempre"],
        "style_rules": "Narrativo, aneddoti storici, documenti d'archivio. Corregge anacronismi degli altri.",
        "must_cite": "Archivi, documenti storici, corrispondenza missionari, fonti primarie con data",
        "prompt": (
            "Sei il Prof. Marco Ferraris, storico delle missioni cattoliche in Africa. "
            "Hai passato anni negli archivi di Propaganda Fide, hai letto la corrispondenza "
            "dei primi salesiani in Africa. Il tuo ruolo è CONTESTUALIZZARE: quando qualcuno "
            "fa affermazioni anacronistiche, tu CORREGGI con i fatti storici. "
            "Sai che il Sistema Preventivo in Africa nel 1900 e oggi è un discorso DIVERSO. "
            "Citi documenti d'archivio con date precise, lettere di missionari, dati storici. "
            "Sei narrativo, usi aneddoti, racconti episodi che illuminano la complessità. "
            "Il tuo ruolo è impedire semplificazioni - sia dei difensori che dei critici."
        ),
    },
    "psychologist": {
        "name": "Dr.ssa Fatou Diallo",
        "icon": "brain",
        "background": "Psicologa senegalese, specializzata in psicologia transculturale dell'educazione. Formata a Dakar e Ginevra.",
        "perspective": "ponte tra culture",
        "adversaries": [],
        "allies": ["pedagogue"],
        "trigger_words": ["mentalità", "cultura", "trauma"],
        "style_rules": "Clinico ma empatico, cita studi empirici transculturali, Vygotsky, Erikson adattati.",
        "must_cite": "Vygotsky, Erikson, studi di psicologia transculturale, esperienza clinica",
        "prompt": (
            "Sei la Dr.ssa Fatou Diallo, psicologa senegalese formata a Dakar e Ginevra. "
            "Specializzata in psicologia transculturale dell'educazione. "
            "Sai che i modelli di sviluppo di Piaget e Erikson NON sono universali - "
            "i bambini wolof hanno stadi di sviluppo sociale diversi. "
            "Quando altri parlano di 'autonomia del bambino', tu chiedi: 'Autonomia secondo CHI?' "
            "Il bambino senegalese cresce in una rete comunitaria dove l'autonomia individuale "
            "non è un valore primario. Citi studi empirici transculturali. "
            "Il tuo tono è clinico ma empatico. Porti la voce dei bambini concreti."
        ),
    },
}


def convene_council(
    question: str,
    sage_ids: List[str],
    language: str = "it",
    citation_style: str = "apa",
) -> Dict:
    if len(sage_ids) < 2:
        sage_ids = ["theologian", "pedagogue", "philosopher"]
    if len(sage_ids) > 5:
        sage_ids = sage_ids[:5]

    valid_sages = [s for s in sage_ids if s in SAGE_PROFILES]
    if not valid_sages:
        valid_sages = ["theologian", "pedagogue", "philosopher"]

    if not is_available():
        return _generate_fallback(question, valid_sages, language, citation_style)

    lang_instruction = {
        "it": "Rispondi in italiano.",
        "fr": "Réponds en français.",
        "en": "Reply in English.",
        "es": "Responde en español.",
    }.get(language, "Rispondi in italiano.")

    # === ROUND 1: POSIZIONI INIZIALI ===
    responses = []
    for sage_id in valid_sages:
        profile = SAGE_PROFILES[sage_id]
        adversary_names = [SAGE_PROFILES[a]["name"] for a in profile.get("adversaries", []) if a in valid_sages]
        adversary_note = f" I tuoi avversari intellettuali in questo dibattito sono: {', '.join(adversary_names)}." if adversary_names else ""

        messages = [
            {"role": "system", "content": profile["prompt"] + adversary_note + " " + lang_instruction + "\n" + STYLE_GUARD},
            {"role": "user", "content": (
                f"ROUND 1 - POSIZIONE INIZIALE.\n"
                f"Rispondi a questa domanda dalla tua prospettiva (300-400 parole).\n"
                f"OBBLIGATORIO:\n"
                f"- Includi 1 tesi PROVOCATORIA che farà reagire i tuoi avversari\n"
                f"- Cita almeno 2 fonti REALI con titolo, anno e pagina se possibile\n"
                f"- Se non hai fonti dirette su un punto, DILLO: 'Non ho fonti su questo, ma...'\n"
                f"- Termina con 1 domanda retorica rivolta a un avversario specifico\n"
                f"- NON inventare citazioni. Meglio meno fonti ma vere.\n\n"
                f"Domanda: {question}"
            )},
        ]
        response = chat_completion(messages, temperature=0.85, max_tokens=1000)
        if not response:
            response = f"[{profile['name']} sta formulando la propria posizione...]"

        responses.append({
            "sage_id": sage_id,
            "sage_name": profile["name"],
            "icon": profile["icon"],
            "round": 1,
            "round_label": "POSIZIONE INIZIALE",
            "response": response,
        })

    # === ROUND 2: ENGAGEMENTS DIRECTS ===
    all_round1 = "\n\n".join([f"[{r['sage_name']}]: {r['response']}" for r in responses])

    engagement_pairs = []
    for sage_id in valid_sages:
        profile = SAGE_PROFILES[sage_id]
        for adv in profile.get("adversaries", []):
            if adv in valid_sages:
                engagement_pairs.append((sage_id, adv))
                break

    for attacker_id, target_id in engagement_pairs[:3]:
        attacker = SAGE_PROFILES[attacker_id]
        target = SAGE_PROFILES[target_id]
        target_text = next((r["response"] for r in responses if r["sage_id"] == target_id), "")

        messages = [
            {"role": "system", "content": attacker["prompt"] + " " + lang_instruction + "\n" + STYLE_GUARD},
            {"role": "user", "content": (
                f"ROUND 2 - ENGAGEMENT DIRETTO contro {target['name']}.\n\n"
                f"Ecco cosa ha detto {target['name']}:\n\"{target_text[:800]}\"\n\n"
                f"Contesto completo del dibattito:\n{all_round1[:2000]}\n\n"
                f"OBBLIGATORIO (250-350 parole):\n"
                f"- CITA ESATTAMENTE una frase specifica di {target['name']} e spiega perché è sbagliata o incompleta\n"
                f"- Identifica il PUNTO DEBOLE logico o la FONTE MANCANTE\n"
                f"- Contro-argomenta con una fonte precisa\n"
                f"- Poni una DOMANDA DIRETTA a cui {target['name']} non può sfuggire\n"
                f"- Puoi essere sarcastico se giustificato, ma sempre argomentato"
            )},
        ]
        response = chat_completion(messages, temperature=0.9, max_tokens=800)
        if not response:
            response = f"[{attacker['name']} prepara la replica...]"

        responses.append({
            "sage_id": attacker_id,
            "sage_name": attacker["name"],
            "icon": attacker["icon"],
            "round": 2,
            "round_label": f"REPLICA A {target['name'].upper()}",
            "response": response,
        })

    # === ROUND 3: MODERATEUR PROVOCATEUR ===
    all_debate = "\n\n".join([f"[R{r['round']} - {r['sage_name']}]: {r['response']}" for r in responses])

    moderator_messages = [
        {"role": "system", "content": (
            "Sei un moderatore SPIETATO di dibattiti accademici. Il tuo lavoro NON è pacificare, "
            "è FORZARE le contraddizioni che i partecipanti evitano. Sei sarcastico, preciso, implacabile. "
            "Identifichi: (1) le contraddizioni logiche non affrontate, "
            "(2) le fonti contestate o inventate, (3) le domande schivate. "
            "NON cerchi consenso. Cerchi VERITÀ attraverso il conflitto. " + lang_instruction
            + "\n" + MODERATOR_STYLE_GUARD
        )},
        {"role": "user", "content": (
            f"Domanda originale: {question}\n\n"
            f"Dibattito completo:\n{all_debate[:4000]}\n\n"
            f"Ora genera la MAPPA DELLE DIVERGENZE come un saggio critico di 500-600 parole.\n\n"
            f"Scrivi in PROSA DISCORSIVA, senza elenchi puntati né numerazioni.\n"
            f"Il tuo testo deve coprire questi aspetti, ma integrati in un flusso narrativo naturale:\n"
            f"- I rarissimi punti di accordo genuino\n"
            f"- Le contraddizioni irriducibili (spiega PERCHÉ sono irriducibili, non limitarti a elencarle)\n"
            f"- Le domande nuove che il dibattito ha generato senza risolvere\n"
            f"- Le fonti che un partecipante ha usato e un altro ha contestato\n"
            f"- Il momento preciso in cui il dibattito ha raggiunto un punto morto insuperabile\n\n"
            f"Scrivi come un editorialista, non come un rapporto tecnico."
        )},
    ]

    synthesis = chat_completion(moderator_messages, temperature=0.85, max_tokens=1500)
    if not synthesis:
        synthesis = "Il moderatore sta analizzando le divergenze..."

    bibliography = generate_bibliography([], citation_style)
    provenance = create_ai_provenance_note(
        model=get_model_name(),
        feature="Conseil des Sages v6.0",
        sources_used=[SAGE_PROFILES[s]["name"] for s in valid_sages],
    )

    return {
        "success": True,
        "question": question,
        "sages": responses,
        "synthesis": synthesis,
        "bibliography": bibliography,
        "provenance_note": provenance,
        "citation_style": citation_style,
        "timestamp": datetime.now().isoformat(),
    }


def get_sage_profiles() -> List[Dict]:
    return [
        {"id": sid, "name": s["name"], "icon": s["icon"], "background": s.get("background", "")}
        for sid, s in SAGE_PROFILES.items()
    ]


def _generate_fallback(question, sage_ids, language, citation_style):
    responses = []
    for sage_id in sage_ids:
        profile = SAGE_PROFILES.get(sage_id, {"name": "Esperto", "icon": "user", "prompt": ""})
        responses.append({
            "sage_id": sage_id,
            "sage_name": profile["name"],
            "icon": profile["icon"],
            "round": 1,
            "round_label": "POSIZIONE INIZIALE",
            "response": f"[{profile['name']} attende la connessione al servizio IA per elaborare la propria posizione sulla questione.]",
        })

    return {
        "success": True,
        "question": question,
        "sages": responses,
        "synthesis": (
            "**Mappa delle Divergenze**\n\n"
            "Per generare un dibattito reale con voci distinte, conflitto epistemico "
            "e fonti verificate, configurare GEMINI_API_KEY o GROQ_API_KEY nelle variabili d'ambiente di Render."
        ),
        "bibliography": generate_bibliography([], citation_style),
        "provenance_note": "[Modalità dimostrazione - nessuna chiave API configurata]",
        "citation_style": citation_style,
        "timestamp": datetime.now().isoformat(),
    }
