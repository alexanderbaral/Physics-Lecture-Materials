# AGENTS.md — Physics Lecture Script

## 1. Purpose and core rules
This repository contains a bilingual LaTeX physics lecture script maintained in VS Code with Codex. Read this file before making changes.

- German is the authoritative master for content and structure.
- English is a Codex-maintained translation, not an independent authoring branch.
- Keep the project simple, readable, modular, and manually editable.
- Prefer semantic LaTeX and maintainability over clever abstractions.
- Do not overengineer or create speculative content structures.
- Write in a concise lecture-script style, not in long prose. Make the essential
  content immediately scannable and let formulas, diagrams, and figures carry
  the explanation wherever possible. Communicate each idea with as little text
  as clarity permits, and clarify complex relationships through deliberate
  spatial arrangement of formulas, labels, and graphics.

### Arbeitsablauf
Die übergeordneten Regeln in `../AGENTS.md` gelten. Dort stehen die aktuellen Bau-, Cache-, Vorschau- und Zuständigkeitsregeln; sie ersetzen die früheren getrennten Buildabläufe.

### 1.1 Evolving chapter design principles
The completed and author-revised chapters define the target style for new
content. Treat the following principles as a provisional, binding design
standard. After each completed chapter, review and refine them with the author
so that future drafts increasingly match the style of the revised material.

#### Content order and orientation
- Arrange topics according to their scientific dependencies. Introduce a
  concept only after the prerequisites needed to understand it, and progress
  from elementary concepts through rules and procedures to more demanding
  applications.
- Begin each section with a short orientation of only a few sentences. State
  the topic's significance, connect it to prior knowledge, announce its later
  use, or identify the section's central problem. Do not front-load detailed
  explanations into this opening.

#### Concise scientific presentation
- Before a displayed equation, write a meaningful introductory sentence whose
  first line fills at least approximately half the available text width.
  Avoid isolated one- or two-word introductions such as "Für" or "Gegeben".
  Move useful context from after the equation into its introduction when
  needed; do not add filler merely to lengthen the line. Check this visually,
  especially in examples and minipages.
- Use prose mainly for orientation, transitions, and interpretation. Let
  formulas, tables, diagrams, and deliberate spatial arrangement carry the
  explanation whenever they express the relationship more directly.
- Avoid extended prose when a precise visual or scientific representation
  makes the same relationship easier to scan.
- Prefer the shortest wording that preserves the scientific reasoning.
  State assumptions beside the formula or step where they become necessary;
  avoid separate explanatory sentences when compact notation makes the point
  clear. The script should read as concise teaching notes, not as a textbook.
- Do not emphasize equations with black frames such as `\boxed`. Use the
  surrounding semantic box, spatial arrangement, or restrained typography to
  communicate their role instead.
- Keep a list visually grouped: the vertical gap from its final item to a
  following independent paragraph must be at least as large as the gaps
  between its items. Reduce internal spacing where appropriate and provide
  sufficient space after the list. Check the rendered result, including lists
  containing displayed equations and lists inside minipages.

#### Semantic roles
- Give each semantic box one clear purpose; do not mix several roles in one
  box:
  - `DefinitionBox` introduces a term together with its notation and necessary
    assumptions.
  - `TheoremBox` states a durable scientific result or formula.
  - `KeyPointBox` emphasizes an especially important rule, consequence, or
    relationship.
  - `ExampleBox` applies the material concretely or checks understanding.
  - `RemarkBox` records pitfalls, technical guidance, interpretations, or a
    supplementary viewpoint.
- Keep formal definitions compact and self-contained. Include the emphasized
  term, the author-established English translation where required, the
  scientific statement, all necessary assumptions, and the associated
  notation. Put applications, longer explanations, and consequences after the
  definition or in separate semantic elements.
- Add a technical term's translation exactly once per language version: place
  it immediately after the term when that term is explicitly introduced for
  the first time, using the central language command:
  German uses `\EnglishTerm{...}` and English uses `\GermanTerm{...}`. This
  applies both to formal definitions and to explicitly introduced technical or
  procedural terms outside a definition box. Do not repeat the translation at
  ordinary later uses of the same term.

#### Examples
- Make every example perform a genuine learning step rather than merely
  substitute numbers into a finished formula. Appropriate steps include
  choosing a representation, recognizing a rule, determining a quantity,
  justifying a statement, interpreting a result, or comparing useful solution
  methods.
- Structure each example as a recognizable learning path where appropriate:
  choose or construct a representation, identify and carry out the relevant
  operation or method, name the resulting scientific state, and interpret
  the result. Show the essential reasoning steps and compress routine algebra
  when it is not itself the learning objective.
- For calculations, make the given information, the quantity sought, the
  calculation, and the result recognizable where appropriate. Carry units
  consistently throughout.
- Before concrete numerical vectors are used in a calculation, identify their
  scientific role through a preceding general formula, concise prose, or
  explicit annotations. Do not apply an operation to unexplained numerical
  vectors; make clear, for example, whether a vector is a support vector, a
  direction vector, a normal vector, or a projection.
- Prefer technical or mechanical-engineering quantities when they arise
  naturally from the topic; do not force an artificial application context.

#### Figures and color
- In coordinate diagrams for concrete numerical examples, show a subtle
  background grid at integer coordinate values and label the integer axis
  ticks (for example 1, 2, 3, 4). Grid spacing and tick values must match the
  numerical coordinates, including when drawing units are enlarged. Keep
  the grid visually subordinate to vectors and labels.
- Place a figure directly beside or immediately after the thought that needs
  it. Use side-by-side text, formulas, tables, and figures when this makes their
  correspondence visible without page turning or unnecessary eye movement.
- A figure may be repeated deliberately when it serves again as the immediate
  working basis of a later theorem, derivation, or example.
- Keep black and grayscale as the visual foundation, with TH Mannheim blue for
  semantic structure. Use additional colors only as local carriers of meaning,
  such as linking corresponding quantities, expressions, or geometric areas.
  Within one representation, a color must retain one meaning and must never be
  added merely for decoration.
- Give recurring scientific roles a stable visual grammar throughout the
  script. Use the same arrow type, alignment, annotation position, color, and
  final-state labeling whenever the same kind of relationship recurs. In
  multi-step procedures, align successive states vertically where practical,
  place an operation beside the state to which it is applied, and explicitly
  name a scientificly significant final state. Use `\Longleftrightarrow` only
  for equivalent statements or states and `\Longrightarrow` for one-way
  consequences.
- Before completing any TikZ figure, visually check every label and
  scientific expression: it must not cross, touch, or be obscured by an axis,
  geometric object, arrow, line, or another label. Use transparent label
  backgrounds unless the author explicitly requests an exception.

#### Cloze design
- Preserve the complete reasoning context in the cloze version: prompts,
  assumptions, diagrams, and the surrounding scientific structure remain
  visible. Hide specifically the learning steps students should reproduce.
- Use a light CD-greige `\Cloze` field for a short result, symbol, or single-line response,
  and a `ClozeArea` grid for multi-line calculations, derivations, drawings, or
  constructions. Size every response area for the handwriting realistically
  required.
- The complete and cloze variants must contain the same material in the same
  order, but they need not have identical pagination. In the complete variant,
  show solutions at their natural size without preserving the cloze field's
  artificial width.

## 2. Inhaltsstruktur
Neue Pfade selbstständig in englischem `snake_case` vergeben, ohne Nummernpräfix und ohne gesonderte Namensfreigabe. Inhaltliche Umstrukturierungen nach Nutzerauftrag.

```
content/chapters_de/<chapter>/_chapter.tex
content/chapters_de/<chapter>/<section>/_section.tex
content/chapters_de/<chapter>/<section>/<subsection>.tex
```
Eine zusätzliche Inhaltsdatei nur für einen echten Unterabschnitt oder eine klar zusammengehörige umfangreiche Einheit anlegen. Inhalte ohne Unterabschnitt direkt in `_section.tex` halten. Keine Datei pro Absatz/Formel und keine Vorratskapitel. EN spiegelt die DE-Struktur, wenn eine Übersetzung beauftragt ist. Reihenfolge über `\input`. Abschnittswechsel auf neuer Seite; der erste Abschnitt darf unter der Kapitelüberschrift beginnen.

## 3. German master and English synchronization
`content/chapters_de/` is the single source of truth. Normal authoring primarily changes German content. Do not automatically update English unless explicitly requested.

When asked to synchronize English:
- compare German master and existing English;
- update affected English content and structure;
- preserve good unchanged English wording;
- keep equations, numbers, examples, assumptions, labels, references, and scientific meaning equivalent;
- write idiomatic scientific English;
- mirror approved German structural changes;
- report genuine ambiguities;
- compile relevant English variants.

### Translation glossary
Use author-established terminology consistently. Follow the first-use and
formatting rules in §1.1; record only explicitly established preferences here.

| German | English | Notes |
|---|---|---|
| Ortsvektor | position vector | Do not use “location vector”. |

Add entries when the author explicitly establishes a preferred translation. Do not fill this table with trivial translations unnecessarily.

## 4. Shared project infrastructure
Keep shared infrastructure compact:
```text
common/
  config.tex
  preamble.tex
  layout.tex
  commands.tex
```

- `config.tex`: mode definitions and defaults.
- `preamble.tex`: packages and technical LaTeX setup.
- `layout.tex`: page geometry, typography/layout, title page, header/footer, branding, semantic box styling.
- `commands.tex`: stable author-facing commands, language helper, cloze interface, scientific shortcuts.

Do not create a general-purpose `header.tex`. The old header in `legacy/` is reference material only. Avoid splitting infrastructure into many tiny files unless later complexity clearly justifies it.

Maintain the bilingual lecture title, institution, and faculty together with the semester and author in `../_shared/lecture_metadata.tex`. Both document entry points load it before the layout. Standalone TikZ builds do not need lecture metadata.

The semester exists once, e.g. `\newcommand{\Semester}{WS 27/28}` or `\newcommand{\Semester}{SS 28}`. Never create `SemesterDE`/`SemesterEN`.

`Vorlesungsskript`/`Lecture Notes`, `Seite`/`Page`, and similar fixed interface strings are language logic, not author metadata. Store the script title, institution, and faculty as one command each whose value uses the central `\Lang{de}{en}` helper.

## 5. Build architecture (Bedienung nach der übergeordneten AGENTS.md)
There is exactly one real document body:
```text
main.tex
```

There are four minimal build entry points under `tools/`:
```text
tools/build-de.tex
tools/build-de-cloze.tex
tools/build-en.tex
tools/build-en-cloze.tex
```
They only select language/cloze mode and load `main.tex`; never duplicate the document body.

Direct compilation of `main.tex` uses the safe default: German, complete (`cloze=false`).

Also maintain `tools/build-all.ps1`. It builds the currently enabled variants
with `latexmk`, clearly reports success or failure per variant, and returns a
non-zero exit status if any build fails. Until English translation begins,
enable only the German complete and German cloze variants. When translation
begins, enable both English variants as well. Use the locally installed TeX
Live distribution; generated outputs should live under `build/` where practical.

## 6. Language, shared resources, labels
Provide one central helper for shared language-dependent text, e.g. `\Lang{deutscher Text}{English text}`. Use it for TikZ labels, title-page interface text, box titles, header/footer text, shared tables, and the bilingual files under `content/front_matter/`. Long chapter prose stays in separate DE/EN content trees.

Shared TikZ figures, images, layout, commands, bibliography, and branding normally exist only once. Do not duplicate TikZ solely for translated labels.

Use language-independent English technical labels, e.g.:
```latex
\label{chap:fundamentals}
\label{sec:fundamentals_vector_addition}
\label{eq:fundamentals_derivative_definition}
\label{fig:fundamentals_vector_components}
\label{def:fundamentals_linear_independence}
```
Every label below a chapter uses the approved technical chapter name as its
namespace immediately after the type prefix. Apply the same namespace to labels
generated through semantic-box arguments, references, equations, figures, and
tables.

## 7. Cloze system
Semantics:
- `cloze=false` → complete lecture script
- `cloze=true` → cloze/student version

Provide a simple short-gap interface such as `\Cloze{<width>}{<content>}`: complete mode shows content; cloze mode shows a subtle writing field.

Also provide a robust long-calculation interface: complete mode shows the
solution; cloze mode shows an exact 5 mm grid. Specify every `ClozeArea` by an
integer number of grid columns and rows,
`\begin{ClozeArea}[<columns>]{<rows>}`; never pass lengths such as `\linewidth`
or `3cm`. The default is 34 columns. Choose the row count from the handwritten
space actually needed, so width and height always contain complete squares.
Support multi-line/`align`-style mathematics robustly. Do not use local ad-hoc
solution switches in chapter files.

Use the light CD-greige `\Cloze` box (`#E5E4D8`) for every short, single-line
inline answer. Keep these backgrounds unobtrusive but recognizable as writing
areas, with pencil legibility taking priority over stronger brand colors.
Use the 5 mm grid (`ClozeArea`) whenever a larger response area or multiple handwritten
lines are needed, especially for longer calculations and derivations.
When adapting an existing grid, preserve its approximate physical area while
rounding both dimensions to whole 5 mm squares.
The width argument of `\Cloze` controls only the writing field in cloze mode. In
the complete version, render the solution at its natural width without
reserving the width of the cloze field.

Definition and example boxes must never break across PDF pages. Keep
`DefinitionBox` and `ExampleBox` unbreakable so that a box which no longer fits
is moved as a whole to the next page.

When an example directly illustrates the preceding definition, keep the
definition and example together on the same PDF page. Use a smaller vertical
gap within this pair while retaining the normal box spacing before the next
content block.

## 8. Layout, typography, branding
Use modern KOMA-Script, preferably `scrreprt`, A4, 12 pt unless a strong technical reason requires otherwise.

Mandatory geometry:
```latex
left=1.5cm
right=1.5cm
top=1.0cm
bottom=1.0cm
includeheadfoot
```
Do not enlarge these margins for conventional print-layout reasons. The script is primarily for digital tablet use and handwritten annotation.

Use Plus Jakarta Sans as the primary text typeface, consistently in the document
and diagram labels. The text font files are bundled under
`../_shared/resources/fonts/plus_jakarta_sans/`, including their SIL Open
Font License. Retain Libertinus Math for formulas; do not force sans-serif
mathematics.

All text inside figures and diagrams must use the same font size as the
surrounding body text. This applies equally to prose, scientific expressions
and symbols, axis labels, annotations, and vector labels. Do not shrink a
figure with `\resizebox`, `\scalebox`, or a similar mechanism when this would
make its labels smaller than the adjacent text; adapt the figure geometry or
surrounding layout instead.

Draw angle arcs in figures and diagrams without arrowheads. Place the angle
symbol or angle measure inside the corresponding angle sector; enlarge the arc
when necessary so the label remains legible and is clearly assigned to that
angle.
Mark every right angle with a quarter-circle arc and a dot inside its angle
sector, never with a square corner.

Maintain TH Mannheim blue in `../_shared/style/branding_colors.tex` and use it sparingly. Body text remains black; otherwise prefer black/grayscale. Style: modern, technical, minimal, calm, tablet-friendly. Do not reproduce the legacy TH Mannheim layout.

This physics lecture script belongs to the Fakultät für Maschinenbau.
Use exclusively the official TH Mannheim/Maschinenbau logo and retain the
faculty metadata. Do not use ZLL or any other faculty/unit subidentity.
The title page uses a white background and the official blue point pattern,
65 mm wide and anchored 5 mm from the bottom and right page edges.
The header uses the official Mannheimer Punkt as an RGB-blue vector PDF.

Both products load branding assets from `../_shared/resources/branding/`. Their paths are set in `../_shared/style/branding.tex`. Each chapter may keep its own visual material in `content/resources/chapters/<chapter>/images/` and `content/resources/chapters/<chapter>/tikz/`, mirroring the approved chapter name under `content/chapters_de/` and `content/chapters_en/`. Missing branding files automatically produce restrained placeholders.

Place TikZ figures reused across both products in `../_shared/resources/tikz/`. Figures shared only between chapters of the script belong in `content/resources/shared/tikz/`.

Always place every new TikZ graphic immediately in its own semantically named
file in the appropriate `content/resources/**/tikz/` folder. Do not leave new
`tikzpicture` environments inline in chapter or section content files; include
the external resource through the project's central TikZ-loading command.

Title page includes logo, language-dependent script title, `Vorlesungsskript`/`Lecture Notes`, author, language-dependent institution/faculty, and semester. Keep the first design restrained and modular.

Keep the header quiet and show the Mannheimer Punkt discreetly at upper right on regular content pages via the central page style.

Footer concept:
- DE: `Physik · Semester WS 27/28                     Seite 13`
- EN: `Physics · Semester WS 27/28                    Page 13`

Values come from central configuration/language logic. Institution/faculty belong primarily on the title page. Prefer KOMA-compatible page-style mechanisms such as `scrlayer-scrpage`.

## 9. Physics conventions
Use modern scientific LaTeX, a clean package set, and no duplicate package loads. Use suitable tools such as `amsmath`/`mathtools`, TikZ, `tcolorbox`, `microtype`, `booktabs`, `tabularx`, `hyperref` only as needed. Avoid obsolete `\rm`, `\bf`, `\it` definitions.

- When a quantity or expression is deliberately set equal to zero as a
  condition to solve (for example, finding a zero of a function), mark the
  target equality with `\overset{!}{=}`. Do not use this notation for ordinary
  identities or for results that merely happen to equal zero.
- Write function limits as `\lim_{x\to a}f(x)=L`, including the analogous
  notation at infinity. Do not introduce the alternative `f(x)\to L`.

### Analytic-geometry notation
- Name distinct points with distinct uppercase letters such as $P$, $Q$, and
  $R$. Use their direct connecting vectors such as $\overrightarrow{PQ}$ and
  $\overrightarrow{OP}$ unless separate position-vector symbols are needed
  later in a calculation.
- Write vector components with exactly one index, for example
  $\vec p=(p_1,p_2,p_3)^{\mathsf T}$ and
  $\vec q=(q_1,q_2,q_3)^{\mathsf T}$. Avoid double indices such as
  $x_{i,j}$ in introductory analytic geometry.
- Use $x_1,x_2,x_3$ for coordinate axes and the components of a general
  position vector $\vec x$. Choose other vector letters from their
  scientific role rather than using $\vec x,\vec y,\vec z$ merely to
  distinguish several vectors.

For displayed transformation chains, align successive equivalence signs
vertically. Each line represents one complete equation; place the operation
that produces the following line in a separate right-hand column after a tall
vertical bar. For a continuing calculation of one expression, align at the
equals signs instead. Do not force simultaneous alignment at equivalence and
equals signs when this creates excessive horizontal gaps.

Use a separate left-aligned equation column in transformation chains so that
the first scientific expression of every line starts at the same horizontal
position. Keep an introductory sentence that directly announces or explains a
longer transformation on the same PDF page as the transformation itself.

Choose one uniform row spacing for each complete transformation chain. Base it
on the tallest or most crowded line in that chain, increasing the spacing when
fractions, roots, stacked indices, or similar constructions need more room.
Never vary the row spacing within one transformation chain. For chains with
tall scientific expressions, add the same explicit vertical space after
every row; changing only an array strut or `\arraystretch` may not create
visible clearance where fractions and roots already determine the row height.

Provide robust central shortcuts where useful, e.g. `\R`, `\N`, `\Q`, `\Z`, `\C`. `siunitx` may be available but is not a core requirement.

Provide calm semantic styling at least for Definition, Merke/Key Point, Beispiel/Example; Satz/Theorem and Hinweis/Remark are also reasonable. Proofs remain visually restrained initially.

Number `KeyPointBox` and `TheoremBox` independently within each chapter, so
their numbering starts with 1.1, 1.2, and so on in the first chapter.
Number `RemarkBox` independently within each chapter as well. Every remark
box also receives a concise descriptive heading through the `remark title`
option, so the automatic number remains visible. Preserve existing titles.

Prefer chapter/section/subsection numbering. Do not introduce `1.1.1.1`-style visible numbering without a concrete need.

## 10. Handwritten notes
`../_shared/legacy/Skript/` is a temporary inbox only.

Workflow:
1. read/interpret the note;
2. choose a short semantic content path if needed;
3. transfer content into approved German LaTeX source;
4. compile and verify;
5. ensure transfer is complete;
6. preserve the original in the shared legacy folder; remove only on explicit request.

Do not permanently retain redundant handwritten material and never delete it before successful transfer/verification.

## 11. Compilation, Git, and generated files
Validate proportionally to the change.

For shared infrastructure changes (`common/*.tex`, language/cloze logic, page style, title page, boxes, shared TikZ infrastructure), run:
```powershell
.\tools\build-all.ps1
```
and require all currently enabled builds to succeed.

If only German prose changes, compile at least affected German variant(s); do not synchronize English unless requested. After English sync, compile relevant English variants.

After visual/layout/TikZ/cloze/title-page changes, visually inspect affected PDF pages when tooling permits. Fix LaTeX errors and meaningful warnings before completion.

Codex may inspect `git status`, `git diff`, and `git log`. Do not commit, push, or publish changes unless explicitly asked. Before handing back substantial work, summarize meaningful changes and `git status`.

Keep generated LaTeX artifacts, logs, and auxiliary files out of source control.
The `build/` folder may contain the final PDFs and their `.synctex.gz` source
maps; the source maps are needed by the PDF viewer to jump from a PDF position
to the corresponding TeX location. Store all other auxiliary files, logs, and
caches under the user's local temporary folder. As an explicit project
exception, version exactly the four deliverables `build-de.pdf`,
`build-de-cloze.pdf`, `build-en.pdf`, and `build-en-cloze.pdf` from `build/`;
ignore all `.synctex.gz` files and every other generated PDF. Source,
configuration, documentation, and required branding assets belong in the
repository.

## 12. Legacy, README, and scope discipline
Except for the temporary inbox under `../_shared/legacy/Skript/`, files under `legacy/` are historical references only. Do not include them in normal builds or copy their package setup wholesale. They may inform fonts, colors, and prior author conventions.

Keep `README.md` concise and human-facing. Explain project structure, the four
supported build variants and which are currently enabled, `tools/build-all.ps1`,
German-master/English-sync workflow, `common/config.tex`, branding, cloze usage,
handwritten-note workflow, and independent semantic filenames.

When multiple technical solutions are valid, prefer the simpler, more maintainable one. Resolve ordinary implementation choices independently; ask only when the intended content or scope is unclear.
