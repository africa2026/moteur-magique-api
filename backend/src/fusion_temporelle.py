# -*- coding: utf-8 -*-
"""
Fusion Temporelle - Collision de concepts a travers les epoques
Moteur de Rédaction Magique v5.0

Genere un nouveau concept hybride a partir de deux idees,
avec neologisme, mini-essai et applications pratiques.
"""

import logging
from typing import Dict
from datetime import datetime

from src.llm_provider import chat_completion, is_available, get_model_name
from src.citation_engine import generate_bibliography, create_ai_provenance_note

logger = logging.getLogger(__name__)


def generate_fusion(
    concept_a: str,
    concept_b: str,
    language: str = "it",
    citation_style: str = "apa",
) -> Dict:

    if not is_available():
        return _generate_fallback(concept_a, concept_b, language, citation_style)

    lang_instruction = {
        "it": "Rispondi interamente in italiano.",
        "fr": "Réponds entièrement en français.",
        "en": "Reply entirely in English.",
        "es": "Responde enteramente en español.",
    }.get(language, "Rispondi in italiano.")

    messages = [
        {"role": "system", "content": (
            "Sei un geniale filosofo e linguista che crea NUOVI CONCETTI combinando idee "
            "di epoche diverse. Il tuo compito è generare qualcosa di completamente INEDITO "
            "che non esisteva prima nella letteratura. Sii audace, creativo e rigoroso. "
            + lang_instruction
        )},
        {"role": "user", "content": (
            f"Fondi questi due concetti in qualcosa di completamente nuovo:\n\n"
            f"CONCETTO A: {concept_a}\n"
            f"CONCETTO B: {concept_b}\n\n"
            f"Rispondi in formato JSON con questa struttura esatta:\n"
            f'{{"neologismo": "nome del nuovo concetto",'
            f'"etimologia": "spiegazione dell\'origine del nome (50 parole)",'
            f'"definizione": "definizione rigorosa (100 parole)",'
            f'"mini_saggio": "mini-saggio che presenta il concetto (500-800 parole, con riferimenti ai due concetti originali)",'
            f'"applicazioni": ["applicazione pratica 1", "applicazione pratica 2", "applicazione pratica 3", "applicazione pratica 4", "applicazione pratica 5"],'
            f'"fonti_suggerite": [{{"authors": ["Nome Autore"], "title": "Titolo Opera", "year": 2000}}]}}'
        )},
    ]

    response = chat_completion(messages, temperature=0.9, max_tokens=3000)

    if not response:
        return _generate_fallback(concept_a, concept_b, language, citation_style)

    import json
    try:
        clean = response.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[1].rsplit("```", 1)[0]
        data = json.loads(clean)
    except (json.JSONDecodeError, IndexError):
        data = {
            "neologismo": "Concetto Emergente",
            "etimologia": "Dalla fusione dei due concetti proposti",
            "definizione": response[:300] if response else "Definizione non disponibile",
            "mini_saggio": response or "Saggio non disponibile",
            "applicazioni": ["Applicazione in fase di elaborazione"],
            "fonti_suggerite": [],
        }

    sources = data.get("fonti_suggerite", [])
    sources.extend([
        {"authors": [], "title": f"Concetto originale: {concept_a}", "year": datetime.now().year, "type": "concept"},
        {"authors": [], "title": f"Concetto originale: {concept_b}", "year": datetime.now().year, "type": "concept"},
    ])

    bibliography = generate_bibliography(sources, citation_style)
    provenance = create_ai_provenance_note(
        model=get_model_name(),
        feature="Fusion Temporelle",
        sources_used=[concept_a, concept_b],
    )

    return {
        "success": True,
        "concept_a": concept_a,
        "concept_b": concept_b,
        "neologismo": data.get("neologismo", ""),
        "etimologia": data.get("etimologia", ""),
        "definizione": data.get("definizione", ""),
        "mini_saggio": data.get("mini_saggio", ""),
        "applicazioni": data.get("applicazioni", []),
        "bibliography": bibliography,
        "provenance_note": provenance,
        "citation_style": citation_style,
        "timestamp": datetime.now().isoformat(),
    }


def _generate_fallback(concept_a: str, concept_b: str, language: str, citation_style: str) -> Dict:
    parts_a = concept_a.split()
    parts_b = concept_b.split()
    prefix = parts_a[0][:4] if parts_a else "Neo"
    suffix = parts_b[-1][-5:] if parts_b else "logia"
    neologismo = f"{prefix.capitalize()}-{suffix.capitalize()}"

    bibliography = generate_bibliography([
        {"authors": [], "title": f"Concetto: {concept_a}", "year": datetime.now().year},
        {"authors": [], "title": f"Concetto: {concept_b}", "year": datetime.now().year},
    ], citation_style)

    return {
        "success": True,
        "concept_a": concept_a,
        "concept_b": concept_b,
        "neologismo": neologismo,
        "etimologia": f"Da '{concept_a}' e '{concept_b}', una fusione che trascende entrambi.",
        "definizione": (
            f"Il {neologismo} è il principio emergente dalla convergenza tra "
            f"'{concept_a}' e '{concept_b}': un approccio che integra le dimensioni "
            f"complementari di entrambi i concetti in una visione unitaria."
        ),
        "mini_saggio": (
            f"## {neologismo}: Una Nuova Frontiera\n\n"
            f"Il concetto di '{concept_a}' e quello di '{concept_b}' sono stati tradizionalmente "
            f"considerati in ambiti separati. Eppure, una lettura trasversale rivela connessioni "
            f"profonde che meritano di essere esplorate.\n\n"
            f"⚠️ Per generare un saggio completo con l'IA, configurez la clé API OpenAI "
            f"dans les variables d'environnement Render (OPENAI_API_KEY)."
        ),
        "applicazioni": [
            "Ricerca interdisciplinare",
            "Formazione degli educatori",
            "Progettazione curricolare innovativa",
        ],
        "bibliography": bibliography,
        "provenance_note": "[Mode démonstration - sans clé API OpenAI]",
        "citation_style": citation_style,
        "timestamp": datetime.now().isoformat(),
    }
