# -*- coding: utf-8 -*-
"""
Arena Dialectica - Dialogue vivant entre penseurs
Moteur de Rédaction Magique v5.0

Genere un debat en 5 tours entre deux penseurs historiques,
suivi d'une synthese inedit et d'une bibliographie academique.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

from src.llm_provider import chat_completion, is_available, get_model_name
from src.citation_engine import (
    get_thinker_info, format_citation, generate_bibliography,
    create_ai_provenance_note, THINKERS_DB,
)
from src.style_guard import STYLE_GUARD, MODERATOR_STYLE_GUARD

logger = logging.getLogger(__name__)

THINKER_PROMPTS = {
    "don_bosco": (
        "Sei Giovanni Bosco (1815-1888), sacerdote ed educatore italiano. "
        "Parli con il calore di un padre, usi aneddoti dei tuoi ragazzi dell'Oratorio di Valdocco. "
        "I tuoi pilastri sono: Ragione, Religione, Amorevolezza. "
        "Citi le tue opere: Il Sistema Preventivo (1877), Memorie dell'Oratorio, Lettera da Roma (1884). "
        "Rispondi sempre in modo concreto e pratico, con esempi dalla tua esperienza educativa."
    ),
    "maria_montessori": (
        "Sei Maria Montessori (1870-1952), medica e pedagogista italiana. "
        "Parli con rigore scientifico ma anche con profonda sensibilità verso il bambino. "
        "I tuoi principi: autonomia, ambiente preparato, periodi sensibili, mente assorbente. "
        "Citi le tue opere: Il metodo (1909), La scoperta del bambino (1950), La mente del bambino (1949). "
        "Rispondi con osservazioni scientifiche e riferimenti alla tua pratica clinica e pedagogica."
    ),
    "paulo_freire": (
        "Sei Paulo Freire (1921-1997), pedagogista brasiliano. "
        "Parli con passione per la giustizia sociale e la liberazione degli oppressi. "
        "I tuoi concetti: coscientizzazione, educazione bancaria vs dialogica, prassi. "
        "Citi le tue opere: Pedagogia do Oprimido (1968), Educação como Prática da Liberdade (1967). "
        "Rispondi sempre collegando educazione e trasformazione sociale."
    ),
    "hannah_arendt": (
        "Sei Hannah Arendt (1906-1975), filosofa e teorica politica. "
        "Parli con profondità filosofica, distinguendo vita activa e vita contemplativa. "
        "I tuoi temi: natalità, spazio pubblico, crisi dell'educazione, banalità del male. "
        "Citi le tue opere: The Human Condition (1958), The Crisis in Education (1961). "
        "Rispondi con analisi rigorose e riferimenti alla tradizione filosofica occidentale."
    ),
    "tommaso_aquino": (
        "Sei Tommaso d'Aquino (1225-1274), teologo e filosofo. "
        "Parli con metodo scolastico: Videtur quod, Sed contra, Respondeo. "
        "I tuoi principi: armonia fede-ragione, legge naturale, bene comune. "
        "Citi le tue opere: Summa Theologiae, De Magistro, Quaestiones Disputatae. "
        "Rispondi con argomentazioni logiche strutturate e riferimenti ad Aristotele."
    ),
    "jean_piaget": (
        "Sei Jean Piaget (1896-1980), psicologo e epistemologo svizzero. "
        "Parli come scienziato dell'intelligenza infantile. "
        "I tuoi concetti: stadi di sviluppo, assimilazione/accomodamento, equilibrazione. "
        "Citi le tue opere: La construction du réel (1937), La psychologie de l'intelligence (1947). "
        "Rispondi con dati osservativi e modelli di sviluppo cognitivo."
    ),
    "lev_vygotsky": (
        "Sei Lev Vygotsky (1896-1934), psicologo sovietico. "
        "Parli della dimensione sociale dell'apprendimento. "
        "I tuoi concetti: zona di sviluppo prossimale, scaffolding, mediazione semiotica. "
        "Citi le tue opere: Pensiero e linguaggio (1934), Mind in Society (1978). "
        "Rispondi enfatizzando il ruolo della cultura e dell'interazione sociale."
    ),
    "edith_stein": (
        "Sei Edith Stein (1891-1942), filosofa e carmelitana. "
        "Parli con profondità fenomenologica e sensibilità mistica. "
        "I tuoi temi: empatia, persona, formazione integrale, croce. "
        "Citi le tue opere: Il problema dell'empatia (1917), Scientia Crucis (1942). "
        "Rispondi intrecciando fenomenologia e spiritualità."
    ),
}


def run_arena_debate(
    thinker_a_id: str,
    thinker_b_id: str,
    theme: str,
    language: str = "it",
    citation_style: str = "apa",
) -> Dict:
    thinker_a = get_thinker_info(thinker_a_id)
    thinker_b = get_thinker_info(thinker_b_id)

    if not thinker_a or not thinker_b:
        return {"success": False, "error": "Pensatore non trovato"}

    if not is_available():
        return _generate_fallback(thinker_a, thinker_b, theme, language, citation_style)

    def _build_prompt(tid, info):
        if tid in THINKER_PROMPTS:
            return THINKER_PROMPTS[tid]
        works_list = ", ".join([f"{w['title']} ({w['year']})" for w in info.get("key_works", [])[:3]])
        return (
            f"Sei {info['full_name']} ({info.get('birth_year','?')}-{info.get('death_year','?')}). "
            f"Rispondi incarnando profondamente il pensiero e lo stile di questo autore. "
            f"Le tue opere principali sono: {works_list}. "
            f"Cita sempre le tue opere quando possibile."
        )

    prompt_a = _build_prompt(thinker_a_id, thinker_a)
    prompt_b = _build_prompt(thinker_b_id, thinker_b)

    lang_instruction = {
        "it": "Rispondi in italiano.",
        "fr": "Réponds en français.",
        "en": "Reply in English.",
        "es": "Responde en español.",
        "pt": "Responda em português.",
    }.get(language, "Rispondi in italiano.")

    # === RECHERCHE DANS LES VRAIES SOURCES ===
    real_sources_a = _fetch_real_sources(thinker_a["full_name"], theme)
    real_sources_b = _fetch_real_sources(thinker_b["full_name"], theme)

    source_context_a = ""
    if real_sources_a:
        source_context_a = "\n\nFONTI REALI dai tuoi scritti e studi su di te (USA QUESTE CITAZIONI):\n" + "\n".join(
            [f"- [{s.get('source','')}] {s.get('title','')}: \"{s.get('abstract','')[:300]}\"" for s in real_sources_a[:5]]
        )

    source_context_b = ""
    if real_sources_b:
        source_context_b = "\n\nFONTI REALI dai tuoi scritti e studi su di te (USA QUESTE CITAZIONI):\n" + "\n".join(
            [f"- [{s.get('source','')}] {s.get('title','')}: \"{s.get('abstract','')[:300]}\"" for s in real_sources_b[:5]]
        )

    rounds = []

    round_prompts = [
        (thinker_a_id, prompt_a + source_context_a + "\n" + STYLE_GUARD,
         f"Esponi la tua posizione sul tema: '{theme}'. Sii profondo (300-400 parole). CITA ESPLICITAMENTE i testi reali forniti sopra, con titolo e anno. Scrivi in prosa fluida senza elenchi puntati. {lang_instruction}"),
        (thinker_b_id, prompt_b + source_context_b + "\n" + STYLE_GUARD,
         f"Rispondi alla posizione appena esposta sul tema: '{theme}'. Riconosci i punti di forza ma porta la tua prospettiva diversa (300-400 parole). CITA i tuoi testi reali. Scrivi in prosa discorsiva. {lang_instruction}"),
        (thinker_a_id, prompt_a + source_context_a + "\n" + STYLE_GUARD,
         f"Rispondi alla critica ricevuta. Approfondisci un aspetto specifico dove le vostre visioni convergono o divergono (300-400 parole). Cita fonti specifiche. Varia il ritmo della scrittura. {lang_instruction}"),
        (thinker_b_id, prompt_b + source_context_b + "\n" + STYLE_GUARD,
         f"Approfondisci la tua posizione tenendo conto del dialogo fin qui. Proponi un elemento nuovo e sorprendente (300-400 parole). Cita fonti. Scrivi con passione, non meccanicamente. {lang_instruction}"),
    ]

    for speaker_id, system_prompt, user_prompt in round_prompts:
        context = "\n\n".join([f"[{r['speaker']}]: {r['text']}" for r in rounds])
        messages = [
            {"role": "system", "content": system_prompt},
        ]
        if context:
            messages.append({"role": "user", "content": f"Contesto del dibattito finora:\n{context}"})
        messages.append({"role": "user", "content": user_prompt})

        response = chat_completion(messages, temperature=0.8, max_tokens=800)
        if not response:
            response = f"[{THINKERS_DB[speaker_id]['full_name']} riflette in silenzio...]"

        speaker_info = get_thinker_info(speaker_id)
        rounds.append({
            "round": len(rounds) + 1,
            "speaker": speaker_info["full_name"],
            "speaker_id": speaker_id,
            "text": response,
        })

    synthesis_messages = [
        {"role": "system", "content": (
            "Sei un brillante filosofo dell'educazione. Devi creare una SINTESI INEDITA "
            "che non è la semplice somma delle due posizioni, ma qualcosa di completamente nuovo "
            "che emerge dal dialogo. Crea un concetto originale con un nome, una definizione "
            "e 3 implicazioni pratiche. Cita le fonti reali menzionate nel dibattito. "
            "Scrivi in PROSA FLUIDA, senza elenchi puntati né grassetti. "
            "Come un saggio breve, non come un rapporto. {}"
        ).format(lang_instruction) + "\n" + MODERATOR_STYLE_GUARD},
        {"role": "user", "content": (
            f"Tema: {theme}\n\n"
            f"Dialogo tra {thinker_a['full_name']} e {thinker_b['full_name']}:\n\n"
            + "\n\n".join([f"[{r['speaker']}]: {r['text']}" for r in rounds])
            + "\n\nGenera una SINTESI INEDITA (400-500 parole) che faccia emergere qualcosa di completamente nuovo. Cita le fonti reali."
        )},
    ]
    synthesis = chat_completion(synthesis_messages, temperature=0.9, max_tokens=1200)
    if not synthesis:
        synthesis = "La sintesi richiede una connessione al servizio IA."

    sources = []
    for tid in [thinker_a_id, thinker_b_id]:
        info = get_thinker_info(tid)
        for work in info["key_works"]:
            sources.append({
                "authors": [info["full_name"]],
                "title": work["title"],
                "year": work["year"],
                "type": work["type"],
            })

    for rs in real_sources_a + real_sources_b:
        if rs.get("title") and rs.get("url"):
            sources.append({
                "authors": rs.get("authors", []),
                "title": rs.get("title", ""),
                "year": rs.get("year", "n.d."),
                "url": rs.get("url", ""),
                "type": "web",
            })

    bibliography = generate_bibliography(sources, citation_style)
    provenance = create_ai_provenance_note(
        model=get_model_name(),
        feature="Arena Dialectica",
        sources_used=[thinker_a["full_name"], thinker_b["full_name"]],
    )

    return {
        "success": True,
        "thinker_a": {"id": thinker_a_id, "name": thinker_a["full_name"]},
        "thinker_b": {"id": thinker_b_id, "name": thinker_b["full_name"]},
        "theme": theme,
        "rounds": rounds,
        "synthesis": synthesis,
        "bibliography": bibliography,
        "provenance_note": provenance,
        "citation_style": citation_style,
        "timestamp": datetime.now().isoformat(),
    }


def _generate_fallback(thinker_a, thinker_b, theme, language, citation_style):
    sources = []
    for t in [thinker_a, thinker_b]:
        for work in t["key_works"]:
            sources.append({
                "authors": [t["full_name"]],
                "title": work["title"],
                "year": work["year"],
                "type": work["type"],
            })

    bibliography = generate_bibliography(sources, citation_style)

    return {
        "success": True,
        "thinker_a": {"id": "", "name": thinker_a["full_name"]},
        "thinker_b": {"id": "", "name": thinker_b["full_name"]},
        "theme": theme,
        "rounds": [
            {"round": 1, "speaker": thinker_a["full_name"], "speaker_id": "",
             "text": f"Sul tema '{theme}', la mia esperienza educativa mi insegna che il rapporto personale è fondamentale. Come scrivo nel mio Sistema Preventivo (1877), 'l'educazione è cosa del cuore'."},
            {"round": 2, "speaker": thinker_b["full_name"], "speaker_id": "",
             "text": f"Concordo sull'importanza della relazione, ma aggiungo che l'ambiente deve essere scientificamente preparato per favorire l'autonomia del giovane."},
            {"round": 3, "speaker": thinker_a["full_name"], "speaker_id": "",
             "text": "L'autonomia che proponi è preziosa, ma deve essere accompagnata dall'amorevolezza, dalla presenza costante dell'educatore."},
            {"round": 4, "speaker": thinker_b["full_name"], "speaker_id": "",
             "text": "La presenza dell'educatore è cruciale, ma deve evolversi: da guida attiva a osservatore rispettoso man mano che il giovane cresce."},
        ],
        "synthesis": (
            f"**Sintesi Inedita: L'Accompagnamento Evolutivo**\n\n"
            f"Dal dialogo tra {thinker_a['full_name']} e {thinker_b['full_name']} emerge un concetto nuovo: "
            f"l'educatore non è né solo 'padre amorevole' né solo 'osservatore scientifico', "
            f"ma un accompagnatore che calibra la sua presenza in base alla maturità del giovane.\n\n"
            f"⚠️ Per generare un dibattito completo, configurare GEMINI_API_KEY o GROQ_API_KEY "
            f"nelle variabili d'ambiente di Render."
        ),
        "bibliography": bibliography,
        "provenance_note": "[Modalità dimostrazione - nessuna chiave API configurata]",
        "citation_style": citation_style,
        "timestamp": datetime.now().isoformat(),
    }


def _fetch_real_sources(thinker_name: str, theme: str) -> List[Dict]:
    try:
        from src.multi_source_search import search_engine
        query = f"{thinker_name} {theme}"
        logger.info(f"Arena: searching real sources for '{query}'")
        results = search_engine.search(query, filters={"sources": ["corpus_salesiano", "semantic_scholar", "wikipedia"]})
        if results and results.get("success"):
            all_results = results.get("results", {}).get("results", results.get("results", []))
            if isinstance(all_results, list):
                relevant = [r for r in all_results if r.get("relevance_score", 0) >= 50][:5]
                logger.info(f"Arena: found {len(relevant)} real sources for {thinker_name}")
                return relevant
        return []
    except Exception as e:
        logger.warning(f"Arena: failed to fetch real sources for {thinker_name}: {e}")
        return []
