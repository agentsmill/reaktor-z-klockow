// Single source of truth for the narration (Polish).
// `show` is what captions display; `say` (optional) is what the TTS reads when an
// acronym needs a phonetic spelling. Both must have the same number of tokens.
// Cues name the words whose timing triggers visuals (prefix match, so Polish
// inflections still hit; `nth` picks a later occurrence). List cues in narration order.
// Dependency-free on purpose: imported by Node asset scripts too.

export type SceneId =
  | "intro"
  | "smr"
  | "poland"
  | "fission"
  | "control"
  | "power"
  | "circulation"
  | "safety"
  | "why"
  | "outro";

export type CueDef = { id: string; word: string; nth?: number };

export type SceneDef = {
  id: SceneId;
  /** Short chapter label shown top-left ("" = hidden). */
  chip: string;
  show: string;
  say?: string;
  cues: CueDef[];
  /** Frames before the voiceover starts (default DEFAULT_LEAD_IN). */
  leadIn?: number;
  /** Frames held after the voiceover ends (default DEFAULT_TAIL). */
  tail?: number;
};

export const sayText = (scene: SceneDef): string => scene.say ?? scene.show;

export const SCENES: SceneDef[] = [
  {
    id: "intro",
    chip: "",
    show: "Mały reaktor jądrowy, który może zasilić setki tysięcy domów. Jak to działa? Zbudujmy go z klocków!",
    cues: [
      { id: "homes", word: "setki" },
      { id: "question", word: "Jak" },
      { id: "build", word: "Zbudujmy" },
    ],
    leadIn: 45,
    tail: 30,
  },
  {
    id: "smr",
    chip: "Co to jest SMR?",
    show: "SMR to mały reaktor modułowy: kilka razy mniejszy od dużego bloku jądrowego i budowany z gotowych modułów z fabryki — trochę jak z klocków.",
    say: "Es-em-er to mały reaktor modułowy: kilka razy mniejszy od dużego bloku jądrowego i budowany z gotowych modułów z fabryki — trochę jak z klocków.",
    cues: [
      { id: "small", word: "mały" },
      { id: "reactor", word: "reaktor" },
      { id: "modular", word: "modułowy" },
      { id: "compare", word: "kilka" },
      { id: "big", word: "dużego" },
      { id: "modules", word: "modułów" },
      { id: "factory", word: "fabryki" },
      { id: "bricks", word: "klocków" },
    ],
  },
  {
    id: "poland",
    chip: "Polski projekt",
    show: "W Polsce takie reaktory chce budować firma Michała Sołowowa — część z nich wspólnie z Orlenem. Wybrano technologię BWRX-300 o mocy trzystu megawatów. Projekt wsparli też polscy przedsiębiorcy: zainwestują w firmę Sołowowa około pół miliarda złotych.",
    say: "W Polsce takie reaktory chce budować firma Michała Sołowowa — część z nich wspólnie z Orlenem. Wybrano technologię be-wu-er-iks-trzysta o mocy trzystu megawatów. Projekt wsparli też polscy przedsiębiorcy: zainwestują w firmę Sołowowa około pół miliarda złotych.",
    cues: [
      { id: "map", word: "Polsce" },
      { id: "solowow", word: "Michała" },
      { id: "orlen", word: "Orlenem" },
      { id: "tech", word: "technologię" },
      { id: "power", word: "trzystu" },
      { id: "investors", word: "przedsiębiorcy" },
      { id: "amount", word: "pół" },
    ],
  },
  {
    id: "fission",
    chip: "Rozszczepienie",
    show: "Paliwem są małe pastylki uranu. Gdy neutron trafi w jądro uranu, jądro rozpada się na dwa mniejsze — to rozszczepienie. Uwalnia się mnóstwo ciepła i dwa, trzy nowe neutrony, które rozbijają kolejne jądra. To reakcja łańcuchowa. Jedna pastylka daje tyle energii, co tona węgla.",
    cues: [
      { id: "pellet", word: "pastylki" },
      { id: "neutron", word: "neutron" },
      { id: "hit", word: "trafi" },
      { id: "split", word: "rozpada" },
      { id: "fission", word: "rozszczepienie" },
      { id: "heat", word: "ciepła" },
      { id: "newNeutrons", word: "nowe" },
      { id: "chain", word: "kolejne" },
      { id: "chainLabel", word: "łańcuchowa" },
      { id: "onePellet", word: "Jedna" },
      { id: "coal", word: "tona" },
    ],
  },
  {
    id: "control",
    chip: "Kontrola reakcji",
    show: "Nadmiar neutronów pochłaniają pręty sterujące, wsuwane od dołu. Gdy każde rozszczepienie wywołuje dokładnie jedno kolejne, reaktor pracuje stabilnie.",
    cues: [
      { id: "excess", word: "Nadmiar" },
      { id: "absorb", word: "pochłaniają" },
      { id: "rods", word: "pręty" },
      { id: "fromBelow", word: "wsuwane" },
      { id: "exactlyOne", word: "dokładnie" },
      { id: "stable", word: "stabilnie" },
    ],
  },
  {
    id: "power",
    chip: "Jak powstaje prąd",
    show: "Ciepło zagotowuje wodę wprost w reaktorze — stąd nazwa: reaktor z wrzącą wodą. Para rozkręca turbinę, a turbina napędza generator prądu. Jak para z czajnika, która kręci wiatraczkiem. Potem para skrapla się i wraca do reaktora jako woda.",
    cues: [
      { id: "boil", word: "zagotowuje" },
      { id: "name", word: "wrzącą" },
      { id: "steam", word: "Para" },
      { id: "turbine", word: "turbinę" },
      { id: "generator", word: "generator" },
      { id: "electricity", word: "prądu" },
      { id: "kettle", word: "czajnika" },
      { id: "condense", word: "skrapla" },
      { id: "return", word: "wraca" },
    ],
  },
  {
    id: "circulation",
    chip: "Naturalny obieg",
    show: "Co ciekawe, w środku reaktora woda krąży bez pomp. Gorąca i pełna pary unosi się wysokim kominem, a chłodniejsza opada po bokach — jak powietrze nad kaloryferem.",
    cues: [
      { id: "inside", word: "środku" },
      { id: "noPumps", word: "pomp" },
      { id: "hot", word: "Gorąca" },
      { id: "rise", word: "unosi" },
      { id: "chimney", word: "kominem" },
      { id: "sink", word: "opada" },
      { id: "radiator", word: "kaloryferem" },
    ],
  },
  {
    id: "safety",
    chip: "Bezpieczeństwo",
    show: "A co, jeśli zabraknie prądu? Pręty wsuwają się automatycznie i reakcja gaśnie. Paliwo nadal trochę grzeje, więc ciepło odbierają skraplacze w basenach z wodą nad reaktorem. Para unosi się, skrapla, a woda sama spływa z powrotem. Bez prądu i bez ludzi — przez co najmniej siedem dni. A sam reaktor stoi głęboko pod ziemią.",
    cues: [
      { id: "blackout", word: "zabraknie" },
      { id: "rodsIn", word: "wsuwają" },
      { id: "off", word: "gaśnie" },
      { id: "decay", word: "grzeje" },
      { id: "ic", word: "skraplacze" },
      { id: "pools", word: "basenach" },
      { id: "rise", word: "unosi" },
      { id: "back", word: "spływa" },
      { id: "noPower", word: "Bez" },
      { id: "days", word: "siedem" },
      { id: "underground", word: "ziemią" },
    ],
  },
  {
    id: "why",
    chip: "Po co nam to?",
    show: "Taki reaktor daje prąd całą dobę, bez względu na pogodę, i nie emituje dwutlenku węgla podczas pracy. Może też zastąpić stare elektrownie węglowe.",
    cues: [
      { id: "allDay", word: "dobę" },
      { id: "weather", word: "pogodę" },
      { id: "co2", word: "dwutlenku" },
      { id: "replace", word: "zastąpić" },
    ],
  },
  {
    id: "outro",
    chip: "Podsumowanie",
    show: "Podsumujmy: uran daje ciepło, ciepło zamienia wodę w parę, para kręci turbiną, a turbina wytwarza prąd. Tak działa mały reaktor modułowy.",
    cues: [
      { id: "uranium", word: "uran" },
      { id: "heat", word: "ciepło" },
      { id: "steam", word: "parę" },
      { id: "turbine", word: "turbiną" },
      { id: "electricity", word: "prąd" },
      { id: "title", word: "Tak" },
    ],
    tail: 150,
  },
];
