# CS Study

A personal study app for computer science, built as an offline-capable web app for the iPhone home screen.
Each subject has modules made up of lessons (basic → advanced), and every lesson has practice questions.
Each question has a worked example, an explanation for every option and a link to further reading.

Subjects: System Design, Data Structures & Algorithms, Operating Systems, Computer Networks, Computer
Architecture, Programming Languages & Compilers, Security & Cryptography, Software Engineering, Theory &
Discrete Maths, Databases & SQL, Synth Building, Embedded Software, and React.
New modules follow `docs/new-module.md`; `docs/RESUME.md` records how the content was generated.

## Run it locally

```sh
./scripts/serve.sh
```

This validates and compiles the content, then serves the app on port 8000. It prints a URL you can open on
your iPhone while it's on the same Wi-Fi.

Offline mode needs HTTPS (or `localhost`), so an iPhone opening a LAN IP address needs HTTPS hosting, for example on GitHub
Pages. A desktop can use offline mode at `http://localhost:8000`. Over plain local Wi-Fi the app can load while connected; secure-context features such as service workers and clipboard access may be unavailable.

## Reading and examples

Lessons cover one small learning objective, usually 3–5 minutes, with a few questions about that unit.
When an older long lesson is split, its saved completion date carries into its shorter lessons. Each short
lesson can then be completed or revisited independently. Existing question answers and bookmarks remain,
and old lesson links lead to the first unfinished replacement (or the first replacement when all are complete).

The layout adapts to phone, tablet and desktop, with automatic dark mode and adjustable reading text.
Real-world analogies appear in optional cards labelled **Real-world analogy**. They start collapsed;
tap or use the keyboard to open one. Each comparison explains its technical mapping and limitations,
and the main explanation stays complete with the card closed.
Lessons include a section navigator. Example panels support copying and an expanded view with zoom;
real SVG diagrams use shapes, connectors and arrowheads, and keep the original text as a reference.
Wide diagrams scroll within their panel; Expand provides a larger view with zoom. Reading, diagrams and expansion work offline once the app is cached. Copy also depends on browser clipboard support, permission and a secure context.
Code comments explain meaningful operations and what demonstrated outputs show; copying an example includes
those comments.

Run `node --test scripts/test-renderer.mjs scripts/test-diagrams.mjs` to check example escaping, source preservation and safe
rendering inside quiz choices, diagram topology and all generated diagram definitions. See `CONTENT_SPEC.md` for diagram and sequential-flow authoring.

## Embedded Software beginner path

Start with **Embedded Software** on the Learn screen. This subject assumes basic programming knowledge
and explains the C and hardware vocabulary as it goes. Follow the modules in order: firmware foundations,
C and device I/O, timing and serial buses, then debugging and a small project.

You can learn and test the portable logic on a computer before using a board. Hardware examples distinguish
the chip, board and SDK requirements; follow the relevant device manuals when connecting real hardware.
Every lesson includes worked practice questions. Optional real-world analogies start collapsed.

## React concepts: beginner to intermediate

Choose **React** on the Learn screen. Start with components and JSX, then work through state updates,
controlled forms and shared state. Finish with Hooks, refs, effects and cleanup, data-fetching lifecycles,
context, performance trade-offs and a small searchable task-list project.

The course assumes basic JavaScript and explains additional syntax as it appears. Each short lesson has
worked practice questions and a glossary; useful analogies remain optional. Examples use function components
and Hooks, and are checked with React and React DOM 19.3.1 in a separate test harness. React is not a runtime
dependency of this study app. See `docs/react-concepts-brief.md` for scope and prerequisites, and
`docs/react-concepts-verification.json` for independent review and validation evidence.

## Practice completed lessons

In **Practice**, choose **Completed lessons only** to use lessons you've marked complete in the selected
subject. Under **Time since completion**, choose **Day range** and set the minimum and maximum with the
sliders or day inputs. A range of **1–10** includes lessons completed yesterday through ten days ago;
**0** includes today. Both limits are included, and age counts local calendar days from the saved
completion date. **Any time** includes all completed lessons.

The mode and day range are remembered on this device and work with the module, difficulty and answer
filters. Answering a question does not reset its lesson's completion date. Unmarking and completing the
lesson again gives it a new completion date.

## Live app

**https://alfiegormley.github.io/cs-study-app/** is hosted on GitHub Pages from the `main` branch.

To publish changes: `node scripts/build.mjs`, then commit (including `data/`, `assets.js` and the stamped
version in `sw.js`) and `git push`.
Pages redeploys in a minute or two, and installed copies update the next time they're opened online.

The update notice stays visible until you tap **Reload**. If a browser copy gets stuck on an older
version, open [the update page](https://alfiegormley.github.io/cs-study-app/update.html) while online,
or use **Settings → Get the latest app version**. It downloads a fresh offline cache and preserves
the progress saved in that browser. Installed home-screen copies check for updates when reopened
or brought back into the foreground while online.

## Put it on your iPhone

1. Host the folder somewhere served over HTTPS (GitHub Pages works: Settings → Pages → deploy from branch).
2. Open the URL in **Safari** on the iPhone.
3. Tap **Share → Add to Home Screen**.
4. Open it online and check **Settings → Offline ready**. **Yes** means a service worker controls the page; it is not a fresh audit of every cached file. Initial installation must finish caching successfully. Reopen Settings if its display has not updated, then try reopening a lesson offline. Browser storage clearing or eviction can remove the cache; external reading links still require a connection.

Progress (completed lessons, answers, bookmarks, reading position) is saved in browser `localStorage` when storage is available. It belongs to that browser/origin, is not synced or backed up by the app, and can be cleared; another hostname or browser may show different progress.

## Adding or editing content

**Follow `docs/CONTENT_PROCESS.md` (mandatory).** Every module is written by one agent, fact-checked by a
separate one, and recorded in a stamped `verification.json`. The build enforces this.

See [CONTENT_SPEC.md](CONTENT_SPEC.md) for the format. After any change:

```sh
node scripts/build.mjs          # validate + compile content/ into data/ and assets.js
node scripts/check-links.mjs    # confirm every link still loads
```

Commit `data/`, `assets.js`, `diagram-catalog.js` and `docs/diagram-migration.json` along with the content. They're what the app actually loads, and the
version hash in `assets.js` tells installed copies to update.

## Layout

| Path | What it is |
|---|---|
| `index.html`, `app.js`, `styles.css`, `markdown.js` | The app UI (no framework or JavaScript bundler; content still requires its build step) |
| `sw.js`, `manifest.webmanifest`, `icons/` | Offline support and home-screen install |
| `content/<subject>/<NN-module>/` | Lesson Markdown and question JSON (source of truth) |
| `data/`, `assets.js` | Generated by `scripts/build.mjs` |
| `diagrams.js`, `diagram-key.js` | SVG renderers and catalogue lookup |
| `content/diagram-overrides.json` | Reviewed diagram definitions and source matches |
| `diagram-catalog.js`, `docs/diagram-migration.json` | Generated diagram catalogue and conversion report |

## Technical dictionary

Tap a dotted-underlined term in a lesson, question or explanation to open a short
 definition. Escape or the close button dismisses it. **Learn → Technical dictionary**
opens the searchable list. Definitions are available offline; external documentation
links need a connection. Answer choices and executable code are left untouched.

Definitions and aliases live in `glossary-data.js`; matching and popovers live in
`glossary.js`. After changes, run `node --test scripts/test-*.mjs` and
`node scripts/build.mjs` to update the offline assets.
