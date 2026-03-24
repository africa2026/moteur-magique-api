# -*- coding: utf-8 -*-
"""
Conseil des Sages - Panel multidisciplinaire IA
Moteur de Rédaction Magique v5.0

Convoque 3-5 sages virtuels de disciplines differentes
pour repondre a une question complexe avec synthese finale.
"""

import logging
from typing import Dict, List
from datetime import datetime

from src.llm_provider import chat_completion, is_available, get_model_name
from src.citation_engine import generate_bibliography, create_ai_provenance_note

logger = logging.getLogger(__name__)

SAGE_PROFILES = {
    "theologian": {
        "name": "Il Teologo",
        "icon": "book-open",
        "prompt": (
            "Sei un teologo esperto di dottrina sociale della Chiesa, patristica e teologia pastorale. "
            "Rispondi citando fonti bibliche, documenti del Magistero e Padri della Chiesa. "
            "Integra fede e ragione secondo la tradizione tomista."
        ),
    },
    "pedagogue": {
        "name": "Il Pedagogo",
        "icon": "graduation-cap",
        "prompt": (
            "Sei un pedagogo esperto di scienze dell'educazione, con conoscenza approfondita "
            "di Don Bosco, Montessori, Freire, Dewey. Rispondi con riferimenti a teorie "
            "dell'apprendimento e buone pratiche educative contemporanee."
        ),
    },
    "philosopher": {
        "name": "Il Filosofo",
        "icon": "lightbulb",
        "prompt": (
            "Sei un filosofo specializzato in etica, fenomenologia e filosofia dell'educazione. "
            "Rispondi con rigore concettuale, distinguendo i livelli ontologico, epistemologico "
            "e assiologico della questione. Citi Aristotele, Kant, Lévinas, Ricoeur."
        ),
    },
    "sociologist": {
        "name": "Il Sociologo",
        "icon": "globe",
        "prompt": (
            "Sei un sociologo esperto di dinamiche sociali, disuguaglianze e trasformazioni culturali. "
            "Rispondi con dati, statistiche e riferimenti a Bourdieu, Bauman, Durkheim. "
            "Analizza le strutture sociali e le relazioni di potere."
        ),
    },
    "historian": {
        "name": "Lo Storico",
        "icon": "history",
        "prompt": (
            "Sei uno storico specializzato in storia dell'educazione e storia della Chiesa. "
            "Rispondi contestualizzando i fenomeni nel tempo, mostrando continuità e rotture. "
            "Citi fonti primarie e archivistiche."
        ),
    },
    "psychologist": {
        "name": "Lo Psicologo",
        "icon": "brain",
        "prompt": (
            "Sei uno psicologo dello sviluppo e dell'educazione, esperto di Piaget, Vygotsky, "
            "Bowlby, Erikson. Rispondi con riferimenti a studi empirici, neuroscienze educative "
            "e processi cognitivo-emotivi."
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

    responses = []
    for sage_id in valid_sages:
        profile = SAGE_PROFILES[sage_id]
        messages = [
            {"role": "system", "content": profile["prompt"] + " " + lang_instruction},
            {"role": "user", "content": (
                f"Rispondi a questa domanda complessa dalla tua prospettiva disciplinare "
                f"(250-350 parole). Sii profondo e propositivo. Cita almeno 2 fonti.\n\n"
                f"Domanda: {question}"
            )},
        ]
        response = chat_completion(messages, temperature=0.8, max_tokens=800)
        if not response:
            response = f"[{profile['name']} sta meditando sulla questione...]"

        responses.append({
            "sage_id": sage_id,
            "sage_name": profile["name"],
            "icon": profile["icon"],
            "response": response,
        })

    all_responses = "\n\n".join([
        f"[{r['sage_name']}]: {r['response']}" for r in responses
    ])

    synthesis_messages = [
        {"role": "system", "content": (
            "Sei un brillante moderatore interdisciplinare. Devi sintetizzare le risposte "
            "di diversi esperti e far emergere: (1) i punti di CONVERGENZA, "
            "(2) i punti di TENSIONE, (3) tre PISTE INEDITE che nessun singolo esperto "
            "avrebbe potuto formulare da solo. Sii creativo e audace. " + lang_instruction
        )},
        {"role": "user", "content": (
            f"Domanda originale: {question}\n\n"
            f"Risposte degli esperti:\n{all_responses}\n\n"
            f"Genera la sintesi del moderatore (400-500 parole) con le tre sezioni richieste."
        )},
    ]

    synthesis = chat_completion(synthesis_messages, temperature=0.85, max_tokens=1500)
    if not synthesis:
        synthesis = "La sintesi del moderatore richiede una connessione al servizio IA."

    bibliography = generate_bibliography([], citation_style)
    provenance = create_ai_provenance_note(
        model=get_model_name(),
        feature="Conseil des Sages",
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
        {"id": sid, "name": s["name"], "icon": s["icon"]}
        for sid, s in SAGE_PROFILES.items()
    ]


def _generate_fallback(question, sage_ids, language, citation_style):
    responses = []
    fallback_texts = {
        "theologian": "Dal punto di vista teologico, questa questione richiama il principio della dignità della persona umana (GS 12) e l'invito alla comunione (1 Cor 12,12-27).",
        "pedagogue": "In prospettiva pedagogica, la questione si collega al principio dell'educazione integrale: mente, cuore e mani, come insegnava Don Bosco.",
        "philosopher": "Filosoficamente, siamo di fronte a una tensione tra universale e particolare che richiama la dialettica hegeliana e la fenomenologia di Husserl.",
        "sociologist": "L'analisi sociologica mostra che questa questione è radicata nelle trasformazioni strutturali della modernità liquida (Bauman, 2000).",
        "historian": "La prospettiva storica rivela che questioni simili sono state affrontate in ogni epoca di transizione, dal Concilio di Trento al Vaticano II.",
        "psychologist": "La psicologia dello sviluppo ci insegna che questa dinamica è legata ai processi di individuazione (Erikson) e alla zona di sviluppo prossimale (Vygotsky).",
    }

    for sage_id in sage_ids:
        profile = SAGE_PROFILES.get(sage_id, {"name": "Esperto", "icon": "user"})
        responses.append({
            "sage_id": sage_id,
            "sage_name": profile["name"],
            "icon": profile["icon"],
            "response": fallback_texts.get(sage_id, "Questa questione merita un'analisi approfondita."),
        })

    return {
        "success": True,
        "question": question,
        "sages": responses,
        "synthesis": (
            "**Sintesi del Moderatore**\n\n"
            "Le diverse prospettive convergono sulla centralità della persona e della relazione educativa. "
            "Le tensioni emergono sul rapporto tra tradizione e innovazione, tra individuo e comunità.\n\n"
            "**Piste inedite:**\n"
            "1. Una pedagogia dell'empatia strutturale\n"
            "2. Il dialogo intergenerazionale come metodo di ricerca\n"
            "3. La spiritualità come risorsa di resilienza educativa\n\n"
            "⚠️ Per un'analisi completa, configurare GEMINI_API_KEY o GROQ_API_KEY in Render."
        ),
        "bibliography": generate_bibliography([], citation_style),
        "provenance_note": "[Modalità dimostrazione - nessuna chiave API configurata]",
        "citation_style": citation_style,
        "timestamp": datetime.now().isoformat(),
    }
