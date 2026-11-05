<h1 align="center">DHH was right</h1>

<p align="center"><b>The best ideas of many web frameworks, in compiled, typed code.</b></p>

---

The name comes from RailsConf 2026, but we do not follow only Rails. This org
takes ideas from Rails, Django, PocketBase, Next.js and Astro, builds a web
stack from them, and finds out how far it gets in Rust:

- **Compiled, statically typed languages.** Rust on the server, TypeScript in
  the browser. These languages suit LLM work best: the compiler and the types
  catch the mistakes of the model before the code runs.
- **HTML over the wire.** The server renders. The client swaps fragments.
- **One database.** Postgres holds the data, the queue, the cache and the
  realtime fan-out.
- **One framework that hands you the whole stack**, from routes to background
  jobs to an admin.

We add one claim of our own, from [d2s](https://github.com/IxDay/d2s):
**ready for day 2 from day 1.** Twelve-factor config, logs on stdout, health
probes, graceful shutdown and deploy checks come in the box, not in a
later sprint.

> **Status.** Most of this code is vibe coded: written with an LLM, as a
> thought exercise. We use it for internal products where mission criticality
> is not needed. Read it, take ideas from it, but do not bet a business on it.

## The stack

| Repo | What it is |
|---|---|
| [**brocanth**](https://github.com/DHHwasRight/brocanth) | The framework. HTML-first apps and API services, Postgres-first, day-2 ready. Routes, models, migrations, policies, jobs, cache, realtime, auth, admin. |
| [**rsx**](https://github.com/DHHwasRight/rsx) | Compile-time HTML templates. A `.rsx` file is Rust, except that a function returning `Element` has a markup body. |
| [**jt**](https://github.com/DHHwasRight/jt) | Compile-time JSON templates. JSON with holes, compiled into straight-line writes. |
| [**zod**](https://github.com/DHHwasRight/zod) | Schemas that a literal must satisfy at compile time and input must satisfy at run time. |
| [**strata**](https://github.com/DHHwasRight/strata) | Layered async caching that reads like memoization. |
| [**htmx**](https://github.com/DHHwasRight/htmx) | dp-swap: partial page updates in TypeScript, with no dependencies. |
| [**prerender**](https://github.com/DHHwasRight/prerender) | A static site generator. Every route is built as a full document and as a fragment per layout depth. |
| [**depoth**](https://github.com/DHHwasRight/depoth) | A static content framework. Templates compile; content does not. |

## Start small, move out as you grow

Small apps run on one Postgres and one binary. Each piece sits behind a trait,
so when one part outgrows Postgres you move only that part: the queue and the
cache sit behind traits, so an external broker or cache store can replace
the Postgres one. The rest of the app does not change.

## How it is built

Mistakes should be compile errors. A misspelled column in a policy, a missing
translation key, or a template that does not type-check fails the build, not
the request. That rule also makes the code easy for a model to write, which
is how most of it got written.
