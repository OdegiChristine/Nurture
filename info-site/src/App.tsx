import { useState, useRef, useEffect, useLayoutEffect } from "react";
import { motion } from "motion/react";
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
  ChevronLeft,
  ChevronRight,
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

const STATS = [
  { end: 362, suffix: "",  unit: "deaths per 100k",  label: "Kenya maternal mortality ratio" },
  { end: 45,  suffix: "%", unit: "of births",         label: "have no skilled attendant" },
  { end: 70,  suffix: "%", unit: "of Kenyans",        label: "use mobile phones" },
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

const CORE_VALUES = [
  {
    emoji: "🤝",
    title: "Empathy First",
    body: "We design every feature with the emotional reality of our users at the centre — their fears, their dignity, and their strength guide every product decision we make.",
    accent: "#ec4899",
    bg: "#fdf2f8",
    border: "#fce7f3",
  },
  {
    emoji: "📡",
    title: "Radical Access",
    body: "If a solution cannot reach a mother in Turkana County on a 2G connection, it is not a solution. We build for the last mile first and let everything else follow.",
    accent: "#1d4ed8",
    bg: "#eff6ff",
    border: "#bfdbfe",
  },
  {
    emoji: "🔬",
    title: "Evidence-Based Care",
    body: "Every recommendation we deliver is grounded in WHO clinical guidelines and peer-reviewed community health research — we do not guess with mothers' lives.",
    accent: "#0369a1",
    bg: "#f0f9ff",
    border: "#bae6fd",
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

/* ─── Hooks ─────────────────────────────────────────────────────────────── */

function useCountUp(end: number, duration = 1800) {
  const [count, setCount] = useState(0);
  const [started, setStarted] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) setStarted(true); },
      { threshold: 0.5 }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (!started) return;
    let startTime: number | null = null;
    const step = (ts: number) => {
      if (!startTime) startTime = ts;
      const progress = Math.min((ts - startTime) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setCount(Math.floor(eased * end));
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }, [started, end, duration]);

  return { count, ref };
}

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

/* ── Animated stat counter ─────────────────────────────────────────────── */

function StatCounter({ stat }: { stat: typeof STATS[number] }) {
  const { count, ref } = useCountUp(stat.end);
  return (
    <div ref={ref} className="text-center px-6 py-10">
      <p
        className="text-5xl font-extrabold text-[#1d4ed8] leading-none tabular-nums"
        style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
      >
        {count}{stat.suffix}
      </p>
      <p className="text-[11px] text-[#ec4899] font-bold uppercase tracking-widest mt-2">
        {stat.unit}
      </p>
      <p className="text-xs text-[#64748b] mt-1">{stat.label}</p>
    </div>
  );
}

/* ── Problem card with hover lift + shadow ─────────────────────────────── */

function ProblemCard({ p }: { p: typeof PROBLEMS[number] }) {
  const [hovered, setHovered] = useState(false);
  return (
    <div
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      className="rounded-2xl border p-7 flex flex-col gap-5 cursor-default"
      style={{
        background: p.bg,
        borderColor: hovered ? p.color + "55" : p.color + "22",
        boxShadow: hovered
          ? `0 20px 48px -8px ${p.shadow}, 0 6px 16px -4px ${p.shadow}`
          : "0 1px 3px rgba(0,0,0,0.04)",
        transform: hovered ? "translateY(-8px)" : "translateY(0)",
        transition:
          "transform 0.3s cubic-bezier(0.34,1.56,0.64,1), box-shadow 0.3s ease, border-color 0.2s ease",
      }}
    >
      <span
        className="w-14 h-14 rounded-2xl flex items-center justify-center shrink-0"
        style={{
          background: hovered ? p.color : p.color + "15",
          color: hovered ? "#fff" : p.color,
          transition: "background 0.22s ease, color 0.22s ease",
        }}
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
  );
}

/* ── Core values carousel ───────────────────────────────────────────────── */

function ValuesCarousel() {
  const total = CORE_VALUES.length;
  const viewportRef = useRef<HTMLDivElement>(null);
  const [viewportWidth, setViewportWidth] = useState(0);
  const [isDesktop, setIsDesktop] = useState(false);
  const [visualIndex, setVisualIndex] = useState(total);
  const [shouldAnimate, setShouldAnimate] = useState(true);
  const active = ((visualIndex % total) + total) % total;
  const gap = isDesktop ? 24 : 16;
  const cardWidth = isDesktop
    ? Math.max(0, (viewportWidth - gap * 2) / 3)
    : viewportWidth;
  const step = cardWidth + gap;
  const trackX = viewportWidth / 2 - cardWidth / 2 - visualIndex * step;
  const repeatedValues = [...CORE_VALUES, ...CORE_VALUES, ...CORE_VALUES];

  useLayoutEffect(() => {
    const viewport = viewportRef.current;
    if (!viewport) return;

    const updateMeasurements = () => {
      setViewportWidth(viewport.clientWidth);
      setIsDesktop(window.matchMedia("(min-width: 640px)").matches);
    };
    const observer = new ResizeObserver(updateMeasurements);

    updateMeasurements();
    observer.observe(viewport);
    return () => observer.disconnect();
  }, []);

  const moveBy = (delta: number) => {
    if (!shouldAnimate) return;
    setVisualIndex((index) => index + delta);
  };

  const goPrev = () => moveBy(-1);
  const goNext = () => moveBy(1);

  const goTo = (index: number) => {
    const forward = (index - active + total) % total;
    if (forward === 0) return;
    moveBy(forward <= total / 2 ? forward : forward - total);
  };

  const normalizeTrack = () => {
    if (visualIndex >= total * 2) {
      setShouldAnimate(false);
      setVisualIndex((index) => index - total);
      requestAnimationFrame(() => setShouldAnimate(true));
    } else if (visualIndex < total) {
      setShouldAnimate(false);
      setVisualIndex((index) => index + total);
      requestAnimationFrame(() => setShouldAnimate(true));
    }
  };

  const Controls = () => (
    <div className="flex items-center justify-center gap-5 mt-10">
      <button
        onClick={goPrev}
        aria-label="Previous value"
        className="w-10 h-10 rounded-full border border-[#bfdbfe] bg-white flex items-center justify-center text-[#1d4ed8] hover:bg-[#eff6ff] transition-colors"
      >
        <ChevronLeft className="w-5 h-5" />
      </button>

      <div className="flex items-center gap-2">
        {CORE_VALUES.map((_, i) => (
          <button
            key={i}
            onClick={() => goTo(i)}
            aria-label={`Go to value ${i + 1}`}
            aria-current={i === active ? "true" : undefined}
            className="rounded-full transition-all duration-300"
            style={{
              width: i === active ? "24px" : "8px",
              height: "8px",
              background: i === active ? "#1d4ed8" : "#cbd5e1",
            }}
          />
        ))}
      </div>

      <button
        onClick={goNext}
        aria-label="Next value"
        className="w-10 h-10 rounded-full border border-[#bfdbfe] bg-white flex items-center justify-center text-[#1d4ed8] hover:bg-[#eff6ff] transition-colors"
      >
        <ChevronRight className="w-5 h-5" />
      </button>
    </div>
  );

  return (
    <div className="w-full">
      <div
        ref={viewportRef}
        className="w-full overflow-hidden pt-5 pb-2 touch-pan-y"
      >
        <motion.div
          className="flex items-end"
          style={{ gap }}
          animate={{ x: trackX }}
          transition={
            shouldAnimate
              ? { type: "spring", stiffness: 260, damping: 30, mass: 0.85 }
              : { duration: 0 }
          }
          onAnimationComplete={normalizeTrack}
          drag="x"
          dragConstraints={{ left: 0, right: 0 }}
          dragElastic={0.08}
          onDragEnd={(_, info) => {
            if (info.offset.x < -55 || info.velocity.x < -450) goNext();
            if (info.offset.x > 55 || info.velocity.x > 450) goPrev();
          }}
        >
          {repeatedValues.map((v, index) => {
            const valueIndex = index % total;
            const isActive = index === visualIndex;
            const isVisible = isDesktop
              ? Math.abs(index - visualIndex) <= 1
              : isActive;

          return (
            <motion.button
              key={`${v.title}-${index}`}
              onClick={() => goTo(valueIndex)}
              tabIndex={isVisible ? 0 : -1}
              aria-hidden={!isVisible}
              className="shrink-0 text-left rounded-2xl border outline-none p-6 focus-visible:ring-2 focus-visible:ring-[#1d4ed8] focus-visible:ring-offset-2"
              animate={{
                y: isDesktop && isActive ? -16 : 0,
                scale: isDesktop && isActive ? 1.03 : 1,
                opacity: isDesktop ? (isActive ? 1 : 0.55) : 1,
              }}
              transition={{ type: "spring", stiffness: 260, damping: 28 }}
              style={{
                width: cardWidth,
                background: isActive ? v.bg : "#f8fafc",
                borderColor: isActive ? v.border : "rgba(0,0,0,0.07)",
                boxShadow: isActive
                  ? `0 24px 52px -10px ${v.accent}28, 0 6px 16px -4px ${v.accent}18`
                  : "0 1px 4px rgba(0,0,0,0.05)",
                minHeight: isDesktop ? (isActive ? "270px" : "220px") : "270px",
              }}
            >
              <span className="text-4xl mb-5 block">{v.emoji}</span>
              <h3
                className="font-extrabold mb-3"
                style={{
                  fontFamily: "'Plus Jakarta Sans', sans-serif",
                  color: isActive ? v.accent : "#0f172a",
                  fontSize: isActive ? "1.125rem" : "1rem",
                  transition: "color 0.25s ease, font-size 0.25s ease",
                }}
              >
                {v.title}
              </h3>
              <p
                style={{
                  color: isActive ? "#374151" : "#94a3b8",
                  fontSize: isActive ? "0.875rem" : "0.8rem",
                  lineHeight: "1.6",
                  transition: "color 0.25s ease",
                }}
              >
                {v.body}
              </p>
            </motion.button>
          );
        })}
        </motion.div>
      </div>

      <p className="sr-only" aria-live="polite">
        Showing {CORE_VALUES[active].title}, value {active + 1} of {total}
      </p>
      <Controls />
    </div>
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
        className="pt-58 pb-42 px-5 bg-cover bg-center relative"
        style={{ backgroundImage: `url(${heroImage})` }}
      >
        <div className="absolute inset-0 bg-white/80" />
        <div className="max-w-4xl mx-auto text-center relative z-10">
          
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
        </div>
      </section>

      {/* ══ Stats — count-up on scroll ═══════════════════════════════════════ */}
      <section className="bg-white border-b border-[#dbeafe]">
        <div className="max-w-4xl mx-auto grid grid-cols-1 sm:grid-cols-3 divide-y sm:divide-y-0 sm:divide-x divide-[#dbeafe]">
          {STATS.map((s) => (
            <StatCounter key={s.label} stat={s} />
          ))}
        </div>
      </section>

      {/* ══ Problem ═════════════════════════════════════════════════════════ */}
      <section id="problem" className="py-20 px-5" style={{ background: "#f8fafc" }}>
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <SectionLabel pink>The Problem</SectionLabel>
            <SectionHeading>The Maternal Health Crisis</SectionHeading>
            <p className="mt-4 text-[#475569] max-w-xl mx-auto text-base leading-relaxed">
              Kenya's maternal mortality rate remains tragically high — driven by three systemic,
              addressable failures.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {PROBLEMS.map((p) => <ProblemCard key={p.title} p={p} />)}
          </div>
        </div>
      </section>

      {/* ══ Solution ════════════════════════════════════════════════════════ */}
      <section id="solution" className="py-20 px-5 bg-white">
        <div className="max-w-6xl mx-auto">
          <div className="mb-12 max-w-2xl">
            <SectionLabel>The Solution</SectionLabel>
            <SectionHeading>Continuous,&nbsp;Stigma-Free Support</SectionHeading>
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

      {/* ══ Vision — statement only ══════════════════════════════════════════ */}
      <section id="vision" className="py-24 px-5 bg-[#1d4ed8]">
        <div className="max-w-3xl mx-auto text-center">
          <p className="text-xs font-bold tracking-[0.18em] uppercase text-[#93c5fd] mb-6">
            Our Vision
          </p>
          <span
            className="block text-[120px] leading-none text-white/10 select-none -mb-8"
            style={{ fontFamily: "Georgia, serif" }}
          >
            "
          </span>
          <h2
            className="text-3xl md:text-5xl font-extrabold text-white leading-[1.15] mb-8"
            style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
          >
            To provide continuous, culturally adapted maternal care from conception to postpartum —
            acting as a digital bridge between marginalized mothers and their health networks.
          </h2>
          <div className="w-16 h-1 bg-[#ec4899] rounded-full mx-auto" />
        </div>
      </section>

      {/* ══ Core Values carousel ════════════════════════════════════════════ */}
      <section className="py-20 px-5 bg-white overflow-hidden">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-14">
            <SectionLabel>What We Stand For</SectionLabel>
            <SectionHeading>Our Core Values</SectionHeading>
            <p className="mt-4 text-[#475569] max-w-lg mx-auto text-sm leading-relaxed">
              Three principles that shape every line of code, every design decision, and every
              community partnership we make.
            </p>
          </div>
          <ValuesCarousel />
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