import {
  createContext,
  useContext,
  useState,
  ReactNode,
  useEffect,
} from "react";
import extra from "./sw.json";
import { patch } from "../services/api";
const sw: Record<string, string> = {
  Overview: "Muhtasari",
  "My courses": "Kozi zangu",
  "Assigned courses": "Kozi ulizopangiwa",
  "Learning materials": "Vifaa vya kujifunzia",
  Assignments: "Kazi za nyumbani",
  Quizzes: "Maswali ya mazoezi",
  "AI tutor": "Msaidizi wa masomo",
  "Learning pathways": "Njia za kujifunza",
  Performance: "Maendeleo",
  "My profile": "Wasifu wangu",
  Students: "Wanafunzi",
  "Review queue": "Mapendekezo ya kukagua",
  "Lesson planning": "Mipango ya masomo",
  Messages: "Ujumbe",
  Notifications: "Taarifa",
  "Linked students": "Wanafunzi waliounganishwa",
  Reports: "Ripoti",
  School: "Shule",
  Users: "Watumiaji",
  "Teacher assignments": "Upangaji wa walimu",
  "Parent links": "Uunganishaji wa wazazi",
  Subscriptions: "Usajili wa huduma",
  Payments: "Malipo",
  Plans: "Mipango",
  "Sign out": "Ondoka",
  "Sign in": "Ingia",
  Register: "Jisajili",
  "Email address": "Barua pepe",
  Password: "Nenosiri",
  "Full name": "Jina kamili",
  Role: "Jukumu",
  Student: "Mwanafunzi",
  Teacher: "Mwalimu",
  Parent: "Mzazi",
  "School administrator": "Msimamizi wa shule",
  "Save changes": "Hifadhi mabadiliko",
  Submit: "Wasilisha",
  Send: "Tuma",
  Cancel: "Ghairi",
  Approve: "Idhinisha",
  Reject: "Kataa",
  "Loading your workspace…": "Tunapakia taarifa zako…",
  "No records yet.": "Hakuna taarifa bado.",
  "Search courses": "Tafuta kozi",
  "Continue learning": "Endelea kujifunza",
  "Your learning at a glance": "Muhtasari wa masomo yako",
  "A little progress, every day.": "Hatua ndogo kila siku.",
  Course: "Kozi",
  Subject: "Somo",
  Title: "Kichwa",
  Description: "Maelezo",
  Instructions: "Maelekezo",
  Content: "Maudhui",
  "Create course": "Unda kozi",
  "Create assignment": "Unda kazi",
  "Add material": "Ongeza nyenzo",
  "View report": "Tazama ripoti",
  "Download report": "Pakua ripoti",
  "School average": "Wastani wa shule",
  "Average score": "Wastani wa alama",
  "Learning activity": "Shughuli za kujifunza",
  "Approved pathways": "Njia zilizoidhinishwa",
  "Ask a question": "Uliza swali",
  "Ask tutor": "Uliza msaidizi",
  "Choose a subject and ask about a topic.":
    "Chagua somo na uulize kuhusu mada.",
  "Your next steps": "Hatua zako zinazofuata",
  "Teacher reviewed": "Imekaguliwa na mwalimu",
  "Draft assistance": "Msaada wa rasimu",
  "Generate draft": "Tengeneza rasimu",
  "Generate pathway": "Tengeneza njia",
  "Review comment": "Maoni ya ukaguzi",
  Regenerate: "Tengeneza tena",
  Archive: "Hifadhi kumbukumbu",
  "Mark as viewed": "Weka kama imesomwa",
  Topic: "Mada",
  Activate: "Washa",
  Deactivate: "Zima",
  Active: "Inatumika",
  Pending: "Inasubiri",
  "Request link": "Omba uunganishaji",
  "Student ID": "Namba ya mwanafunzi",
  Recipient: "Mpokeaji",
  Message: "Ujumbe",
  "Choose a student": "Chagua mwanafunzi",
  Interests: "Mapendeleo",
  "Learning preference": "Njia ya kujifunza",
  Reading: "Kusoma",
  Video: "Video",
  Practice: "Mazoezi",
  Language: "Lugha",
  Home: "Mwanzo",
  About: "Kuhusu sisi",
  Features: "Huduma",
  Contact: "Mawasiliano",
  "Get started": "Anza sasa",
  "View courses": "Tazama kozi",
  "Teacher review required": "Ukaguzi wa mwalimu unahitajika",
  "Academic demonstration": "Mfano wa kielimu",
  "Simulated payment": "Malipo ya majaribio",
  "Verify payment": "Hakiki malipo",
  "Choose plan": "Chagua mpango",
  Receipt: "Risiti",
  "Premium active": "Huduma ya ziada inatumika",
  "Basic access": "Huduma ya msingi",
  Enrollment: "Usajili wa kozi",
  "Enroll student": "Sajili mwanafunzi",
  "Assign teacher": "Pangia mwalimu",
  Region: "Mkoa",
  "Update school": "Sasisha shule",
  "Create user": "Unda mtumiaji",
  "Audit trail": "Kumbukumbu za vitendo",
  "Welcome back": "Karibu tena",
  Score: "Alama",
  Feedback: "Mrejesho",
  "Save reviewed quiz": "Hifadhi maswali yaliyokaguliwa",
  "Save reviewed lesson": "Hifadhi somo lililokaguliwa",
  Form: "Kidato",
  "Print report": "Chapisha ripoti",
  "Start quiz": "Anza maswali",
  "Submit answers": "Wasilisha majibu",
  "Study notes": "Maelezo ya masomo",
  Download: "Pakua",
  Read: "Soma",
  "Create plan": "Unda mpango",
  Suspend: "Simamisha",
  Restore: "Rudisha",
  "Price in TZS": "Bei kwa TZS",
  "Duration in days": "Muda kwa siku",
  Create: "Unda",
  "Pending review": "Inasubiri ukaguzi",
  "Reviewed learning, connected schools.":
    "Masomo yaliyokaguliwa, shule zilizounganishwa.",
};
const Context = createContext<{
  lang: string;
  t: (s: string) => string;
  toggle: () => void;
}>(null!);
export function tr(
  value: string,
  language = localStorage.getItem("eduai-language") || "en",
): string {
  const key = value.trim();
  if (language !== "sw") return value;
  const translated = (extra as Record<string, string>)[key] || sw[key];
  if (translated) return value.replace(key, translated);
  if (/^Only \d+ matching bank/.test(key))
    return "Benki ina maswali machache yanayolingana; ongeza maswali yaliyokaguliwa mwenyewe.";
  if (key.startsWith("Local generation unavailable"))
    return "Uzalishaji wa ndani haupatikani; benki ya maswali imetumika.";
  return value;
}
export function Trans({ value }: { value: string }) {
  const { t } = useI18n();
  return <>{t(value)}</>;
}
export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, setLang] = useState(
    localStorage.getItem("eduai-language") || "en",
  );
  useEffect(() => {
    localStorage.setItem("eduai-language", lang);
    document.documentElement.lang = lang;
  }, [lang]);
  useEffect(() => {
    const sync = () => setLang(localStorage.getItem("eduai-language") || "en");
    window.addEventListener("eduai-language", sync);
    return () => window.removeEventListener("eduai-language", sync);
  }, []);
  return (
    <Context.Provider
      value={{
        lang,
        t: (s) => tr(s, lang),
        toggle: () => {
          const next = lang === "en" ? "sw" : "en";
          setLang(next);
          localStorage.setItem("eduai-language", next);
          if (sessionStorage.getItem("eduai-token"))
            patch("/me/language", { language: next })
              .then((u) => {
                sessionStorage.setItem("eduai-user", JSON.stringify(u));
              })
              .catch(() => {});
        },
      }}
    >
      {children}
    </Context.Provider>
  );
}
export const useI18n = () => useContext(Context);
