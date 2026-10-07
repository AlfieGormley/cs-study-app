from pathlib import Path
import json
B=Path('content/theory/05-computability');p=B/'compu-cfg.md';s=p.read_text()
def r(a,b):
 global s
 assert a in s,a
 s=s.replace(a,b)
r('Every `<div>` needs a `</div>`, nested to any depth.', 'Nested block structures can have arbitrarily many pending delimiters in the mathematical model; concrete language and markup rules add their own exceptions and constraints.')
r('You can enumerate a grammar\'s short strings by breadth-first search over **sentential forms** (partly rewritten strings), always expanding the leftmost variable:', 'For the balanced-parentheses grammar below, breadth-first search over **sentential forms** (partly rewritten strings), always expanding the leftmost variable, enumerates all strings up to the bound. Terminals are single characters, and all variables must be keys of G. This routine is not a terminating enumerator for arbitrary CFGs: a rule such as S → SS can grow variables indefinitely without exceeding a terminal-count bound. For general CFGs, enumerate the finitely many candidate terminal strings and decide membership with a parser.')
r('A compiler using this grammar would not know which value to compute.', 'The grammar alone leaves grouping unspecified; a parser needs an additional disambiguation policy or an unambiguous grammar.')
r('the `else` binds to the nearest `if`.', 'the `else` binds to the nearest eligible unmatched `if`.')
r('Strings with i = j = k can always be parsed two ways. Worse, deciding whether an arbitrary CFG is ambiguous is undecidable, which you will be able to prove by the end of this module.', 'In the obvious union grammar, strings with i = j = k have two derivations. That observation alone does not prove inherent ambiguity: the theorem rules out every equivalent unambiguous CFG, not just this construction. Deciding whether an arbitrary CFG is ambiguous is also undecidable; a full proof of these results is beyond this lesson.')
r('- plus optionally `S → ε` if the empty string is in the language.', '- plus optionally `S → ε` if the empty string is in the language. If this exception is used, S must not appear on any right-hand side, so the empty production cannot occur inside a nonempty derivation.')
r('and break long right-hand sides into chains of pairs.', 'replace terminals in mixed/long right-hand sides with fresh variables, and break long right-hand sides into chains of pairs.')
r('and every parse tree is a binary tree.', 'with n terminal-production nodes and n − 1 binary-production nodes. The variable skeleton is a full binary tree; terminal-production nodes still have one terminal child in the complete parse tree.')
r('- **Parser generators** (yacc, Bison, ANTLR) take a grammar and emit a parser. They do not use CYK, because O(n³) is too slow for a million-line codebase. Instead they restrict the grammar to a subclass (LL(k) or LR(k)) that can be parsed in **linear time** with a stack.', '- **Parser generators** take grammars and produce parsers. Deterministic LL(k) and LR(k) parsers have linear input-time bounds for a fixed suitable grammar. Bison also offers GLR parsing, and ANTLR uses adaptive prediction; these capabilities should not all be described as fixed-k deterministic parsing with the same guarantee.')
r('- Regex is not enough for nested structures. "Parse HTML with a regex" fails because arbitrarily deep nesting is not regular.', '- Formal regular expressions cannot recognise arbitrary balanced nesting. Some practical regex engines add recursion or other non-regular features; HTML parsing also has rules beyond simple balanced tags.')
r('Practical parsers use LL or LR subclasses for linear time.', 'Fixed-grammar deterministic LL/LR parsers can run in linear input time; other practical parsing methods have different guarantees.')
p.write_text(s)
p=B/'compu-cfg.questions.json';qs=json.loads(p.read_text());q={x['id'].split('-q')[-1]:x for x in qs}
q['2']['prompt']+=' Assume a formal regular expression without non-regular extensions such as recursive subpatterns.'
q['4']['options'][3]['explanation']='The layered E/T/F grammar gives one tree for this expression; the displayed ambiguous grammar permits five. An ambiguous grammar can still give a unique tree to some other strings.'
q['5']['prompt']+=' Treat a, b and c as identifier tokens (id), not literal terminals added to the grammar.'
q['5']['options'][2]['explanation']='This layered grammar is unambiguous: each string in its language has exactly one parse tree.'
q['6']['options'][0]['text']='Every rule is A → BC or A → a, with an optional S → ε exception whose start symbol never appears on a right-hand side'
q['6']['options'][0]['explanation']='Correct under the stated epsilon exception. Preventing that start symbol on right-hand sides preserves the nonempty-derivation counting argument.'
q['7']['prompt']='In a hypothetical timing model T(n) = c n³ for a fixed grammar and environment, CYK takes 0.01 s at 100 tokens. What does this model predict at 1,000 tokens?'
q['7']['workedExample']+='\n\nThis is a stipulated scaling model, not a measured benchmark prediction: big-O alone does not establish an exact runtime ratio.'
q['10']['options'][2]['explanation']='Correct. Inherent ambiguity is a theorem about every grammar for L. Merely finding two derivations in the obvious union grammar does not establish that theorem.'
q['10']['workedExample']=q['10']['workedExample'].replace('every CFG for L gives some aⁿbⁿcⁿ two trees.', 'no CFG for L is unambiguous. The full proof is beyond this exercise.').replace('tell the parser generator which alternative wins (precedence declarations, or PEG ordered choice).', 'choose a parsing/disambiguation policy whose accepted language and intended trees are separately checked. An inherently ambiguous CFL has no equivalent unambiguous CFG; switching formalisms is not automatically language-preserving.')
q['11']['options'][0]['explanation']='Correct. A conflict in a restricted parser construction does not itself prove grammar ambiguity: an unambiguous grammar may still fall outside that parser class.'
q['11']['workedExample']=q['11']['workedExample'].replace('you will see the technique, reduction from the Post correspondence problem, in the last lesson', 'a standard proof reduces from the Post correspondence problem; this module states the result without the full construction')
p.write_text(json.dumps(qs,ensure_ascii=False,indent=2)+'\n')
p=B/'compu-pda-pumping.md';s=p.read_text()
r('stack:  A  A  A  ·\n           A', 'stack: A$ AA$ A$ $   (after each symbol)')
r('A PDA is a 6-tuple (Q, Σ, Γ, δ, q₀, F):', 'One PDA convention is a 6-tuple (Q, Σ, Γ, δ, q₀, F), starting with an empty stack. The examples abbreviate an initial epsilon move that pushes the bottom marker $, and the simulator starts after that move:')
r('A **deterministic PDA** (DPDA) never has a choice of move,', 'A **deterministic PDA** (DPDA) has at most one enabled move in each configuration, including no choice between an enabled epsilon move and a move consuming the next symbol,')
r('Even-length palindromes `w wᴿ` need real nondeterminism,', 'Even-length palindromes `w wᴿ` over the two-symbol alphabet {a,b} need nondeterminism in the PDA model,')
r('Even palindromes `w wᴿ` are context-free but not deterministic:', 'Even palindromes `w wᴿ` with w ∈ {a,b}* are context-free but not deterministic context-free:')
r('Accept on an empty stack.', 'Accept on an empty stack only after all input has been consumed.')
r('- **PDA → CFG.** Harder: create a variable A_pq for every pair of states, meaning "the strings that take the PDA from p to q with the stack back where it started". Rules follow from how pushes and pops pair up.', '- **PDA → CFG.** First normalise the PDA so acceptance occurs with an empty stack and moves push or pop one symbol. Variables A_pq then describe computations from state p with an empty stack to state q with an empty stack. Pair matching pushes and pops and concatenate such balanced subcomputations. This sketch omits the full normalisation and rule construction.')
r('This is why programming languages are designed with explicit delimiters.', 'Explicit delimiters can make deterministic parsing easier; they are not sufficient by themselves to make every grammar deterministic.')
r('which is the class yacc and Bison handle in linear time.', 'under the usual end-of-input convention. Practical LR/LALR generator modes accept particular grammar subclasses; Bison’s GLR mode has different guarantees.')
r('Choosing the lowest repetition keeps |vxy| ≤ p,', 'Choose a longest root-to-leaf path and a repeated variable among its lowest k + 1 variable nodes; the upper selected subtree then yields at most 2ᵏ = p terminals. This keeps |vxy| ≤ p,')
r('- **Parsers** for JSON, XML and programming languages are PDAs in disguise:', '- **Nested syntax** in JSON, XML and programming languages motivates stack parsing; complete language rules may require further checks. For a deterministic context-free grammar,')
r('which is why C compilers use the "lexer hack" to feed symbol-table information back into the lexer.', 'which motivates techniques such as the "lexer hack" to supply symbol-table information during parsing; not every C compiler uses the same technique.')
r('`w wᴿ` needs nondeterminism;', '`w wᴿ` over a two-symbol alphabet needs nondeterminism in the PDA model;')
p.write_text(s)
p=B/'compu-pda-pumping.questions.json';qs=json.loads(p.read_text());q={x['id'].split('-q')[-1]:x for x in qs}
q['1']['options'][3]['explanation']='Every branch of this particular PDA makes only a bounded number of epsilon state changes, and its other moves consume input. In general, the absence of epsilon pushes alone does not rule out epsilon cycles.'
q['2']['workedExample']=q['2']['workedExample'].replace("so the PDA can't, for example, compare two separate counts it pushed earlier. That restriction is why aⁿbⁿ is possible but aⁿbⁿcⁿ is not.", 'so it cannot access arbitrary stored cells as a TM can. The fact that aⁿbⁿcⁿ is impossible is established by the CFL pumping proof, not merely this informal memory analogy.')
q['4']['prompt']=q['4']['prompt'].replace('For s = aᵖbᵖ,', 'Choose a pumping length p ≥ 2. For s = aᵖbᵖ,')
q['5']['prompt']=q['5']['prompt'].replace('Let s = aᵖbᵖcᵖ.', 'Choose p ≥ 2 and let s = aᵖbᵖcᵖ.')
q['5']['workedExample']=q['5']['workedExample'].replace('∀s (|s|≥p)', '∀s ∈ L (|s|≥p)')
q['6']['workedExample']=q['6']['workedExample'].replace('two stacks would be needed.', 'the direct product construction may require two independent stacks; one stack does not in general suffice.')
q['9']['prompt']+=' You may enlarge the pumping length so that p ≥ 4.'
q['9']['options'][1]['explanation']='For p ≥ 4, taking v = ab, x empty and y = ab at the start pumps four symbols in the alternating sequence. The result remains (ab) raised to an even power, hence a square, for every pump count.'
q['11']['options'][1]['explanation']='Correct with standard end-of-input conventions. This is a language-class theorem; it does not mean that every grammar for such a language is accepted by every practical LR/LALR parser generator.'
q['11']['options'][0]['explanation']='Correct. The language {wwᴿ : w ∈ {a,b}*} is a witness; the unary version would be regular.'
p.write_text(json.dumps(qs,ensure_ascii=False,indent=2)+'\n')
