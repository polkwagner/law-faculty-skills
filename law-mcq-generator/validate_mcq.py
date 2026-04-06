#!/usr/bin/env python3
"""
Validation script for law school MCQ exam documents.
Checks exam .docx and answer key .docx for structural integrity,
answer distribution, narrative coherence, and summary accuracy.

Usage:
    python3 validate_mcq.py exam.docx answer_key.docx
"""

import sys
import re
from collections import Counter, defaultdict
from docx import Document


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_paragraphs(path):
    """Return list of paragraph text strings from a .docx file."""
    doc = Document(path)
    return [p.text for p in doc.paragraphs]


def median(values):
    s = sorted(values)
    n = len(s)
    if n % 2 == 1:
        return s[n // 2]
    return (s[n // 2 - 1] + s[n // 2]) / 2


# ---------------------------------------------------------------------------
# Exam parsing
# ---------------------------------------------------------------------------

def parse_exam(paragraphs):
    """
    Parse exam paragraphs into structured data.
    Returns:
        fact_patterns: dict  letter -> {
            'header_range': (start_q, end_q),
            'subtitle': str,
            'narrative': str,
            'narrative_word_count': int,
            'questions': [qnum, ...]
        }
        questions: dict  qnum -> {
            'stem': str,
            'choices': {'a': str, 'b': str, ...},
            'fact_pattern': letter
        }
    """
    fact_patterns = {}
    questions = {}

    # Regex patterns
    fp_header_re = re.compile(
        r'^Questions?\s+(\d+)\s+through\s+(\d+)\s+relate\s+to\s+Fact\s+Pattern\s+([A-Z])',
        re.IGNORECASE
    )
    fp_label_re = re.compile(r'^FACT\s+PATTERN\s+([A-Z])$', re.IGNORECASE)
    question_stem_re = re.compile(r'^(\d+)\.\s+')
    choice_re = re.compile(r'^\(([a-d])\)\s+')

    current_fp = None
    current_fp_header_range = None
    current_subtitle = None
    narrative_lines = []
    collecting_narrative = False
    first_question_in_fp = True

    current_qnum = None
    current_stem = None
    current_choices = {}

    i = 0
    while i < len(paragraphs):
        text = paragraphs[i].strip()
        if not text:
            i += 1
            continue

        # Check for "Questions X through Y relate to Fact Pattern Z"
        m = fp_header_re.match(text)
        if m:
            current_fp_header_range = (int(m.group(1)), int(m.group(2)))
            i += 1
            continue

        # Check for "FACT PATTERN X"
        m = fp_label_re.match(text)
        if m:
            # Save previous question if any
            if current_qnum is not None and current_stem is not None:
                questions[current_qnum] = {
                    'stem': current_stem,
                    'choices': dict(current_choices),
                    'fact_pattern': current_fp
                }
                current_qnum = None
                current_stem = None
                current_choices = {}

            current_fp = m.group(1).upper()
            fact_patterns[current_fp] = {
                'header_range': current_fp_header_range,
                'subtitle': '',
                'narrative': '',
                'narrative_word_count': 0,
                'questions': []
            }
            collecting_narrative = False
            first_question_in_fp = True
            # Next non-empty line should be subtitle
            i += 1
            while i < len(paragraphs) and not paragraphs[i].strip():
                i += 1
            if i < len(paragraphs):
                subtitle = paragraphs[i].strip()
                fact_patterns[current_fp]['subtitle'] = subtitle
                collecting_narrative = True
                narrative_lines = []
            i += 1
            continue

        # Check for question stem
        m = question_stem_re.match(text)
        if m:
            # Save previous question if any
            if current_qnum is not None and current_stem is not None:
                questions[current_qnum] = {
                    'stem': current_stem,
                    'choices': dict(current_choices),
                    'fact_pattern': current_fp
                }

            # If we were collecting narrative, finalize it
            if collecting_narrative and first_question_in_fp and current_fp:
                narr = ' '.join(narrative_lines)
                fact_patterns[current_fp]['narrative'] = narr
                fact_patterns[current_fp]['narrative_word_count'] = len(narr.split())
                collecting_narrative = False
                first_question_in_fp = False

            qnum = int(m.group(1))
            current_qnum = qnum
            current_stem = text
            current_choices = {}
            if current_fp:
                fact_patterns[current_fp]['questions'].append(qnum)
            i += 1
            continue

        # Check for answer choice
        m = choice_re.match(text)
        if m:
            letter = m.group(1)
            choice_text = choice_re.sub('', text)
            current_choices[letter] = choice_text
            i += 1
            continue

        # If collecting narrative, add to narrative
        if collecting_narrative and first_question_in_fp and current_fp:
            narrative_lines.append(text)
            i += 1
            continue

        i += 1

    # Save last question
    if current_qnum is not None and current_stem is not None:
        questions[current_qnum] = {
            'stem': current_stem,
            'choices': dict(current_choices),
            'fact_pattern': current_fp
        }

    return fact_patterns, questions


# ---------------------------------------------------------------------------
# Answer key parsing
# ---------------------------------------------------------------------------

def parse_answer_key(paragraphs):
    """
    Parse answer key paragraphs.
    Returns:
        answers: dict  qnum -> {
            'correct': letter,
            'taxonomy': str,
            'difficulty': str,
            'distractors': [letter, ...]
        }
        summary: dict with stated counts from the summary section
    """
    answers = {}
    summary = {
        'difficulty': {},
        'position': {},
        'taxonomy': {}
    }

    question_header_re = re.compile(r'^Question\s+(\d+)$', re.IGNORECASE)
    correct_re = re.compile(
        r'Correct\s+Answer:\s*\(([a-dA-D])\)\s*\|\s*Taxonomy:\s*(\w+)\s*\|\s*Difficulty:\s*(\w+)',
        re.IGNORECASE
    )
    distractor_re = re.compile(r'^\(([a-d])\)\s+\[(\w+)\]')

    current_qnum = None
    current_distractors = []
    in_summary = False

    for text_raw in paragraphs:
        text = text_raw.strip()
        if not text:
            continue

        # Detect summary section
        if re.match(r'^EXAM-LEVEL\s+QUALITY\s+SUMMARY', text, re.IGNORECASE):
            # Save last question's distractors
            if current_qnum is not None:
                answers[current_qnum]['distractors'] = list(current_distractors)
            in_summary = True
            current_qnum = None
            continue

        if in_summary:
            # Parse difficulty distribution
            m = re.match(r'^(Moderate|Hard|Very Hard)\s*\((\w+)\):\s*(\d+)', text)
            if m:
                code = m.group(2)
                count = int(m.group(3))
                summary['difficulty'][code] = count
                continue

            # Parse position distribution
            m = re.match(r'^\(([a-d])\):\s*(\d+)', text)
            if m:
                letter = m.group(1)
                count = int(m.group(2))
                summary['position'][letter] = count
                continue

            # Parse taxonomy distribution
            m = re.match(r'^(\w+)\s+\([^)]+\):\s*(\d+)', text)
            if m:
                code = m.group(1)
                count = int(m.group(2))
                if code in ('EA', 'AE', 'FB', 'RI', 'DD', 'NR', 'FS'):
                    summary['taxonomy'][code] = count
                continue

            continue

        # Check for question header
        m = question_header_re.match(text)
        if m:
            # Save previous question's distractors
            if current_qnum is not None and current_qnum in answers:
                answers[current_qnum]['distractors'] = list(current_distractors)
            current_qnum = int(m.group(1))
            current_distractors = []
            continue

        # Check for correct answer line
        m = correct_re.search(text)
        if m and current_qnum is not None:
            answers[current_qnum] = {
                'correct': m.group(1).lower(),
                'taxonomy': m.group(2).upper(),
                'difficulty': m.group(3).upper(),
                'distractors': []
            }
            continue

        # Check for distractor
        m = distractor_re.match(text)
        if m and current_qnum is not None:
            current_distractors.append(m.group(1))
            continue

    # Save last question's distractors if not in summary
    if current_qnum is not None and current_qnum in answers:
        answers[current_qnum]['distractors'] = list(current_distractors)

    return answers, summary


# ---------------------------------------------------------------------------
# Validation checks
# ---------------------------------------------------------------------------

def check_narrative_completeness(fact_patterns):
    """Check 1: Narrative completeness (200-400 words)."""
    issues = []
    for letter in sorted(fact_patterns.keys()):
        fp = fact_patterns[letter]
        wc = fp['narrative_word_count']
        narr = fp['narrative']
        if not narr.strip():
            issues.append(f"Fact Pattern {letter}: missing narrative text")
        elif wc < 200:
            issues.append(f"Fact Pattern {letter}: narrative too short ({wc} words, need 200-400)")
        elif wc > 400:
            issues.append(f"Fact Pattern {letter}: narrative too long ({wc} words, need 200-400)")
    return issues


def check_question_structure(questions):
    """Check 2: Question structure (sequential numbering, 4 choices a-d, no duplicates)."""
    issues = []
    expected_letters = ['a', 'b', 'c', 'd']

    if not questions:
        issues.append("No questions found")
        return issues

    qnums = sorted(questions.keys())
    # Check sequential
    for i, qnum in enumerate(qnums):
        expected = i + 1
        if qnum != expected:
            issues.append(f"Question numbering gap or duplicate: expected Q{expected}, found Q{qnum}")
            break

    # Check each question
    for qnum in qnums:
        q = questions[qnum]
        letters = sorted(q['choices'].keys())
        if letters != expected_letters:
            missing = [l for l in expected_letters if l not in letters]
            extra = [l for l in letters if l not in expected_letters]
            detail = ""
            if missing:
                detail += f" missing ({', '.join(missing)})"
            if extra:
                detail += f" extra ({', '.join(extra)})"
            issues.append(f"Q{qnum}: expected choices (a)-(d), found ({', '.join(letters)}){detail}")

        # Check for duplicate choice text
        choice_texts = {}
        for letter, text in q['choices'].items():
            clean = text.strip()
            if clean in choice_texts.values():
                dup_letter = [k for k, v in choice_texts.items() if v == clean][0]
                issues.append(f"Q{qnum}: choices ({dup_letter}) and ({letter}) have identical text")
            choice_texts[letter] = clean

    return issues


def check_fact_pattern_headers(fact_patterns):
    """Check 3: Fact pattern header ranges match actual question numbers."""
    issues = []
    for letter in sorted(fact_patterns.keys()):
        fp = fact_patterns[letter]
        header_range = fp.get('header_range')
        actual_qs = sorted(fp['questions'])
        if not header_range:
            issues.append(f"Fact Pattern {letter}: no header range found")
            continue
        if not actual_qs:
            issues.append(f"Fact Pattern {letter}: header says Q{header_range[0]}-{header_range[1]} but no questions found")
            continue

        expected_start, expected_end = header_range
        actual_start, actual_end = actual_qs[0], actual_qs[-1]

        if expected_start != actual_start or expected_end != actual_end:
            issues.append(
                f"Fact Pattern {letter}: header says Q{expected_start}-{expected_end}, "
                f"but actual questions are Q{actual_start}-{actual_end}"
            )
    return issues


def check_answer_choice_length(questions, answers):
    """Check 4: Correct answer length <= 1.4x median of all 4 choices."""
    issues = []
    for qnum in sorted(questions.keys()):
        q = questions[qnum]
        if qnum not in answers:
            continue
        correct_letter = answers[qnum]['correct']
        if correct_letter not in q['choices']:
            continue

        lengths = []
        for letter in sorted(q['choices'].keys()):
            lengths.append(len(q['choices'][letter]))

        correct_len = len(q['choices'][correct_letter])
        med = median(lengths)
        if med == 0:
            continue
        ratio = correct_len / med
        if ratio > 1.4:
            issues.append(
                f"Q{qnum}: correct answer ({correct_letter}) is {ratio:.2f}x median (threshold: 1.4x)"
            )
    return issues


def check_position_distribution(questions, answers, fact_patterns):
    """Check 5: Correct answer position distribution."""
    issues = []
    n = len(questions)
    if n == 0:
        issues.append("No questions to check distribution")
        return issues

    # Global distribution
    position_counts = Counter()
    for qnum in questions:
        if qnum in answers:
            position_counts[answers[qnum]['correct']] += 1

    expected = n / 4
    tolerance = 2
    for letter in 'abcd':
        count = position_counts.get(letter, 0)
        if abs(count - expected) > tolerance:
            issues.append(
                f"Global: ({letter}) appears {count} times, expected {expected:.0f} +/- {tolerance}"
            )

    # Per-cluster distribution
    for fp_letter in sorted(fact_patterns.keys()):
        fp = fact_patterns[fp_letter]
        fp_qs = fp['questions']
        if not fp_qs:
            continue

        cluster_letters = []
        for qnum in fp_qs:
            if qnum in answers:
                cluster_letters.append(answers[qnum]['correct'])

        unique = set(cluster_letters)
        n_qs = len(fp_qs)
        if n_qs >= 5 and len(unique) < 3:
            issues.append(
                f"Fact Pattern {fp_letter} ({n_qs} questions): only {len(unique)} distinct correct "
                f"answer position(s) ({', '.join(sorted(unique))}), need at least 3"
            )
        elif 3 <= n_qs <= 4 and len(unique) < 2:
            issues.append(
                f"Fact Pattern {fp_letter} ({n_qs} questions): only {len(unique)} distinct correct "
                f"answer position(s), need at least 2"
            )

    return issues


def normalize_quotes(text):
    """Replace smart quotes and curly quotes with straight equivalents."""
    text = text.replace('\u2018', "'").replace('\u2019', "'")  # single smart quotes
    text = text.replace('\u201C', '"').replace('\u201D', '"')  # double smart quotes
    text = text.replace('\u2013', '-').replace('\u2014', '--')  # en/em dashes
    return text


def strip_legal_references(text):
    """
    Remove case citations, statute references, and legal authority names from text
    so that proper noun extraction focuses on fact-pattern entities only.
    """
    text = normalize_quotes(text)
    # Remove case citations: "X v. Y" patterns (including trailing "Inc.", "Ltd.", etc.)
    # e.g., "Graham v. John Deere", "Campbell v. Acuff-Rose Music, Inc."
    # Also handles "MGM Studios, Inc. v. Grokster, Ltd."
    text = re.sub(
        r'(?:[A-Z][A-Za-z\.\',\- ]*?\s+v\.\s+[A-Z][A-Za-z\.\',\- ]*?'
        r'(?:,?\s*(?:Inc|Ltd|Corp|Co|LLC|LP|LLP)\.?)?)'
        r'(?=[\.,;\)\s\?!:]|$)',
        ' ', text
    )

    # Remove statute references: "§107", "35 U.S.C. §112", "17 U.S.C. §1201(a)(2)"
    text = re.sub(r'\d+\s+U\.S\.C\.\s*§\s*[\d\w()]+', ' ', text)
    text = re.sub(r'§\s*[\d\w()]+', ' ', text)

    # Remove named acts, legal frameworks, and doctrinal test names
    act_patterns = [
        r'(?:the\s+)?Defend\s+Trade\s+Secrets?\s+Act',
        r'(?:the\s+)?America\s+Invents?\s+Act',
        r'(?:the\s+)?Copyright\s+Act',
        r'(?:the\s+)?Lanham\s+Act',
        r'(?:the\s+)?Trademark\s+Dilution\s+Revision\s+Act',
        r'(?:the\s+)?ELVIS\s+Act',
        r'(?:the\s+)?TDRA',
        r'(?:the\s+)?DTSA',
        r'(?:the\s+)?UTSA',
        r'(?:the\s+)?AIA\b',
        r'(?:the\s+)?DMCA',
        r'(?:the\s+)?First\s+Amendment',
        r'(?:the\s+)?Mayo/Alice\s+(?:two-step\s+)?framework',
        r'(?:the\s+)?Abercrombie\s+spectrum',
        r'(?:the\s+)?Rogers\s+test',
        r'(?:the\s+)?Rogers\b',
        r'(?:the\s+)?Sleekcraft\s+factors?',
        r'(?:the\s+)?Tea\s+Rose[\-\u2013]Rectanus\s+doctrine',
        r'(?:the\s+)?Tea\s+Rose\s+doctrine',
        r'(?:the\s+)?Vernor\s+framework',
        r'Under\s+Rogers\b',
    ]
    for pat in act_patterns:
        text = re.sub(pat, ' ', text, flags=re.IGNORECASE)

    return text


def extract_factual_entities(text):
    """
    Extract proper nouns that are likely fact-pattern entities (people, companies,
    products, places) from text that has already had legal references removed.
    Returns a set of candidate entity strings.
    """
    results = set()

    # Common words to skip (sentence starters, function words, legal terms)
    skip_words = {
        'The', 'This', 'That', 'These', 'Those', 'A', 'An', 'In', 'On', 'At',
        'For', 'To', 'From', 'By', 'With', 'Of', 'And', 'Or', 'But', 'If',
        'Is', 'Are', 'Was', 'Were', 'Has', 'Have', 'Had', 'Do', 'Does', 'Did',
        'Not', 'No', 'Yes', 'It', 'Its', 'He', 'She', 'His', 'Her', 'They',
        'Their', 'We', 'Our', 'You', 'Your', 'Which', 'What', 'When', 'Where',
        'Who', 'How', 'Why', 'Each', 'Every', 'All', 'Some', 'Any', 'Both',
        'Either', 'Neither', 'Most', 'Many', 'Much', 'More', 'Other', 'Such',
        'Only', 'Also', 'However', 'Because', 'Although', 'While', 'Since',
        'Under', 'After', 'Before', 'During', 'Between', 'Through', 'Over',
        'About', 'Into', 'Upon', 'Within', 'Without', 'Against', 'Among',
        'Assume', 'Would', 'Could', 'Should', 'May', 'Might', 'Must',
        'Shall', 'Will', 'Can', 'Here', 'There', 'So', 'Yet', 'Thus',
        'Even', 'Still', 'Just', 'Rather', 'Very', 'Too', 'Now', 'Then',
        'As', 'Once', 'Until', 'Unless', 'Select', 'Separately', 'Prior',
        'First', 'Second', 'Third', 'Fourth', 'Fifth', 'Sixth', 'Seventh',
        'Eighth', 'Ninth', 'Tenth', 'Next', 'Finally', 'Further', 'Additionally',
        'Moreover', 'Furthermore', 'Independently', 'Alternatively',
        'Accordingly', 'Specifically', 'Particularly', 'Notably', 'Instead',
        'Indeed', 'Overall', 'Conversely', 'Nonetheless', 'Regardless',
        'Meanwhile', 'Otherwise', 'Similarly', 'Consequently', 'Therefore',
        'Notwithstanding', 'Subsequently', 'Claim', 'Claims', 'Infringement',
        'Question', 'Questions', 'Correct', 'Choice', 'Choices', 'Answer',
        'Applying', 'Considering', 'Following', 'Including', 'Regarding',
    }

    # Legal / generic terms that should never count as fact-pattern entities
    legal_skip = {
        'DTSA', 'UTSA', 'USPTO', 'AIA', 'DMCA', 'TDRA', 'PHOSITA', 'NDA',
        'DRM', 'BPM', 'NPBL', 'LIDAR', 'CLIA', 'ELISA', 'IL', 'AI', 'USB',
        'Copyright', 'Lanham', 'Amendment', 'Congress', 'Act', 'Supreme',
        'Court', 'Federal', 'Circuit', 'Patent', 'Trademark', 'Trade',
        'Secret', 'Secrets', 'Design', 'Utility', 'Dilution', 'Revision',
        'Doctrine', 'Section', 'Statute', 'Rule', 'Standard', 'Test',
        'Analysis', 'Framework', 'Spectrum', 'Correct', 'Fact', 'Pattern',
        'Question', 'Claim', 'Premium', 'Vault',
    }

    # Multi-word proper nouns (e.g., "NovaDyne Robotics", "Dr. Tamura")
    # Note: single quotes are used as word boundaries, not part of names
    multi_word_re = re.compile(
        r'\b((?:(?:Dr|Mr|Ms|Mrs|Prof)\.\s+)?'
        r'(?:[A-Z][a-zA-Z]+(?:\s+(?:of|the|and|for|de|la|le|&)\s+)?){2,}'
        r'(?:(?:Inc|Corp|Co|Ltd|LLC|LP|LLP|Jr|Sr|II|III|IV)\b\.?)?)'
    )
    for m in multi_word_re.finditer(text):
        candidate = m.group(1).strip().rstrip('.,;:\'")')
        words = candidate.split()
        # Filter: at least one word must not be in skip/legal sets
        non_skip = [w for w in words
                    if w.rstrip('.,;:') not in skip_words
                    and w.rstrip('.,;:') not in legal_skip]
        if len(non_skip) >= 1:
            results.add(candidate)

    # CamelCase words (e.g., "PathSense", "MelodyMind", "NovaDyne")
    camel_re = re.compile(r'\b([A-Z][a-z]+[A-Z][a-zA-Z]*)\b')
    for m in camel_re.finditer(text):
        candidate = m.group(1)
        if candidate not in legal_skip and len(candidate) >= 4:
            results.add(candidate)

    # Mid-sentence capitalized names (after lowercase text)
    mid_re = re.compile(r'(?<=[a-z,;]\s)([A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,})*)')
    for m in mid_re.finditer(text):
        candidate = m.group(1).strip().rstrip('.,;:')
        words = candidate.split()
        if all(w not in skip_words and w not in legal_skip for w in words):
            results.add(candidate)

    # ALL-CAPS words that look like acronyms/brands (3+ chars, not legal terms)
    # Only match standalone words, not fragments
    allcaps_re = re.compile(r'\b([A-Z]{3,})\b')
    for m in allcaps_re.finditer(text):
        candidate = m.group(1)
        if candidate not in legal_skip and candidate not in skip_words:
            # Skip words that are common English words in ALL CAPS
            common_upper = {
                'THE', 'AND', 'FOR', 'NOT', 'BUT', 'ALL', 'CAN', 'HER',
                'WAS', 'ONE', 'OUR', 'OUT', 'HAS', 'HAD', 'HOT', 'OIL',
                'OLD', 'RED', 'SIT', 'TOP', 'TWO', 'WAR', 'FAR',
                'USE', 'WAY', 'HIM', 'HOW', 'MAN', 'NEW', 'NOW',
            }
            if candidate not in common_upper:
                results.add(candidate)

    return results


def check_narrative_coherence(fact_patterns, questions, answers):
    """Check 6: Entities in question stems should appear in narrative or 'Assume' instructions."""
    issues = []

    for fp_letter in sorted(fact_patterns.keys()):
        fp = fact_patterns[fp_letter]
        narrative_text = fp['narrative'] + ' ' + fp['subtitle']
        narrative_lower = narrative_text.lower()

        # Also build full cluster text (narrative + all stems) for broader context
        all_stems_text = ''
        for qnum in fp['questions']:
            if qnum in questions:
                all_stems_text += ' ' + questions[qnum]['stem']

        for qnum in fp['questions']:
            if qnum not in questions:
                continue
            q = questions[qnum]
            stem = q['stem']

            # Strip legal references before extracting entities
            cleaned_stem = strip_legal_references(stem)
            stem_entities = extract_factual_entities(cleaned_stem)

            # Also check "Assume for purposes of this question only" text
            assume_match = re.search(
                r'[Aa]ssume\s+for\s+purposes\s+of\s+this\s+question\s+only\s+that\s+(.*?)(?:\.\s|$)',
                stem
            )
            assume_text = assume_match.group(1) if assume_match else ''

            # Entities that are introduced by the question stem itself
            # (in quotes, or after "a ___" / "the ___" introductory phrases)
            # are self-contained and don't need to appear in the narrative.
            # We detect this by checking if the entity appears in quotes.
            norm_stem = normalize_quotes(stem)
            quoted_entities = set()
            for qm in re.finditer(r"['\"]([^'\"]+)['\"]", norm_stem):
                quoted_entities.add(qm.group(1).strip().upper())

            for entity in stem_entities:
                entity_lower = entity.lower()

                # Skip entities introduced by the question itself (in quotes)
                if entity.upper() in quoted_entities:
                    continue

                # Check in narrative text (substring match)
                if entity_lower in narrative_lower:
                    continue

                # Check in assume clause
                if assume_text and entity_lower in assume_text.lower():
                    continue

                # Check if any significant word of entity appears in narrative
                entity_words = entity.split()
                if any(w.lower() in narrative_lower
                       for w in entity_words
                       if len(w) >= 3 and w[0].isupper()):
                    continue

                # Check possessive forms (e.g., "NovaDyne's" -> "NovaDyne")
                entity_base = entity.rstrip("'s").rstrip("\u2019s")
                if entity_base.lower() in narrative_lower:
                    continue

                issues.append(
                    f"Q{qnum}: entity '{entity}' not found in "
                    f"Fact Pattern {fp_letter} narrative"
                )

    return issues


def check_question_coverage(questions, answers):
    """Check 7: Every exam question has a corresponding answer key entry."""
    issues = []
    for qnum in sorted(questions.keys()):
        if qnum not in answers:
            issues.append(f"Q{qnum}: missing from answer key")
    # Also check for extra answers
    for qnum in sorted(answers.keys()):
        if qnum not in questions:
            issues.append(f"Q{qnum}: in answer key but not in exam")
    return issues


def check_correct_answer_validity(questions, answers):
    """Check 8: Each correct answer letter exists in the exam choices."""
    issues = []
    valid_letters = set('abcd')
    for qnum in sorted(answers.keys()):
        ans = answers[qnum]
        letter = ans['correct']
        if letter not in valid_letters:
            issues.append(f"Q{qnum}: correct answer '{letter}' is not a valid letter (a-d)")
            continue
        if qnum in questions:
            if letter not in questions[qnum]['choices']:
                issues.append(f"Q{qnum}: correct answer ({letter}) not among exam choices")
    return issues


def check_distractor_completeness(answers):
    """Check 9: Each question should have exactly 3 distractor entries."""
    issues = []
    for qnum in sorted(answers.keys()):
        ans = answers[qnum]
        distractors = ans.get('distractors', [])
        correct = ans['correct']

        # Expected: 3 distractors (one for each non-correct letter)
        expected_letters = sorted([l for l in 'abcd' if l != correct])
        actual_letters = sorted(distractors)

        if len(distractors) != 3:
            issues.append(
                f"Q{qnum}: expected 3 distractors, found {len(distractors)} "
                f"({', '.join(actual_letters) if actual_letters else 'none'})"
            )
        elif actual_letters != expected_letters:
            missing = [l for l in expected_letters if l not in actual_letters]
            extra = [l for l in actual_letters if l not in expected_letters]
            detail_parts = []
            if missing:
                detail_parts.append(f"missing ({', '.join(missing)})")
            if extra:
                detail_parts.append(f"extra ({', '.join(extra)})")
            issues.append(f"Q{qnum}: distractor letters mismatch: {'; '.join(detail_parts)}")
    return issues


def check_valid_codes(answers):
    """Check 10: Taxonomy and difficulty codes are valid."""
    issues = []
    valid_taxonomy = {'EA', 'AE', 'FB', 'FS', 'RI', 'DD', 'NR'}
    valid_difficulty = {'M', 'H', 'VH'}

    for qnum in sorted(answers.keys()):
        ans = answers[qnum]
        if ans['taxonomy'] not in valid_taxonomy:
            issues.append(f"Q{qnum}: invalid taxonomy code '{ans['taxonomy']}'")
        if ans['difficulty'] not in valid_difficulty:
            issues.append(f"Q{qnum}: invalid difficulty code '{ans['difficulty']}'")
    return issues


def check_summary_statistics(answers, summary):
    """Check 11: Summary section counts match actual per-question data."""
    issues = []

    # Recount difficulty
    diff_counts = Counter()
    pos_counts = Counter()
    tax_counts = Counter()

    for qnum in answers:
        ans = answers[qnum]
        diff_counts[ans['difficulty']] += 1
        pos_counts[ans['correct']] += 1
        tax_counts[ans['taxonomy']] += 1

    # Compare difficulty
    for code in sorted(set(list(diff_counts.keys()) + list(summary.get('difficulty', {}).keys()))):
        actual = diff_counts.get(code, 0)
        stated = summary.get('difficulty', {}).get(code, None)
        if stated is not None and stated != actual:
            issues.append(f"Difficulty: stated {code}={stated} but counted {code}={actual}")
        elif stated is None and actual > 0:
            issues.append(f"Difficulty: {code}={actual} not mentioned in summary")

    # Compare position
    for letter in 'abcd':
        actual = pos_counts.get(letter, 0)
        stated = summary.get('position', {}).get(letter, None)
        if stated is not None and stated != actual:
            issues.append(f"Position: stated ({letter})={stated} but counted ({letter})={actual}")
        elif stated is None and actual > 0:
            issues.append(f"Position: ({letter})={actual} not mentioned in summary")

    # Compare taxonomy
    for code in sorted(set(list(tax_counts.keys()) + list(summary.get('taxonomy', {}).keys()))):
        actual = tax_counts.get(code, 0)
        stated = summary.get('taxonomy', {}).get(code, None)
        if stated is not None and stated != actual:
            issues.append(f"Taxonomy: stated {code}={stated} but counted {code}={actual}")
        elif stated is None and actual > 0:
            issues.append(f"Taxonomy: {code}={actual} not mentioned in summary")

    return issues


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 validate_mcq.py exam.docx answer_key.docx")
        sys.exit(2)

    exam_path = sys.argv[1]
    key_path = sys.argv[2]

    import os
    exam_name = os.path.basename(exam_path)
    key_name = os.path.basename(key_path)

    print("=== MCQ EXAM VALIDATION ===")
    print(f"Exam: {exam_name}")
    print(f"Key:  {key_name}")
    print()

    # Load and parse
    exam_paras = load_paragraphs(exam_path)
    key_paras = load_paragraphs(key_path)

    fact_patterns, questions = parse_exam(exam_paras)
    answers, summary = parse_answer_key(key_paras)

    all_checks = []

    # --- Exam Document Checks ---
    print("--- Exam Document ---")

    checks = [
        (1, "Narrative completeness", check_narrative_completeness(fact_patterns)),
        (2, "Question structure", check_question_structure(questions)),
        (3, "Fact pattern headers", check_fact_pattern_headers(fact_patterns)),
        (4, "Answer choice length", check_answer_choice_length(questions, answers)),
        (5, "Position distribution", check_position_distribution(questions, answers, fact_patterns)),
        (6, "Narrative-question coherence", check_narrative_coherence(fact_patterns, questions, answers)),
    ]

    for num, label, issues in checks:
        status = "PASS" if not issues else "FAIL"
        all_checks.append((num, label, issues))
        # Pad the label for alignment
        padded = f"[{num}] {label}:"
        print(f"{padded:42s} {status}")
        if issues:
            for issue in issues:
                print(f"    {issue}")

    print()
    print("--- Answer Key ---")

    key_checks = [
        (7, "Question coverage", check_question_coverage(questions, answers)),
        (8, "Correct answer validity", check_correct_answer_validity(questions, answers)),
        (9, "Distractor completeness", check_distractor_completeness(answers)),
        (10, "Valid codes", check_valid_codes(answers)),
        (11, "Summary statistics", check_summary_statistics(answers, summary)),
    ]

    for num, label, issues in key_checks:
        status = "PASS" if not issues else "FAIL"
        all_checks.append((num, label, issues))
        padded = f"[{num}] {label}:"
        print(f"{padded:42s} {status}")
        if issues:
            for issue in issues:
                print(f"    {issue}")

    # Final result
    failed = [c for c in all_checks if c[2]]
    print()
    if failed:
        print(f"=== RESULT: FAIL ({len(failed)} check(s) failed) ===")
        sys.exit(1)
    else:
        print("=== RESULT: PASS (all checks passed) ===")
        sys.exit(0)


if __name__ == '__main__':
    main()
