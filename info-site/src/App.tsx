import { useState } from "react";
import {
  Menu,
  X,
  Clock,
  HeartHandshake,
  Activity,
  Utensils,
  MessageSquare,
  BellRing,
  LayoutDashboard,
  Heart,
  ExternalLink,
} from "lucide-react";
import { FaGithub, FaLinkedin } from "react-icons/fa";
import heroImage from "./assets/woman4.png";
import christine from "./assets/christine.jpeg";
import tracey from "./assets/tracey.jpeg";
import david2 from "./assets/david2.jpeg";
import woman1 from "./assets/woman1.jpg";
import james from "./assets/james.jpeg";
import lynn from "./assets/lynn.jpeg";

/* ─── Data ─────────────────────────────────────────────────────────────── */

const NAV = [
  { label: "Problem", id: "problem" },
  { label: "Solution", id: "solution" },
  { label: "Who We Serve", id: "users" },
  { label: "Vision", id: "vision" },
  { label: "Team", id: "team" },
];

const PROBLEMS = [
  {
    icon: <Clock className="w-7 h-7" />,
    title: "The Three Delays",
    body: "Delays in deciding to seek care, reaching care, and receiving care remain the leading drivers of preventable maternal mortality across rural Kenya.",
    color: "#1d4ed8",
    bg: "#eff6ff",
  },
  {
    icon: <HeartHandshake className="w-7 h-7" />,
    title: "Stigma & Isolation",
    body: "Teenage mothers often avoid clinics due to social stigma, missing crucial antenatal visits that could catch life-threatening complications early.",
    color: "#ec4899",
    bg: "#fdf2f8",
  },
  {
    icon: <Activity className="w-7 h-7" />,
    title: "Episodic Care",
    body: "Mothers lack continuous guidance on danger signs and hyper-local nutrition between clinic visits, leaving critical gaps in their care journey.",
    color: "#0369a1",
    bg: "#f0f9ff",
  },
];

const FEATURES = [
  {
    icon: <Utensils className="w-6 h-6" />,
    label: "AI Nutrition Assistant",
    desc: "Generates locally-sourced, affordable meal plans based on trimester and local availability — grounded in Kenyan staple foods and seasonal produce.",
    accent: "#1d4ed8",
    lightBg: "#eff6ff",
  },
  {
    icon: <MessageSquare className="w-6 h-6" />,
    label: "Conversational Triage",
    desc: "Daily symptom check-ins via accessible platforms like WhatsApp to detect high-risk warning signs early, before they become emergencies.",
    accent: "#ec4899",
    lightBg: "#fdf2f8",
  },
  {
    icon: <BellRing className="w-6 h-6" />,
    label: "Automated Reminders",
    desc: "Gentle, culturally appropriate nudges for ANC clinic visits and daily supplements delivered in Swahili or local dialects.",
    accent: "#0369a1",
    lightBg: "#f0f9ff",
  },
  {
    icon: <LayoutDashboard className="w-6 h-6" />,
    label: "CHP Dashboard",
    desc: "Connects mothers directly to Community Health Promoters for targeted, proactive intervention — giving CHPs a real-time view of their cohorts.",
    accent: "#be185d",
    lightBg: "#fdf2f8",
  },
];

const TEAM = [
  {
    name: "Christine Odegi",
    role: "Product Lead & UX Researcher",
    photo: christine,
    linkedin: "https://www.linkedin.com/in/christine-awuor-odegi",
    github: "https://github.com/OdegiChristine",
  },
  {
    name: "Lynn Omae",
    role: "AI & Machine Learning Engineer",
    photo: lynn,
    linkedin: "https://www.linkedin.com/in/lynn-nyanduko-860174354?trk=contact-info",
    github: "https://github.com/LynnOmae",
  },
  {
    name: "James Moseti",
    role: "Fullstack Software Engineer",
    photo: james,
    linkedin: "https://linkedin.com/in/james-moseti",
    github: "https://github.com/james-moseti",
  },
  {
    name: "Tracey Ayuma",
    role: "Community Health & Data Analyst",
    photo: tracey,
    linkedin: "https://www.linkedin.com/in/tracey-isanya",
    github: "https://github.com/traceyuma",
  },
  {
    name: "David Nzambuli",
    role: "Backend Engineer & DevOps",
    photo: david2,
    linkedin: "https://www.linkedin.com/in/nzambuli",
    github: "https://github.com/broken555wheel",
  },
];

const PARTNERS = [
  { name: "JKUAT", href: "#" },
  { name: "JHUB Africa", href: "#" },
  { name: "Amref Health Africa", href: "#" },
];

/* ─── Helpers ───────────────────────────────────────────────────────────── */

function goto(id: string) {
  document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
}

/* ─── Components ────────────────────────────────────────────────────────── */

function SectionLabel({ children, pink }: { children: string; pink?: boolean }) {
  return (
    <p
      className="text-xs font-bold tracking-[0.18em] uppercase mb-3"
      style={{ color: pink ? "#ec4899" : "#1d4ed8" }}
    >
      {children}
    </p>
  );
}

function SectionHeading({ children }: { children: React.ReactNode }) {
  return (
    <h2
      className="text-3xl md:text-4xl font-extrabold text-[#0f172a] leading-tight"
      style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
    >
      {children}
    </h2>
  );
}

/* ─── App ────────────────────────────────────────────────────────────────── */

export default function App() {
  const [open, setOpen] = useState(false);

  return (
    <div
      className="min-h-screen bg-white text-[#0f172a]"
      style={{ fontFamily: "'DM Sans', sans-serif" }}
    >

      {/* ══ Navbar ══════════════════════════════════════════════════════════ */}
      <header className="fixed inset-x-0 top-0 z-50 bg-white border-b border-[#dbeafe]">
        <div className="max-w-6xl mx-auto px-5 h-16 flex items-center justify-between">

          {/* Logo */}
          <button
            onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
            className="flex items-center gap-2"
          >
            <span
              className="w-8 h-8 rounded-lg flex items-center justify-center"
              style={{ background: "#1d4ed8" }}
            >
              <Heart className="w-4 h-4 text-white" fill="white" />
            </span>
            <span
              className="text-base font-extrabold text-[#1d4ed8]"
              style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
            >
              Nurture
            </span>
          </button>

          {/* Desktop links */}
          <nav className="hidden md:flex items-center gap-7">
            {NAV.map((n) => (
              <button
                key={n.id}
                onClick={() => goto(n.id)}
                className="text-sm text-[#475569] hover:text-[#1d4ed8] transition-colors font-medium"
              >
                {n.label}
              </button>
            ))}
          </nav>

          {/* CTA */}
          <button
            onClick={() => goto("users")}
            className="hidden md:inline-flex items-center gap-1.5 px-5 py-2.5 rounded-full text-sm font-bold text-white"
            style={{ background: "#ec4899" }}
          >
            Join the Pilot
          </button>

          {/* Mobile toggle */}
          <button
            className="md:hidden text-[#1d4ed8]"
            onClick={() => setOpen(!open)}
            aria-label="Toggle menu"
          >
            {open ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile drawer */}
        {open && (
          <div className="md:hidden border-t border-[#dbeafe] bg-white px-5 py-5 flex flex-col gap-5">
            {NAV.map((n) => (
              <button
                key={n.id}
                onClick={() => { goto(n.id); setOpen(false); }}
                className="text-sm font-medium text-left text-[#0f172a] hover:text-[#1d4ed8] transition-colors"
              >
                {n.label}
              </button>
            ))}
            <button
              onClick={() => { goto("users"); setOpen(false); }}
              className="self-start px-5 py-2.5 rounded-full text-sm font-bold text-white"
              style={{ background: "#ec4899" }}
            >
              Join the Pilot
            </button>
          </div>
        )}
      </header>

      {/* ══ Hero ════════════════════════════════════════════════════════════ */}
      <section 
        className="pt-32 pb-20 px-5 bg-cover bg-center relative"
        style={{ backgroundImage: `url(${heroImage})` }}
      >
        {/* Overlay for better text readability */}
        <div className="absolute inset-0 bg-white/60" />
        
        <div className="max-w-4xl mx-auto text-center relative z-10">
          {/* Eyebrow badge */}
          {/* <span
            className="inline-block px-4 py-1.5 rounded-full text-xs font-bold tracking-widest uppercase mb-8 border"
            style={{ color: "#1d4ed8", borderColor: "#bfdbfe", background: "#eff6ff" }}
          >
            Maternal Health · Kenya
          </span> */}

          <h1
            className="text-4xl sm:text-5xl md:text-6xl font-extrabold leading-[1.08] mb-6 text-[#0f172a]"
            style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
          >
            Bridging the Gap in{" "}
            <span className="text-[#1d4ed8]">Maternal Health.</span>
          </h1>

          <p className="text-lg md:text-xl text-[#475569] max-w-2xl mx-auto mb-10 leading-relaxed">
            An AI-powered companion providing stigma-free, localized, and continuous care for
            adolescent mothers and women in marginalized Kenyan communities.
          </p>

          <button
            className="inline-flex items-center gap-2 px-8 py-4 rounded-full text-base font-bold text-white shadow-md hover:opacity-90 transition-opacity"
            style={{ background: "#ec4899" }}
          >
            Join the Pilot
          </button>

          {/* Trust strip */}
          <div className="mt-16 flex flex-col sm:flex-row items-center justify-center gap-6 sm:gap-10">
            {[
              { n: "362", unit: "deaths per 100k", label: "Kenya maternal mortality ratio" },
              { n: "45%", unit: "of births", label: "have no skilled attendant" },
              { n: "70%", unit: "of Kenyans", label: "use mobile phones" },
            ].map((s) => (
              <div key={s.label} className="text-center">
                <p
                  className="text-3xl font-extrabold text-[#1d4ed8] leading-none"
                  style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
                >
                  {s.n}
                </p>
                <p className="text-[11px] text-[#ec4899] font-semibold uppercase tracking-widest mt-0.5">{s.unit}</p>
                <p className="text-xs text-[#64748b] mt-0.5">{s.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ══ Problem ═════════════════════════════════════════════════════════ */}
      <section id="problem" className="py-20 px-5" style={{ background: "#f8fafc" }}>
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <SectionLabel pink>The Crisis</SectionLabel>
            <SectionHeading>The Maternal Health Crisis</SectionHeading>
            <p className="mt-4 text-[#475569] max-w-xl mx-auto text-base leading-relaxed">
              Kenya's maternal mortality rate remains tragically high — driven by three systemic, addressable failures.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {PROBLEMS.map((p) => (
              <div
                key={p.title}
                className="rounded-2xl border p-7 flex flex-col gap-5"
                style={{ background: p.bg, borderColor: p.color + "22" }}
              >
                <span
                  className="w-14 h-14 rounded-2xl flex items-center justify-center shrink-0"
                  style={{ background: p.color + "15", color: p.color }}
                >
                  {p.icon}
                </span>
                <div>
                  <h3
                    className="text-lg font-bold mb-2"
                    style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", color: "#0f172a" }}
                  >
                    {p.title}
                  </h3>
                  <p className="text-sm text-[#475569] leading-relaxed">{p.body}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ══ Solution ════════════════════════════════════════════════════════ */}
      <section id="solution" className="py-20 px-5 bg-white">
        <div className="max-w-6xl mx-auto">
          <div className="mb-12 max-w-2xl">
            <SectionLabel>The Solution</SectionLabel>
            <SectionHeading>Our Solution: Continuous,&nbsp;Stigma-Free Support</SectionHeading>
            <p className="mt-4 text-[#475569] text-base leading-relaxed">
              The Maternal Companion meets mothers where they are — on their phones, in their
              language, with care tailored to their community.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            {FEATURES.map((f) => (
              <div
                key={f.label}
                className="rounded-2xl border p-7 flex gap-5 items-start"
                style={{ borderColor: f.accent + "22", background: f.lightBg }}
              >
                <span
                  className="w-12 h-12 rounded-xl flex items-center justify-center shrink-0"
                  style={{ background: f.accent + "18", color: f.accent }}
                >
                  {f.icon}
                </span>
                <div>
                  <h3
                    className="text-base font-bold mb-1.5"
                    style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", color: "#0f172a" }}
                  >
                    {f.label}
                  </h3>
                  <p className="text-sm text-[#475569] leading-relaxed">{f.desc}</p>
                </div>
              </div>
            ))}
          </div>

          {/* WhatsApp mockup callout */}
          <div className="mt-10 rounded-2xl border border-[#bfdbfe] bg-[#eff6ff] p-7 flex flex-col sm:flex-row items-center gap-6">
            <div className="w-16 h-16 rounded-2xl bg-[#1d4ed8] flex items-center justify-center shrink-0">
              <MessageSquare className="w-8 h-8 text-white" />
            </div>
            <div>
              <p
                className="font-bold text-[#1d4ed8] mb-1"
                style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
              >
                Accessible on any phone — no smartphone required.
              </p>
              <p className="text-sm text-[#475569] leading-relaxed">
                Our conversational interface runs over WhatsApp and USSD, ensuring mothers in areas
                with limited data or older devices still receive full, uninterrupted care.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ══ Target Users ════════════════════════════════════════════════════ */}
      <section id="users" className="py-20 px-5" style={{ background: "#fdf2f8" }}>
        <div className="max-w-6xl mx-auto grid md:grid-cols-2 gap-12 items-center">
          <div>
            <SectionLabel pink>Who We Serve</SectionLabel>
            <SectionHeading>Who We Serve</SectionHeading>
            <p className="mt-5 text-[#475569] text-base leading-relaxed mb-6">
              Our primary users are adolescent mothers (15–19) and women in rural or ASAL regions.
              We also build tools to empower Community Health Promoters (CHPs) to triage and monitor
              their cohorts effectively.
            </p>

            <div className="flex flex-col gap-4">
              {[
                { label: "Adolescent Mothers (15–19)", sub: "Primary target — highest vulnerability, lowest access", color: "#ec4899" },
                { label: "Rural & ASAL Women", sub: "Underserved geography, limited facility access", color: "#1d4ed8" },
                { label: "Community Health Promoters", sub: "Power users managing cohorts of 20–50 mothers", color: "#0369a1" },
              ].map((u) => (
                <div
                  key={u.label}
                  className="flex items-start gap-4 bg-white rounded-xl p-5 border border-[#fce7f3]"
                >
                  <span
                    className="w-3 h-3 rounded-full shrink-0 mt-1.5"
                    style={{ background: u.color }}
                  />
                  <div>
                    <p
                      className="font-bold text-sm text-[#0f172a]"
                      style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
                    >
                      {u.label}
                    </p>
                    <p className="text-xs text-[#64748b] mt-0.5">{u.sub}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Photo */}
          <div className="rounded-3xl overflow-hidden border border-[#fce7f3] bg-pink-50">
            <img
              src={woman1}
              alt="A community health worker speaking with a young mother in a rural setting"
              className="w-full h-72 md:h-full object-cover"
            />
          </div>
        </div>
      </section>

      {/* ══ Vision ══════════════════════════════════════════════════════════ */}
      <section id="vision" className="py-20 px-5 bg-[#1d4ed8]">
        <div className="max-w-4xl mx-auto text-center">
          <p className="text-xs font-bold tracking-[0.18em] uppercase text-[#93c5fd] mb-4">
            Our Vision
          </p>
          <h2
            className="text-3xl md:text-5xl font-extrabold text-white leading-tight mb-6"
            style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
          >
            Our Vision
          </h2>
          <p className="text-[#bfdbfe] text-lg leading-relaxed max-w-2xl mx-auto mb-12">
            To provide continuous, culturally adapted maternal care from conception to postpartum,
            acting as a digital bridge between marginalized mothers and their health networks.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {[
              { icon: "🌍", heading: "Pan-African Reach", body: "Starting in Kenya, scaling to ASAL and East African markets by 2027." },
              { icon: "🤝", heading: "Health System Integration", body: "Embedded within national Community Health Strategy — not parallel to it." },
              { icon: "📊", heading: "Evidence-Driven", body: "Every intervention tracked against WHO maternal health indicators." },
            ].map((v) => (
              <div
                key={v.heading}
                className="rounded-2xl bg-white/10 border border-white/20 p-6 text-left"
              >
                <span className="text-3xl mb-4 block">{v.icon}</span>
                <p
                  className="font-bold text-white mb-2"
                  style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
                >
                  {v.heading}
                </p>
                <p className="text-sm text-[#bfdbfe] leading-relaxed">{v.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ══ Team ════════════════════════════════════════════════════════════ */}
      <section id="team" className="py-20 px-5 bg-white">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <SectionLabel pink>Our Team</SectionLabel>
            <SectionHeading>The Innovators Behind the Platform</SectionHeading>
            <p className="mt-4 text-[#475569] max-w-xl mx-auto text-sm leading-relaxed">
              A multidisciplinary team of engineers, health researchers, and designers united
              by a shared belief that technology can close the maternal care gap.
            </p>
          </div>

          {/* Row of 3 */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-7 mb-7">
            {TEAM.slice(0, 3).map((m) => (
              <TeamCard key={m.name} member={m} />
            ))}
          </div>

          {/* Row of 2 — centered */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-7 sm:max-w-2xl mx-auto">
            {TEAM.slice(3).map((m) => (
              <TeamCard key={m.name} member={m} />
            ))}
          </div>
        </div>
      </section>

      {/* ══ Footer ══════════════════════════════════════════════════════════ */}
      <footer className="border-t border-[#dbeafe] bg-[#f8fafc] py-10 px-5">
        <div className="max-w-6xl mx-auto">
          {/* Top row */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
            {/* Brand */}
            <div>
              <div className="flex items-center gap-2.5 mb-4">
                <span
                  className="w-8 h-8 rounded-lg flex items-center justify-center"
                  style={{ background: "#1d4ed8" }}
                >
                  <Heart className="w-4 h-4 text-white" fill="white" />
                </span>
                <span
                  className="text-base font-extrabold text-[#1d4ed8]"
                  style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
                >
                  Nurture
                </span>
              </div>
              <p className="text-sm text-[#64748b] leading-relaxed">
                Bridging the gap in maternal health through AI-powered care.
              </p>
            </div>

            {/* Quick Links */}
            <div>
              <h3 
                className="text-sm font-bold text-[#0f172a] mb-4"
                style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
              >
                Quick Links
              </h3>
              <ul className="space-y-2">
                {NAV.map((n) => (
                  <li key={n.id}>
                    <button
                      onClick={() => goto(n.id)}
                      className="text-sm text-[#64748b] hover:text-[#1d4ed8] transition-colors"
                    >
                      {n.label}
                    </button>
                  </li>
                ))}
              </ul>
            </div>

            {/* Contact */}
            <div>
              <h3 
                className="text-sm font-bold text-[#0f172a] mb-4"
                style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
              >
                Contact
              </h3>
              <div className="space-y-2">
                <a
                  href="mailto:hello@afyaventures.co.ke"
                  className="text-sm text-[#64748b] hover:text-[#1d4ed8] transition-colors block"
                >
                  hello@nurture.co.ke
                </a>
                <p className="text-sm text-[#64748b]">
                  Nairobi, Kenya
                </p>
              </div>
            </div>

            {/* Partners */}
            <div>
              <h3 
                className="text-sm font-bold text-[#0f172a] mb-4"
                style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
              >
                Partners
              </h3>
              <ul className="space-y-2">
                {PARTNERS.map((p) => (
                  <li key={p.name}>
                    <a
                      href={p.href}
                      className="flex items-center gap-1 text-sm text-[#64748b] hover:text-[#1d4ed8] transition-colors"
                    >
                      {p.name}
                      <ExternalLink className="w-3 h-3 opacity-60" />
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Bottom row */}
          <div className="border-t border-[#dbeafe] pt-6 flex flex-col sm:flex-row items-center justify-between gap-3">
            <p className="text-xs text-[#94a3b8]">
              © 2025 Nurture. All rights reserved.
            </p>
            <p className="text-xs text-[#94a3b8]">
              Built with purpose — for every mother Kenya's system has left behind.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

/* ─── Team Card ─────────────────────────────────────────────────────────── */

type Member = {
  name: string;
  role: string;
  photo: string;
  linkedin: string;
  github: string;
};

function TeamCard({ member: m }: { member: Member }) {
  return (
    <div className="flex flex-col items-center text-center group">
      {/* Circular photo */}
      <div className="relative mb-5">
        <div
          className="w-28 h-28 rounded-full overflow-hidden border-4 border-[#dbeafe] bg-[#eff6ff]"
          style={{ transition: "border-color 0.2s" }}
        >
          <img
            src={m.photo}
            alt={`${m.name}, ${m.role}`}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
        </div>
        {/* Pink ring on hover */}
        <div className="absolute inset-0 rounded-full border-4 border-transparent group-hover:border-[#ec4899] transition-all duration-300 pointer-events-none" />
      </div>

      <h3
        className="text-base font-bold text-[#0f172a] mb-0.5"
        style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
      >
        {m.name}
      </h3>
      <p className="text-xs text-[#64748b] mb-4 leading-snug max-w-[180px]">{m.role}</p>

      {/* Social links */}
      <div className="flex items-center gap-3">
        <a
          href={m.linkedin}
          aria-label={`${m.name} LinkedIn`}
          className="w-8 h-8 rounded-full border border-[#bfdbfe] bg-[#eff6ff] flex items-center justify-center text-[#1d4ed8] hover:bg-[#1d4ed8] hover:text-white transition-colors"
        >
          <FaLinkedin className="w-3.5 h-3.5" />
        </a>
        <a
          href={m.github}
          aria-label={`${m.name} GitHub`}
          className="w-8 h-8 rounded-full border border-[#fce7f3] bg-[#fdf2f8] flex items-center justify-center text-[#ec4899] hover:bg-[#ec4899] hover:text-white transition-colors"
        >
          <FaGithub className="w-3.5 h-3.5" />
        </a>
      </div>
    </div>
  );
}