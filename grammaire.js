(() => {
  const grammarSources = [
    "exo/presente-indicativo.json",
    "exo/preterito-perfecto.json",
    "exo/preterito-indefinido.json",
    "exo/imperfecto.json",
    "exo/pluscuamperfecto.json",
    "exo/futuro.json",
    "exo/condicional.json",
    "exo/imperativo.json",
    "exo/subjonctif-imparfait.json",
    "exo/subjonctif.json",
    "exo/como-si.json",
    "exo/hypothese.json",
    "exo/comparatifs.json",
    "exo/obligation.json",
    "exo/connecteurs.json",
  ];

  const courseSources = [
    "cours/presente-indicativo.json",
    "cours/preterito-perfecto.json",
    "cours/preterito-indefinido.json",
    "cours/imperfecto.json",
    "cours/pluscuamperfecto.json",
    "cours/futuro.json",
    "cours/condicional.json",
    "cours/imperativo.json",
    "cours/subjonctif.json",
    "cours/subjonctif-imparfait.json",
  ];

  const comparatifSectionIds = {
    Progression: "progression",
    Corrélatifs: "correlatifs",
    "Supériorité et infériorité": "superiorite",
    Égalité: "egalite",
  };

  const grammarGroups = [
    {
      title: "Temps de l'indicatif",
      ids: [
        "presente-indicativo",
        "preterito-perfecto",
        "preterito-indefinido",
        "imperfecto",
        "pluscuamperfecto",
        "futuro",
        "condicional",
      ],
    },
    {
      title: "Ordres et subjonctif",
      ids: ["imperativo", "subjonctif", "subjonctif-imparfait"],
    },
    {
      title: "Hypothèse et irréel",
      ids: ["hypothese", "como-si"],
    },
    {
      title: "Comparatifs",
      ids: [
        "comparatifs::progression",
        "comparatifs::correlatifs",
        "comparatifs::superiorite",
        "comparatifs::egalite",
      ],
    },
    {
      title: "Structures utiles",
      ids: ["obligation", "connecteurs"],
    },
  ];

  let grammarTopics = [];
  let grammarLoadState = "idle";
  let grammarLoadError = "";
  let activeGrammarTopicId = "";

  async function loadGrammarTopics() {
    if (grammarLoadState === "loaded" || grammarLoadState === "loading") return;
    grammarLoadState = "loading";

    try {
      const responses = await Promise.all(
        grammarSources.map(async (source) => {
          const response = await fetch(source);
          if (!response.ok) throw new Error(`Impossible de charger ${source}`);
          return response.json();
        }),
      );

      const courseResponses = await Promise.all(
        courseSources.map(async (source) => {
          const response = await fetch(source);
          if (!response.ok) throw new Error(`Impossible de charger ${source}`);
          return response.json();
        }),
      );
      const coursesById = new Map(courseResponses.map((course) => [course.topicId, course]));

      grammarTopics = responses.flatMap((topic) => {
        if (topic.id !== "comparatifs" || !Array.isArray(topic.sections) || !topic.sections.length) {
          return [{ ...topic, course: coursesById.get(topic.id) || null }];
        }

        return topic.sections.map((section) => {
          const exercisesById = new Map((topic.exercises || []).map((exercise) => [exercise.id, exercise]));
          const exercises = (section.exerciseIds || [])
            .map((id) => exercisesById.get(id))
            .filter(Boolean);

          return {
            id: `comparatifs::${comparatifSectionIds[section.title] || section.title.toLowerCase().replace(/[^a-z0-9]+/g, "-")}`,
            title: section.title,
            subtitle: section.subtitle || "",
            rule: topic.rule,
            examples: section.examples || topic.examples,
            exercises,
          };
        });
      });

      activeGrammarTopicId = grammarTopics[0]?.id || "";
      grammarLoadState = "loaded";
    } catch (error) {
      grammarLoadState = "error";
      grammarLoadError = error.message || "Erreur de chargement des exercices.";
    }

    window.dispatchEvent(new CustomEvent("grammar:loaded"));
  }

  function getActiveTopic() {
    return grammarTopics.find((topic) => topic.id === activeGrammarTopicId) || grammarTopics[0] || null;
  }

  function textForExample(example) {
    if (!example) return "";
    if (typeof example === "string") return example;
    if (example.sentence && example.meaning) return `${example.sentence} (${example.meaning})`;
    if (example.exemple && example.formule) return `${example.formule} : ${example.exemple}`;
    if (example.es && example.fr) return `${example.es} (${example.fr})`;
    return Object.values(example).filter(Boolean).join(" - ");
  }

  function buildListHtml(items) {
    if (!Array.isArray(items) || !items.length) return "";
    return `<ul>${items.map((item) => `<li>${item}</li>`).join("")}</ul>`;
  }

  function buildEndingsHtml(endings) {
    if (!Array.isArray(endings) || !endings.length) return "";
    return endings
      .map(
        (ending) => `
          <div class="grammar-ending-card">
            <strong>${ending.group}</strong>
            <span>${(ending.forms || []).join(" · ")}</span>
          </div>
        `,
      )
      .join("");
  }

  function buildIrregularsHtml(irregulars) {
    if (!Array.isArray(irregulars) || !irregulars.length) return "";
    return `
      <div class="grammar-course-section grammar-irregulars">
        <h3>Irréguliers à connaître</h3>
        <div class="grammar-irregular-grid">
          ${irregulars
            .map(
              (item) => `
                <div class="grammar-irregular-card">
                  <strong>${item.pattern || "Cas irrégulier"}</strong>
                  ${item.verbs?.length ? `<span>${item.verbs.join(" · ")}</span>` : ""}
                  ${item.example ? `<p>${item.example}</p>` : ""}
                </div>
              `,
            )
            .join("")}
        </div>
      </div>
    `;
  }

  function buildCourseHtml(course) {
    if (!course) return "";
    return `
      <div class="analysis-card grammar-course">
        <div class="grammar-course-head">
          <span class="pill">cours</span>
          <h3>${course.title}</h3>
        </div>

        ${course.use ? `<p class="grammar-course-use">${course.use}</p>` : ""}

        <div class="grammar-course-grid">
          <section class="grammar-course-section">
            <h3>Formation</h3>
            ${buildListHtml(course.formation)}
          </section>

          <section class="grammar-course-section">
            <h3>Terminaisons</h3>
            <div class="grammar-ending-grid">${buildEndingsHtml(course.endings)}</div>
          </section>
        </div>

        ${buildIrregularsHtml(course.irregulars)}

        ${
          course.tips?.length || course.miniExamples?.length
            ? `
              <div class="grammar-course-grid">
                <section class="grammar-course-section">
                  <h3>À retenir</h3>
                  ${buildListHtml(course.tips)}
                </section>
                <section class="grammar-course-section">
                  <h3>Mini-exemples</h3>
                  ${buildListHtml(course.miniExamples)}
                </section>
              </div>
            `
            : ""
        }
      </div>
    `;
  }

  function buildExerciseHtml(exercise, index) {
    return `
      <details class="grammar-exercise">
        <summary>
          <span class="pill">${String(index + 1).padStart(2, "0")}</span>
          <strong>${exercise.prompt}</strong>
        </summary>
        <div class="grammar-answer">
          <p><span>Indice</span>${exercise.hint || "Relis la règle puis repère le déclencheur."}</p>
          <p><span>Réponse</span>${exercise.answer}</p>
        </div>
      </details>
    `;
  }

  function buildTopicButtonHtml(item, activeTopic) {
    return `
      <button
        class="grammar-topic ${item.id === activeTopic.id ? "active" : ""}"
        type="button"
        data-grammar-topic="${item.id}"
      >
        <strong>${item.title}</strong>
        <span>${item.exercises?.length || 0} exercices</span>
      </button>
    `;
  }

  function buildTopicListHtml(activeTopic) {
    const topicsById = new Map(grammarTopics.map((item) => [item.id, item]));
    const groupedIds = new Set(grammarGroups.flatMap((group) => group.ids));

    const groupedHtml = grammarGroups
      .map((group) => {
        const topics = group.ids.map((id) => topicsById.get(id)).filter(Boolean);
        if (!topics.length) return "";

        return `
          <div class="grammar-topic-group">
            <div class="grammar-topic-separator">${group.title}</div>
            ${topics.map((item) => buildTopicButtonHtml(item, activeTopic)).join("")}
          </div>
        `;
      })
      .join("");

    const ungroupedTopics = grammarTopics.filter((item) => !groupedIds.has(item.id));
    if (!ungroupedTopics.length) return groupedHtml;

    return `
      ${groupedHtml}
      <div class="grammar-topic-group">
        <div class="grammar-topic-separator">Autres</div>
        ${ungroupedTopics.map((item) => buildTopicButtonHtml(item, activeTopic)).join("")}
      </div>
    `;
  }

  function buildGrammarHtml() {
    loadGrammarTopics();

    if (grammarLoadState === "idle" || grammarLoadState === "loading") {
      return `
        <div class="chapter-header">
          <div>
            <p class="kicker">Grammaire</p>
            <h1 class="chapter-title">Reviser les points de grammaire</h1>
            <p class="chapter-intro">Chargement des exercices...</p>
          </div>
        </div>
      `;
    }

    if (grammarLoadState === "error") {
      return `
        <div class="note-box">
          <h3>Exercices indisponibles</h3>
          <p>${grammarLoadError}</p>
        </div>
      `;
    }

    const topic = getActiveTopic();
    if (!topic) {
      return `
        <div class="note-box">
          <h3>Aucun thème</h3>
          <p>Aucun exercice de grammaire n'a encore ete ajoute.</p>
        </div>
      `;
    }

    return `
      <div class="chapter-header">
        <div>
          <p class="kicker">Grammaire</p>
          <h1 class="chapter-title">Reviser les points de grammaire</h1>
          <p class="chapter-intro">Des exercices courts, classes par theme, a partir de ce qui revient dans les repassos.</p>
        </div>
        <div class="chapter-tools">
          <button class="nav-button" type="button" data-home>Tout voir</button>
        </div>
      </div>

      <div class="grammar-layout">
        <aside class="grammar-topic-list" aria-label="Themes de grammaire">
          ${buildTopicListHtml(topic)}
        </aside>

        <article class="grammar-panel">
          <div class="analysis-card grammar-rule">
            <span class="pill">${topic.exercises?.length || 0} exercices</span>
            <h2>${topic.title}</h2>
            ${topic.subtitle ? `<p class="grammar-subtitle">${topic.subtitle}</p>` : ""}
            <p>${topic.rule}</p>
            <div class="grammar-examples">
              ${(topic.examples || []).map((example) => `<span>${textForExample(example)}</span>`).join("")}
            </div>
          </div>

          ${buildCourseHtml(topic.course)}

          <div class="grammar-exercise-list">${(topic.exercises || []).map(buildExerciseHtml).join("")}</div>
        </article>
      </div>
    `;
  }

  document.addEventListener("click", (event) => {
    const topicTarget = event.target.closest("[data-grammar-topic]");
    if (!topicTarget) return;

    activeGrammarTopicId = topicTarget.dataset.grammarTopic;
    const grammarView = document.querySelector("#grammarView");
    if (grammarView) grammarView.innerHTML = buildGrammarHtml();
  });

  window.addEventListener("grammar:loaded", () => {
    const grammarView = document.querySelector("#grammarView");
    if (!grammarView || grammarView.classList.contains("hidden")) return;
    grammarView.innerHTML = buildGrammarHtml();
  });

  window.buildGrammarHtml = buildGrammarHtml;
})();
